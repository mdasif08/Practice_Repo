#!/usr/bin/env python3
"""
Repository Manager Service - Handles all repository-related operations
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
        'service': 'repo-manager',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/repos', methods=['GET'])
def get_repositories():
    """Get all repositories."""
    try:
        # Get unique repositories from commits table
        query = """
            SELECT DISTINCT repository_name, 
                   COUNT(*) as commit_count,
                   MAX(timestamp_commit) as last_commit
            FROM commits 
            GROUP BY repository_name 
            ORDER BY last_commit DESC
        """
        repositories = db_service.execute_query(query)
        
        return jsonify({
            'success': True,
            'repositories': repositories,
            'count': len(repositories)
        })
    except Exception as e:
        logger.error(f"Error getting repositories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/repos/<repository_name>', methods=['GET'])
def get_repository(repository_name):
    """Get specific repository details."""
    try:
        # Get repository statistics
        query = """
            SELECT repository_name,
                   COUNT(*) as total_commits,
                   COUNT(DISTINCT author) as unique_authors,
                   MAX(timestamp_commit) as last_commit,
                   MIN(timestamp_commit) as first_commit
            FROM commits 
            WHERE repository_name = %s
            GROUP BY repository_name
        """
        result = db_service.execute_query(query, (repository_name,))
        
        if result:
            repo_data = result[0]
            
            # Get recent commits for this repository
            recent_commits = db_service.get_commits_by_repository(repository_name, 10)
            
            repo_data['recent_commits'] = recent_commits
            
            return jsonify({
                'success': True,
                'repository': repo_data
            })
        else:
            return jsonify({'error': 'Repository not found'}), 404
    except Exception as e:
        logger.error(f"Error getting repository {repository_name}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/repos/<repository_name>/commits', methods=['GET'])
def get_repository_commits(repository_name):
    """Get commits for a specific repository."""
    try:
        limit = request.args.get('limit', 100, type=int)
        commits = db_service.get_commits_by_repository(repository_name, limit)
        
        return jsonify({
            'success': True,
            'commits': commits,
            'repository': repository_name,
            'count': len(commits)
        })
    except Exception as e:
        logger.error(f"Error getting commits for repository {repository_name}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/repos', methods=['POST'])
def add_repository():
    """Add a new repository (by adding a commit)."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['repository_name', 'commit_hash', 'author', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add timestamp if not provided
        if 'timestamp_commit' not in data:
            data['timestamp_commit'] = datetime.now()
        
        # Save commit (which creates the repository)
        result = db_service.save_commit(data)
        
        return jsonify({
            'success': True,
            'message': 'Repository added successfully',
            'repository_name': data['repository_name']
        })
    except Exception as e:
        logger.error(f"Error adding repository: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/repos/statistics', methods=['GET'])
def get_repository_statistics():
    """Get repository statistics."""
    try:
        # Get overall statistics
        query = """
            SELECT 
                COUNT(DISTINCT repository_name) as total_repositories,
                COUNT(*) as total_commits,
                COUNT(DISTINCT author) as total_authors,
                AVG(commits_per_repo) as avg_commits_per_repo
            FROM (
                SELECT repository_name, author,
                       COUNT(*) as commits_per_repo
                FROM commits 
                GROUP BY repository_name, author
            ) repo_stats
        """
        result = db_service.execute_query(query)
        
        if result:
            stats = result[0]
            
            # Get top repositories by commit count
            top_repos_query = """
                SELECT repository_name, COUNT(*) as commit_count
                FROM commits 
                GROUP BY repository_name 
                ORDER BY commit_count DESC 
                LIMIT 5
            """
            top_repos = db_service.execute_query(top_repos_query)
            stats['top_repositories'] = top_repos
            
            return jsonify({
                'success': True,
                'statistics': stats
            })
        else:
            return jsonify({
                'success': True,
                'statistics': {
                    'total_repositories': 0,
                    'total_commits': 0,
                    'total_authors': 0,
                    'avg_commits_per_repo': 0,
                    'top_repositories': []
                }
            })
    except Exception as e:
        logger.error(f"Error getting repository statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info(f"🚀 Starting Repository Manager Service on port {config.REPO_SERVICE_PORT}")
    app.run(host='0.0.0.0', port=config.REPO_SERVICE_PORT, debug=True)
