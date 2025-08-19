"""
GitHub Commit Fetcher Service for CraftNudge Git Commit Logger.
Fetches commits from GitHub API and stores them in the database.
"""

import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database_service import DatabaseService
from services.repository_manager import RepositoryManager
from config.env_manager import env_manager

logger = logging.getLogger('GitHubCommitFetcher')


class GitHubCommitFetcher:
    """Service for fetching commits from GitHub API and storing in database."""
    
    def __init__(self, database_service: DatabaseService = None, repository_manager: RepositoryManager = None):
        self.db = database_service or DatabaseService()
        self.repo_manager = repository_manager or RepositoryManager(self.db)
        self.github_token = self._get_github_token()
        self.base_url = "https://api.github.com"
        
    def _get_github_token(self) -> str:
        """Get GitHub token from environment."""
        if env_manager and hasattr(env_manager, 'GITHUB_TOKEN'):
            return env_manager.GITHUB_TOKEN
        return ''
    
    def fetch_repository_commits(self, repo_owner: str, repo_name: str, max_commits: int = 10) -> Dict[str, Any]:
        """
        Fetch commits from a GitHub repository and store in database.
        
        Args:
            repo_owner: Repository owner (username)
            repo_name: Repository name
            max_commits: Maximum number of commits to fetch
            
        Returns:
            Dictionary with fetch results
        """
        try:
            if not self.github_token:
                raise ValueError("GitHub token not configured")
            
            # GitHub API call
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/commits"
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers, params={'per_page': max_commits})
            response.raise_for_status()
            
            commits_data = response.json()
            saved_count = 0
            
            for commit_data in commits_data:
                try:
                    # Extract commit information
                    commit_hash = commit_data['sha']
                    author_info = commit_data['commit']['author']
                    commit_info = commit_data['commit']
                    
                    # Get author name (prefer GitHub username if available)
                    author_name = commit_data['author']['login'] if commit_data.get('author') else author_info['name']
                    
                    # Create commit object
                    commit_obj = {
                        'commit_hash': commit_hash,
                        'author': author_name,
                        'author_email': author_info['email'],
                        'message': commit_info['message'],
                        'timestamp_commit': datetime.fromisoformat(author_info['date'].replace('Z', '+00:00')),
                        'branch': 'main',
                        'repository_name': repo_name,
                        'files_changed': [],
                        'lines_added': 0,
                        'lines_deleted': 0
                    }
                    
                    # Use repository manager to save commit with proper repository association
                    commit_id = self.repo_manager.save_commit_with_repository(
                        commit_obj, repo_owner, repo_name
                    )
                    saved_count += 1
                    logger.info(f"Saved commit {commit_hash[:8]} from {repo_name}")
                        
                except Exception as e:
                    logger.error(f"Error processing commit {commit_data.get('sha', 'unknown')}: {str(e)}")
                    continue
            
            return {
                'status': 'success',
                'repository': f"{repo_owner}/{repo_name}",
                'total_fetched': len(commits_data),
                'saved_count': saved_count,
                'message': f'Fetched {len(commits_data)} commits from {repo_name}, saved {saved_count} new commits'
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError("GitHub token is invalid or expired")
            elif e.response.status_code == 404:
                raise ValueError(f"Repository {repo_owner}/{repo_name} not found")
            elif e.response.status_code == 403:
                raise ValueError("GitHub API rate limit exceeded")
            else:
                raise ValueError(f"GitHub API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching commits from {repo_owner}/{repo_name}: {str(e)}")
            raise
    
    def fetch_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        """
        Fetch all repositories for a user and register them in the database.
        
        Args:
            username: GitHub username
            
        Returns:
            List of repository information
        """
        try:
            if not self.github_token:
                raise ValueError("GitHub token not configured")
            
            url = f"{self.base_url}/users/{username}/repos"
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            repositories = response.json()
            
            # Register repositories in the database
            for repo in repositories:
                try:
                    self.repo_manager.register_repository(
                        owner=username,
                        name=repo['name'],
                        description=repo.get('description'),
                        language=repo.get('language'),
                        is_private=repo.get('private', False)
                    )
                except Exception as e:
                    logger.warning(f"Failed to register repository {repo['name']}: {str(e)}")
                    continue
            
            return repositories
            
        except Exception as e:
            logger.error(f"Error fetching repositories for {username}: {str(e)}")
            raise
    
    def fetch_repository_details(self, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """
        Fetch detailed information about a specific repository.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            
        Returns:
            Repository details
        """
        try:
            if not self.github_token:
                raise ValueError("GitHub token not configured")
            
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}"
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            repo_data = response.json()
            
            # Register/update repository in database
            repo_id = self.repo_manager.register_repository(
                owner=repo_owner,
                name=repo_name,
                description=repo_data.get('description'),
                language=repo_data.get('language'),
                is_private=repo_data.get('private', False)
            )
            
            return {
                'id': repo_id,
                'name': repo_name,
                'owner': repo_owner,
                'full_name': repo_data['full_name'],
                'description': repo_data.get('description'),
                'language': repo_data.get('language'),
                'is_private': repo_data.get('private', False),
                'html_url': repo_data.get('html_url'),
                'clone_url': repo_data.get('clone_url'),
                'stargazers_count': repo_data.get('stargazers_count', 0),
                'forks_count': repo_data.get('forks_count', 0),
                'updated_at': repo_data.get('updated_at')
            }
            
        except Exception as e:
            logger.error(f"Error fetching repository details for {repo_owner}/{repo_name}: {str(e)}")
            raise
    
    def fetch_all_repository_commits(self, username: str, max_commits_per_repo: int = 5) -> Dict[str, Any]:
        """
        Fetch commits from all repositories for a user.
        
        Args:
            username: GitHub username
            max_commits_per_repo: Maximum commits per repository
            
        Returns:
            Summary of all fetch operations
        """
        try:
            repositories = self.fetch_user_repositories(username)
            results = []
            total_saved = 0
            
            for repo in repositories:
                try:
                    result = self.fetch_repository_commits(
                        username, 
                        repo['name'], 
                        max_commits_per_repo
                    )
                    results.append(result)
                    total_saved += result['saved_count']
                    
                except Exception as e:
                    logger.error(f"Error fetching commits from {repo['name']}: {str(e)}")
                    results.append({
                        'status': 'error',
                        'repository': repo['name'],
                        'error': str(e)
                    })
            
            return {
                'status': 'completed',
                'total_repositories': len(repositories),
                'successful_fetches': len([r for r in results if r['status'] == 'success']),
                'total_saved_commits': total_saved,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error fetching all repository commits: {str(e)}")
            raise
