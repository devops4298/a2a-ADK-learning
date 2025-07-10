#!/usr/bin/env python3
"""
Production startup script for TypeScript Playwright Cucumber Code Review Agent A2A Server.
This script starts the A2A server that VS Code Copilot Chat can discover and use.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from code_review_agent.a2a_server import create_fastapi_app
from code_review_agent.config import get_config


def setup_logging(config):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('code_review_agent.log')
        ]
    )


async def main():
    """Main entry point."""
    # Get configuration
    config = get_config()
    
    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    # Validate configuration
    errors = config.validate()
    if errors:
        logger.error("Configuration errors:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    logger.info("Starting TypeScript Playwright Cucumber Code Review Agent A2A Server")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Host: {config.HOST}")
    logger.info(f"Port: {config.PORT}")
    logger.info(f"Debug: {config.DEBUG}")
    
    try:
        # Create the FastAPI app
        app = create_fastapi_app()

        logger.info("=" * 60)
        logger.info("🚀 Code Review Agent Server Started Successfully!")
        logger.info("=" * 60)
        logger.info(f"📡 Server URL: http://{config.HOST}:{config.PORT}")
        logger.info("🤖 Agent ID: ts-playwright-cucumber-reviewer")
        logger.info("📋 Capabilities: analyze_code, fix_code, get_standards, chat")
        logger.info("")
        logger.info("🔗 VS Code Copilot Chat Integration:")
        logger.info("   1. Configure VS Code to use this agent endpoint")
        logger.info("   2. Use the agent in Copilot Chat to interact")
        logger.info("   3. Ask questions like:")
        logger.info("      • 'Analyze this TypeScript code'")
        logger.info("      • 'Fix issues in this Playwright test'")
        logger.info("      • 'Show me Cucumber standards'")
        logger.info("")
        logger.info("📋 Available Endpoints:")
        logger.info(f"   • GET  {config.HOST}:{config.PORT}/health")
        logger.info(f"   • GET  {config.HOST}:{config.PORT}/agent")
        logger.info(f"   • POST {config.HOST}:{config.PORT}/analyze")
        logger.info(f"   • POST {config.HOST}:{config.PORT}/fix")
        logger.info(f"   • GET  {config.HOST}:{config.PORT}/standards")
        logger.info(f"   • POST {config.HOST}:{config.PORT}/chat")
        logger.info("")
        logger.info("Press Ctrl+C to stop the server")
        logger.info("=" * 60)

        # Start the server
        import uvicorn
        uvicorn_config = uvicorn.Config(app, host=config.HOST, port=config.PORT, log_level="info")
        server = uvicorn.Server(uvicorn_config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Received shutdown signal")
        logger.info("Stopping Code Review Agent A2A Server...")
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        sys.exit(1)
    
    finally:
        logger.info("✅ Code Review Agent A2A Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
        sys.exit(0)
