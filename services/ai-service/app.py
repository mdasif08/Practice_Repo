#!/usr/bin/env python3
"""
AI Service - Microservice for AI agent orchestration and analysis.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.agent_orchestrator import AgentOrchestrator
from services.database_service import DatabaseService
from config.env_manager import env_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
db_service = DatabaseService()
agent_orchestrator = AgentOrchestrator(db_service)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'ai-service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/agents/status', methods=['GET'])
def get_agents_status():
    """Get AI agents status."""
    try:
        status = {
            'ollama_running': agent_orchestrator.check_ollama_status(),
            'code_llama_available': agent_orchestrator.ensure_model_available('codellama:7b'),
            'ollama_available': agent_orchestrator.ensure_model_available('llama2:7b')
        }
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting agents status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/agents/analyze/commit', methods=['POST'])
def analyze_commit():
    """Analyze a commit using AI agents."""
    try:
        data = request.get_json()
        commit_hash = data.get('commit_hash')
        repository_name = data.get('repository_name')
        
        if not commit_hash:
            return jsonify({'error': 'Commit hash is required'}), 400
        
        result = agent_orchestrator.analyze_commit(commit_hash, repository_name)
        return jsonify({
            'success': True,
            'analysis': result
        })
    except Exception as e:
        logger.error(f"Error analyzing commit: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/agents/analyze/code', methods=['POST'])
def analyze_code():
    """Analyze code changes using Code Llama."""
    try:
        data = request.get_json()
        code_changes = data.get('code_changes')
        
        if not code_changes:
            return jsonify({'error': 'Code changes are required'}), 400
        
        result = agent_orchestrator.analyze_code_changes(code_changes)
        return jsonify({
            'success': True,
            'analysis': result
        })
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/agents/interactions', methods=['GET'])
def get_agent_interactions():
    """Get all agent interactions."""
    try:
        interactions = agent_orchestrator.get_all_interactions()
        return jsonify({
            'success': True,
            'interactions': interactions,
            'count': len(interactions)
        })
    except Exception as e:
        logger.error(f"Error getting agent interactions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/agents/interactions/<interaction_id>', methods=['GET'])
def get_agent_interaction(interaction_id):
    """Get specific agent interaction."""
    try:
        interaction = agent_orchestrator.get_interaction_by_id(interaction_id)
        if interaction:
            return jsonify({
                'success': True,
                'interaction': interaction
            })
        else:
            return jsonify({'error': 'Interaction not found'}), 404
    except Exception as e:
        logger.error(f"Error getting interaction {interaction_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/agents/statistics', methods=['GET'])
def get_ai_statistics():
    """Get AI service statistics."""
    try:
        stats = agent_orchestrator.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting AI statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004, debug=True)
