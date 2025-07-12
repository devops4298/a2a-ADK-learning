# Confluence Knowledge Agent

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285f4.svg)](https://google.github.io/adk-docs/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready AI-powered assistant for searching and retrieving information from Confluence documentation. Built with Google's Agent Development Kit (ADK) following official standards and best practices.

## 🚀 Features

- **🤖 AI-Powered Search**: Advanced natural language understanding using Google's Gemini models
- **🧠 RAG-Powered Search**: Semantic search using Google embeddings and ChromaDB vector database
- **📚 Multi-Space Support**: Search across all your Confluence spaces simultaneously
- **🎯 Accurate Citations**: Provides proper citations with direct links to source pages
- **⚡ Fast Response**: Optimized for quick information retrieval and processing
- **🔒 Production Ready**: Secure, scalable, and monitoring-ready architecture
- **🐳 Docker Support**: Complete containerization for easy deployment
- **📊 Health Monitoring**: Built-in health checks and statistics endpoints
- **🔧 CLI Management**: Comprehensive command-line interface for administration
- **🎨 Web Interface**: Beautiful Streamlit frontend for easy interaction
- **📱 User-Friendly**: Intuitive chat interface with real-time responses

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Development](#development)
- [Contributing](#contributing)

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google AI API key or Vertex AI setup
- Confluence data (see [Data Preparation](#data-preparation))

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/confluence-knowledge-agent.git
cd confluence-knowledge-agent

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (add your Google AI API key)
nano .env
```

### 3. Start the Server

```bash
# Using CLI
confluence-agent serve

# Or directly
python -m confluence_knowledge_agent.cli serve
```

### 4. Test the Agent

**Option A: Web Interface (Recommended)**
```bash
# Start the beautiful Streamlit frontend
streamlit run streamlit_app.py

# Or start both backend and frontend automatically
python3 run_app.py
```
Visit `http://localhost:8501` for the interactive web interface.

**Option B: API Testing**
```bash
# Health check
curl http://localhost:8080/health

# Ask a question
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I get started?"}'
```

## 📦 Installation

### Option 1: Package Installation

```bash
pip install confluence-knowledge-agent
```

### Option 2: Development Installation

```bash
git clone https://github.com/your-org/confluence-knowledge-agent.git
cd confluence-knowledge-agent
pip install -r requirements-dev.txt
pip install -e .
```

### Option 3: Docker Installation

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or build manually
docker build -t confluence-agent .
docker run -p 8080:8080 confluence-agent
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Key configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API key | Required |
| `GOOGLE_CLOUD_PROJECT` | GCP project (for Vertex AI) | Optional |
| `CONFLUENCE_DATA_DIR` | Path to Confluence data | `./confluence_data` |
| `SERVER_HOST` | Server host | `0.0.0.0` |
| `SERVER_PORT` | Server port | `8080` |
| `AGENT_MODEL` | AI model to use | `gemini-2.0-flash` |

### Authentication Setup

#### Option 1: Google AI API (Development)

1. Get an API key from [Google AI Studio](https://aistudio.google.com/)
2. Set the environment variable:
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

#### Option 2: Vertex AI (Production)

1. Set up Google Cloud authentication:
   ```bash
   gcloud auth application-default login
   ```
2. Configure environment:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_CLOUD_LOCATION="us-central1"
   export GOOGLE_GENAI_USE_VERTEXAI="true"
   ```

### Data Preparation

The agent requires Confluence data in a specific format:

```
confluence_data/
├── index.json              # Main index file (empty by default)
└── SPACE_KEY/             # Space directories (add your spaces here)
    ├── page_id_1.json     # Individual page files
    └── page_id_2.json
```

#### Sample Data Structure

**`confluence_data/index.json`**:
```json
[
  {
    "id": "123456",
    "space_key": "DOCS",
    "title": "Getting Started Guide"
  }
]
```

**Note**: The index.json file is empty by default. Add your Confluence data following this structure.

**`confluence_data/DOCS/123456.json`**:
```json
{
  "content": "Page content here...",
  "metadata": {
    "title": "Getting Started Guide",
    "url": "https://company.atlassian.net/wiki/spaces/DOCS/pages/123456",
    "last_updated": "2024-01-15T10:30:00Z",
    "space_key": "DOCS",
    "author": "Author Name"
  }
}
```

## 🎯 Usage

### 🎨 **Web Interface (Recommended)**

**Quick Start - Launch Everything:**
```bash
# Start both backend and frontend automatically
python3 run_app.py
```

**Manual Start:**
```bash
# Terminal 1: Start the backend
python3 -m confluence_knowledge_agent.cli serve

# Terminal 2: Start the frontend
streamlit run streamlit_app.py
```

**Access Points:**
- 🎨 **Web Interface**: http://localhost:8501
- 📊 **API Backend**: http://localhost:8080
- 📚 **API Docs**: http://localhost:8080/docs

### 💻 **Command Line Interface**

```bash
# Start the server
confluence-agent serve

# Validate data structure
confluence-agent validate

# Show knowledge base statistics
confluence-agent stats

# Show configuration
confluence-agent config

# Run tests
confluence-agent test
```

### Python API

```python
from confluence_knowledge_agent.tools.confluence_search import search_confluence_knowledge

# Search the knowledge base
result = search_confluence_knowledge("How do I deploy the application?")
print(result)
```

### REST API

#### Chat Endpoint

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the system requirements?",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

#### Health Check

```bash
curl http://localhost:8080/health
```

#### Statistics

```bash
curl http://localhost:8080/stats
```

## 📚 API Documentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/chat` | POST | Chat with the agent |
| `/stats` | GET | Knowledge base statistics |
| `/docs` | GET | Interactive API documentation |

### Request/Response Models

#### Chat Request
```json
{
  "message": "string (required, 1-2000 chars)",
  "user_id": "string (optional)",
  "session_id": "string (optional)"
}
```

#### Chat Response
```json
{
  "response": "string",
  "user_id": "string", 
  "session_id": "string",
  "timestamp": "string (ISO 8601)"
}
```

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

## 🐳 Deployment

### Docker Deployment

#### Using Docker Compose (Recommended)

```bash
# Production deployment
docker-compose up -d

# With UI (optional)
docker-compose --profile ui up -d

# View logs
docker-compose logs -f
```

#### Manual Docker

```bash
# Build image
docker build -t confluence-agent .

# Run container
docker run -d \
  --name confluence-agent \
  -p 8080:8080 \
  -e GOOGLE_API_KEY="your_key" \
  -v ./confluence_data:/app/confluence_data:ro \
  confluence-agent
```

### Cloud Deployment

#### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/confluence-agent
gcloud run deploy confluence-agent \
  --image gcr.io/PROJECT_ID/confluence-agent \
  --platform managed \
  --port 8080 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=PROJECT_ID
```

#### AWS ECS

```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag confluence-agent:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/confluence-agent:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/confluence-agent:latest
```

#### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: confluence-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: confluence-agent
  template:
    metadata:
      labels:
        app: confluence-agent
    spec:
      containers:
      - name: confluence-agent
        image: confluence-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: confluence-secrets
              key: google-api-key
```

## 🛠 Development

### 📚 **Developer Documentation**

**New to the project?** Start with our comprehensive developer documentation:

**👉 [Complete Developer Documentation](docs/README.md)**

The documentation includes:
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Getting started and overview
- **[File Documentation](docs/FILE_DOCUMENTATION.md)** - Detailed code documentation
- **[Function Reference](docs/FUNCTION_REFERENCE.md)** - Complete API reference
- **[ADK Integration](docs/ADK_INTEGRATION.md)** - Google ADK patterns and best practices
- **[Data Flow](docs/DATA_FLOW.md)** - Request lifecycle and system behavior
- **[Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)** - Day-to-day development procedures
- **[Architecture Diagrams](docs/ARCHITECTURE_DIAGRAMS.md)** - Visual system architecture

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/confluence-knowledge-agent.git
cd confluence-knowledge-agent

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .

# Install pre-commit hooks (optional)
pre-commit install
```

**📖 For detailed setup instructions and development procedures, see [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)**

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=confluence_knowledge_agent

# Run specific test file
pytest confluence_knowledge_agent/tests/test_knowledge_base.py
```

### Code Quality

```bash
# Format code
black confluence_knowledge_agent/

# Lint code
flake8 confluence_knowledge_agent/

# Type checking
mypy confluence_knowledge_agent/
```

### Project Structure

```
confluence_knowledge_agent/
├── __init__.py              # Package initialization
├── agent.py                 # Main agent definition
├── cli.py                   # Command line interface
├── server.py                # FastAPI server
├── config/                  # Configuration management
│   ├── __init__.py
│   └── settings.py
├── tools/                   # ADK tools
│   ├── __init__.py
│   ├── confluence_search.py
│   └── knowledge_base.py
├── data/                    # Data management
│   ├── __init__.py
│   ├── scraper.py
│   └── validator.py
└── tests/                   # Test suite
    ├── __init__.py
    └── test_knowledge_base.py
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `pytest`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Developer Documentation**: [Complete Documentation Suite](docs/README.md)
- **ADK Documentation**: [Google ADK Documentation](https://google.github.io/adk-docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/confluence-knowledge-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/confluence-knowledge-agent/discussions)

## 🙏 Acknowledgments

- Built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- Powered by [Google Gemini](https://ai.google.dev/)
- Web framework by [FastAPI](https://fastapi.tiangolo.com/)

---

**🎉 Ready to deploy your production-ready Confluence Knowledge Agent!**
