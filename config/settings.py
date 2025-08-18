"""
Configuration management service for CraftNudge Git Commit Logger.
Handles all application settings and environment variables.
"""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Application settings with environment variable support."""
    
    def __init__(self):
        # Data storage settings
        self.DATA_DIR = os.getenv("DATA_DIR", "data")
        self.BEHAVIORS_DIR = os.getenv("BEHAVIORS_DIR", "behaviors")
        self.COMMITS_FILE = os.getenv("COMMITS_FILE", "commits.jsonl")
        
        # Git settings
        self.GIT_REPO_PATH = os.getenv("GIT_REPO_PATH")
        
        # Logging settings
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.ENABLE_DEBUG = os.getenv("ENABLE_DEBUG", "false").lower() == "true"
        
        # CLI settings
        self.CLI_COLORS = os.getenv("CLI_COLORS", "true").lower() == "true"
        self.CLI_PROGRESS = os.getenv("CLI_PROGRESS", "true").lower() == "true"
    
    @property
    def commits_file_path(self) -> Path:
        """Get the full path to the commits JSONL file."""
        data_path = Path(self.DATA_DIR) / self.BEHAVIORS_DIR
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path / self.COMMITS_FILE
    
    @property
    def git_repo_path(self) -> Optional[Path]:
        """Get the Git repository path, defaulting to current directory."""
        if self.GIT_REPO_PATH:
            return Path(self.GIT_REPO_PATH)
        return Path.cwd()


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def update_settings(**kwargs) -> None:
    """Update settings with new values."""
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
