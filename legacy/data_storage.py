"""
Data storage service for CraftNudge Git Commit Logger.
Handles JSONL file operations for storing commit metadata.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from config.settings import get_settings
from utils.error_handler import handle_file_errors, DataStorageError


class CommitEntry:
    """Data model for a commit entry in the JSONL file."""
    
    def __init__(self, commit_hash: str, author: str, message: str, 
                 timestamp_commit: datetime, changed_files: List[str], 
                 repository_path: str, branch: str, 
                 entry_id: Optional[str] = None, 
                 timestamp: Optional[datetime] = None):
        self.id = entry_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.commit_hash = commit_hash
        self.author = author
        self.message = message
        self.timestamp_commit = timestamp_commit
        self.changed_files = changed_files
        self.repository_path = repository_path
        self.branch = branch
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'commit_hash': self.commit_hash,
            'author': self.author,
            'message': self.message,
            'timestamp_commit': self.timestamp_commit.isoformat(),
            'changed_files': self.changed_files,
            'repository_path': self.repository_path,
            'branch': self.branch
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommitEntry':
        """Create from dictionary."""
        # Parse timestamps
        timestamp = datetime.fromisoformat(data['timestamp'])
        timestamp_commit = datetime.fromisoformat(data['timestamp_commit'])
        
        return cls(
            commit_hash=data['commit_hash'],
            author=data['author'],
            message=data['message'],
            timestamp_commit=timestamp_commit,
            changed_files=data['changed_files'],
            repository_path=data['repository_path'],
            branch=data['branch'],
            entry_id=data.get('id'),
            timestamp=timestamp
        )


class DataStorageService:
    """Service for handling JSONL data storage operations."""
    
    def __init__(self, file_path: Optional[Path] = None):
        self.settings = get_settings()
        self.file_path = file_path or self.settings.commits_file_path
        self._ensure_data_directory()
    
    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    @handle_file_errors
    def save_commit(self, commit_data: Dict[str, Any]) -> str:
        """
        Save a commit entry to the JSONL file.
        
        Args:
            commit_data: Dictionary containing commit metadata
            
        Returns:
            The unique ID of the saved entry
        """
        # Create commit entry
        entry = CommitEntry(
            commit_hash=commit_data['commit_hash'],
            author=commit_data['author'],
            message=commit_data['message'],
            timestamp_commit=commit_data['timestamp_commit'],
            changed_files=commit_data['changed_files'],
            repository_path=commit_data['repository_path'],
            branch=commit_data['branch']
        )
        
        # Write to JSONL file (append mode)
        with open(self.file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry.to_dict()) + '\n')
        
        return entry.id
    
    @handle_file_errors
    def load_commits(self, limit: Optional[int] = None) -> List[CommitEntry]:
        """
        Load commit entries from the JSONL file.
        
        Args:
            limit: Maximum number of entries to load (None for all)
            
        Returns:
            List of CommitEntry objects
        """
        if not self.file_path.exists():
            return []
        
        entries = []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if limit and len(entries) >= limit:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    entry = CommitEntry.from_dict(data)
                    entries.append(entry)
                except (json.JSONDecodeError, ValueError) as e:
                    # Log malformed lines but continue processing
                    print(f"Warning: Skipping malformed line {line_num}: {e}")
                    continue
        
        return entries
    
    @handle_file_errors
    def get_commit_count(self) -> int:
        """Get the total number of commit entries."""
        if not self.file_path.exists():
            return 0
        
        count = 0
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    count += 1
        
        return count
    
    @handle_file_errors
    def search_commits(self, 
                      author: Optional[str] = None,
                      message_contains: Optional[str] = None,
                      date_from: Optional[datetime] = None,
                      date_to: Optional[datetime] = None) -> List[CommitEntry]:
        """
        Search commits based on various criteria.
        
        Args:
            author: Filter by author name
            message_contains: Filter by commit message content
            date_from: Filter commits from this date
            date_to: Filter commits until this date
            
        Returns:
            List of matching CommitEntry objects
        """
        all_commits = self.load_commits()
        filtered_commits = []
        
        for commit in all_commits:
            # Filter by author
            if author and author.lower() not in commit.author.lower():
                continue
            
            # Filter by message content
            if message_contains and message_contains.lower() not in commit.message.lower():
                continue
            
            # Filter by date range
            if date_from and commit.timestamp_commit < date_from:
                continue
            if date_to and commit.timestamp_commit > date_to:
                continue
            
            filtered_commits.append(commit)
        
        return filtered_commits
    
    @handle_file_errors
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored commits.
        
        Returns:
            Dictionary containing various statistics
        """
        commits = self.load_commits()
        
        if not commits:
            return {
                'total_commits': 0,
                'unique_authors': 0,
                'date_range': None,
                'most_active_author': None,
                'average_files_per_commit': 0
            }
        
        # Calculate statistics
        authors = [commit.author for commit in commits]
        unique_authors = list(set(authors))
        
        # Most active author
        author_counts = {}
        for author in authors:
            author_counts[author] = author_counts.get(author, 0) + 1
        most_active_author = max(author_counts.items(), key=lambda x: x[1])
        
        # Date range
        timestamps = [commit.timestamp_commit for commit in commits]
        date_range = {
            'earliest': min(timestamps),
            'latest': max(timestamps)
        }
        
        # Average files per commit
        total_files = sum(len(commit.changed_files) for commit in commits)
        avg_files = total_files / len(commits)
        
        return {
            'total_commits': len(commits),
            'unique_authors': len(unique_authors),
            'date_range': date_range,
            'most_active_author': {
                'name': most_active_author[0],
                'commits': most_active_author[1]
            },
            'average_files_per_commit': round(avg_files, 2)
        }
    
    @handle_file_errors
    def backup_data(self, backup_path: Path) -> None:
        """
        Create a backup of the commits data.
        
        Args:
            backup_path: Path where backup should be created
        """
        if not self.file_path.exists():
            raise DataStorageError("No data file to backup")
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        import shutil
        shutil.copy2(self.file_path, backup_path)
    
    @handle_file_errors
    def clear_data(self) -> None:
        """Clear all stored commit data."""
        if self.file_path.exists():
            self.file_path.unlink()
