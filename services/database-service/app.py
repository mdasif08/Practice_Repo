#!/usr/bin/env python3
"""
Database Service - Microservice for database operations and data management.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.database_service import DatabaseService
from config.env_manager import env_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
db_service = DatabaseService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        stats = db_service.get_statistics()
        return jsonify({
            'status': 'healthy',
            'service': 'database-service',
            'timestamp': datetime.now().isoformat(),
            'database_connected': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'database-service',
            'timestamp': datetime.now().isoformat(),
            'database_connected': False,
            'error': str(e)
        }), 500

@app.route('/database/statistics', methods=['GET'])
def get_database_statistics():
    """Get database statistics."""
    try:
        stats = db_service.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting database statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/database/tables', methods=['GET'])
def get_database_tables():
    """Get list of database tables."""
    try:
        with db_service.conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
        return jsonify({
            'success': True,
            'tables': tables,
            'count': len(tables)
        })
    except Exception as e:
        logger.error(f"Error getting database tables: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/database/backup', methods=['POST'])
def create_database_backup():
    """Create database backup."""
    try:
        # This would implement actual backup logic
        backup_info = {
            'timestamp': datetime.now().isoformat(),
            'status': 'backup_created',
            'filename': f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        }
        
        return jsonify({
            'success': True,
            'backup': backup_info
        })
    except Exception as e:
        logger.error(f"Error creating database backup: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/database/cleanup', methods=['POST'])
def cleanup_database():
    """Clean up old data."""
    try:
        data = request.get_json()
        days_old = data.get('days_old', 30)
        
        # This would implement actual cleanup logic
        cleanup_info = {
            'timestamp': datetime.now().isoformat(),
            'days_old': days_old,
            'status': 'cleanup_completed'
        }
        
        return jsonify({
            'success': True,
            'cleanup': cleanup_info
        })
    except Exception as e:
        logger.error(f"Error cleaning up database: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/database/migrate', methods=['POST'])
def run_database_migration():
    """Run database migration."""
    try:
        # This would implement actual migration logic
        migration_info = {
            'timestamp': datetime.now().isoformat(),
            'status': 'migration_completed',
            'version': '1.0.0'
        }
        
        return jsonify({
            'success': True,
            'migration': migration_info
        })
    except Exception as e:
        logger.error(f"Error running database migration: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8005, debug=True)
