#!/usr/bin/env python3
"""
Production GitHub API Service - Fetch commits with proper authentication
"""

import requests
import logging
from datetime import datetime
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class GitHubService:
    """Production GitHub API service for fetching commits."""
    
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CraftNudge-Microservice/1.0'
        }
        
        if not self.token:
            logger.error("❌ No GitHub token provided. GitHub API calls will fail.")
    
    def fetch_repository_commits(self, owner: str, repo: str, max_commits: int = 100) -> Dict:
        """Fetch commits from a GitHub repository."""
        try:
            # Validate GitHub token
            if not self.token:
                return {
                    'success': False,
                    'error': 'GitHub token not configured. Please set GITHUB_TOKEN environment variable.',
                    'repository': f"{owner}/{repo}"
                }
            
            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            params = {
                'per_page': min(max_commits, 100),  # GitHub max is 100 per page
                'page': 1
            }
            
            logger.info(f"🔍 Fetching commits from {owner}/{repo}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            commits_data = response.json()
            logger.info(f"✅ Successfully fetched {len(commits_data)} commits from {owner}/{repo}")
            
            # Process commits
            processed_commits = []
            for commit_data in commits_data:
                processed_commit = self._process_commit_data(commit_data, owner, repo)
                if processed_commit:
                    processed_commits.append(processed_commit)
            
            return {
                'success': True,
                'repository': f"{owner}/{repo}",
                'commits_fetched': len(processed_commits),
                'commits': processed_commits
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching commits from {owner}/{repo}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to fetch commits from GitHub: {str(e)}',
                'repository': f"{owner}/{repo}"
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching commits from {owner}/{repo}: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'repository': f"{owner}/{repo}"
            }
    
    def _process_commit_data(self, commit_data: Dict, owner: str, repo: str) -> Optional[Dict]:
        """Process raw GitHub commit data into our format."""
        try:
            commit_id = commit_data['sha']
            commit_info = commit_data['commit']
            author_info = commit_info['author']
            
            # Get author name (prefer GitHub username if available)
            author_name = commit_data['author']['login'] if commit_data.get('author') else author_info['name']
            
            # Parse timestamp
            timestamp = datetime.fromisoformat(author_info['date'].replace('Z', '+00:00'))
            
            # Get changed files
            changed_files = self._get_commit_files(owner, repo, commit_id)
            
            return {
                'commit_id': commit_id,
                'author': author_name,
                'message': commit_info['message'],
                'timestamp': timestamp,
                'changed_files': changed_files
            }
            
        except Exception as e:
            logger.error(f"⚠️ Error processing commit {commit_data.get('sha', 'unknown')}: {str(e)}")
            return None
    
    def _get_commit_files(self, owner: str, repo: str, commit_id: str) -> List[Dict]:
        """Get files changed in a specific commit."""
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/commits/{commit_id}"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            commit_detail = response.json()
            files = commit_detail.get('files', [])
            
            changed_files = []
            for file_info in files:
                changed_files.append({
                    'file_name': file_info['filename'],
                    'change_type': self._determine_change_type(file_info['status'])
                })
            
            return changed_files
            
        except Exception as e:
            logger.error(f"⚠️ Error fetching files for commit {commit_id}: {str(e)}")
            return []
    
    def _determine_change_type(self, status: str) -> str:
        """Determine change type from GitHub status."""
        status_mapping = {
            'added': 'added',
            'modified': 'modified',
            'removed': 'deleted',
            'renamed': 'renamed'
        }
        return status_mapping.get(status, 'modified')
    
    def test_connection(self) -> Dict:
        """Test GitHub API connection."""
        try:
            # Check if token is configured
            if not self.token:
                return {
                    'success': False,
                    'authenticated': False,
                    'error': 'GitHub token not configured',
                    'message': 'Please set GITHUB_TOKEN environment variable to use GitHub API'
                }
            
            response = requests.get(f"{self.base_url}/user", headers=self.headers, timeout=10)
            response.raise_for_status()
            
            user_data = response.json()
            return {
                'success': True,
                'authenticated': True,
                'username': user_data.get('login'),
                'rate_limit_remaining': response.headers.get('X-RateLimit-Remaining'),
                'message': f'Successfully connected to GitHub API as {user_data.get("login")}'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'authenticated': False,
                'error': str(e),
                'message': 'Failed to connect to GitHub API. Please check your token and network connection.'
            }
        except Exception as e:
            return {
                'success': False,
                'authenticated': False,
                'error': str(e),
                'message': 'Unexpected error testing GitHub API connection.'
            }

# Global GitHub service instance
github_service = GitHubService()
