"""
Confluence Knowledge Base

Handles loading, indexing, and searching of Confluence documentation.
Implements RAG (Retrieval-Augmented Generation) with vector embeddings for semantic search.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field

# Vector database and embeddings
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Install with: pip install chromadb")

# Google embeddings
try:
    import google.generativeai as genai
    from google.generativeai import embed_content
    GOOGLE_EMBEDDINGS_AVAILABLE = True
except ImportError:
    GOOGLE_EMBEDDINGS_AVAILABLE = False
    logging.warning("Google GenerativeAI not available. Install with: pip install google-generativeai")

from ..config.settings import get_data_config

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of a document for vector search."""
    chunk_id: str
    document_id: str
    title: str
    content: str
    chunk_index: int
    url: str
    space_key: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfluenceDocument:
    """Represents a Confluence document with metadata."""
    id: str
    title: str
    content: str
    url: str
    last_updated: str
    space_key: str
    space_name: Optional[str] = None
    author: Optional[str] = None
    labels: Optional[List[str]] = None
    chunks: Optional[List[DocumentChunk]] = None


class ConfluenceKnowledgeBase:
    """
    Manages Confluence knowledge base operations with RAG support.

    Provides functionality to load, index, and search Confluence documents
    using both keyword matching and semantic vector search.
    """

    def __init__(self, data_dir: Optional[str] = None, use_embeddings: bool = True):
        """
        Initialize the knowledge base.

        Args:
            data_dir: Directory containing Confluence data. If None, uses config default.
            use_embeddings: Whether to use vector embeddings for search (default: True)
        """
        self.config = get_data_config()
        self.data_dir = Path(data_dir or self.config["data_dir"])
        self.documents: List[ConfluenceDocument] = []
        self.index_file = self.data_dir / self.config["index_file"]

        # Vector search configuration
        self.use_embeddings = use_embeddings and CHROMADB_AVAILABLE and GOOGLE_EMBEDDINGS_AVAILABLE
        self.vector_db = None
        self.collection = None
        self.embedding_model = "models/text-embedding-004"  # Google's latest embedding model
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks
        self.relevance_threshold = 0.4   # Minimum similarity score to consider relevant (more permissive)

        # Initialize Google AI if available
        if self.use_embeddings:
            self._initialize_embeddings()

        # Load documents on initialization
        self._load_documents()

    def _initialize_embeddings(self) -> None:
        """Initialize the vector database and embedding model."""
        try:
            # Configure Google AI
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.warning("GOOGLE_API_KEY not found. Falling back to keyword search.")
                self.use_embeddings = False
                return

            genai.configure(api_key=api_key)

            # Initialize ChromaDB
            vector_db_path = self.data_dir / "vector_db"
            vector_db_path.mkdir(exist_ok=True)

            self.vector_db = chromadb.PersistentClient(
                path=str(vector_db_path),
                settings=Settings(anonymized_telemetry=False)
            )

            # Get or create collection
            collection_name = "confluence_documents"
            try:
                self.collection = self.vector_db.get_collection(collection_name)
                logger.info(f"Using existing vector collection: {collection_name}")
            except:
                self.collection = self.vector_db.create_collection(
                    name=collection_name,
                    metadata={"description": "Confluence document chunks with embeddings"}
                )
                logger.info(f"Created new vector collection: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            self.use_embeddings = False

    def _chunk_document(self, doc: ConfluenceDocument) -> List[DocumentChunk]:
        """
        Split a document into chunks for vector indexing.

        Args:
            doc: Document to chunk

        Returns:
            List of document chunks
        """
        chunks = []
        content = f"{doc.title}\n\n{doc.content}"

        # Simple chunking by character count with overlap
        start = 0
        chunk_index = 0

        while start < len(content):
            end = start + self.chunk_size

            # Try to break at sentence boundaries
            if end < len(content):
                # Look for sentence endings within the last 100 characters
                sentence_end = content.rfind('.', start, end)
                if sentence_end > start + self.chunk_size - 100:
                    end = sentence_end + 1

            chunk_content = content[start:end].strip()

            if chunk_content:
                chunk = DocumentChunk(
                    chunk_id=f"{doc.id}_chunk_{chunk_index}",
                    document_id=doc.id,
                    title=doc.title,
                    content=chunk_content,
                    chunk_index=chunk_index,
                    url=doc.url,
                    space_key=doc.space_key,
                    metadata={
                        "author": doc.author,
                        "last_updated": doc.last_updated,
                        "space_name": doc.space_name,
                        "labels": doc.labels or []
                    }
                )
                chunks.append(chunk)
                chunk_index += 1

            # Move start position with overlap
            start = max(start + self.chunk_size - self.chunk_overlap, end)

            if start >= len(content):
                break

        return chunks

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text using Google's embedding model.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if failed
        """
        try:
            # Use Google's embedding model
            result = embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    def _index_document_chunks(self, doc: ConfluenceDocument) -> None:
        """
        Index document chunks in the vector database.

        Args:
            doc: Document to index
        """
        if not self.use_embeddings or not self.collection:
            return

        chunks = self._chunk_document(doc)
        doc.chunks = chunks

        if not chunks:
            return

        # Prepare data for ChromaDB
        chunk_ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks:
            # Generate embedding
            embedding = self._generate_embedding(chunk.content)
            if embedding is None:
                continue

            chunk_ids.append(chunk.chunk_id)
            embeddings.append(embedding)
            documents.append(chunk.content)
            metadatas.append({
                "document_id": chunk.document_id,
                "title": chunk.title,
                "chunk_index": chunk.chunk_index,
                "url": chunk.url,
                "space_key": chunk.space_key,
                "author": chunk.metadata.get("author") or "",
                "last_updated": chunk.metadata.get("last_updated") or "",
                "space_name": chunk.metadata.get("space_name") or "",
                "labels": ",".join(chunk.metadata.get("labels") or [])
            })

        if chunk_ids:
            try:
                # Check if chunks already exist and remove them
                existing_ids = set()
                try:
                    existing_results = self.collection.get(
                        where={"document_id": doc.id}
                    )
                    existing_ids = set(existing_results['ids'])
                    if existing_ids:
                        self.collection.delete(ids=list(existing_ids))
                        logger.debug(f"Removed {len(existing_ids)} existing chunks for document {doc.id}")
                except:
                    pass  # Collection might be empty

                # Add new chunks
                self.collection.add(
                    ids=chunk_ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
                logger.debug(f"Indexed {len(chunk_ids)} chunks for document {doc.id}")

            except Exception as e:
                logger.error(f"Failed to index chunks for document {doc.id}: {e}")
    
    def _load_documents(self) -> None:
        """Load all documents from the data directory."""
        if not self.index_file.exists():
            logger.warning(f"Index file not found: {self.index_file}. Creating empty knowledge base.")
            return
        
        try:
            with open(self.index_file, 'r', encoding=self.config["encoding"]) as f:
                index_data = json.load(f)
            
            loaded_count = 0
            for page_meta in index_data:
                if self._load_document(page_meta):
                    loaded_count += 1
            
            logger.info(f"Successfully loaded {loaded_count} documents from {self.data_dir}")
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
    
    def _load_document(self, page_meta: Dict[str, Any]) -> bool:
        """
        Load a single document from metadata.
        
        Args:
            page_meta: Document metadata from index
            
        Returns:
            bool: True if document was loaded successfully
        """
        try:
            space_key = page_meta.get("space_key", "")
            page_id = page_meta.get("id", "")
            
            if not space_key or not page_id:
                logger.warning(f"Invalid metadata: missing space_key or id")
                return False
            
            page_file = self.data_dir / space_key / f"{page_id}.json"
            
            if not page_file.exists():
                logger.warning(f"Document file not found: {page_file}")
                return False
            
            # Check file size
            if page_file.stat().st_size > self.config["max_file_size"]:
                logger.warning(f"Document too large: {page_file}")
                return False
            
            with open(page_file, 'r', encoding=self.config["encoding"]) as f:
                page_data = json.load(f)
            
            metadata = page_data.get("metadata", {})
            
            doc = ConfluenceDocument(
                id=page_id,
                title=metadata.get("title", "Untitled"),
                content=page_data.get("content", ""),
                url=metadata.get("url", ""),
                last_updated=metadata.get("last_updated", ""),
                space_key=space_key,
                space_name=metadata.get("space_name"),
                author=metadata.get("author"),
                labels=metadata.get("labels", [])
            )
            
            self.documents.append(doc)

            # Index document chunks for vector search
            if self.use_embeddings:
                self._index_document_chunks(doc)

            return True
            
        except Exception as e:
            logger.error(f"Error loading document {page_meta}: {e}")
            return False
    
    def search(self, query: str, limit: Optional[int] = None) -> List[ConfluenceDocument]:
        """
        Search documents using vector similarity or keyword matching.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of matching documents sorted by relevance
        """
        if not query.strip():
            return []

        limit = limit or self.config["search_limit"]

        # Use vector search if available, otherwise fall back to keyword search
        if self.use_embeddings and self.collection:
            return self._vector_search(query, limit)
        else:
            return self._keyword_search(query, limit)

    def _vector_search(self, query: str, limit: int) -> List[ConfluenceDocument]:
        """
        Perform semantic search using vector embeddings.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of matching documents sorted by semantic similarity
        """
        try:
            # Generate embedding for the query
            query_embedding = self._generate_embedding(query)
            if query_embedding is None:
                logger.warning("Failed to generate query embedding, falling back to keyword search")
                return self._keyword_search(query, limit)

            # Search vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(limit * 3, 50),  # Get more chunks to find diverse documents
                include=["documents", "metadatas", "distances"]
            )

            if not results['ids'] or not results['ids'][0]:
                return []

            # Group chunks by document and calculate document scores
            doc_scores = {}
            doc_chunks = {}

            for i, _ in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                document_id = metadata['document_id']
                distance = results['distances'][0][i]

                # Convert distance to similarity score (lower distance = higher similarity)
                similarity = 1.0 - distance

                if document_id not in doc_scores:
                    doc_scores[document_id] = []
                    doc_chunks[document_id] = []

                doc_scores[document_id].append(similarity)
                doc_chunks[document_id].append({
                    'content': results['documents'][0][i],
                    'metadata': metadata,
                    'similarity': similarity
                })

            # Calculate final document scores (average of top chunks)
            final_scores = []
            for doc_id, scores in doc_scores.items():
                # Use the average of the top 2 chunk scores for each document
                top_scores = sorted(scores, reverse=True)[:2]
                avg_score = sum(top_scores) / len(top_scores)

                # Only include documents that meet the relevance threshold
                logger.debug(f"Document {doc_id} avg_score: {avg_score:.3f}, threshold: {self.relevance_threshold}")
                if avg_score >= self.relevance_threshold:
                    final_scores.append((avg_score, doc_id))

            # Sort by score and get top documents
            final_scores.sort(key=lambda x: x[0], reverse=True)

            # Return documents in order of relevance
            result_docs = []
            for score, doc_id in final_scores[:limit]:
                doc = self.get_document_by_id(doc_id)
                if doc:
                    result_docs.append(doc)

            return result_docs

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return self._keyword_search(query, limit)

    def _keyword_search(self, query: str, limit: int) -> List[ConfluenceDocument]:
        """
        Search documents using keyword matching (fallback method).

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of matching documents sorted by relevance
        """
        query_terms = query.lower().split()

        # Score documents based on term frequency and position
        scored_docs = []

        for doc in self.documents:
            score = self._calculate_relevance_score(doc, query_terms)
            # Only include documents with meaningful relevance (at least 5 points for stricter matching)
            if score >= 5.0:
                scored_docs.append((score, doc))

        # Sort by score (descending) and return top results
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs[:limit]]
    
    def _calculate_relevance_score(self, doc: ConfluenceDocument, query_terms: List[str]) -> float:
        """
        Calculate relevance score for a document.
        
        Args:
            doc: Document to score
            query_terms: List of query terms
            
        Returns:
            float: Relevance score
        """
        score = 0.0
        
        # Combine searchable text
        title_text = doc.title.lower()
        content_text = doc.content.lower()
        
        for term in query_terms:
            # Title matches are weighted higher
            title_matches = title_text.count(term)
            content_matches = content_text.count(term)
            
            # Scoring weights
            score += title_matches * 3.0  # Title matches worth more
            score += content_matches * 1.0  # Content matches
            
            # Bonus for exact phrase matches
            if term in title_text:
                score += 2.0
        
        return score
    
    def get_document_by_id(self, doc_id: str) -> Optional[ConfluenceDocument]:
        """
        Get a document by its ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        return None
    
    def get_documents_by_space(self, space_key: str) -> List[ConfluenceDocument]:
        """
        Get all documents from a specific space.
        
        Args:
            space_key: Confluence space key
            
        Returns:
            List of documents in the space
        """
        return [doc for doc in self.documents if doc.space_key == space_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics.

        Returns:
            Dict containing statistics
        """
        spaces = set(doc.space_key for doc in self.documents)
        total_content_length = sum(len(doc.content) for doc in self.documents)

        # Vector database stats
        vector_stats = {}
        if self.use_embeddings and self.collection:
            try:
                collection_count = self.collection.count()
                vector_stats = {
                    "vector_search_enabled": True,
                    "total_chunks": collection_count,
                    "embedding_model": self.embedding_model,
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap
                }
            except Exception as e:
                vector_stats = {
                    "vector_search_enabled": True,
                    "error": str(e)
                }
        else:
            vector_stats = {
                "vector_search_enabled": False,
                "reason": "ChromaDB or Google embeddings not available"
            }

        return {
            "total_documents": len(self.documents),
            "total_spaces": len(spaces),
            "spaces": list(spaces),
            "total_content_length": total_content_length,
            "average_content_length": (
                total_content_length / len(self.documents) if self.documents else 0
            ),
            "data_directory": str(self.data_dir),
            "index_file": str(self.index_file),
            "vector_search": vector_stats
        }

    def reindex_embeddings(self) -> bool:
        """
        Reindex all documents in the vector database.

        Returns:
            bool: True if successful
        """
        if not self.use_embeddings or not self.collection:
            logger.warning("Vector search not available for reindexing")
            return False

        try:
            # Clear existing collection
            self.collection.delete()
            logger.info("Cleared existing vector index")

            # Reindex all documents
            for doc in self.documents:
                self._index_document_chunks(doc)

            logger.info(f"Successfully reindexed {len(self.documents)} documents")
            return True

        except Exception as e:
            logger.error(f"Failed to reindex embeddings: {e}")
            return False
