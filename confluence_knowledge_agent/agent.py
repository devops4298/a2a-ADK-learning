"""
Confluence Knowledge Agent

Production-ready ADK agent following Google ADK standards.
Provides intelligent search and retrieval from Confluence documentation.
"""

import os
import logging
from typing import Dict, List, Optional
from google.adk import Agent
from .tools.confluence_search import search_confluence_knowledge
from .config.settings import get_agent_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_confluence_agent() -> Agent:
    """
    Create and configure the Confluence Knowledge Agent.
    
    Returns:
        Agent: Configured ADK agent with Confluence search capabilities
    """
    config = get_agent_config()
    
    try:
        agent = Agent(
            name=config["name"],
            model=config["model"],
            description=config["description"],
            instruction=config["instruction"],
            tools=[search_confluence_knowledge],
        )
        
        logger.info(f"Successfully created Confluence Knowledge Agent: {config['name']}")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        # Create fallback agent
        return Agent(
            name="confluence_knowledge_agent_fallback",
            model="gemini-2.0-flash",
            description="Fallback Confluence knowledge assistant",
            instruction="""I'm a Confluence knowledge assistant, but I'm currently unable to access 
            the knowledge base. Please check the configuration and ensure the confluence data 
            directory exists with proper index.json file."""
        )


# Create the root agent instance
root_agent = create_confluence_agent()
