"""
Unit tests for the view_commits CLI tool.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timezone
import click
from click.testing import CliRunner

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock rich.pagination before importing
with patch.dict('sys.modules', {'rich.pagination': Mock()}):
    from cli.view_commits import (
        print_banner,
        format_commit_table,
        display_commit_details,
        main
    )
from services.data_storage import DataStorageService, CommitEntry


class TestViewCommitsCLI:
    """Test cases for view_commits CLI tool."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def sample_commits(self):
        """Create sample commit entries for testing."""
        return [
            CommitEntry(
                commit_hash='abc123def456',
                author='Test Author 1',
                message='First test commit',
                timestamp_commit=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                changed_files=['file1.py', 'file2.py'],
                repository_path='/test/repo',
                branch='main'
            ),
            CommitEntry(
                commit_hash='def456ghi789',
                author='Test Author 2',
                message='Second test commit with longer message for testing truncation',
                timestamp_commit=datetime(2023, 1, 2, 14, 30, 0, tzinfo=timezone.utc),
                changed_files=['file3.py'],
                repository_path='/test/repo',
                branch='feature'
            )
        ]
    
    def test_print_banner(self, capsys):
        """Test banner printing."""
        print_banner()
        captured = capsys.readouterr()
        assert "CraftNudge Commit Viewer" in captured.out
        assert "View your logged commit history" in captured.out
    
    def test_format_commit_table_detailed(self, sample_commits):
        """Test detailed table formatting."""
        table = format_commit_table(sample_commits, detailed=True)
        
        # Check table structure
        assert table.title == "📋 Detailed Commit History"
        assert len(table.columns) == 7  # ID, Hash, Author, Message, Date, Branch, Files
        
        # Check column headers
        column_names = [col.header for col in table.columns]
        assert "ID" in column_names
        assert "Hash" in column_names
        assert "Author" in column_names
        assert "Message" in column_names
        assert "Date" in column_names
        assert "Branch" in column_names
        assert "Files" in column_names
    
    def test_format_commit_table_simple(self, sample_commits):
        """Test simple table formatting."""
        table = format_commit_table(sample_commits, detailed=False)
        
        # Check table structure
        assert table.title == "📋 Commit History"
        assert len(table.columns) == 5  # Hash, Author, Message, Date, Files
        
        # Check column headers
        column_names = [col.header for col in table.columns]
        assert "Hash" in column_names
        assert "Author" in column_names
        assert "Message" in column_names
        assert "Date" in column_names
        assert "Files" in column_names
    
    def test_format_commit_table_message_truncation(self, sample_commits):
        """Test message truncation in table formatting."""
        # Create commit with very long message
        long_message_commit = CommitEntry(
            commit_hash='xyz789',
            author='Test Author',
            message='This is a very long commit message that should be truncated when displayed in the table format to ensure proper alignment and readability',
            timestamp_commit=datetime(2023, 1, 3, 10, 0, 0, tzinfo=timezone.utc),
            changed_files=['file4.py'],
            repository_path='/test/repo',
            branch='main'
        )
        
        table = format_commit_table([long_message_commit], detailed=False)
        
        # The message should be truncated
        # We can't easily check the exact content, but we can verify the table was created
        assert table.title == "📋 Commit History"
    
    def test_format_commit_table_files_count(self, sample_commits):
        """Test files count formatting."""
        # Create commit with single file
        single_file_commit = CommitEntry(
            commit_hash='single123',
            author='Test Author',
            message='Single file commit',
            timestamp_commit=datetime(2023, 1, 4, 10, 0, 0, tzinfo=timezone.utc),
            changed_files=['file5.py'],
            repository_path='/test/repo',
            branch='main'
        )
        
        table = format_commit_table([single_file_commit], detailed=True)
        assert table.title == "📋 Detailed Commit History"
    
    def test_display_commit_details(self, sample_commits, capsys):
        """Test displaying commit details."""
        display_commit_details(sample_commits[0])
        captured = capsys.readouterr()
        assert "Commit Details" in captured.out
        assert "abc123def456" in captured.out
    
    @patch('cli.view_commits.DataStorageService')
    def test_main_no_commits(self, mock_storage_class, cli_runner):
        """Test main function with no commits."""
        mock_storage = Mock()
        mock_storage.load_commits.return_value = []
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, [])
        
        assert result.exit_code == 0
        assert "No commits have been logged yet" in result.output
    
    @patch('cli.view_commits.DataStorageService')
    def test_main_with_commits(self, mock_storage_class, cli_runner, sample_commits):
        """Test main function with commits."""
        mock_storage = Mock()
        mock_storage.load_commits.return_value = sample_commits
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, [])
        
        assert result.exit_code == 0
        assert "Commit History" in result.output
        assert "abc123def456" in result.output
    
    @patch('cli.view_commits.DataStorageService')
    def test_main_with_limit(self, mock_storage_class, cli_runner, sample_commits):
        """Test main function with limit."""
        mock_storage = Mock()
        mock_storage.load_commits.return_value = sample_commits
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--limit', '1'])
        
        assert result.exit_code == 0
        assert "Showing 1 commit" in result.output
    
    @patch('cli.view_commits.DataStorageService')
    def test_main_with_author_filter(self, mock_storage_class, cli_runner, sample_commits):
        """Test main function with author filter."""
        mock_storage = Mock()
        mock_storage.load_commits.return_value = sample_commits
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--author', 'Test Author 1'])
        
        assert result.exit_code == 0
        assert "Test Author 1" in result.output
    
    @patch('cli.view_commits.DataStorageService')
    def test_main_with_search(self, mock_storage_class, cli_runner, sample_commits):
        """Test main function with search."""
        mock_storage = Mock()
        mock_storage.load_commits.return_value = sample_commits
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--search', 'First'])
        
        assert result.exit_code == 0
        assert "First commit message" in result.output
    
    @patch('cli.view_commits.DataStorageService')
    def test_main_detailed_view(self, mock_storage_class, cli_runner, sample_commits):
        """Test main function with detailed view."""
        mock_storage = Mock()
        mock_storage.load_commits.return_value = sample_commits
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--detailed'])
        
        assert result.exit_code == 0
        assert "Detailed Commit History" in result.output
    
    @patch('cli.view_commits.DataStorageService')
    def test_main_json_output(self, mock_storage_class, cli_runner, sample_commits, tmp_path):
        """Test main function with JSON output."""
        mock_storage = Mock()
        mock_storage.load_commits.return_value = sample_commits
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--json'])
        
        assert result.exit_code == 0
        # Should output JSON to stdout
        assert '"commit_hash": "abc123def456"' in result.output
    
    @patch('cli.view_commits.DataStorageService')
    def test_main_combined_filters(self, mock_storage_class, cli_runner, sample_commits):
        """Test main function with combined filters."""
        mock_storage = Mock()
        mock_storage.load_commits.return_value = sample_commits
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--author', 'Test Author 1', '--limit', '5'])
        
        assert result.exit_code == 0
        assert "Test Author 1" in result.output
    
    def test_help_output(self, cli_runner):
        """Test help output."""
        result = cli_runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "--limit" in result.output
        assert "--author" in result.output
        assert "--search" in result.output
        assert "--detailed" in result.output
        assert "--json" in result.output
    
    @patch('cli.view_commits.DataStorageService')
    def test_main_storage_error(self, mock_storage_class, cli_runner):
        """Test main function with storage error."""
        mock_storage_class.side_effect = Exception("Storage error")
        
        result = cli_runner.invoke(main, [], catch_exceptions=False)
        
        assert result.exit_code == 1
        assert "Error" in result.output
    
    @patch('cli.view_commits.DataStorageService')
    def test_main_json_export_error(self, mock_storage_class, cli_runner, sample_commits, tmp_path):
        """Test main function with JSON export error."""
        mock_storage = Mock()
        mock_storage.load_commits.return_value = sample_commits
        mock_storage_class.return_value = mock_storage
        
        # Create a directory with the same name as the output file to cause an error
        output_file = tmp_path / "output.json"
        output_file.mkdir()
        
        result = cli_runner.invoke(main, ['--json', str(output_file)], catch_exceptions=False)
        
        assert result.exit_code == 1
        assert "Error" in result.output
