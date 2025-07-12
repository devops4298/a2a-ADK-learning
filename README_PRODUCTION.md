# COM Insurance Confluence Knowledge Agent

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285f4.svg)](https://google.github.io/adk-docs/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

A production-ready AI-powered assistant for searching and retrieving information from COM Insurance Confluence documentation. Built with Google's Agent Development Kit (ADK) and powered by advanced RAG technology.

## 🚀 Features

- **🤖 AI-Powered Search**: Advanced natural language understanding using Google's Gemini models
- **🧠 RAG-Powered Search**: Semantic search using Google embeddings and ChromaDB vector database
- **🔍 Chrome Cookie Authentication**: Seamlessly uses your Chrome browser cookies for Confluence access
- **📚 EQE Space Support**: Specifically configured for COM Insurance EQE Confluence space
- **🎯 Accurate Citations**: Provides proper citations with direct links to source pages
- **⚡ Fast Response**: Optimized for quick information retrieval and processing
- **🔒 Production Ready**: Secure, scalable, and monitoring-ready architecture
- **📊 Health Monitoring**: Built-in health checks and statistics endpoints
- **🔧 CLI Management**: Comprehensive command-line interface for administration

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9 or higher
- Google Chrome browser
- Access to COM Insurance Confluence (https://COMinsurence.atlassian.net)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd confluence_knowledge_agent

# Install dependencies
pip3 install -r requirements.txt
```

### 3. Setup Environment

```bash
# Set your Google API key for embeddings
export GOOGLE_API_KEY="your-google-api-key"

# Optional: Use Vertex AI instead
export GOOGLE_CLOUD_PROJECT="your-project"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
```

### 4. Scrape Confluence Data

**Important**: First, log into https://COMinsurence.atlassian.net in Chrome to authenticate.

```bash
# Scrape the EQE space
python3 -m confluence_knowledge_agent.cli scrape

# Or specify custom options
python3 -m confluence_knowledge_agent.cli scrape --space-key EQE --output-dir confluence_data
```

### 5. Start the Agent

```bash
# Start the server
python3 -m confluence_knowledge_agent.cli serve

# The agent will be available at http://localhost:8080
```

## 📋 Available Commands

```bash
# Scrape Confluence space
python3 -m confluence_knowledge_agent.cli scrape

# Start the server
python3 -m confluence_knowledge_agent.cli serve

# Show knowledge base statistics
python3 -m confluence_knowledge_agent.cli stats

# Show data directory summary
python3 -m confluence_knowledge_agent.cli summary

# Validate data structure
python3 -m confluence_knowledge_agent.cli validate

# Show configuration
python3 -m confluence_knowledge_agent.cli config
```

## 🔧 Configuration

The agent uses the following configuration files:

- `confluence_knowledge_agent/config/agent.yaml` - Agent configuration
- `confluence_knowledge_agent/config/data.yaml` - Data source configuration
- `confluence_knowledge_agent/config/server.yaml` - Server configuration

## 📊 API Endpoints

Once the server is running, you can access:

- **Chat**: `POST /chat` - Send messages to the agent
- **Health**: `GET /health` - Health check endpoint
- **Stats**: `GET /stats` - Knowledge base statistics
- **Detailed Stats**: `GET /stats/detailed` - Detailed statistics with vector search info
- **API Docs**: `GET /docs` - Interactive API documentation

## 💬 Usage Examples

### Chat API

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I deploy applications?"}'
```

### Health Check

```bash
curl http://localhost:8080/health
```

### Statistics

```bash
curl http://localhost:8080/stats/detailed
```

## 🔍 How It Works

1. **Data Scraping**: The scraper uses Chrome cookies to authenticate with Confluence and downloads all pages from the EQE space
2. **Content Processing**: Pages are parsed, cleaned, and split into chunks for optimal search performance
3. **Vector Indexing**: Content is converted to embeddings using Google's text-embedding-004 model and stored in ChromaDB
4. **Semantic Search**: User queries are converted to embeddings and matched against the vector database for relevant content
5. **Response Generation**: The agent provides formatted responses with proper citations and source links

## 🛠️ Troubleshooting

### Authentication Issues

If you get authentication errors:
1. Open Chrome and log into https://COMinsurence.atlassian.net
2. Make sure you have access to the EQE space
3. Run the scrape command again

### No Results Found

If searches return no results:
1. Check if data was scraped: `python3 -m confluence_knowledge_agent.cli summary`
2. Verify vector search is enabled: `curl http://localhost:8080/stats/detailed`
3. Try rephrasing your query with different terms

### Performance Issues

For better performance:
1. Ensure you have sufficient RAM (4GB+ recommended)
2. Use SSD storage for faster vector database operations
3. Set appropriate chunk sizes in the configuration

## 📁 Project Structure

```
confluence_knowledge_agent/
├── agent.py                 # Main agent implementation
├── cli.py                   # Command-line interface
├── server.py                # FastAPI server
├── monitoring.py            # Health checks and metrics
├── config/                  # Configuration files
├── tools/                   # Agent tools
│   ├── confluence_search.py # Search functionality
│   └── knowledge_base.py    # RAG implementation
└── data/                    # Data management
    └── scraper.py           # Confluence scraper

confluence_data/             # Scraped data (created after scraping)
├── EQE/                     # Space-specific documents
├── vector_db/               # ChromaDB vector database
└── index.json               # Document index
```

## 🎯 Production Notes

This is a production-ready local deployment. The agent:

- ✅ Runs locally on your machine
- ✅ Uses your Chrome authentication
- ✅ Stores data locally for privacy
- ✅ Provides semantic search with vector embeddings
- ✅ Includes health monitoring and statistics
- ✅ Has comprehensive error handling
- ✅ Supports graceful fallbacks

## 📚 Additional Documentation

- [RAG Implementation Details](docs/RAG_IMPLEMENTATION.md)
- [ADK Integration Guide](docs/ADK_INTEGRATION.md)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs for detailed error messages
3. Ensure all prerequisites are met
4. Verify your Confluence access permissions

---

**Built with ❤️ for COM Insurance using Google ADK and modern AI technologies.**
