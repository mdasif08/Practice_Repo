#!/usr/bin/env python3
"""
Repository Service - Microservice for repository management and operations.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.repository_manager import RepositoryManager
from services.database_service import DatabaseService
from config.env_manager import env_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
db_service = DatabaseService()
repo_manager = RepositoryManager(db_service)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'repository-service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/repositories', methods=['GET'])
def get_repositories():
    """Get all repositories."""
    try:
        repositories = repo_manager.get_all_repositories()
        return jsonify({
            'success': True,
            'repositories': repositories,
            'count': len(repositories)
        })
    except Exception as e:
        logger.error(f"Error getting repositories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/repositories', methods=['POST'])
def register_repository():
    """Register a new repository."""
    try:
        data = request.get_json()
        repo_id = repo_manager.register_repository(
            owner=data['owner'],
            name=data['name'],
            description=data.get('description'),
            language=data.get('language'),
            is_private=data.get('is_private', False)
        )
        return jsonify({
            'success': True,
            'repository_id': repo_id,
            'message': 'Repository registered successfully'
        })
    except Exception as e:
        logger.error(f"Error registering repository: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/repositories/<owner>/<name>', methods=['GET'])
def get_repository(owner, name):
    """Get specific repository."""
    try:
        repo = repo_manager.get_repository(owner, name)
        if repo:
            return jsonify({
                'success': True,
                'repository': repo
            })
        else:
            return jsonify({'error': 'Repository not found'}), 404
    except Exception as e:
        logger.error(f"Error getting repository {owner}/{name}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/repositories/<owner>/<name>/commits', methods=['GET'])
def get_repository_commits(owner, name):
    """Get commits for a specific repository."""
    try:
        commits = repo_manager.get_repository_commits(owner, name)
        return jsonify({
            'success': True,
            'commits': commits,
            'count': len(commits)
        })
    except Exception as e:
        logger.error(f"Error getting repository commits: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/repositories/statistics', methods=['GET'])
def get_repository_statistics():
    """Get repository statistics."""
    try:
        stats = repo_manager.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting repository statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)
