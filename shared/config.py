#!/usr/bin/env python3
"""
Shared Configuration - Used by all microservices
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for all services."""
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'newDB')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    
    # GitHub Configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', '')
    
    # AI Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    CODE_LLAMA_MODEL = os.getenv('CODE_LLAMA_MODEL', 'codellama:7b')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2:7b')
    
    # Service Configuration
    COMMIT_SERVICE_PORT = int(os.getenv('COMMIT_SERVICE_PORT', '8001'))
    REPO_SERVICE_PORT = int(os.getenv('REPO_SERVICE_PORT', '8002'))
    WEBHOOK_SERVICE_PORT = int(os.getenv('WEBHOOK_SERVICE_PORT', '8003'))
    AI_SERVICE_PORT = int(os.getenv('AI_SERVICE_PORT', '8004'))
    
    # Monitor Configuration
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '30'))
    ENABLE_AGENTS = os.getenv('ENABLE_AGENTS', 'true').lower() == 'true'
    ENABLE_WEBHOOKS = os.getenv('ENABLE_WEBHOOKS', 'true').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_database_url(cls):
        """Get database connection URL."""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def validate_config(cls):
        """Validate configuration."""
        required_vars = [
            'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Global config instance
config = Config()
