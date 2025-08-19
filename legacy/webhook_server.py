#!/usr/bin/env python3
"""
Webhook Server for CraftNudge Git Commit Logger.
Handles GitHub webhooks and provides API endpoints for commit management.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.database_service import DatabaseService
from services.github_commit_fetcher import GitHubCommitFetcher
from services.repository_manager import RepositoryManager
from services.github_webhook_handler import GitHubWebhookHandler
from config.env_manager import env_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
db_service = DatabaseService()
repo_manager = RepositoryManager(db_service)
github_fetcher = GitHubCommitFetcher(db_service, repo_manager)
webhook_handler = GitHubWebhookHandler(db_service)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'CraftNudge Git Commit Logger'
    })

@app.route('/webhook', methods=['POST'])
def github_webhook():
    """Handle GitHub webhooks."""
    try:
        event_type = request.headers.get('X-GitHub-Event')
        if not event_type:
            return jsonify({'error': 'No GitHub event type'}), 400
        
        # Process the webhook
        result = webhook_handler.process_webhook(event_type, request.json)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
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

@app.route('/fetch-repo-commits', methods=['POST'])
def fetch_repo_commits():
    """Enhanced endpoint to fetch commits from a specific repository with repository registration."""
    try:
        data = request.get_json()
        repo_owner = data.get('repo_owner', 'mdasif08')
        repo_name = data.get('repo_name')
        max_commits = data.get('max_commits', 10)
        
        if not repo_name:
            return jsonify({'error': 'Repository name is required'}), 400
        
        # First, fetch repository details to ensure it's registered
        repo_details = github_fetcher.fetch_repository_details(repo_owner, repo_name)
        
        # Then fetch commits
        result = github_fetcher.fetch_repository_commits(repo_owner, repo_name, max_commits)
        
        # Add repository details to the response
        result['repository_details'] = repo_details
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error fetching repository commits: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/fetch-all-repos', methods=['POST'])
def fetch_all_repositories():
    """Fetch all repositories for a user."""
    try:
        data = request.get_json()
        username = data.get('username', 'mdasif08')
        max_commits_per_repo = data.get('max_commits_per_repo', 5)
        
        result = github_fetcher.fetch_all_repository_commits(username, max_commits_per_repo)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error fetching all repositories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/migrate-repositories', methods=['POST'])
def migrate_repositories():
    """Migrate existing commits to proper repository isolation."""
    try:
        result = db_service.migrate_commits_to_repositories()
        
        return jsonify({
            'status': 'success',
            'message': f'Migrated {result["migrated_commits"]} commits across {result["processed_repositories"]} repositories',
            'details': result
        })
        
    except Exception as e:
        logger.error(f"Error migrating repositories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/repository/<owner>/<name>/commits', methods=['GET'])
def get_repository_commits(owner, name):
    """Get commits for a specific repository with proper isolation."""
    try:
        # Ensure repository is properly registered
        repo_id = repo_manager.ensure_repository_isolation(owner, name)
        
        # Get commits for this repository
        commits = repo_manager.get_commits_by_repository(owner, name, limit=50)
        
        return jsonify({
            'repository': f"{owner}/{name}",
            'repository_id': repo_id,
            'commits': commits,
            'commit_count': len(commits)
        })
        
    except Exception as e:
        logger.error(f"Error getting repository commits: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/recent-commits', methods=['GET'])
def get_recent_commits():
    """Get recent commits with proper repository filtering."""
    try:
        limit = request.args.get('limit', 10, type=int)
        repo_name = request.args.get('repo')
        
        if repo_name:
            # Get commits for specific repository with proper isolation
            commits = repo_manager.get_commits_by_repository('mdasif08', repo_name, limit)
        else:
            # Get all commits (excluding Practice_Repo)
            commits = db_service.get_recent_commits(limit)
        
        return jsonify({
            'commits': commits,
            'count': len(commits),
            'repository_filter': repo_name if repo_name else 'all'
        })
        
    except Exception as e:
        logger.error(f"Error getting recent commits: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/repositories', methods=['GET'])
def get_repositories():
    """Get all registered repositories."""
    try:
        repositories = repo_manager.get_all_repositories()
        return jsonify({
            'repositories': repositories,
            'count': len(repositories)
        })
        
    except Exception as e:
        logger.error(f"Error getting repositories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/repository/<owner>/<name>', methods=['GET'])
def get_repository_details(owner, name):
    """Get details for a specific repository."""
    try:
        repo_id = repo_manager.get_repository_id(owner, name)
        if not repo_id:
            return jsonify({'error': 'Repository not found'}), 404
        
        repo_details = repo_manager.get_repository_by_id(repo_id)
        commits = repo_manager.get_commits_by_repository(owner, name, limit=20)
        
        return jsonify({
            'repository': repo_details,
            'commits': commits,
            'commit_count': len(commits)
        })
        
    except Exception as e:
        logger.error(f"Error getting repository details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get database statistics with proper repository isolation."""
    try:
        stats = db_service.get_statistics()
        repo_stats = repo_manager.get_repository_statistics()
        
        return jsonify({
            'database_stats': stats,
            'repository_stats': repo_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/fix-null-repos', methods=['POST'])
def fix_null_repositories():
    """Fix commits with NULL repository names."""
    try:
        data = request.get_json()
        default_repo_name = data.get('default_repo_name', 'Practice_Repo')
        
        updated_count = db_service.fix_null_repository_names(default_repo_name)
        
        return jsonify({
            'message': f'Fixed {updated_count} commits with NULL repository names',
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Error fixing null repositories: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(env_manager.PORT) if hasattr(env_manager, 'PORT') else 5000
    app.run(host='0.0.0.0', port=port, debug=True)
