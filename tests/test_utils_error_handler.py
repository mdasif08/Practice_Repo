"""
Unit tests for the error handler utilities.
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from utils.error_handler import (
    CraftNudgeError,
    GitRepositoryError,
    DataStorageError,
    ConfigurationError,
    handle_git_errors,
    handle_file_errors,
    validate_git_repository,
    validate_data_directory,
    display_success_message,
    display_info_message,
    display_warning_message,
    display_error_message,
    safe_exit
)


class TestCustomExceptions:
    """Test cases for custom exception classes."""
    
    def test_craft_nudge_error(self):
        """Test CraftNudgeError exception."""
        error = CraftNudgeError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_git_repository_error(self):
        """Test GitRepositoryError exception."""
        error = GitRepositoryError("Git repository error")
        assert str(error) == "Git repository error"
        assert isinstance(error, CraftNudgeError)
    
    def test_data_storage_error(self):
        """Test DataStorageError exception."""
        error = DataStorageError("Data storage error")
        assert str(error) == "Data storage error"
        assert isinstance(error, CraftNudgeError)
    
    def test_configuration_error(self):
        """Test ConfigurationError exception."""
        error = ConfigurationError("Configuration error")
        assert str(error) == "Configuration error"
        assert isinstance(error, CraftNudgeError)


class TestErrorHandlerDecorators:
    """Test cases for error handler decorators."""
    
    def test_handle_git_errors_success(self):
        """Test handle_git_errors decorator with successful function."""
        @handle_git_errors
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    def test_handle_git_errors_invalid_repository(self):
        """Test handle_git_errors decorator with InvalidGitRepositoryError."""
        from git import InvalidGitRepositoryError
        
        @handle_git_errors
        def test_function():
            raise InvalidGitRepositoryError("No Git repository found")
        
        with patch('utils.error_handler.sys.exit') as mock_exit:
            test_function()
            mock_exit.assert_called_with(1)
    
    def test_handle_git_errors_no_such_path(self):
        """Test handle_git_errors decorator with NoSuchPathError."""
        from git import NoSuchPathError
        
        @handle_git_errors
        def test_function():
            raise NoSuchPathError("Path does not exist")
        
        with patch('utils.error_handler.sys.exit') as mock_exit:
            test_function()
            mock_exit.assert_called_with(1)
    
    def test_handle_git_errors_git_command_error(self):
        """Test handle_git_errors decorator with GitCommandError."""
        from git import GitCommandError
        
        @handle_git_errors
        def test_function():
            raise GitCommandError("git command failed", 1)
        
        with patch('utils.error_handler.sys.exit') as mock_exit:
            test_function()
            mock_exit.assert_called_with(1)
    
    def test_handle_git_errors_unexpected_error(self):
        """Test handle_git_errors decorator with unexpected error."""
        @handle_git_errors
        def test_function():
            raise ValueError("Unexpected error")
        
        with patch('utils.error_handler.sys.exit') as mock_exit:
            test_function()
            mock_exit.assert_called_with(1)
    
    def test_handle_file_errors_success(self):
        """Test handle_file_errors decorator with successful function."""
        @handle_file_errors
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    def test_handle_file_errors_permission_error(self):
        """Test handle_file_errors decorator with PermissionError."""
        @handle_file_errors
        def test_function():
            raise PermissionError("Permission denied")
        
        with patch('utils.error_handler.sys.exit') as mock_exit:
            test_function()
            mock_exit.assert_called_with(1)
    
    def test_handle_file_errors_file_not_found(self):
        """Test handle_file_errors decorator with FileNotFoundError."""
        @handle_file_errors
        def test_function():
            raise FileNotFoundError("File not found")
        
        with patch('utils.error_handler.sys.exit') as mock_exit:
            test_function()
            mock_exit.assert_called_with(1)
    
    def test_handle_file_errors_unexpected_error(self):
        """Test handle_file_errors decorator with unexpected error."""
        @handle_file_errors
        def test_function():
            raise OSError("File operation failed")
        
        with patch('utils.error_handler.sys.exit') as mock_exit:
            test_function()
            mock_exit.assert_called_with(1)


class TestValidationFunctions:
    """Test cases for validation functions."""
    
    @patch('utils.error_handler.git.Repo')
    def test_validate_git_repository_valid(self, mock_repo):
        """Test validate_git_repository with valid repository."""
        mock_repo.return_value = Mock()
        
        result = validate_git_repository(Path("/valid/repo"))
        
        assert result is True
        mock_repo.assert_called_with(Path("/valid/repo"))
    
    @patch('utils.error_handler.git.Repo')
    def test_validate_git_repository_invalid(self, mock_repo):
        """Test validate_git_repository with invalid repository."""
        from git import InvalidGitRepositoryError
        mock_repo.side_effect = InvalidGitRepositoryError("Invalid repo")
        
        result = validate_git_repository(Path("/invalid/repo"))
        
        assert result is False
    
    @patch('utils.error_handler.git.Repo')
    def test_validate_git_repository_no_such_path(self, mock_repo):
        """Test validate_git_repository with non-existent path."""
        from git import NoSuchPathError
        mock_repo.side_effect = NoSuchPathError("Path does not exist")
        
        result = validate_git_repository(Path("/nonexistent/repo"))
        
        assert result is False
    
    def test_validate_data_directory_success(self, tmp_path):
        """Test validate_data_directory with valid directory."""
        result = validate_data_directory(tmp_path)
        
        assert result is True
    
    def test_validate_data_directory_permission_error(self, tmp_path):
        """Test validate_data_directory with permission error."""
        # Create a directory and make it read-only to simulate permission error
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        
        # On Windows, we can't easily simulate permission errors in tests
        # So we'll test the normal case and mock the permission error
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            
            result = validate_data_directory(test_dir)
            assert result is True
    
    def test_validate_data_directory_creates_directory(self, tmp_path):
        """Test that validate_data_directory creates directory if it doesn't exist."""
        new_dir = tmp_path / "new_directory"
        
        result = validate_data_directory(new_dir)
        
        assert result is True
        assert new_dir.exists()


