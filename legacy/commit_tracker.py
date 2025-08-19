"""
Commit tracker service for CraftNudge Git Commit Logger.
Core service for extracting and logging Git commit metadata.
"""

import git
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config.settings import get_settings
from services.data_storage import DataStorageService
from utils.error_handler import (
    handle_git_errors, 
    validate_git_repository, 
    display_success_message,
    display_info_message,
    GitRepositoryError
)

console = Console()


class CommitTrackerService:
    """Service for tracking and logging Git commits."""
    
    def __init__(self, repo_path: Optional[Path] = None):
        self.settings = get_settings()
        self.repo_path = repo_path or self.settings.git_repo_path
        self.storage_service = DataStorageService()
        self._validate_repository()
    
    def _validate_repository(self) -> None:
        """Validate that the repository path is a valid Git repository."""
        if not validate_git_repository(self.repo_path):
            raise GitRepositoryError(
                f"No valid Git repository found at: {self.repo_path}"
            )
    
    @handle_git_errors
    def get_latest_commit(self) -> Optional[git.Commit]:
        """Get the latest commit from the repository."""
        repo = git.Repo(self.repo_path)
        try:
            return repo.head.commit
        except git.BadName:
            # No commits yet
            return None
    
    @handle_git_errors
    def get_commit_metadata(self, commit: git.Commit) -> Dict[str, Any]:
        """
        Extract metadata from a Git commit.
        
        Args:
            commit: Git commit object
            
        Returns:
            Dictionary containing commit metadata
        """
        # Get changed files
        changed_files = []
        if commit.parents:
            # Compare with parent commit
            diff = commit.diff(commit.parents[0])
            changed_files = [item.a_path or item.b_path for item in diff if item.a_path or item.b_path]
        else:
            # First commit - get all files in the commit
            changed_files = [item.name for item in commit.tree.traverse()]
        
        # Get current branch
        repo = git.Repo(self.repo_path)
        try:
            branch = repo.active_branch.name
        except TypeError:
            # Detached HEAD state
            branch = "detached"
        
        return {
            'commit_hash': commit.hexsha,
            'author': commit.author.name,
            'message': commit.message.strip(),
            'timestamp_commit': commit.committed_datetime.replace(tzinfo=timezone.utc),
            'changed_files': changed_files,
            'repository_path': str(self.repo_path.absolute()),
            'branch': branch
        }
    
    @handle_git_errors
    def track_latest_commit(self) -> Optional[str]:
        """
        Track and log the latest commit if it hasn't been logged before.
        
        Returns:
            Entry ID if commit was logged, None if already logged or no commits
        """
        latest_commit = self.get_latest_commit()
        if not latest_commit:
            display_info_message("No commits found in the repository.")
            return None
        
        # Check if this commit has already been logged
        existing_commits = self.storage_service.load_commits()
        for existing in existing_commits:
            if existing.commit_hash == latest_commit.hexsha:
                display_info_message(
                    f"Commit {latest_commit.hexsha[:8]} has already been logged."
                )
                return existing.id
        
        # Extract metadata and save
        metadata = self.get_commit_metadata(latest_commit)
        entry_id = self.storage_service.save_commit(metadata)
        
        display_success_message(
            f"✅ Successfully logged commit {latest_commit.hexsha[:8]}\n"
            f"Author: {metadata['author']}\n"
            f"Message: {metadata['message'][:50]}{'...' if len(metadata['message']) > 50 else ''}\n"
            f"Files changed: {len(metadata['changed_files'])}"
        )
        
        return entry_id
    
    @handle_git_errors
    def track_all_commits(self, limit: Optional[int] = None) -> List[str]:
        """
        Track and log all commits in the repository.
        
        Args:
            limit: Maximum number of commits to process
            
        Returns:
            List of entry IDs for logged commits
        """
        repo = git.Repo(self.repo_path)
        commits = list(repo.iter_commits('HEAD'))
        
        if limit:
            commits = commits[:limit]
        
        if not commits:
            display_info_message("No commits found in the repository.")
            return []
        
        # Get existing commit hashes to avoid duplicates
        existing_commits = self.storage_service.load_commits()
        existing_hashes = {commit.commit_hash for commit in existing_commits}
        
        # Filter out already logged commits
        new_commits = [commit for commit in commits if commit.hexsha not in existing_hashes]
        
        if not new_commits:
            display_info_message("All commits have already been logged.")
            return []
        
        entry_ids = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Logging {len(new_commits)} commits...", 
                total=len(new_commits)
            )
            
            for commit in new_commits:
                metadata = self.get_commit_metadata(commit)
                entry_id = self.storage_service.save_commit(metadata)
                entry_ids.append(entry_id)
                progress.advance(task)
        
        display_success_message(
            f"✅ Successfully logged {len(entry_ids)} new commits."
        )
        
        return entry_ids
    
    @handle_git_errors
    def track_commit_range(self, start_commit: str, end_commit: str = "HEAD") -> List[str]:
        """
        Track and log commits in a specific range.
        
        Args:
            start_commit: Starting commit hash or reference
            end_commit: Ending commit hash or reference (default: HEAD)
            
        Returns:
            List of entry IDs for logged commits
        """
        repo = git.Repo(self.repo_path)
        
        try:
            start = repo.commit(start_commit)
            end = repo.commit(end_commit)
        except git.BadName as e:
            raise GitRepositoryError(f"Invalid commit reference: {e}")
        
        # Get commits in range
        commits = list(repo.iter_commits(f"{start.hexsha}..{end.hexsha}"))
        
        if not commits:
            display_info_message("No commits found in the specified range.")
            return []
        
        # Get existing commit hashes to avoid duplicates
        existing_commits = self.storage_service.load_commits()
        existing_hashes = {commit.commit_hash for commit in existing_commits}
        
        # Filter out already logged commits
        new_commits = [commit for commit in commits if commit.hexsha not in existing_hashes]
        
        if not new_commits:
            display_info_message("All commits in range have already been logged.")
            return []
        
        entry_ids = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Logging {len(new_commits)} commits in range...", 
                total=len(new_commits)
            )
            
            for commit in new_commits:
                metadata = self.get_commit_metadata(commit)
                entry_id = self.storage_service.save_commit(metadata)
                entry_ids.append(entry_id)
                progress.advance(task)
        
        display_success_message(
            f"✅ Successfully logged {len(entry_ids)} commits in range."
        )
        
        return entry_ids
    
    def get_repository_info(self) -> Dict[str, Any]:
        """
        Get information about the current repository.
        
        Returns:
            Dictionary containing repository information
        """
        repo = git.Repo(self.repo_path)
        
        try:
            active_branch = repo.active_branch.name
        except TypeError:
            active_branch = "detached"
        
        return {
            'repository_path': str(self.repo_path.absolute()),
            'active_branch': active_branch,
            'remote_urls': [remote.url for remote in repo.remotes],
            'total_commits': len(list(repo.iter_commits('HEAD'))),
            'is_dirty': repo.is_dirty(),
            'untracked_files': repo.untracked_files
        }
    
    def get_tracking_summary(self) -> Dict[str, Any]:
        """
        Get a summary of tracking status.
        
        Returns:
            Dictionary containing tracking summary
        """
        repo_info = self.get_repository_info()
        storage_stats = self.storage_service.get_statistics()
        
        return {
            'repository': repo_info,
            'storage': storage_stats,
            'tracking_status': {
                'total_repo_commits': repo_info['total_commits'],
                'total_logged_commits': storage_stats['total_commits'],
                'coverage_percentage': round(
                    (storage_stats['total_commits'] / repo_info['total_commits'] * 100) 
                    if repo_info['total_commits'] > 0 else 0, 
                    2
                )
            }
        }
