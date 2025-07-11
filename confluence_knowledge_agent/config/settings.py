"""
Configuration settings for Confluence Knowledge Agent.

Centralizes all configuration management following ADK best practices.
"""

import os
from typing import Dict, Any
from pathlib import Path


def get_agent_config() -> Dict[str, Any]:
    """
    Get agent configuration settings.
    
    Returns:
        Dict containing agent configuration
    """
    return {
        "name": os.getenv("AGENT_NAME", "confluence_knowledge_agent"),
        "model": os.getenv("AGENT_MODEL", "gemini-2.0-flash"),
        "description": os.getenv(
            "AGENT_DESCRIPTION", 
            "AI-powered assistant for searching and retrieving information from Confluence documentation"
        ),
        "instruction": os.getenv(
            "AGENT_INSTRUCTION",
            """You are a helpful Confluence knowledge assistant. Your role is to help users find 
            information from Confluence documentation quickly and accurately.

            When a user asks a question:
            1. Use the search_confluence_knowledge tool to find relevant information
            2. Provide comprehensive answers based on the retrieved content
            3. Always include proper citations to source Confluence pages
            4. If no relevant information is found, clearly state that
            5. Be helpful and guide users to find what they need

            Format your responses clearly and include citations in this format:
            [Page Title](URL) - Last updated: DATE

            Only provide information that is available in the knowledge base. If you cannot find 
            relevant information, politely inform the user and suggest alternative approaches."""
        ),
        "max_tokens": int(os.getenv("AGENT_MAX_TOKENS", "8192")),
        "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.1")),
    }


def get_data_config() -> Dict[str, Any]:
    """
    Get data configuration settings.
    
    Returns:
        Dict containing data configuration
    """
    return {
        "data_dir": os.getenv("CONFLUENCE_DATA_DIR", "./confluence_data"),
        "index_file": os.getenv("CONFLUENCE_INDEX_FILE", "index.json"),
        "max_file_size": int(os.getenv("MAX_FILE_SIZE", "10485760")),  # 10MB
        "encoding": os.getenv("FILE_ENCODING", "utf-8"),
        "search_limit": int(os.getenv("SEARCH_LIMIT", "5")),
        "content_preview_length": int(os.getenv("CONTENT_PREVIEW_LENGTH", "500")),
    }


def get_server_config() -> Dict[str, Any]:
    """
    Get server configuration settings.
    
    Returns:
        Dict containing server configuration
    """
    return {
        "host": os.getenv("SERVER_HOST", "0.0.0.0"),
        "port": int(os.getenv("SERVER_PORT", "8080")),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "cors_origins": os.getenv("CORS_ORIGINS", "*").split(","),
        "api_title": os.getenv("API_TITLE", "Confluence Knowledge Agent API"),
        "api_version": os.getenv("API_VERSION", "1.0.0"),
    }


def get_auth_config() -> Dict[str, Any]:
    """
    Get authentication configuration settings.
    
    Returns:
        Dict containing authentication configuration
    """
    return {
        "google_api_key": os.getenv("GOOGLE_API_KEY"),
        "google_cloud_project": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "google_cloud_location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        "use_vertex_ai": os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true",
    }


def validate_config() -> bool:
    """
    Validate that required configuration is present.
    
    Returns:
        bool: True if configuration is valid
    """
    auth_config = get_auth_config()
    
    if auth_config["use_vertex_ai"]:
        if not auth_config["google_cloud_project"]:
            return False
    else:
        if not auth_config["google_api_key"]:
            return False
    
    data_config = get_data_config()
    data_dir = Path(data_config["data_dir"])
    
    # Check if data directory exists
    if not data_dir.exists():
        return False
    
    return True
