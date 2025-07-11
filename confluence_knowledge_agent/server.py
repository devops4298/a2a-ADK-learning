"""
Production-ready FastAPI server for Confluence Knowledge Agent.

Implements ADK best practices for deployment and monitoring.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from google.adk.runners import InMemoryRunner, types
from .agent import root_agent
from .config.settings import get_server_config, get_auth_config, validate_config
from .tools.confluence_search import get_knowledge_base_stats
from .monitoring import health_checker, metrics_collector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global runner instance
runner: Optional[InMemoryRunner] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    global runner
    
    # Startup
    logger.info("Starting Confluence Knowledge Agent server...")
    
    # Validate configuration
    if not validate_config():
        logger.warning("Configuration validation failed. Some features may not work properly.")
    
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


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    config = get_server_config()
    
    app = FastAPI(
        title=config["api_title"],
        description="AI-powered assistant for searching and retrieving information from Confluence documentation",
        version=config["api_version"],
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config["cors_origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


# Request/Response models
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message", min_length=1, max_length=2000)
    user_id: Optional[str] = Field(None, description="Optional user ID")
    session_id: Optional[str] = Field(None, description="Optional session ID")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="Agent response")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    timestamp: str = Field(..., description="Response timestamp")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    agent_name: str = Field(..., description="Agent name")
    version: str = Field(..., description="API version")
    configuration_valid: bool = Field(..., description="Whether configuration is valid")


class StatsResponse(BaseModel):
    """Knowledge base stats response model."""
    stats: Dict[str, Any] = Field(..., description="Knowledge base statistics")


# Create app instance
app = create_app()


async def get_runner() -> InMemoryRunner:
    """
    Dependency to get the ADK runner.
    
    Returns:
        InMemoryRunner: The runner instance
        
    Raises:
        HTTPException: If runner is not available
    """
    if runner is None:
        raise HTTPException(
            status_code=503,
            detail="ADK Runner not available. Please check server configuration."
        )
    return runner


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        HealthResponse: Service health information
    """
    config = get_server_config()

    return HealthResponse(
        status="healthy",
        agent_name=root_agent.name,
        version=config["api_version"],
        configuration_valid=validate_config()
    )


@app.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check endpoint.

    Returns:
        Dict: Comprehensive health information
    """
    return health_checker.get_comprehensive_health()


@app.get("/metrics")
async def get_metrics():
    """
    Get service metrics.

    Returns:
        Dict: Service metrics and statistics
    """
    return metrics_collector.get_metrics()


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get knowledge base statistics.
    
    Returns:
        StatsResponse: Knowledge base statistics
    """
    try:
        stats_text = get_knowledge_base_stats()
        # Parse the stats text into a structured format
        # For now, return as text in a structured response
        return StatsResponse(stats={"summary": stats_text})
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    runner: InMemoryRunner = Depends(get_runner)
):
    """
    Chat with the Confluence Knowledge Agent.

    Args:
        request: Chat request containing user message
        runner: ADK runner dependency

    Returns:
        ChatResponse: Agent response
    """
    # Track metrics
    metrics_collector.increment_request_count()

    try:
        # Generate IDs if not provided
        user_id = request.user_id or str(uuid.uuid4())
        session_id = request.session_id or str(uuid.uuid4())
        
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
        
        # Create message content
        message_content = types.Content(parts=[types.Part(text=request.message)])
        
        # Run the agent
        events = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message_content
        ):
            events.append(event)
        
        # Extract the response from events
        response_text = ""
        for event in events:
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
        
        if not response_text:
            response_text = "I apologize, but I couldn't generate a response. Please try again."
        
        # Get current timestamp
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        return ChatResponse(
            response=response_text,
            user_id=user_id,
            session_id=session_id,
            timestamp=timestamp
        )
        
    except Exception as e:
        metrics_collector.increment_error_count()
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def run_server():
    """Run the server with production settings."""
    config = get_server_config()
    
    logger.info(f"Starting server on {config['host']}:{config['port']}")
    logger.info(f"Debug mode: {config['debug']}")
    logger.info(f"API documentation: http://{config['host']}:{config['port']}/docs")
    
    uvicorn.run(
        "confluence_knowledge_agent.server:app",
        host=config["host"],
        port=config["port"],
        log_level=config["log_level"].lower(),
        reload=config["debug"],
        access_log=True
    )


if __name__ == "__main__":
    run_server()
