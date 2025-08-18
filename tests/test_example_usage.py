"""
Unit tests for the example_usage script.
"""

import pytest
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from example_usage import main
from services.commit_tracker import CommitTrackerService
from services.data_storage import DataStorageService, CommitEntry
from utils.error_handler import GitRepositoryError, DataStorageError


class TestExampleUsage:
    """Test cases for example usage script."""
    
    @patch('example_usage.CommitTrackerService')
    @patch('example_usage.DataStorageService')
    def test_main_success(self, mock_storage_class, mock_tracker_class, capsys):
        """Test main function with successful execution."""
        # Mock tracker
        mock_tracker = Mock()
        mock_tracker.get_repository_info.return_value = {
            'repository_path': '/test/repo',
            'active_branch': 'main',
            'total_commits': 10,
            'is_dirty': False
        }
        mock_tracker.get_tracking_summary.return_value = {
            'tracking_status': {
                'total_logged_commits': 5,
                'coverage_percentage': 50.0
            }
        }
        mock_tracker.track_latest_commit.return_value = 'test-id'
        mock_tracker_class.return_value = mock_tracker
        
        # Mock storage
        mock_storage = Mock()
        mock_storage.get_statistics.return_value = {
            'total_commits': 5,
            'unique_authors': 2,
            'average_files_per_commit': 3.5,
            'most_active_author': {
                'name': 'Test Author',
                'commits': 3
            }
        }
        mock_storage.load_commits.return_value = [
            CommitEntry(
                commit_hash='abc123def456',
                author='Test Author',
                message='Test commit',
                timestamp_commit=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                changed_files=['file1.py'],
                repository_path='/test/repo',
                branch='main'
            )
        ]
        mock_storage_class.return_value = mock_storage
        
        result = main()
        
        # main() doesn't return anything, so we check the output
        captured = capsys.readouterr()
        assert "🚀 CraftNudge Git Commit Logger - Example Usage" in captured.out
        assert "✅ Example completed successfully!" in captured.out
        
        # Verify all methods were called
        mock_tracker.get_repository_info.assert_called_once()
        mock_tracker.get_tracking_summary.assert_called_once()
        mock_tracker.track_latest_commit.assert_called_once()
        mock_storage.get_statistics.assert_called_once()
        mock_storage.load_commits.assert_called_once()
    
    @patch('example_usage.CommitTrackerService')
    def test_main_tracker_error(self, mock_tracker_class, capsys):
        """Test main function with tracker initialization error."""
        mock_tracker_class.side_effect = Exception("Tracker error")
        
        result = main()
        
        captured = capsys.readouterr()
        assert "❌ Error" in captured.out
        assert "Tracker error" in captured.out
    
    @patch('example_usage.CommitTrackerService')
    @patch('example_usage.DataStorageService')
    def test_main_no_commits(self, mock_storage_class, mock_tracker_class, capsys):
        """Test main function with no commits to track."""
        # Mock tracker
        mock_tracker = Mock()
        mock_tracker.get_repository_info.return_value = {
            'repository_path': '/test/repo',
            'active_branch': 'main',
            'total_commits': 0,
            'is_dirty': False
        }
        mock_tracker.get_tracking_summary.return_value = {
            'tracking_status': {
                'total_logged_commits': 0,
                'coverage_percentage': 0.0
            }
        }
        mock_tracker.track_latest_commit.return_value = None  # No new commits
        mock_tracker_class.return_value = mock_tracker
        
        # Mock storage
        mock_storage = Mock()
        mock_storage.get_statistics.return_value = {
            'total_commits': 0,
            'unique_authors': 0,
            'average_files_per_commit': 0,
            'most_active_author': None
        }
        mock_storage.load_commits.return_value = []
        mock_storage_class.return_value = mock_storage
        
        result = main()
        
        captured = capsys.readouterr()
        assert "ℹ️  No new commits to track" in captured.out
        assert "No commits logged yet" in captured.out
        assert "No commits found" in captured.out
    
    @patch('example_usage.CommitTrackerService')
    @patch('example_usage.DataStorageService')
    def test_main_with_statistics(self, mock_storage_class, mock_tracker_class, capsys):
        """Test main function with commit statistics."""
        # Mock tracker
        mock_tracker = Mock()
        mock_tracker.get_repository_info.return_value = {
            'repository_path': '/test/repo',
            'active_branch': 'main',
            'total_commits': 10,
            'is_dirty': False
        }
        mock_tracker.get_tracking_summary.return_value = {
            'tracking_status': {
                'total_logged_commits': 5,
                'coverage_percentage': 50.0
            }
        }
        mock_tracker.track_latest_commit.return_value = 'test-id'
        mock_tracker_class.return_value = mock_tracker
        
        # Mock storage with statistics
        mock_storage = Mock()
        mock_storage.get_statistics.return_value = {
            'total_commits': 10,
            'unique_authors': 3,
            'average_files_per_commit': 2.5,
            'most_active_author': {
                'name': 'Most Active Author',
                'commits': 5
            }
        }
        mock_storage.load_commits.return_value = [
            CommitEntry(
                commit_hash='abc123def456',
                author='Test Author',
                message='Test commit',
                timestamp_commit=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                changed_files=['file1.py'],
                repository_path='/test/repo',
                branch='main'
            )
        ]
        mock_storage_class.return_value = mock_storage
        
        result = main()
        
        captured = capsys.readouterr()
        assert "Total commits logged: 10" in captured.out
        assert "Unique authors: 3" in captured.out
        assert "Average files per commit: 2.5" in captured.out
        assert "Most active author: Most Active Author (5 commits)" in captured.out
    
    @patch('example_usage.CommitTrackerService')
    @patch('example_usage.DataStorageService')
    def test_main_dirty_repository(self, mock_storage_class, mock_tracker_class, capsys):
        """Test main function with dirty repository."""
        # Mock tracker
        mock_tracker = Mock()
        mock_tracker.get_repository_info.return_value = {
            'repository_path': '/test/repo',
            'active_branch': 'main',
            'total_commits': 10,
            'is_dirty': True  # Dirty repository
        }
        mock_tracker.get_tracking_summary.return_value = {
            'tracking_status': {
                'total_logged_commits': 5,
                'coverage_percentage': 50.0
            }
        }
        mock_tracker.track_latest_commit.return_value = 'test-id'
        mock_tracker_class.return_value = mock_tracker
        
        # Mock storage
        mock_storage = Mock()
        mock_storage.get_statistics.return_value = {
            'total_commits': 5,
            'unique_authors': 2,
            'average_files_per_commit': 3.5,
            'most_active_author': {
                'name': 'Test Author',
                'commits': 3
            }
        }
        mock_storage.load_commits.return_value = []
        mock_storage_class.return_value = mock_storage
        
        result = main()
        
        captured = capsys.readouterr()
        assert "Repository status: Dirty" in captured.out


