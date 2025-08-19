"""
Unit tests for the track_commit CLI tool.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import click
from click.testing import CliRunner

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.track_commit import (
    print_banner,
    display_summary,
    display_statistics,
    main
)
from services.commit_tracker import CommitTrackerService
from services.data_storage import DataStorageService
from utils.error_handler import GitRepositoryError


class TestTrackCommitCLI:
    """Test cases for track_commit CLI tool."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def mock_tracker(self):
        """Create a mock CommitTrackerService."""
        tracker = Mock(spec=CommitTrackerService)
        tracker.get_tracking_summary.return_value = {
            'repository': {
                'repository_path': '/test/repo',
                'active_branch': 'main',
                'total_commits': 10,
                'is_dirty': False,
                'untracked_files': []
            },
            'tracking_status': {
                'total_logged_commits': 5,
                'coverage_percentage': 50.0
            }
        }
        return tracker
    
    @pytest.fixture
    def mock_storage(self):
        """Create a mock DataStorageService."""
        storage = Mock(spec=DataStorageService)
        storage.get_statistics.return_value = {
            'total_commits': 5,
            'unique_authors': 2,
            'average_files_per_commit': 3.5,
            'most_active_author': {
                'name': 'Test Author',
                'commits': 3
            },
            'date_range': {
                'earliest': Mock(),
                'latest': Mock()
            }
        }
        return storage
    
    def test_print_banner(self, capsys):
        """Test banner printing."""
        print_banner()
        captured = capsys.readouterr()
        assert "CraftNudge Git Logger" in captured.out
        assert "Track your coding patterns" in captured.out
    
    def test_display_summary(self, mock_tracker, capsys):
        """Test summary display."""
        display_summary(mock_tracker)
        captured = capsys.readouterr()
        assert "Tracking Summary" in captured.out
        assert "Repository Path" in captured.out
        assert "Active Branch" in captured.out
    
    def test_display_statistics_with_data(self, mock_storage, capsys):
        """Test statistics display with data."""
        display_statistics(mock_storage)
        captured = capsys.readouterr()
        assert "Commit Statistics" in captured.out
        assert "Total Commits" in captured.out
        assert "5" in captured.out  # Total commits
    
    def test_display_statistics_empty(self, capsys):
        """Test statistics display with no data."""
        empty_storage = Mock(spec=DataStorageService)
        empty_storage.get_statistics.return_value = {
            'total_commits': 0,
            'unique_authors': 0,
            'average_files_per_commit': 0,
            'most_active_author': None,
            'date_range': None
        }
        
        display_statistics(empty_storage)
        captured = capsys.readouterr()
        assert "No commits have been logged yet" in captured.out
    
    @patch('cli.track_commit.CommitTrackerService')
    @patch('cli.track_commit.DataStorageService')
    def test_track_latest_commit_success(self, mock_storage_class, mock_tracker_class, cli_runner):
        """Test successful latest commit tracking."""
        mock_tracker = Mock()
        mock_tracker.track_latest_commit.return_value = 'test-id'
        mock_tracker_class.return_value = mock_tracker
        
        mock_storage = Mock()
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--latest'])
        
        assert result.exit_code == 0
        assert "Latest commit tracked successfully" in result.output
    
    @patch('cli.track_commit.CommitTrackerService')
    def test_track_commit_no_repository(self, mock_tracker_class, cli_runner):
        """Test commit tracking with no Git repository."""
        mock_tracker_class.side_effect = GitRepositoryError("No Git repository found")
        
        result = cli_runner.invoke(main, ['--latest'], catch_exceptions=False)
        
        assert result.exit_code == 1
        assert "Failed to initialize services" in result.output
    
    @patch('cli.track_commit.CommitTrackerService')
    @patch('cli.track_commit.DataStorageService')
    def test_track_latest_commit_no_new_commits(self, mock_storage_class, mock_tracker_class, cli_runner):
        """Test commit tracking when no new commits exist."""
        mock_tracker = Mock()
        mock_tracker.track_latest_commit.return_value = None
        mock_tracker_class.return_value = mock_tracker
        
        result = cli_runner.invoke(main, ['--latest'])
        
        assert result.exit_code == 0
        assert "No new commits to track" in result.output
    
    @patch('cli.track_commit.CommitTrackerService')
    @patch('cli.track_commit.DataStorageService')
    def test_track_all_commits(self, mock_storage_class, mock_tracker_class, cli_runner):
        """Test tracking all commits."""
        mock_tracker = Mock()
        mock_tracker.track_all_commits.return_value = ['id1', 'id2']
        mock_tracker_class.return_value = mock_tracker
        
        mock_storage = Mock()
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--all'])
        
        assert result.exit_code == 0
        assert "Successfully tracked 2 commits" in result.output
    
    @patch('cli.track_commit.CommitTrackerService')
    @patch('cli.track_commit.DataStorageService')
    def test_track_commit_range(self, mock_storage_class, mock_tracker_class, cli_runner):
        """Test tracking commit range."""
        mock_tracker = Mock()
        mock_tracker.track_commit_range.return_value = ['id1']
        mock_tracker_class.return_value = mock_tracker
        
        mock_storage = Mock()
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--range', 'abc123', 'def456'])
        
        assert result.exit_code == 0
        assert "Tracked 1 commits in range" in result.output
    
    def test_track_commit_range_invalid(self, cli_runner):
        """Test tracking commit range with invalid arguments."""
        result = cli_runner.invoke(main, ['--range', 'abc123'])
        
        assert result.exit_code != 0
        assert "Error" in result.output
    
    @patch('cli.track_commit.CommitTrackerService')
    def test_show_summary(self, mock_tracker_class, cli_runner):
        """Test showing tracking summary."""
        mock_tracker = Mock()
        mock_tracker.get_tracking_summary.return_value = {
            'repository': {
                'repository_path': '/test/repo',
                'active_branch': 'main',
                'total_commits': 10,
                'is_dirty': False,
                'untracked_files': []
            },
            'tracking_status': {
                'total_logged_commits': 5,
                'coverage_percentage': 50.0
            }
        }
        mock_tracker_class.return_value = mock_tracker
        
        result = cli_runner.invoke(main, ['--summary'])
        
        assert result.exit_code == 0
        assert "Tracking Summary" in result.output
    
    @patch('cli.track_commit.CommitTrackerService')
    @patch('cli.track_commit.DataStorageService')
    def test_show_statistics(self, mock_storage_class, mock_tracker_class, cli_runner):
        """Test showing commit statistics."""
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker
        
        mock_storage = Mock()
        mock_storage.get_statistics.return_value = {
            'total_commits': 5,
            'unique_authors': 2,
            'average_files_per_commit': 3.5,
            'most_active_author': {
                'name': 'Test Author',
                'commits': 3
            },
            'date_range': {
                'earliest': Mock(),
                'latest': Mock()
            }
        }
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--stats'])
        
        assert result.exit_code == 0
        assert "Commit Statistics" in result.output
    
    def test_help_output(self, cli_runner):
        """Test help output."""
        result = cli_runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "--all" in result.output
        assert "--latest" in result.output
    
    @patch('cli.track_commit.CommitTrackerService')
    @patch('cli.track_commit.DataStorageService')
    def test_default_behavior(self, mock_storage_class, mock_tracker_class, cli_runner):
        """Test default behavior (no flags)."""
        mock_tracker = Mock()
        mock_tracker.track_latest_commit.return_value = 'test-id'
        mock_tracker_class.return_value = mock_tracker
        
        mock_storage = Mock()
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, [])
        
        assert result.exit_code == 0
        assert "Latest commit tracked successfully" in result.output
    
    @patch('cli.track_commit.CommitTrackerService')
    @patch('cli.track_commit.DataStorageService')
    def test_track_all_commits_with_limit(self, mock_storage_class, mock_tracker_class, cli_runner):
        """Test tracking all commits with limit."""
        mock_tracker = Mock()
        mock_tracker.track_all_commits.return_value = ['id1']
        mock_tracker_class.return_value = mock_tracker
        
        mock_storage = Mock()
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--all', '--limit', '5'])
        
        assert result.exit_code == 0
        mock_tracker.track_all_commits.assert_called_with(limit=5)
    
    @patch('cli.track_commit.CommitTrackerService')
    @patch('cli.track_commit.DataStorageService')
    def test_track_commit_with_repo_path(self, mock_storage_class, mock_tracker_class, cli_runner, tmp_path):
        """Test tracking commit with custom repository path."""
        mock_tracker = Mock()
        mock_tracker.track_latest_commit.return_value = 'test-id'
        mock_tracker_class.return_value = mock_tracker
        
        mock_storage = Mock()
        mock_storage_class.return_value = mock_storage
        
        result = cli_runner.invoke(main, ['--repo-path', str(tmp_path)])
        
        assert result.exit_code == 0
        mock_tracker_class.assert_called_with(repo_path=tmp_path)