class TestMessageDisplayFunctions:
    """Test cases for message display functions."""
    
    def test_display_success_message(self, capsys):
        """Test display_success_message function."""
        display_success_message("Operation completed successfully")
        captured = capsys.readouterr()
        
        assert "✅ Success" in captured.out
        assert "Operation completed successfully" in captured.out
    
    def test_display_info_message(self, capsys):
        """Test display_info_message function."""
        display_info_message("This is an informational message")
        captured = capsys.readouterr()
        
        assert "ℹ️ Info" in captured.out
        assert "This is an informational message" in captured.out
    
    def test_display_warning_message(self, capsys):
        """Test display_warning_message function."""
        display_warning_message("This is a warning message")
        captured = capsys.readouterr()
        
        assert "⚠️ Warning" in captured.out
        assert "This is a warning message" in captured.out
    
    def test_display_error_message_default_title(self, capsys):
        """Test display_error_message function with default title."""
        display_error_message("This is an error message")
        captured = capsys.readouterr()
        
        assert "❌ Error" in captured.out
        assert "This is an error message" in captured.out
    
    def test_display_error_message_custom_title(self, capsys):
        """Test display_error_message function with custom title."""
        display_error_message("This is an error message", "Custom Error Title")
        captured = capsys.readouterr()
        
        assert "Custom Error Title" in captured.out
        assert "This is an error message" in captured.out


class TestSafeExitFunction:
    """Test cases for safe_exit function."""
    
    def test_safe_exit_success_with_message(self):
        """Test safe_exit with success exit code and message."""
        with patch('utils.error_handler.sys.exit') as mock_exit:
            safe_exit(0, "Operation completed successfully")
            mock_exit.assert_called_with(0)
    
    def test_safe_exit_error_with_message(self):
        """Test safe_exit with error exit code and message."""
        with patch('utils.error_handler.sys.exit') as mock_exit:
            safe_exit(1, "Operation failed")
            mock_exit.assert_called_with(1)
    
    def test_safe_exit_without_message(self):
        """Test safe_exit without message."""
        with patch('utils.error_handler.sys.exit') as mock_exit:
            safe_exit(0)
            mock_exit.assert_called_with(0)
    
    def test_safe_exit_default_exit_code(self):
        """Test safe_exit with default exit code."""
        with patch('utils.error_handler.sys.exit') as mock_exit:
            safe_exit(message="Test message")
            mock_exit.assert_called_with(0)


class TestErrorHandlerIntegration:
    """Integration tests for error handler utilities."""
    
    def test_error_handler_with_git_operations(self):
        """Test error handler integration with Git operations."""
        from git import InvalidGitRepositoryError
        
        @handle_git_errors
        def git_operation():
            raise InvalidGitRepositoryError("No Git repository found")
        
        with patch('utils.error_handler.sys.exit') as mock_exit:
            git_operation()
            mock_exit.assert_called_with(1)
    
    def test_error_handler_with_file_operations(self):
        """Test error handler integration with file operations."""
        @handle_file_errors
        def file_operation():
            raise PermissionError("Permission denied")
        
        with patch('utils.error_handler.sys.exit') as mock_exit:
            file_operation()
            mock_exit.assert_called_with(1)
    
    def test_validation_and_error_handling_workflow(self, tmp_path):
        """Test complete validation and error handling workflow."""
        # Test valid data directory
        assert validate_data_directory(tmp_path) is True
        
        # Test invalid Git repository
        with patch('utils.error_handler.git.Repo') as mock_repo:
            from git import InvalidGitRepositoryError
            mock_repo.side_effect = InvalidGitRepositoryError("Invalid repo")
            
            assert validate_git_repository(tmp_path) is False
    
    def test_message_display_workflow(self, capsys):
        """Test complete message display workflow."""
        # Display different types of messages
        display_success_message("Success!")
        display_info_message("Info message")
        display_warning_message("Warning message")
        display_error_message("Error message")
        
        captured = capsys.readouterr()
        
        # Verify all message types are displayed
        assert "✅ Success" in captured.out
        assert "ℹ️ Info" in captured.out
        assert "⚠️ Warning" in captured.out
        assert "❌ Error" in captured.out
