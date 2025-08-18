"""
Unit tests for the DataStorageService.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from services.data_storage import DataStorageService, CommitEntry


class TestDataStorageService:
    """Test cases for DataStorageService."""
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
            yield Path(f.name)
        # Cleanup
        if Path(f.name).exists():
            Path(f.name).unlink()
    
    @pytest.fixture
    def sample_commit_data(self):
        """Create sample commit data for testing."""
        return {
            'commit_hash': 'abc123def456',
            'author': 'Test Author',
            'message': 'Test commit message',
            'timestamp_commit': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'changed_files': ['test_file.py', 'README.md'],
            'repository_path': '/path/to/repo',
            'branch': 'main'
        }
    
    def test_init_creates_directory(self, temp_file):
        """Test that initialization creates the data directory."""
        data_dir = temp_file.parent / "test_data" / "behaviors"
        service = DataStorageService(file_path=data_dir / "commits.jsonl")
        
        assert data_dir.exists()
        assert service.file_path.parent == data_dir
    
    def test_save_commit(self, temp_file, sample_commit_data):
        """Test saving a commit entry."""
        service = DataStorageService(file_path=temp_file)
        entry_id = service.save_commit(sample_commit_data)
        
        # Verify file was created and contains data
        assert temp_file.exists()
        assert entry_id is not None
        
        # Read and verify the saved data
        with open(temp_file, 'r') as f:
            line = f.readline().strip()
            data = json.loads(line)
            
            assert data['commit_hash'] == sample_commit_data['commit_hash']
            assert data['author'] == sample_commit_data['author']
            assert data['message'] == sample_commit_data['message']
            assert data['changed_files'] == sample_commit_data['changed_files']
    
    def test_load_commits_empty_file(self, temp_file):
        """Test loading commits from empty file."""
        service = DataStorageService(file_path=temp_file)
        commits = service.load_commits()
        
        assert commits == []
    
    def test_load_commits_with_data(self, temp_file, sample_commit_data):
        """Test loading commits from file with data."""
        service = DataStorageService(file_path=temp_file)
        
        # Save some commits
        service.save_commit(sample_commit_data)
        
        # Modify data for second commit
        sample_commit_data['commit_hash'] = 'def456ghi789'
        sample_commit_data['message'] = 'Second commit'
        service.save_commit(sample_commit_data)
        
        # Load commits
        commits = service.load_commits()
        
        assert len(commits) == 2
        assert commits[0].commit_hash == 'abc123def456'
        assert commits[1].commit_hash == 'def456ghi789'
        assert commits[0].message == 'Test commit message'
        assert commits[1].message == 'Second commit'
    
    def test_load_commits_with_limit(self, temp_file, sample_commit_data):
        """Test loading commits with limit."""
        service = DataStorageService(file_path=temp_file)
        
        # Save multiple commits
        for i in range(5):
            sample_commit_data['commit_hash'] = f'hash{i:03d}'
            sample_commit_data['message'] = f'Commit {i}'
            service.save_commit(sample_commit_data)
        
        # Load with limit
        commits = service.load_commits(limit=3)
        
        assert len(commits) == 3
        assert commits[0].commit_hash == 'hash000'
        assert commits[1].commit_hash == 'hash001'
        assert commits[2].commit_hash == 'hash002'
    
    def test_get_commit_count(self, temp_file, sample_commit_data):
        """Test getting commit count."""
        service = DataStorageService(file_path=temp_file)
        
        # Empty file
        assert service.get_commit_count() == 0
        
        # Add commits
        service.save_commit(sample_commit_data)
        assert service.get_commit_count() == 1
        
        sample_commit_data['commit_hash'] = 'def456ghi789'
        service.save_commit(sample_commit_data)
        assert service.get_commit_count() == 2
    
    def test_search_commits_by_author(self, temp_file, sample_commit_data):
        """Test searching commits by author."""
        service = DataStorageService(file_path=temp_file)
        
        # Save commits with different authors
        service.save_commit(sample_commit_data)
        
        sample_commit_data['commit_hash'] = 'def456ghi789'
        sample_commit_data['author'] = 'Another Author'
        service.save_commit(sample_commit_data)
        
        # Search by author
        results = service.search_commits(author='Test')
        assert len(results) == 1
        assert results[0].author == 'Test Author'
        
        results = service.search_commits(author='Another')
        assert len(results) == 1
        assert results[0].author == 'Another Author'
    
    def test_search_commits_by_message(self, temp_file, sample_commit_data):
        """Test searching commits by message content."""
        service = DataStorageService(file_path=temp_file)
        
        # Save commits with different messages
        service.save_commit(sample_commit_data)
        
        sample_commit_data['commit_hash'] = 'def456ghi789'
        sample_commit_data['message'] = 'Fix bug in login'
        service.save_commit(sample_commit_data)
        
        # Search by message
        results = service.search_commits(message_contains='Test')
        assert len(results) == 1
        assert 'Test commit message' in results[0].message
        
        results = service.search_commits(message_contains='bug')
        assert len(results) == 1
        assert 'Fix bug in login' in results[0].message
    
    def test_get_statistics(self, temp_file, sample_commit_data):
        """Test getting commit statistics."""
        service = DataStorageService(file_path=temp_file)
        
        # Empty statistics
        stats = service.get_statistics()
        assert stats['total_commits'] == 0
        assert stats['unique_authors'] == 0
        assert stats['average_files_per_commit'] == 0
        
        # Add commits
        service.save_commit(sample_commit_data)
        
        sample_commit_data['commit_hash'] = 'def456ghi789'
        sample_commit_data['author'] = 'Another Author'
        sample_commit_data['changed_files'] = ['file1.py', 'file2.py', 'file3.py']
        service.save_commit(sample_commit_data)
        
        # Get statistics
        stats = service.get_statistics()
        assert stats['total_commits'] == 2
        assert stats['unique_authors'] == 2
        assert stats['average_files_per_commit'] == 2.5  # (2 + 3) / 2
        assert stats['most_active_author']['name'] in ['Test Author', 'Another Author']
        assert stats['most_active_author']['commits'] == 1
    
    def test_backup_data(self, temp_file, sample_commit_data):
        """Test backing up data."""
        service = DataStorageService(file_path=temp_file)
        
        # Save some data
        service.save_commit(sample_commit_data)
        
        # Create backup
        backup_path = temp_file.parent / "backup.jsonl"
        service.backup_data(backup_path)
        
        # Verify backup exists and contains data
        assert backup_path.exists()
        assert backup_path.stat().st_size > 0
        
        # Cleanup
        backup_path.unlink()
    
    def test_clear_data(self, temp_file, sample_commit_data):
        """Test clearing all data."""
        storage = DataStorageService(file_path=temp_file)
        
        # Add some data first
        for commit in sample_commit_data:
            storage.save_commit(commit)
        
        # Verify data exists
        commits = storage.load_commits()
        assert len(commits) == 2
        
        # Clear data
        storage.clear_data()
        
        # Verify data is cleared
        commits = storage.load_commits()
        assert len(commits) == 0


class TestCommitEntry:
    """Test cases for CommitEntry model."""
    
    def test_commit_entry_creation(self):
        """Test creating a CommitEntry."""
        data = {
            'commit_hash': 'abc123def456',
            'author': 'Test Author',
            'message': 'Test commit message',
            'timestamp_commit': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'changed_files': ['test_file.py'],
            'repository_path': '/path/to/repo',
            'branch': 'main'
        }
        
        entry = CommitEntry(**data)
        
        assert entry.commit_hash == 'abc123def456'
        assert entry.author == 'Test Author'
        assert entry.message == 'Test commit message'
        assert entry.changed_files == ['test_file.py']
        assert entry.repository_path == '/path/to/repo'
        assert entry.branch == 'main'
        assert entry.id is not None
        assert entry.timestamp is not None
    
    def test_commit_entry_defaults(self):
        """Test CommitEntry default values."""
        data = {
            'commit_hash': 'abc123def456',
            'author': 'Test Author',
            'message': 'Test commit message',
            'timestamp_commit': datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'changed_files': ['test_file.py'],
            'repository_path': '/path/to/repo',
            'branch': 'main'
        }
        
        entry = CommitEntry(**data)
        
        # Should have generated ID and timestamp
        assert len(entry.id) > 0
        assert entry.timestamp is not None
        assert entry.timestamp.tzinfo is not None  # Should be timezone-aware
