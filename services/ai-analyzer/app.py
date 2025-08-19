#!/usr/bin/env python3
"""
AI Analyzer Service - Handles AI analysis operations
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

class AIAnalyzer:
    """Simple AI analyzer using Ollama."""
    
    def __init__(self):
        self.ollama_url = config.OLLAMA_BASE_URL
        self.code_llama_model = config.CODE_LLAMA_MODEL
        self.llama_model = config.OLLAMA_MODEL
    
    def check_ollama_status(self):
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama status check failed: {str(e)}")
            return False
    
    def analyze_commit(self, commit_hash, repository_name=None):
        """Analyze a commit using AI."""
        try:
            # Get commit from database
            commit = db_service.get_commit_by_hash(commit_hash)
            if not commit:
                return {
                    'success': False,
                    'error': 'Commit not found'
                }
            
            # Create analysis prompt
            prompt = f"""
            Analyze this Git commit and provide insights:
            
            Commit Hash: {commit['commit_hash']}
            Author: {commit['author']}
            Message: {commit['message']}
            Repository: {commit['repository_name']}
            Files Changed: {commit.get('files_changed', [])}
            
            Please provide:
            1. Brief summary of what this commit does
            2. Potential impact assessment
            3. Code quality insights
            4. Suggestions for improvement
            """
            
            # Send to Ollama
            analysis = self._query_ollama(prompt, self.llama_model)
            
            return {
                'success': True,
                'commit_hash': commit_hash,
                'analysis': analysis,
                'model_used': self.llama_model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing commit {commit_hash}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_code_changes(self, code_changes):
        """Analyze code changes using Code Llama."""
        try:
            # Create code analysis prompt
            prompt = f"""
            Analyze these code changes and provide insights:
            
            {code_changes}
            
            Please provide:
            1. What the code changes do
            2. Potential bugs or issues
            3. Code quality assessment
            4. Security considerations
            5. Performance implications
            """
            
            # Send to Code Llama
            analysis = self._query_ollama(prompt, self.code_llama_model)
            
            return {
                'success': True,
                'analysis': analysis,
                'model_used': self.code_llama_model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code changes: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _query_ollama(self, prompt, model):
        """Query Ollama API."""
        try:
            url = f"{self.ollama_url}/api/generate"
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', 'No response from AI model')
            
        except Exception as e:
            logger.error(f"Error querying Ollama: {str(e)}")
            return f"Error: {str(e)}"

# Initialize AI analyzer
ai_analyzer = AIAnalyzer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        ollama_status = ai_analyzer.check_ollama_status()
        return jsonify({
            'status': 'healthy',
            'service': 'ai-analyzer',
            'timestamp': datetime.now().isoformat(),
            'ollama_available': ollama_status
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'ai-analyzer',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@app.route('/analyze/commit/<commit_hash>', methods=['GET'])
def analyze_commit(commit_hash):
    """Analyze a specific commit."""
    try:
        result = ai_analyzer.analyze_commit(commit_hash)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in analyze_commit endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze/code', methods=['POST'])
def analyze_code():
    """Analyze code changes."""
    try:
        data = request.get_json()
        code_changes = data.get('code_changes', '')
        
        if not code_changes:
            return jsonify({'error': 'Code changes are required'}), 400
        
        result = ai_analyzer.analyze_code_changes(code_changes)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in analyze_code endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze/commit', methods=['POST'])
def analyze_commit_post():
    """Analyze a commit via POST request."""
    try:
        data = request.get_json()
        commit_hash = data.get('commit_hash', '')
        repository_name = data.get('repository_name', '')
        
        if not commit_hash:
            return jsonify({'error': 'Commit hash is required'}), 400
        
        result = ai_analyzer.analyze_commit(commit_hash, repository_name)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in analyze_commit_post endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_ai_status():
    """Get AI service status."""
    try:
        ollama_status = ai_analyzer.check_ollama_status()
        
        return jsonify({
            'success': True,
            'ollama_running': ollama_status,
            'models_available': {
                'code_llama': config.CODE_LLAMA_MODEL,
                'llama': config.LLAMA_MODEL
            },
            'ollama_url': config.OLLAMA_BASE_URL,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting AI status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def get_available_models():
    """Get available AI models."""
    try:
        if not ai_analyzer.check_ollama_status():
            return jsonify({
                'success': False,
                'error': 'Ollama is not running'
            }), 503
        
        # Get models from Ollama
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags")
        response.raise_for_status()
        
        models_data = response.json()
        models = [model['name'] for model in models_data.get('models', [])]
        
        return jsonify({
            'success': True,
            'models': models,
            'recommended_models': {
                'code_analysis': config.CODE_LLAMA_MODEL,
                'commit_analysis': config.LLAMA_MODEL
            }
        })
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['POST'])
def test_ai_analysis():
    """Test AI analysis with sample data."""
    try:
        # Test commit analysis
        test_commit = {
            'commit_hash': 'test123',
            'author': 'test_user',
            'message': 'Add new feature for user authentication',
            'repository_name': 'test-repo',
            'files_changed': ['auth.py', 'login.py']
        }
        
        # Save test commit to database
        db_service.save_commit(test_commit)
        
        # Analyze the test commit
        result = ai_analyzer.analyze_commit('test123')
        
        return jsonify({
            'success': True,
            'test_result': result,
            'message': 'AI analysis test completed'
        })
    except Exception as e:
        logger.error(f"Error in test_ai_analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info(f"🚀 Starting AI Analyzer Service on port {config.AI_SERVICE_PORT}")
    app.run(host='0.0.0.0', port=config.AI_SERVICE_PORT, debug=True)
