"""
GitHub Webhook Handler for CraftNudge Git Commit Logger.
Handles incoming webhooks from GitHub and triggers agent processing.
"""

import hmac
import hashlib
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import subprocess
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database_service import DatabaseService
from services.commit_tracker import CommitTrackerService
from utils.error_handler import DataStorageError, GitRepositoryError


class GitHubWebhookHandler:
    """Handles GitHub webhook events and triggers commit processing."""
    
    def __init__(self, webhook_secret: str = None, database_service: DatabaseService = None):
        """Initialize webhook handler."""
        self.webhook_secret = webhook_secret
        self.db = database_service or DatabaseService()
        self.commit_tracker = None
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature."""
        if not self.webhook_secret:
            return True  # Skip verification if no secret configured
        
        expected_signature = f"sha256={hmac.new(self.webhook_secret.encode(), payload, hashlib.sha256).hexdigest()}"
        return hmac.compare_digest(signature, expected_signature)
    
    def handle_push_event(self, event_data: Dict[str, Any]) -> List[str]:
        """Handle GitHub push event."""
        try:
            repository = event_data['repository']['full_name']
            commits = event_data.get('commits', [])
            processed_commits = []
            
            for commit_data in commits:
                commit_hash = commit_data['id']
                
                # Check if commit already exists
                existing_commit = self.db.get_commit_by_hash(commit_hash)
                if existing_commit:
                    print(f"Commit {commit_hash} already exists, skipping...")
                    continue
                
                # Extract commit information
                commit_info = {
                    'commit_hash': commit_hash,
                    'author': commit_data['author']['name'],
                    'message': commit_data['message'],
                    'timestamp_commit': datetime.fromisoformat(commit_data['timestamp'].replace('Z', '+00:00')),
                    'branch': event_data['ref'].replace('refs/heads/', ''),
                    'repository_path': repository,
                    'changed_files': [file['filename'] for file in commit_data.get('modified', []) + 
                                    commit_data.get('added', []) + commit_data.get('removed', [])],
                    'metadata': {
                        'github_event_id': event_data.get('head_commit', {}).get('id'),
                        'pusher': event_data.get('pusher', {}).get('name'),
                        'event_timestamp': datetime.now().isoformat()
                    }
                }
                
                # Save to database
                commit_id = self.db.save_commit(commit_info)
                processed_commits.append(commit_hash)
                
                print(f"Processed commit {commit_hash} from {repository}")
            
            return processed_commits
            
        except Exception as e:
            raise DataStorageError(f"Failed to handle push event: {str(e)}")
    
    def handle_pull_request_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GitHub pull request event."""
        try:
            repository = event_data['repository']['full_name']
            pr_data = event_data['pull_request']
            
            # Extract PR information
            pr_info = {
                'repository': repository,
                'pr_number': pr_data['number'],
                'title': pr_data['title'],
                'author': pr_data['user']['login'],
                'state': pr_data['state'],
                'action': event_data['action'],
                'head_commit': pr_data['head']['sha'],
                'base_commit': pr_data['base']['sha'],
                'created_at': pr_data['created_at'],
                'updated_at': pr_data['updated_at']
            }
            
            # Save PR event to database
            event_id = self.db.save_github_event(
                event_type='pull_request',
                repository=repository,
                commit_hash=pr_data['head']['sha'],
                event_data=pr_info
            )
            
            print(f"Processed PR #{pr_data['number']} from {repository}")
            return pr_info
            
        except Exception as e:
            raise DataStorageError(f"Failed to handle pull request event: {str(e)}")
    
    def handle_webhook(self, event_type: str, payload: bytes, signature: str = None) -> Dict[str, Any]:
        """Handle incoming webhook."""
        try:
            # Verify signature
            if not self.verify_signature(payload, signature or ''):
                raise ValueError("Invalid webhook signature")
            
            # Parse payload
            event_data = json.loads(payload.decode('utf-8'))
            
            # Save event to database
            repository = event_data.get('repository', {}).get('full_name', 'unknown')
            commit_hash = None
            
            if event_type == 'push':
                commit_hash = event_data.get('head_commit', {}).get('id')
            elif event_type == 'pull_request':
                commit_hash = event_data.get('pull_request', {}).get('head', {}).get('sha')
            
            event_id = self.db.save_github_event(
                event_type=event_type,
                repository=repository,
                commit_hash=commit_hash,
                event_data=event_data
            )
            
            # Process based on event type
            result = {}
            if event_type == 'push':
                result['processed_commits'] = self.handle_push_event(event_data)
            elif event_type == 'pull_request':
                result['pr_info'] = self.handle_pull_request_event(event_data)
            else:
                result['message'] = f"Event type '{event_type}' not specifically handled"
            
            # Mark event as processed
            self.db.mark_event_processed(event_id)
            
            return {
                'event_id': event_id,
                'event_type': event_type,
                'repository': repository,
                'processed': True,
                'result': result
            }
            
        except Exception as e:
            raise DataStorageError(f"Failed to handle webhook: {str(e)}")
    
    def pull_latest_commits(self, repository_path: str, branch: str = 'main') -> List[str]:
        """Pull latest commits from GitHub repository."""
        try:
            if not self.commit_tracker:
                self.commit_tracker = CommitTrackerService(repo_path=Path(repository_path))
            
            # Pull latest changes
            subprocess.run(['git', 'pull', 'origin', branch], 
                         cwd=repository_path, check=True, capture_output=True)
            
            # Get latest commits
            latest_commit = self.commit_tracker.get_latest_commit()
            if latest_commit:
                commit_metadata = self.commit_tracker.get_commit_metadata(latest_commit)
                
                # Check if commit already exists
                existing_commit = self.db.get_commit_by_hash(commit_metadata['commit_hash'])
                if not existing_commit:
                    # Save to database
                    commit_id = self.db.save_commit(commit_metadata)
                    return [commit_metadata['commit_hash']]
            
            return []
            
        except Exception as e:
            raise GitRepositoryError(f"Failed to pull latest commits: {str(e)}")
    
    def process_unprocessed_events(self) -> List[Dict[str, Any]]:
        """Process all unprocessed GitHub events."""
        try:
            unprocessed_events = self.db.get_unprocessed_github_events()
            processed_results = []
            
            for event in unprocessed_events:
                try:
                    event_data = event['event_data']
                    event_type = event['event_type']
                    
                    if event_type == 'push':
                        result = self.handle_push_event(event_data)
                        processed_results.append({
                            'event_id': event['id'],
                            'type': 'push',
                            'result': result
                        })
                    elif event_type == 'pull_request':
                        result = self.handle_pull_request_event(event_data)
                        processed_results.append({
                            'event_id': event['id'],
                            'type': 'pull_request',
                            'result': result
                        })
                    
                    # Mark as processed
                    self.db.mark_event_processed(event['id'])
                    
                except Exception as e:
                    print(f"Failed to process event {event['id']}: {str(e)}")
                    continue
            
            return processed_results
            
        except Exception as e:
            raise DataStorageError(f"Failed to process unprocessed events: {str(e)}")
    
    def get_webhook_statistics(self) -> Dict[str, Any]:
        """Get webhook processing statistics."""
        try:
            stats = self.db.get_statistics()
            
            # Add webhook-specific stats
            with self.db.conn.cursor() as cursor:
                # Total webhook events
                cursor.execute("SELECT COUNT(*) as total_events FROM github_events")
                total_events = cursor.fetchone()[0]
                
                # Events by type
                cursor.execute("""
                    SELECT event_type, COUNT(*) as count 
                    FROM github_events 
                    GROUP BY event_type
                """)
                events_by_type = dict(cursor.fetchall())
                
                # Recent activity
                cursor.execute("""
                    SELECT COUNT(*) as recent_events 
                    FROM github_events 
                    WHERE timestamp > NOW() - INTERVAL '24 hours'
                """)
                recent_events = cursor.fetchone()[0]
            
            return {
                **stats,
                'total_webhook_events': total_events,
                'events_by_type': events_by_type,
                'recent_events_24h': recent_events
            }
            
        except Exception as e:
            raise DataStorageError(f"Failed to get webhook statistics: {str(e)}")
    
    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
