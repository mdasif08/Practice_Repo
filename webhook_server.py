#!/usr/bin/env python3
"""
GitHub Webhook Server for CraftNudge Git Commit Logger.
Handles incoming webhooks from GitHub and triggers commit processing.
"""

import json, hmac, hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging, os
from pathlib import Path
import sys
import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.github_webhook_handler import GitHubWebhookHandler
from services.database_service import DatabaseService
from utils.error_handler import DataStorageError
from config.env_manager import env_manager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('WebhookServer')

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize services
db_service = None
webhook_handler = None
env_manager = None

def initialize_services():
    """Initialize database and webhook handler services."""
    global db_service, webhook_handler
    
    try:
        db_service = DatabaseService()
        webhook_handler = GitHubWebhookHandler(
            webhook_secret=env_manager.GITHUB_WEBHOOK_SECRET,
            database_service=db_service
        )
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events."""
    try:
        # Get webhook data
        payload = request.get_data()
        signature = request.headers.get('X-Hub-Signature-256', '')
        event_type = request.headers.get('X-GitHub-Event', '')
        
        logger.info(f"Received {event_type} webhook from GitHub")
        
        # Handle the webhook
        result = webhook_handler.handle_webhook(event_type, payload, signature)
        
        logger.info(f"Successfully processed {event_type} webhook")
        return jsonify({
            'status': 'success',
            'message': f'Processed {event_type} event',
            'result': result
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid webhook signature: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Invalid webhook signature'
        }), 401
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error processing webhook: {str(e)}'
        }), 500

@app.route('/webhook/status', methods=['GET'])
def webhook_status():
    """Get webhook processing status."""
    try:
        stats = webhook_handler.get_webhook_statistics()
        return jsonify({
            'status': 'success',
            'statistics': stats
        }), 200
    except Exception as e:
        logger.error(f"Error getting webhook status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error getting status: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        db_stats = db_service.get_statistics()
        
        # Check webhook handler
        webhook_stats = webhook_handler.get_webhook_statistics()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'webhook_handler': 'active',
            'statistics': {
                'database': db_stats,
                'webhook': webhook_stats
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@app.route('/process/events', methods=['POST'])
def process_events():
    """Manually trigger processing of unprocessed events."""
    try:
        results = webhook_handler.process_unprocessed_events()
        return jsonify({
            'status': 'success',
            'message': f'Processed {len(results)} events',
            'results': results
        }), 200
    except Exception as e:
        logger.error(f"Error processing events: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error processing events: {str(e)}'
        }), 500

@app.route('/pull/latest', methods=['POST'])
def pull_latest_commits():
    """Manually pull latest commits from a repository."""
    try:
        data = request.get_json()
        repository_path = data.get('repository_path')
        branch = data.get('branch', 'main')
        
        if not repository_path:
            return jsonify({
                'status': 'error',
                'message': 'repository_path is required'
            }), 400
        
        commits = webhook_handler.pull_latest_commits(repository_path, branch)
        
        return jsonify({
            'status': 'success',
            'message': f'Pulled {len(commits)} new commits',
            'commits': commits
        }), 200
    except Exception as e:
        logger.error(f"Error pulling latest commits: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error pulling commits: {str(e)}'
        }), 500

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify route registration."""
    return jsonify({
        'status': 'success',
        'message': 'Test endpoint working'
    }), 200

@app.route('/fetch-github-commits', methods=['POST'])
def fetch_github_commits():
    """Fetch real commits from GitHub and store in database."""
    try:
        data = request.get_json()
        repo_owner = data.get('repo_owner', 'mdasif08')
        repo_name = data.get('repo_name', 'Practice_Repo')
        max_commits = data.get('max_commits', 5)
        
        # GitHub API call
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
        headers = {
            'Authorization': f'Bearer {env_manager.GITHUB_TOKEN}',
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
                
                # Check if commit already exists
                existing_commit = db_service.get_commit_by_hash(commit_hash)
                if not existing_commit:
                    db_service.save_commit(commit_obj)
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing commit {commit_data.get('sha', 'unknown')}: {str(e)}")
                continue
        
        return jsonify({
            'status': 'success',
            'message': f'Fetched {len(commits_data)} commits, saved {saved_count} new commits',
            'total_fetched': len(commits_data),
            'saved_count': saved_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching GitHub commits: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error fetching commits: {str(e)}'
        }), 500

@app.route('/recent-commits', methods=['GET'])
def get_recent_commits():
    """Get recent commits for the frontend."""
    try:
        # Get query parameters
        author_filter = request.args.get('author', None)
        limit = int(request.args.get('limit', 20))
        
        # Get recent commits from database
        commits = db_service.get_recent_commits(limit=limit)
        
        # Filter by author if specified
        if author_filter:
            commits = [commit for commit in commits if commit['author'] == author_filter]
        
        return jsonify({
            'status': 'success',
            'commits': commits,
            'filter': author_filter if author_filter else 'all',
            'total_count': len(commits)
        }), 200
    except Exception as e:
        logger.error(f"Error getting recent commits: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error getting commits: {str(e)}'
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with basic information."""
    return jsonify({
        'service': 'CraftNudge GitHub Webhook Server',
        'version': '1.0.0',
        'endpoints': {
            'POST /webhook/github': 'Handle GitHub webhook events',
            'GET /webhook/status': 'Get webhook processing statistics',
            'GET /health': 'Health check',
            'POST /process/events': 'Manually process unprocessed events',
            'POST /pull/latest': 'Manually pull latest commits'
        },
        'timestamp': datetime.now().isoformat()
    }), 200

def main():
    """Main function to run the webhook server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CraftNudge GitHub Webhook Server')
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, 
                       help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--secret', 
                       help='GitHub webhook secret (or set GITHUB_WEBHOOK_SECRET env var)')
    
    args = parser.parse_args()
    
    # Set webhook secret if provided
    if args.secret:
        os.environ['GITHUB_WEBHOOK_SECRET'] = args.secret
    
    try:
        # Initialize services
        initialize_services()
        
        logger.info(f"Starting webhook server on {args.host}:{args.port}")
        
        # Run the Flask app
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start webhook server: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup
        if db_service:
            db_service.close()

if __name__ == '__main__':
    main()
