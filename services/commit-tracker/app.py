#!/usr/bin/env python3
"""
Production Commit Tracker Service - CraftNudge Microservice
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add shared components to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database import db_service
from shared.github_service import github_service
from shared.config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'commit-tracker',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/track-commits', methods=['POST'])
def track_commits():
    """Main endpoint to track commits from GitHub repository."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['owner', 'repo']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        owner = data['owner']
        repo = data['repo']
        max_commits = data.get('max_commits', 50)
        
        logger.info(f"🚀 Starting commit tracking for {owner}/{repo}")
        
        # Fetch commits from GitHub
        github_result = github_service.fetch_repository_commits(owner, repo, max_commits)
        
        if not github_result['success']:
            logger.error(f"❌ GitHub API error: {github_result['error']}")
            return jsonify({
                'success': False,
                'error': github_result['error'],
                'repository': f"{owner}/{repo}",
                'message': 'Failed to fetch commits from GitHub. Please check your GitHub token and repository access.'
            }), 400
        
        # Store commits in database
        stored_commits = []
        for commit_data in github_result['commits']:
            try:
                db_service.upsert_commit(commit_data)
                stored_commits.append(commit_data['commit_id'])
                logger.info(f"✅ Stored commit: {commit_data['commit_id']}")
            except Exception as e:
                logger.error(f"❌ Error storing commit {commit_data['commit_id']}: {str(e)}")
                continue
        
        # Get stored commits from database
        stored_commits_data = db_service.get_all_commits(max_commits)
        
        return jsonify({
            'success': True,
            'repository': f"{owner}/{repo}",
            'commits_fetched': len(github_result['commits']),
            'commits_stored': len(stored_commits),
            'commits': stored_commits_data,
            'message': f'Successfully tracked {len(stored_commits)} commits from {owner}/{repo}'
        })
        
    except Exception as e:
        logger.error(f"Error in track-commits: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/commits', methods=['GET'])
def get_commits():
    """Get all commits from database."""
    try:
        limit = request.args.get('limit', 100, type=int)
        commits = db_service.get_all_commits(limit)
        
        return jsonify({
            'success': True,
            'commits': commits,
            'count': len(commits)
        })
    except Exception as e:
        logger.error(f"Error getting commits: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/commits/<commit_id>', methods=['GET'])
def get_commit(commit_id):
    """Get specific commit by ID."""
    try:
        commit = db_service.get_commit_by_id(commit_id)
        
        if commit:
            return jsonify({
                'success': True,
                'commit': commit
            })
        else:
            return jsonify({'error': 'Commit not found'}), 404
    except Exception as e:
        logger.error(f"Error getting commit {commit_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/commits/statistics', methods=['GET'])
def get_commit_statistics():
    """Get commit statistics."""
    try:
        stats = db_service.get_commit_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting commit statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/commits/clear-all', methods=['DELETE'])
def clear_all_commits():
    """Clear all commits from database."""
    try:
        db_service.clear_all_commits()
        
        return jsonify({
            'success': True,
            'message': 'All commits cleared from database'
        })
    except Exception as e:
        logger.error(f"Error clearing commits: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/github/test', methods=['GET'])
def test_github_connection():
    """Test GitHub API connection."""
    try:
        result = github_service.test_connection()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error testing GitHub connection: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info(f"🚀 Starting Production Commit Tracker Service on port {config.COMMIT_SERVICE_PORT}")
    app.run(host='0.0.0.0', port=config.COMMIT_SERVICE_PORT, debug=True)
