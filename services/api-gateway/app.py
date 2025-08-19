#!/usr/bin/env python3
"""
API Gateway - Routes requests to appropriate microservices
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import requests
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Service URLs
COMMIT_SERVICE_URL = os.getenv('COMMIT_SERVICE_URL', 'http://localhost:8001')
REPO_SERVICE_URL = os.getenv('REPO_SERVICE_URL', 'http://localhost:8002')
WEBHOOK_SERVICE_URL = os.getenv('WEBHOOK_SERVICE_URL', 'http://localhost:8003')
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://localhost:8004')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'api-gateway',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'commit-tracker': COMMIT_SERVICE_URL,
            'repo-manager': REPO_SERVICE_URL,
            'webhook-handler': WEBHOOK_SERVICE_URL,
            'ai-analyzer': AI_SERVICE_URL
        }
    })

# Main Track Commits Route
@app.route('/track-commits', methods=['POST'])
def track_commits():
    """Route track-commits requests to commit-tracker service."""
    try:
        target_url = f"{COMMIT_SERVICE_URL}/track-commits"
        response = requests.post(target_url, json=request.get_json())
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Error routing track-commits to commit service: {str(e)}")
        return jsonify({'error': str(e)}), 500

# GitHub Test Route
@app.route('/github/test', methods=['GET'])
def github_test():
    """Route GitHub test requests to commit-tracker service."""
    try:
        target_url = f"{COMMIT_SERVICE_URL}/github/test"
        response = requests.get(target_url)
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Error routing github test to commit service: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Commit Tracker Routes
@app.route('/commits', methods=['GET', 'POST'])
@app.route('/commits/<path:subpath>', methods=['GET', 'POST', 'DELETE'])
def commit_routes(subpath=None):
    """Route commit-related requests to commit-tracker service."""
    try:
        # Build target URL
        if subpath:
            target_url = f"{COMMIT_SERVICE_URL}/commits/{subpath}"
        else:
            target_url = f"{COMMIT_SERVICE_URL}/commits"
        
        # Forward request
        if request.method == 'GET':
            response = requests.get(target_url, params=request.args)
        elif request.method == 'DELETE':
            response = requests.delete(target_url)
        else:
            response = requests.post(target_url, json=request.get_json())
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Error routing to commit service: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Repository Manager Routes
@app.route('/repos', methods=['GET', 'POST'])
@app.route('/repos/<path:subpath>', methods=['GET', 'POST'])
def repo_routes(subpath=None):
    """Route repository-related requests to repo-manager service."""
    try:
        # Build target URL
        if subpath:
            target_url = f"{REPO_SERVICE_URL}/repos/{subpath}"
        else:
            target_url = f"{REPO_SERVICE_URL}/repos"
        
        # Forward request
        if request.method == 'GET':
            response = requests.get(target_url, params=request.args)
        else:
            response = requests.post(target_url, json=request.get_json())
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Error routing to repo service: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Webhook Handler Routes
@app.route('/webhook', methods=['GET', 'POST'])
@app.route('/webhook/<path:subpath>', methods=['GET', 'POST'])
def webhook_routes(subpath=None):
    """Route webhook-related requests to webhook-handler service."""
    try:
        # Build target URL
        if subpath:
            target_url = f"{WEBHOOK_SERVICE_URL}/webhook/{subpath}"
        else:
            target_url = f"{WEBHOOK_SERVICE_URL}/webhook"
        
        # Forward request
        if request.method == 'GET':
            response = requests.get(target_url, params=request.args)
        else:
            response = requests.post(target_url, json=request.get_json())
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Error routing to webhook service: {str(e)}")
        return jsonify({'error': str(e)}), 500

# AI Analyzer Routes
@app.route('/analyze', methods=['GET', 'POST'])
@app.route('/analyze/<path:subpath>', methods=['GET', 'POST'])
def ai_routes(subpath=None):
    """Route AI-related requests to ai-analyzer service."""
    try:
        # Build target URL
        if subpath:
            target_url = f"{AI_SERVICE_URL}/analyze/{subpath}"
        else:
            target_url = f"{AI_SERVICE_URL}/analyze"
        
        # Forward request
        if request.method == 'GET':
            response = requests.get(target_url, params=request.args)
        else:
            response = requests.post(target_url, json=request.get_json())
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Error routing to AI service: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Service Status Routes
@app.route('/status', methods=['GET'])
def get_all_services_status():
    """Get status of all services."""
    try:
        services_status = {}
        
        # Check each service
        services = {
            'commit-tracker': COMMIT_SERVICE_URL,
            'repo-manager': REPO_SERVICE_URL,
            'webhook-handler': WEBHOOK_SERVICE_URL,
            'ai-analyzer': AI_SERVICE_URL
        }
        
        for service_name, service_url in services.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=5)
                services_status[service_name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'url': service_url
                }
            except Exception as e:
                services_status[service_name] = {
                    'status': 'unhealthy',
                    'url': service_url,
                    'error': str(e)
                }
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'services': services_status
        })
        
    except Exception as e:
        logger.error(f"Error getting services status: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('GATEWAY_PORT', 8000))
    logger.info(f"🚀 Starting API Gateway on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
