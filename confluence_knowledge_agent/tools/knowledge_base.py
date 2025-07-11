"""
Confluence Knowledge Base

Handles loading, indexing, and searching of Confluence documentation.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from ..config.settings import get_data_config

logger = logging.getLogger(__name__)


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


class ConfluenceKnowledgeBase:
    """
    Manages Confluence knowledge base operations.
    
    Provides functionality to load, index, and search Confluence documents
    following ADK best practices for tool implementation.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the knowledge base.
        
        Args:
            data_dir: Directory containing Confluence data. If None, uses config default.
        """
        self.config = get_data_config()
        self.data_dir = Path(data_dir or self.config["data_dir"])
        self.documents: List[ConfluenceDocument] = []
        self.index_file = self.data_dir / self.config["index_file"]
        
        # Load documents on initialization
        self._load_documents()
    
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
            return True
            
        except Exception as e:
            logger.error(f"Error loading document {page_meta}: {e}")
            return False
    
    def search(self, query: str, limit: Optional[int] = None) -> List[ConfluenceDocument]:
        """
        Search documents using keyword matching.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching documents sorted by relevance
        """
        if not query.strip():
            return []
        
        limit = limit or self.config["search_limit"]
        query_terms = query.lower().split()
        
        # Score documents based on term frequency and position
        scored_docs = []
        
        for doc in self.documents:
            score = self._calculate_relevance_score(doc, query_terms)
            if score > 0:
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
        
        return {
            "total_documents": len(self.documents),
            "total_spaces": len(spaces),
            "spaces": list(spaces),
            "total_content_length": total_content_length,
            "average_content_length": (
                total_content_length / len(self.documents) if self.documents else 0
            ),
            "data_directory": str(self.data_dir),
            "index_file": str(self.index_file)
        }
