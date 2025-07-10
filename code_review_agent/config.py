"""
Production configuration for the Code Review Agent A2A Server.
"""
import os
from typing import Dict, Any, List
from pathlib import Path


class Config:
    """Base configuration class."""

    # Server settings
    HOST = os.getenv('HOST', 'localhost')
    PORT = int(os.getenv('PORT', 8080))
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

    # A2A Agent settings
    AGENT_ID = "ts-playwright-cucumber-reviewer"
    AGENT_NAME = "TypeScript Playwright Cucumber Code Reviewer"
    AGENT_VERSION = "1.0.0"
    AGENT_DESCRIPTION = "AI-powered code review assistant for TypeScript, Playwright, and Cucumber projects"

    # Google AI settings (for ADK integration if needed)
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    GOOGLE_CLOUD_LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

    # Analysis settings
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 1024 * 1024))  # 1MB
    SUPPORTED_EXTENSIONS = ['.ts', '.js', '.tsx', '.jsx', '.spec.ts', '.test.ts', '.feature']

    # Linting settings
    ENABLE_ESLINT = os.getenv('ENABLE_ESLINT', 'true').lower() == 'true'
    ENABLE_PRETTIER = os.getenv('ENABLE_PRETTIER', 'true').lower() == 'true'
    ENABLE_CUSTOM_RULES = os.getenv('ENABLE_CUSTOM_RULES', 'true').lower() == 'true'

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return any errors."""
        errors = []

        # Check port range
        if not (1024 <= cls.PORT <= 65535):
            errors.append(f"PORT must be between 1024 and 65535, got {cls.PORT}")

        # Check file size limit
        if cls.MAX_FILE_SIZE <= 0:
            errors.append("MAX_FILE_SIZE must be positive")

        return errors


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    HOST = '0.0.0.0'
    LOG_LEVEL = 'WARNING'
    
    # Security settings for production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://vscode.dev,https://github.dev').split(',')


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = 'DEBUG'


def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Global config instance
config = get_config()
