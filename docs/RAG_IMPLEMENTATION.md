# RAG (Retrieval-Augmented Generation) Implementation

This document explains the advanced RAG-based search system implemented in the Confluence Knowledge Agent, which replaces simple keyword matching with semantic vector search.

## 🎯 Overview

The system now uses **Google's text-embedding-004 model** with **ChromaDB vector database** to provide semantic search capabilities that understand meaning and context, not just exact keyword matches.

## 🏗️ Architecture

### Components

1. **Text Embeddings**: Google's `text-embedding-004` model
2. **Vector Database**: ChromaDB for storing and querying embeddings
3. **Document Chunking**: Smart text splitting with overlap
4. **Semantic Search**: Cosine similarity-based retrieval
5. **Fallback System**: Keyword search when vector search unavailable

### Data Flow

```
User Query → Embedding Generation → Vector Search → Document Retrieval → Response Generation
     ↓              ↓                    ↓               ↓                ↓
"Deploy apps" → [0.1, 0.3, ...] → ChromaDB Query → Relevant Chunks → Formatted Answer
```

## 🔧 Implementation Details

### Document Processing

**1. Document Loading**
- Documents loaded from `confluence_data/` directory
- Metadata extracted (title, URL, space, author, etc.)
- Content preprocessed for embedding

**2. Document Chunking**
```python
chunk_size = 1000        # Characters per chunk
chunk_overlap = 200      # Overlap between chunks
```

**Benefits of Chunking:**
- Better granularity for search
- Handles long documents effectively
- Preserves context with overlap
- Improves embedding quality

**3. Embedding Generation**
- Uses Google's `text-embedding-004` model
- Each chunk converted to 768-dimensional vector
- Embeddings stored in ChromaDB with metadata

### Search Process

**1. Query Processing**
```python
# User query: "How to deploy applications?"
query_embedding = embed_content(
    model="models/text-embedding-004",
    content=query,
    task_type="retrieval_query"
)
```

**2. Vector Search**
```python
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=limit * 3,  # Get more chunks for diversity
    include=["documents", "metadatas", "distances"]
)
```

**3. Result Ranking**
- Chunks grouped by document
- Document scores calculated from top chunk similarities
- Results ranked by semantic relevance

## 🎯 Search Quality Improvements

### Before (Keyword Search)
```
Query: "authentication and user access"
Results: Documents containing exact words "authentication", "user", "access"
Issues: Misses synonyms, related concepts, context
```

### After (Vector Search)
```
Query: "authentication and user access"
Results: 
1. User Management and Permissions (Perfect semantic match)
2. Security Best Practices (Related concepts)
3. Getting Started Guide (Contains login info)
Benefits: Understands meaning, finds related concepts, better ranking
```

## 📊 Performance Metrics

### Current Statistics
- **Documents**: 7 loaded
- **Chunks**: 19 indexed
- **Spaces**: 4 (ADMIN, DOCS, SECURITY, API)
- **Embedding Model**: text-embedding-004
- **Vector Database**: ChromaDB persistent storage

### Search Capabilities
- **Semantic Understanding**: ✅ Finds related concepts
- **Synonym Handling**: ✅ Matches different terms for same concept
- **Context Awareness**: ✅ Understands document context
- **Multilingual**: ✅ Google embeddings support multiple languages
- **Fallback**: ✅ Keyword search when vector search fails

## 🔄 Backward Compatibility

The implementation maintains full backward compatibility:

```python
# Same API interface
results = kb.search("deployment guide", limit=5)

# Automatic fallback
if vector_search_available:
    return vector_search(query)
else:
    return keyword_search(query)
```

## 🛠️ Configuration

### Environment Variables
```bash
# Required for embeddings
GOOGLE_API_KEY=your_google_ai_api_key

# Optional: Use Vertex AI instead
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
```

### Dependencies
```bash
pip install chromadb numpy google-generativeai
```

### Vector Database Location
```
confluence_data/
├── vector_db/          # ChromaDB storage
│   ├── chroma.sqlite3  # Vector index
│   └── ...
├── index.json          # Document index
└── SPACE/              # Document files
    └── doc.json
```

## 🚀 Usage Examples

### Basic Search
```python
from confluence_knowledge_agent.tools.knowledge_base import ConfluenceKnowledgeBase

kb = ConfluenceKnowledgeBase()
results = kb.search("How to deploy applications?")
```

### API Usage
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need help with user authentication"}'
```

### Statistics
```bash
curl http://localhost:8080/stats/detailed
```

## 🔍 Search Examples

### Deployment Queries
```
"How to deploy applications?" → Application Deployment Guide
"Docker deployment steps" → Deployment Guide (Docker section)
"Container orchestration" → Deployment Guide (Kubernetes section)
```

### Security Queries
```
"user authentication" → User Management, Security Best Practices
"access control" → User Management and Permissions
"password security" → Security Best Practices
```

### Configuration Queries
```
"system setup" → System Configuration Guide
"environment variables" → Configuration Guide
"database configuration" → Configuration Guide
```

## 🎯 Benefits

### For Users
- **Better Results**: Finds relevant information even with different wording
- **Faster Discovery**: Less need to try different search terms
- **Context Understanding**: Understands what you're really looking for

### For Developers
- **Improved Accuracy**: Higher precision and recall
- **Reduced Maintenance**: Less need to manually tune search terms
- **Scalable**: Handles growing document collections efficiently

### For Organizations
- **Better Knowledge Discovery**: Employees find information faster
- **Reduced Support Load**: Self-service becomes more effective
- **Improved Productivity**: Less time searching, more time working

## 🔧 Advanced Features

### Reindexing
```python
kb = ConfluenceKnowledgeBase()
success = kb.reindex_embeddings()  # Rebuild vector index
```

### Custom Chunking
```python
kb = ConfluenceKnowledgeBase()
kb.chunk_size = 1500      # Larger chunks
kb.chunk_overlap = 300    # More overlap
```

### Search Tuning
```python
# Get more diverse results
results = kb._vector_search(query, limit=10)

# Fallback to keyword search
results = kb._keyword_search(query, limit=5)
```

## 🚀 Future Enhancements

### Planned Improvements
1. **Hybrid Search**: Combine vector and keyword scores
2. **Query Expansion**: Automatically expand queries with related terms
3. **Personalization**: Learn from user search patterns
4. **Multi-modal**: Support for images and documents
5. **Real-time Updates**: Incremental indexing for new documents

### Performance Optimizations
1. **Caching**: Cache embeddings for common queries
2. **Batch Processing**: Process multiple documents simultaneously
3. **Compression**: Reduce vector storage size
4. **Distributed Search**: Scale across multiple nodes

## 📈 Monitoring

### Key Metrics
- Search response time
- Embedding generation time
- Vector database size
- Search result relevance scores
- Fallback usage frequency

### Health Checks
```bash
# Check vector search status
curl http://localhost:8080/stats/detailed

# Verify embeddings are working
curl -X POST http://localhost:8080/chat \
  -d '{"message": "test semantic search"}'
```

## 🎉 Conclusion

The RAG implementation transforms the Confluence Knowledge Agent from a simple keyword matcher into an intelligent semantic search system that truly understands user intent and document meaning. This provides a significantly better user experience and more accurate results.

**The system is now production-ready with enterprise-grade semantic search capabilities!** 🚀
