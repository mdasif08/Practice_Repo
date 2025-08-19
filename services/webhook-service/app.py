#!/usr/bin/env python3
"""
Webhook Service - Microservice for handling GitHub webhooks and events.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.github_webhook_handler import GitHubWebhookHandler
from services.database_service import DatabaseService
from config.env_manager import env_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
db_service = DatabaseService()
webhook_handler = GitHubWebhookHandler(db_service)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'webhook-service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/webhook/github', methods=['POST'])
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

@app.route('/webhook/events', methods=['GET'])
def get_webhook_events():
    """Get all webhook events."""
    try:
        events = webhook_handler.get_all_events()
        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        })
    except Exception as e:
        logger.error(f"Error getting webhook events: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/events/unprocessed', methods=['GET'])
def get_unprocessed_events():
    """Get unprocessed webhook events."""
    try:
        events = webhook_handler.get_unprocessed_events()
        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        })
    except Exception as e:
        logger.error(f"Error getting unprocessed events: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/events/<event_id>/process', methods=['POST'])
def process_event(event_id):
    """Manually process a specific event."""
    try:
        result = webhook_handler.process_event_by_id(event_id)
        return jsonify({
            'success': True,
            'result': result,
            'message': 'Event processed successfully'
        })
    except Exception as e:
        logger.error(f"Error processing event {event_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/statistics', methods=['GET'])
def get_webhook_statistics():
    """Get webhook statistics."""
    try:
        stats = webhook_handler.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting webhook statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003, debug=True)
