# ADK Integration Documentation

This document explains how the Confluence Knowledge Agent integrates with Google's Agent Development Kit (ADK) and follows ADK patterns and best practices.

## 🎯 ADK Compliance Overview

Our agent strictly follows Google ADK standards in these key areas:

1. **Agent Definition**: Proper use of the `Agent` class
2. **Function Tools**: Implementation using `FunctionTool` pattern
3. **Session Management**: Correct usage of ADK runners and sessions
4. **Configuration**: Environment-based configuration following ADK patterns
5. **Error Handling**: Robust error handling throughout the agent lifecycle

## 🤖 Agent Definition (`agent.py`)

### ADK Agent Class Usage

```python
from google.adk import Agent

def create_confluence_agent() -> Agent:
    config = get_agent_config()
    
    agent = Agent(
        name=config["name"],                    # Unique agent identifier
        model=config["model"],                  # AI model specification
        description=config["description"],      # Agent description
        instruction=config["instruction"],      # System prompt
        tools=[search_confluence_knowledge],    # List of available tools
    )
    
    return agent
```

### Key ADK Patterns

#### 1. **Model Specification**
```python
model="gemini-2.0-flash"  # Explicit model specification required by ADK
```

#### 2. **Tool Integration**
```python
tools=[search_confluence_knowledge]  # Functions automatically converted to FunctionTools
```

#### 3. **System Instructions**
```python
instruction="""
You are a helpful Confluence knowledge assistant. Your role is to help users find 
information from Confluence documentation quickly and accurately.

When a user asks a question:
1. Use the search_confluence_knowledge tool to find relevant information
2. Provide comprehensive answers based on the retrieved content
3. Always include proper citations to source Confluence pages
4. If no relevant information is found, clearly state that
"""
```

## 🛠️ Function Tools Implementation

### ADK FunctionTool Pattern

ADK automatically converts Python functions into `FunctionTool` objects when they are passed to an agent. Our main tool follows this pattern:

```python
def search_confluence_knowledge(query: str, limit: int = 5) -> str:
    """
    Search the Confluence knowledge base for relevant information.
    
    This function tool searches through Confluence documentation to find
    relevant pages and content based on the user's query.
    
    Args:
        query (str): The search query to find relevant documentation
        limit (int): Maximum number of results to return (default: 5, max: 10)
        
    Returns:
        str: Formatted search results with citations and content previews
    """
    # Implementation here...
```

### ADK Requirements for Function Tools

1. **Type Hints**: All parameters and return values must have type hints
2. **Docstrings**: Comprehensive docstrings that ADK uses for tool descriptions
3. **Parameter Descriptions**: Clear descriptions in the docstring for each parameter
4. **Return Type**: Must return a string that the agent can use in its response

### Tool Registration Process

```python
# In agent.py
from .tools.confluence_search import search_confluence_knowledge

# ADK automatically converts this function to a FunctionTool
agent = Agent(
    name="confluence_knowledge_agent",
    model="gemini-2.0-flash",
    tools=[search_confluence_knowledge],  # ← Automatic FunctionTool conversion
)
```

## 🏃‍♂️ Session Management and Runners

### ADK InMemoryRunner Usage

```python
from google.adk.runners import InMemoryRunner, types

# Initialize runner with our agent
runner = InMemoryRunner(
    agent=root_agent,
    app_name="confluence_knowledge_agent"
)
```

### Session Lifecycle

#### 1. **Session Creation**
```python
# Create session if it doesn't exist
try:
    await runner.session_service.get_session(
        app_name="confluence_knowledge_agent",
        user_id=user_id,
        session_id=session_id
    )
except:
    # Session doesn't exist, create it
    await runner.session_service.create_session(
        app_name="confluence_knowledge_agent",
        user_id=user_id,
        session_id=session_id
    )
```

#### 2. **Message Processing**
```python
# Create message content using ADK types
message_content = types.Content(parts=[types.Part(text=request.message)])

# Run the agent
events = []
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=message_content
):
    events.append(event)
```

#### 3. **Response Extraction**
```python
# Extract the response from events
response_text = ""
for event in events:
    if hasattr(event, 'content') and event.content:
        if hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text
```

### ADK Event System

ADK uses an event-driven architecture where agent responses are streamed as events:

```python
async for event in runner.run_async(...):
    # Events can contain:
    # - Partial responses
    # - Tool calls
    # - Error information
    # - Completion signals
    
    if hasattr(event, 'content'):
        # Process content events
        pass
```

