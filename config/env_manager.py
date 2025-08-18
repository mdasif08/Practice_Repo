#!/usr/bin/env python3
"""
Environment Configuration Manager
Handles loading and managing environment variables securely.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

class EnvironmentManager:
    """Manages environment variables and configuration."""
    
    def __init__(self):
        """Initialize and load environment variables."""
        # Load .env file from project root
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        
        # Database configuration
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_PORT = int(os.getenv('DB_PORT', 5432))
        self.DB_NAME = os.getenv('DB_NAME', 'newDB')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
        
        # GitHub configuration
        self.GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
        self.GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', '')
        
        # Ollama configuration
        self.OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.CODE_LLAMA_MODEL = os.getenv('CODE_LLAMA_MODEL', 'codellama:7b')
        self.OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2:7b')
        
        # Webhook server configuration
        self.WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', '0.0.0.0')
        self.WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 5000))
        
        # Monitor configuration
        self.CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 30))
        self.ENABLE_AGENTS = os.getenv('ENABLE_AGENTS', 'true').lower() == 'true'
        self.ENABLE_WEBHOOKS = os.getenv('ENABLE_WEBHOOKS', 'true').lower() == 'true'
    
    def get_database_url(self):
        """Get PostgreSQL connection URL."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def validate_config(self):
        """Validate that required configuration is present."""
        missing = []
        
        if not self.GITHUB_TOKEN:
            missing.append('GITHUB_TOKEN')
        
        if missing:
            print(f"⚠️ Warning: Missing environment variables: {', '.join(missing)}")
            print("   Some features may not work properly.")
            return False
        
        return True
    
    def print_config(self):
        """Print current configuration (without sensitive data)."""
        print("🔧 Current Configuration:")
        print(f"   Database: {self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")
        print(f"   GitHub Token: {'✅ Set' if self.GITHUB_TOKEN else '❌ Missing'}")
        print(f"   Webhook Server: {self.WEBHOOK_HOST}:{self.WEBHOOK_PORT}")
        print(f"   Ollama URL: {self.OLLAMA_BASE_URL}")
        print(f"   Check Interval: {self.CHECK_INTERVAL}s")
        print(f"   Agents Enabled: {self.ENABLE_AGENTS}")
        print(f"   Webhooks Enabled: {self.ENABLE_WEBHOOKS}")

# Global instance
env_manager = EnvironmentManager()
