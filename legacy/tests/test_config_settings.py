"""
Unit tests for the configuration settings module.
"""

import pytest
import os
from unittest.mock import patch, Mock
from pathlib import Path

from config.settings import Settings, get_settings, update_settings


class TestSettings:
    """Test cases for Settings class."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        
        assert settings.DATA_DIR == "data"
        assert settings.BEHAVIORS_DIR == "behaviors"
        assert settings.COMMITS_FILE == "commits.jsonl"
        assert settings.GIT_REPO_PATH is None
        assert settings.LOG_LEVEL == "INFO"
        assert settings.ENABLE_DEBUG is False
        assert settings.CLI_COLORS is True
        assert settings.CLI_PROGRESS is True
    
    @patch.dict(os.environ, {
        'DATA_DIR': '/custom/data',
        'BEHAVIORS_DIR': 'custom_behaviors',
        'COMMITS_FILE': 'custom_commits.jsonl',
        'GIT_REPO_PATH': '/custom/repo',
        'LOG_LEVEL': 'DEBUG',
        'ENABLE_DEBUG': 'true',
        'CLI_COLORS': 'false',
        'CLI_PROGRESS': 'false'
    })
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        settings = Settings()
        
        assert settings.DATA_DIR == "/custom/data"
        assert settings.BEHAVIORS_DIR == "custom_behaviors"
        assert settings.COMMITS_FILE == "custom_commits.jsonl"
        assert settings.GIT_REPO_PATH == "/custom/repo"
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.ENABLE_DEBUG is True
        assert settings.CLI_COLORS is False
        assert settings.CLI_PROGRESS is False
    
    @patch.dict(os.environ, {
        'ENABLE_DEBUG': 'invalid',
        'CLI_COLORS': 'invalid',
        'CLI_PROGRESS': 'invalid'
    })
    def test_boolean_environment_variables(self):
        """Test boolean environment variable parsing."""
        settings = Settings()
        
        # Invalid values should default to False
        assert settings.ENABLE_DEBUG is False
        assert settings.CLI_COLORS is False
        assert settings.CLI_PROGRESS is False
    
    def test_boolean_environment_variables_case_insensitive(self):
        """Test boolean environment variables with case insensitive values."""
        with patch.dict('os.environ', {
            'ENABLE_DEBUG': 'TRUE',
            'CLI_COLORS': 'False',
            'CLI_PROGRESS': 'yes'
        }):
            settings = Settings()
            
            assert settings.ENABLE_DEBUG is True
            assert settings.CLI_COLORS is False
            assert settings.CLI_PROGRESS is True
    
    def test_commits_file_path_property(self, tmp_path):
        """Test commits_file_path property."""
        with patch.dict('os.environ', {'DATA_DIR': str(tmp_path)}):
            settings = Settings()
            
            expected_path = tmp_path / 'behaviors' / 'commits.jsonl'
            assert settings.commits_file_path == expected_path
    
    def test_commits_file_path_creates_directory(self, tmp_path):
        """Test that commits_file_path creates directory if it doesn't exist."""
        with patch.dict('os.environ', {'DATA_DIR': str(tmp_path)}):
            settings = Settings()
            
            # Mock the mkdir method
            with patch.object(Path, 'mkdir') as mock_mkdir:
                settings.commits_file_path
                mock_mkdir.assert_called_with(parents=True, exist_ok=True)
    
    def test_git_repo_path_property_with_env_var(self):
        """Test git_repo_path property with environment variable set."""
        with patch.dict(os.environ, {'GIT_REPO_PATH': '/custom/repo'}):
            settings = Settings()
            result = settings.git_repo_path
            
            assert result == Path('/custom/repo')
    
    def test_git_repo_path_property_without_env_var(self):
        """Test git_repo_path property without environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('config.settings.Path') as mock_path:
                mock_path.cwd.return_value = Path('/current/directory')
                
                settings = Settings()
                result = settings.git_repo_path
                
                assert result == Path('/current/directory')
    
    def test_git_repo_path_property_none(self):
        """Test git_repo_path property when GIT_REPO_PATH is None."""
        with patch.dict(os.environ, {'GIT_REPO_PATH': ''}):
            with patch('config.settings.Path') as mock_path:
                mock_path.cwd.return_value = Path('/current/directory')
                
                settings = Settings()
                result = settings.git_repo_path
                
                assert result == Path('/current/directory')


class TestSettingsFunctions:
    """Test cases for settings utility functions."""
    
    def test_get_settings(self):
        """Test get_settings function."""
        settings = get_settings()
        
        assert isinstance(settings, Settings)
        assert settings.DATA_DIR == "data"
        assert settings.BEHAVIORS_DIR == "behaviors"
    
    def test_update_settings(self):
        """Test update_settings function."""
        settings = get_settings()
        original_data_dir = settings.DATA_DIR
        
        # Update a setting
        update_settings(DATA_DIR="updated_data")
        
        assert settings.DATA_DIR == "updated_data"
        
        # Update multiple settings
        update_settings(BEHAVIORS_DIR="updated_behaviors", LOG_LEVEL="ERROR")
        
        assert settings.BEHAVIORS_DIR == "updated_behaviors"
        assert settings.LOG_LEVEL == "ERROR"
    
    def test_update_settings_invalid_attribute(self):
        """Test update_settings with invalid attribute."""
        settings = get_settings()
        original_data_dir = settings.DATA_DIR
        
        # Try to update non-existent attribute
        update_settings(INVALID_ATTR="value")
        
        # Should not affect existing settings
        assert settings.DATA_DIR == original_data_dir
        assert not hasattr(settings, 'INVALID_ATTR')
    
    def test_settings_singleton_behavior(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    def test_update_settings_affects_singleton(self):
        """Test that update_settings affects the singleton instance."""
        settings1 = get_settings()
        update_settings(DATA_DIR="test_value")
        settings2 = get_settings()
        
        assert settings1.DATA_DIR == "test_value"
        assert settings2.DATA_DIR == "test_value"
        assert settings1 is settings2


class TestSettingsIntegration:
    """Integration tests for settings."""
    
    def test_full_settings_workflow(self):
        """Test complete settings workflow."""
        # Test default settings
        settings = Settings()
        assert settings.data_dir == 'data'
        assert settings.behaviors_dir == 'behaviors'
        assert settings.commits_file == 'commits.jsonl'
        
        # Test updating settings
        settings.update_settings({
            'data_dir': 'custom_data',
            'behaviors_dir': 'custom_behaviors'
        })
        
        assert settings.data_dir == 'custom_data'
        assert settings.behaviors_dir == 'custom_behaviors'
        assert settings.commits_file == 'commits.jsonl'  # Unchanged
        
        # Test singleton behavior
        new_settings = Settings()
        assert new_settings.data_dir == 'custom_data'  # Should reflect changes
    
    def test_environment_override_workflow(self):
        """Test environment variable override workflow."""
        # Test with environment variables
        with patch.dict('os.environ', {
            'CRAFTNUDGE_DATA_DIR': '/env/data',
            'CRAFTNUDGE_BEHAVIORS_DIR': '/env/behaviors'
        }):
            settings = Settings()
            
            assert settings.data_dir == '/env/data'
            assert settings.behaviors_dir == '/env/behaviors'
            
            # Environment should override defaults
            assert settings.data_dir != 'data'
            assert settings.behaviors_dir != 'behaviors'
    
    def test_settings_persistence(self):
        """Test that settings persist across multiple calls."""
        # Initial state
        settings1 = get_settings()
        original_data_dir = settings1.DATA_DIR
        
        # Update settings
        update_settings(DATA_DIR="persistent_data")
        
        # Get settings again
        settings2 = get_settings()
        
        # Verify persistence
        assert settings1.DATA_DIR == "persistent_data"
        assert settings2.DATA_DIR == "persistent_data"
        assert settings1 is settings2
        
        # Reset to original
        update_settings(DATA_DIR=original_data_dir)
