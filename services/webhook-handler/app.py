#!/usr/bin/env python3
"""
Webhook Handler Service - Handles GitHub webhooks and commit fetching
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import sys
from pathlib import Path
import requests
import json

# Add shared components to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database import db_service
from shared.config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class GitHubFetcher:
    """Simple GitHub API fetcher for commits."""
    
    def __init__(self):
        self.token = config.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
    
    def fetch_repository_commits(self, repo_owner, repo_name, max_commits=10):
        """Fetch commits from a GitHub repository."""
        try:
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/commits"
            headers = {
                'Authorization': f'Bearer {self.token}' if self.token else '',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers, params={'per_page': max_commits})
            response.raise_for_status()
            
            commits_data = response.json()
            logger.info(f"✅ Successfully fetched {len(commits_data)} commits from {repo_owner}/{repo_name}")
            
            # Process and save commits
            processed_commits = self.process_commits(commits_data, repo_name)
            
            return {
                'success': True,
                'repository': f"{repo_owner}/{repo_name}",
                'commits_fetched': len(processed_commits),
                'commits': processed_commits
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching commits: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_commits(self, commits_data, repo_name):
        """Process GitHub commits and save to database."""
        processed_commits = []
        
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
                    'branch': "main",  # Default branch
                    'repository_name': repo_name,
                    'files_changed': [],
                    'lines_added': 0,
                    'lines_deleted': 0
                }
                
                # Save to database
                db_service.save_commit(commit_obj)
                processed_commits.append(commit_obj)
                
            except Exception as e:
                logger.error(f"⚠️ Error processing commit {commit_data.get('sha', 'unknown')}: {str(e)}")
                continue
        
        return processed_commits

# Initialize GitHub fetcher
github_fetcher = GitHubFetcher()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'webhook-handler',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhooks."""
    try:
        event_type = request.headers.get('X-GitHub-Event')
        if not event_type:
            return jsonify({'error': 'No GitHub event type'}), 400
        
        data = request.json
        logger.info(f"📥 Received GitHub webhook: {event_type}")
        
        # Process different event types
        if event_type == 'push':
            return process_push_event(data)
        elif event_type == 'create':
            return process_create_event(data)
        elif event_type == 'delete':
            return process_delete_event(data)
        else:
            return jsonify({
                'success': True,
                'message': f'Event {event_type} received but not processed',
                'event_type': event_type
            })
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

def process_push_event(data):
    """Process push event."""
    try:
        repository = data.get('repository', {})
        repo_name = repository.get('name', '')
        repo_owner = repository.get('owner', {}).get('login', '')
        
        commits = data.get('commits', [])
        logger.info(f"📝 Processing {len(commits)} commits for {repo_owner}/{repo_name}")
        
        # Process each commit
        processed_commits = []
        for commit in commits:
            commit_obj = {
                'commit_hash': commit['id'],
                'author': commit['author']['name'],
                'author_email': commit['author']['email'],
                'message': commit['message'],
                'timestamp_commit': datetime.fromisoformat(commit['timestamp']),
                'branch': data.get('ref', '').replace('refs/heads/', ''),
                'repository_name': repo_name,
                'files_changed': [file['filename'] for file in commit.get('modified', [])],
                'lines_added': 0,
                'lines_deleted': 0
            }
            
            db_service.save_commit(commit_obj)
            processed_commits.append(commit_obj)
            
            # 🔥 AUTOMATIC AI ANALYSIS TRIGGER
            try:
                logger.info(f"🤖 Triggering AI analysis for commit: {commit['id']}")
                ai_analysis_result = trigger_ai_analysis(commit['id'], repo_name)
                logger.info(f"✅ AI analysis completed for commit: {commit['id']}")
            except Exception as ai_error:
                logger.error(f"❌ AI analysis failed for commit {commit['id']}: {str(ai_error)}")
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(processed_commits)} commits with AI analysis',
            'repository': f"{repo_owner}/{repo_name}",
            'commits_processed': len(processed_commits)
        })
        
    except Exception as e:
        logger.error(f"Error processing push event: {str(e)}")
        return jsonify({'error': str(e)}), 500

def process_create_event(data):
    """Process create event (new branch/tag)."""
    try:
        repository = data.get('repository', {})
        repo_name = repository.get('name', '')
        ref_type = data.get('ref_type', '')
        ref_name = data.get('ref', '')
        
        logger.info(f"🆕 New {ref_type} created: {ref_name} in {repo_name}")
        
        return jsonify({
            'success': True,
            'message': f'New {ref_type} created',
            'repository': repo_name,
            'ref_type': ref_type,
            'ref_name': ref_name
        })
        
    except Exception as e:
        logger.error(f"Error processing create event: {str(e)}")
        return jsonify({'error': str(e)}), 500

def process_delete_event(data):
    """Process delete event (branch/tag deleted)."""
    try:
        repository = data.get('repository', {})
        repo_name = repository.get('name', '')
        ref_type = data.get('ref_type', '')
        ref_name = data.get('ref', '')
        
        logger.info(f"🗑️ {ref_type} deleted: {ref_name} in {repo_name}")
        
        return jsonify({
            'success': True,
            'message': f'{ref_type} deleted',
            'repository': repo_name,
            'ref_type': ref_type,
            'ref_name': ref_name
        })
        
    except Exception as e:
        logger.error(f"Error processing delete event: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/fetch-commits', methods=['POST'])
def fetch_commits():
    """Fetch commits from a specific repository."""
    try:
        data = request.get_json()
        repo_owner = data.get('repo_owner', 'mdasif08')
        repo_name = data.get('repo_name')
        max_commits = data.get('max_commits', 10)
        
        if not repo_name:
            return jsonify({'error': 'Repository name is required'}), 400
        
        result = github_fetcher.fetch_repository_commits(repo_owner, repo_name, max_commits)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error fetching commits: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/events', methods=['GET'])
def get_webhook_events():
    """Get recent webhook events (simplified)."""
    try:
        # This would typically query a webhook events table
        # For now, return a simple response
        return jsonify({
            'success': True,
            'events': [
                {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'webhook_received',
                    'message': 'Webhook handler is working'
                }
            ],
            'count': 1
        })
    except Exception as e:
        logger.error(f"Error getting webhook events: {str(e)}")
        return jsonify({'error': str(e)}), 500

def trigger_ai_analysis(commit_hash, repository_name):
    """Trigger AI analysis for a commit."""
    try:
        # Call AI Analyzer service
        ai_service_url = f"http://ai-analyzer:8004/analyze/commit/{commit_hash}"
        
        response = requests.post(ai_service_url, json={
            'commit_hash': commit_hash,
            'repository_name': repository_name
        }, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"AI service returned status {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to trigger AI analysis: {str(e)}")
        return None

if __name__ == '__main__':
    logger.info(f"🚀 Starting Webhook Handler Service on port {config.WEBHOOK_SERVICE_PORT}")
    app.run(host='0.0.0.0', port=config.WEBHOOK_SERVICE_PORT, debug=True)
