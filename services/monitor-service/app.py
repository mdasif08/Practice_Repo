#!/usr/bin/env python3
"""
Monitor Service - Microservice for continuous monitoring and background tasks.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import threading
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.continuous_monitor import ContinuousMonitor
from services.database_service import DatabaseService
from config.env_manager import env_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
db_service = DatabaseService()
monitor = ContinuousMonitor(database_service=db_service)

# Global monitor thread
monitor_thread = None
monitor_running = False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'monitor-service',
        'timestamp': datetime.now().isoformat(),
        'monitor_running': monitor_running
    })

@app.route('/monitor/start', methods=['POST'])
def start_monitor():
    """Start the continuous monitor."""
    global monitor_thread, monitor_running
    
    try:
        if monitor_running:
            return jsonify({
                'success': False,
                'message': 'Monitor is already running'
            }), 400
        
        monitor_running = True
        monitor_thread = threading.Thread(target=monitor.start_monitoring)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Monitor started successfully'
        })
    except Exception as e:
        logger.error(f"Error starting monitor: {str(e)}")
        monitor_running = False
        return jsonify({'error': str(e)}), 500

@app.route('/monitor/stop', methods=['POST'])
def stop_monitor():
    """Stop the continuous monitor."""
    global monitor_running
    
    try:
        if not monitor_running:
            return jsonify({
                'success': False,
                'message': 'Monitor is not running'
            }), 400
        
        monitor.stop_monitoring()
        monitor_running = False
        
        return jsonify({
            'success': True,
            'message': 'Monitor stopped successfully'
        })
    except Exception as e:
        logger.error(f"Error stopping monitor: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/monitor/status', methods=['GET'])
def get_monitor_status():
    """Get monitor status."""
    try:
        status = {
            'running': monitor_running,
            'check_interval': monitor.check_interval,
            'enable_agents': monitor.enable_agents,
            'enable_webhooks': monitor.enable_webhooks,
            'last_check': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting monitor status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/monitor/run-once', methods=['POST'])
def run_monitor_once():
    """Run monitor cycle once."""
    try:
        result = monitor.run_monitoring_cycle()
        return jsonify({
            'success': True,
            'result': result,
            'message': 'Monitor cycle completed'
        })
    except Exception as e:
        logger.error(f"Error running monitor cycle: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/monitor/events', methods=['GET'])
def get_monitor_events():
    """Get recent monitor events."""
    try:
        # This would implement actual event retrieval
        events = [
            {
                'timestamp': datetime.now().isoformat(),
                'type': 'monitor_cycle',
                'status': 'completed',
                'message': 'Monitoring cycle completed successfully'
            }
        ]
        
        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        })
    except Exception as e:
        logger.error(f"Error getting monitor events: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/monitor/statistics', methods=['GET'])
def get_monitor_statistics():
    """Get monitor statistics."""
    try:
        stats = {
            'total_cycles': 0,
            'successful_cycles': 0,
            'failed_cycles': 0,
            'last_successful_cycle': None,
            'uptime': '0:00:00'
        }
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting monitor statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006, debug=True)