## ⚙️ Configuration Following ADK Patterns

### Environment-Based Configuration

ADK recommends environment-based configuration for production deployments:

```python
def get_agent_config() -> Dict[str, Any]:
    return {
        "name": os.getenv("AGENT_NAME", "confluence_knowledge_agent"),
        "model": os.getenv("AGENT_MODEL", "gemini-2.0-flash"),
        "description": os.getenv("AGENT_DESCRIPTION", "..."),
        "instruction": os.getenv("AGENT_INSTRUCTION", "..."),
        "max_tokens": int(os.getenv("AGENT_MAX_TOKENS", "8192")),
        "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.1")),
    }
```

### Authentication Configuration

#### Google AI API (Development)
```python
def get_auth_config() -> Dict[str, Any]:
    return {
        "google_api_key": os.getenv("GOOGLE_API_KEY"),
        "use_vertex_ai": False,
    }
```

#### Vertex AI (Production)
```python
def get_auth_config() -> Dict[str, Any]:
    return {
        "google_cloud_project": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "google_cloud_location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        "use_vertex_ai": os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true",
    }
```

## 🔄 ADK Lifecycle Management

### Application Startup

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events following ADK patterns."""
    global runner
    
    # Startup
    logger.info("Starting Confluence Knowledge Agent server...")
    
    # Validate configuration
    if not validate_config():
        logger.warning("Configuration validation failed.")
    
    # Initialize ADK runner
    try:
        runner = InMemoryRunner(
            agent=root_agent,
            app_name="confluence_knowledge_agent"
        )
        logger.info("ADK Runner initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ADK Runner: {e}")
        runner = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down Confluence Knowledge Agent server...")
    if runner:
        try:
            await runner.close()
            logger.info("ADK Runner closed successfully")
        except Exception as e:
            logger.error(f"Error closing ADK Runner: {e}")
```

### Error Handling

ADK requires robust error handling throughout the agent lifecycle:

```python
def create_confluence_agent() -> Agent:
    config = get_agent_config()
    
    try:
        agent = Agent(
            name=config["name"],
            model=config["model"],
            description=config["description"],
            instruction=config["instruction"],
            tools=[search_confluence_knowledge],
        )
        
        logger.info(f"Successfully created agent: {config['name']}")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        # Create fallback agent following ADK patterns
        return Agent(
            name="confluence_knowledge_agent_fallback",
            model="gemini-2.0-flash",
            description="Fallback Confluence knowledge assistant",
            instruction="I'm currently unable to access the knowledge base..."
        )
```

## 📊 ADK Best Practices Implemented

### 1. **Proper Logging**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### 2. **Graceful Degradation**
- Fallback agents when configuration fails
- Error messages that guide users to solutions
- Continued operation even with partial failures

### 3. **Resource Management**
- Proper cleanup of ADK runners
- Memory-efficient document loading
- Connection pooling and session reuse

### 4. **Production Readiness**
- Health checks that validate ADK components
- Metrics collection for monitoring
- Proper async/await usage throughout

## 🔍 Debugging ADK Integration

### Common Issues and Solutions

#### 1. **Model Not Found Error**
```
ValueError: No model found for confluence_knowledge_agent
```
**Solution**: Ensure model is specified in agent creation:
```python
agent = Agent(
    name="confluence_knowledge_agent",
    model="gemini-2.0-flash",  # ← Required!
    # ... other parameters
)
```

#### 2. **Authentication Errors**
```
Missing key inputs argument! To use the Google AI API, provide (api_key) arguments
```
**Solution**: Set proper environment variables:
```bash
export GOOGLE_API_KEY="your_api_key_here"
# OR for Vertex AI:
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

#### 3. **Session Errors**
```
Session not found: session_id
```
**Solution**: Ensure session creation before use:
```python
await runner.session_service.create_session(
    app_name="confluence_knowledge_agent",
    user_id=user_id,
    session_id=session_id
)
```

### ADK Debugging Tools

1. **Enable Debug Logging**:
```python
logging.getLogger("google.adk").setLevel(logging.DEBUG)
```

2. **Event Inspection**:
```python
async for event in runner.run_async(...):
    logger.debug(f"ADK Event: {type(event).__name__} - {event}")
```

3. **Configuration Validation**:
```python
def validate_config() -> bool:
    """Validate ADK configuration before startup."""
    # Check authentication
    # Validate data availability
    # Test agent creation
    return True
```

---

This documentation ensures that developers understand how our agent properly integrates with Google ADK and follows all recommended patterns and best practices.
