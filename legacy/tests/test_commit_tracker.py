"""
Unit tests for the CommitTrackerService.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timezone

from services.commit_tracker import CommitTrackerService
from utils.error_handler import GitRepositoryError


class TestCommitTrackerService:
    """Test cases for CommitTrackerService."""
    
    @pytest.fixture
    def mock_repo_path(self, tmp_path):
        """Create a mock repository path."""
        return tmp_path / "test_repo"
    
    @pytest.fixture
    def mock_git_repo(self):
        """Create a mock Git repository."""
        repo = Mock()
        repo.head.commit = Mock()
        repo.active_branch.name = "main"
        repo.is_dirty.return_value = False
        repo.untracked_files = []
        repo.remotes = []
        return repo
    
    @pytest.fixture
    def mock_commit(self):
        """Create a mock Git commit."""
        commit = Mock()
        commit.hexsha = "abc123def456"
        commit.author.name = "Test Author"
        commit.message = "Test commit message"
        commit.committed_datetime = datetime(2023, 1, 1, 12, 0, 0)
        commit.parents = [Mock()]
        commit.tree.traverse.return_value = []
        return commit
    
    def test_init_with_valid_repo(self, mock_repo_path, mock_git_repo):
        """Test initialization with valid repository."""
        with patch('git.Repo', return_value=mock_git_repo):
            with patch('services.commit_tracker.validate_git_repository', return_value=True):
                service = CommitTrackerService(repo_path=mock_repo_path)
                assert service.repo_path == mock_repo_path
    
    def test_init_with_invalid_repo(self, mock_repo_path):
        """Test initialization with invalid repository."""
        with patch('services.commit_tracker.validate_git_repository', return_value=False):
            with pytest.raises(GitRepositoryError):
                CommitTrackerService(repo_path=mock_repo_path)
    
    def test_get_latest_commit(self, mock_repo_path, mock_git_repo, mock_commit):
        """Test getting the latest commit."""
        mock_git_repo.head.commit = mock_commit
        
        with patch('git.Repo', return_value=mock_git_repo):
            with patch('services.commit_tracker.validate_git_repository', return_value=True):
                service = CommitTrackerService(repo_path=mock_repo_path)
                result = service.get_latest_commit()
                assert result == mock_commit
    
    @patch('services.commit_tracker.git.Repo')
    def test_get_latest_commit_no_commits(self, mock_git_repo, mock_repo_path):
        """Test get_latest_commit with no commits in repository."""
        mock_repo = Mock()
        mock_repo.head.commit = None  # No commits
        mock_git_repo.return_value = mock_repo
        
        tracker = CommitTrackerService(repo_path=mock_repo_path)
        
        result = tracker.get_latest_commit()
        
        assert result is None
    
    def test_get_commit_metadata(self, mock_repo_path, mock_git_repo, mock_commit):
        """Test extracting commit metadata."""
        # Mock diff items
        diff_item = Mock()
        diff_item.a_path = "test_file.py"
        diff_item.b_path = None
        mock_commit.diff.return_value = [diff_item]
        
        with patch('git.Repo', return_value=mock_git_repo):
            with patch('services.commit_tracker.validate_git_repository', return_value=True):
                service = CommitTrackerService(repo_path=mock_repo_path)
                metadata = service.get_commit_metadata(mock_commit)
                
                assert metadata['commit_hash'] == "abc123def456"
                assert metadata['author'] == "Test Author"
                assert metadata['message'] == "Test commit message"
                assert metadata['changed_files'] == ["test_file.py"]
                assert metadata['branch'] == "main"
    
    def test_get_commit_metadata_first_commit(self, mock_repo_path, mock_git_repo, mock_commit):
        """Test extracting metadata from first commit (no parents)."""
        mock_commit.parents = []
        tree_item = Mock()
        tree_item.name = "first_file.py"
        mock_commit.tree.traverse.return_value = [tree_item]
        
        with patch('git.Repo', return_value=mock_git_repo):
            with patch('services.commit_tracker.validate_git_repository', return_value=True):
                service = CommitTrackerService(repo_path=mock_repo_path)
                metadata = service.get_commit_metadata(mock_commit)
                
                assert metadata['changed_files'] == ["first_file.py"]
    
    @patch('services.commit_tracker.git.Repo')
    def test_get_commit_metadata_detached_head(self, mock_git_repo, mock_repo_path, mock_commit):
        """Test get_commit_metadata with detached HEAD."""
        mock_repo = Mock()
        mock_repo.head.is_detached = True
        mock_repo.head.commit = mock_commit
        mock_git_repo.return_value = mock_repo
        
        tracker = CommitTrackerService(repo_path=mock_repo_path)
        
        # Should handle detached HEAD gracefully
        metadata = tracker.get_commit_metadata(mock_commit)
        
        assert metadata['commit_hash'] == 'test-hash'
        assert metadata['author'] == 'Test Author'
        assert metadata['message'] == 'Test commit message'
        assert metadata['branch'] == 'detached'
    
    def test_get_repository_info(self, mock_repo_path, mock_git_repo):
        """Test getting repository information."""
        mock_git_repo.iter_commits.return_value = [Mock(), Mock(), Mock()]  # 3 commits
        
        with patch('git.Repo', return_value=mock_git_repo):
            with patch('services.commit_tracker.validate_git_repository', return_value=True):
                service = CommitTrackerService(repo_path=mock_repo_path)
                info = service.get_repository_info()
                
                assert info['repository_path'] == str(mock_repo_path.absolute())
                assert info['active_branch'] == "main"
                assert info['total_commits'] == 3
                assert info['is_dirty'] is False
                assert info['untracked_files'] == []
    
    @patch('services.commit_tracker.git.Repo')
    def test_get_repository_info_detached_head(self, mock_git_repo, mock_repo_path):
        """Test get_repository_info with detached HEAD."""
        mock_repo = Mock()
        mock_repo.head.is_detached = True
        mock_repo.head.commit = Mock()
        mock_repo.is_dirty.return_value = False
        mock_repo.untracked_files = []
        mock_git_repo.return_value = mock_repo
        
        tracker = CommitTrackerService(repo_path=mock_repo_path)
        
        info = tracker.get_repository_info()
        
        assert info['repository_path'] == str(mock_repo_path)
        assert info['active_branch'] == 'detached'
        assert info['is_dirty'] is False
        assert info['untracked_files'] == []