class TestExampleUsageIntegration:
    """Integration tests for example usage."""
    
    def test_commit_entry_creation(self):
        """Test CommitEntry creation for examples."""
        commit_data = {
            'commit_hash': 'abc123def456',
            'author': 'Test Author',
            'message': 'Test commit message',
            'timestamp_commit': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'changed_files': ['file1.py', 'file2.py'],
            'repository_path': '/test/repo',
            'branch': 'main'
        }
        
        entry = CommitEntry(**commit_data)
        
        assert entry.commit_hash == 'abc123def456'
        assert entry.author == 'Test Author'
        assert entry.message == 'Test commit message'
        assert len(entry.changed_files) == 2
        assert entry.repository_path == '/test/repo'
        assert entry.branch == 'main'
        assert entry.id is not None
        assert entry.timestamp is not None
    
    def test_commit_entry_serialization(self):
        """Test CommitEntry serialization for examples."""
        commit_data = {
            'commit_hash': 'abc123def456',
            'author': 'Test Author',
            'message': 'Test commit message',
            'timestamp_commit': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'changed_files': ['file1.py'],
            'repository_path': '/test/repo',
            'branch': 'main'
        }
        
        entry = CommitEntry(**commit_data)
        serialized = entry.to_dict()
        
        assert serialized['commit_hash'] == 'abc123def456'
        assert serialized['author'] == 'Test Author'
        assert serialized['message'] == 'Test commit message'
        assert serialized['changed_files'] == ['file1.py']
        assert 'id' in serialized
        assert 'timestamp' in serialized
    
    @patch('example_usage.CommitTrackerService')
    @patch('example_usage.DataStorageService')
    def test_complete_workflow_simulation(self, mock_storage_class, mock_tracker_class, capsys):
        """Test simulation of complete workflow."""
        # Mock tracker
        mock_tracker = Mock()
        mock_tracker.get_repository_info.return_value = {
            'repository_path': '/test/repo',
            'active_branch': 'main',
            'total_commits': 10,
            'is_dirty': False
        }
        mock_tracker.get_tracking_summary.return_value = {
            'tracking_status': {
                'total_logged_commits': 5,
                'coverage_percentage': 50.0
            }
        }
        mock_tracker.track_latest_commit.return_value = 'test-id'
        mock_tracker_class.return_value = mock_tracker
        
        # Mock storage
        mock_storage = Mock()
        mock_storage.get_statistics.return_value = {
            'total_commits': 1,
            'unique_authors': 1,
            'average_files_per_commit': 0,
            'most_active_author': {
                'name': 'Test Author',
                'commits': 1
            }
        }
        mock_storage.load_commits.return_value = [
            CommitEntry(
                commit_hash='abc123def456',
                author='Test Author',
                message='Test commit',
                timestamp_commit=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                changed_files=['file1.py'],
                repository_path='/test/repo',
                branch='main'
            )
        ]
        mock_storage_class.return_value = mock_storage
        
        # Test the complete workflow
        main()
        
        captured = capsys.readouterr()
        assert "🚀 CraftNudge Git Commit Logger - Example Usage" in captured.out
        assert "✅ Example completed successfully!" in captured.out
