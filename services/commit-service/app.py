#!/usr/bin/env python3
"""
Commit Service - Microservice for Git commit tracking and management.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.commit_tracker import CommitTracker
from services.database_service import DatabaseService
from config.env_manager import env_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
db_service = DatabaseService()
commit_tracker = CommitTracker(db_service)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'commit-service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/commits', methods=['GET'])
def get_commits():
    """Get all commits."""
    try:
        commits = commit_tracker.get_all_commits()
        return jsonify({
            'success': True,
            'commits': commits,
            'count': len(commits)
        })
    except Exception as e:
        logger.error(f"Error getting commits: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/commits/<commit_hash>', methods=['GET'])
def get_commit(commit_hash):
    """Get specific commit by hash."""
    try:
        commit = commit_tracker.get_commit_by_hash(commit_hash)
        if commit:
            return jsonify({
                'success': True,
                'commit': commit
            })
        else:
            return jsonify({'error': 'Commit not found'}), 404
    except Exception as e:
        logger.error(f"Error getting commit {commit_hash}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/commits', methods=['POST'])
def track_commit():
    """Track a new commit."""
    try:
        data = request.get_json()
        commit_id = commit_tracker.track_commit(data)
        return jsonify({
            'success': True,
            'commit_id': commit_id,
            'message': 'Commit tracked successfully'
        })
    except Exception as e:
        logger.error(f"Error tracking commit: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/commits/statistics', methods=['GET'])
def get_commit_statistics():
    """Get commit statistics."""
    try:
        stats = commit_tracker.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
