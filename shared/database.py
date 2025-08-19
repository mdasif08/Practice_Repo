#!/usr/bin/env python3
"""
Production Database Service - CraftNudge Schema
"""

import psycopg2
import os
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        """Initialize database connection."""
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL database."""
        try:
            # Get database configuration from environment variables
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'newDB')
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', 'root')
            
            # Create connection
            self.conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            
            logger.info("✅ Database connection established")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            raise
    
    def get_connection(self):
        """Get database connection."""
        if self.conn is None or self.conn.closed:
            self.connect()
        return self.conn
    
    def execute_query(self, query, params=None):
        """Execute a query and return results."""
        try:
            with self.get_connection().cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    self.conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Query execution failed: {str(e)}")
            self.conn.rollback()
            raise
    
    def upsert_commit(self, commit_data):
        """Upsert commit data using ON CONFLICT."""
        try:
            # Insert or update commit
            commit_query = """
                INSERT INTO CraftNudge.Commits (commit_id, author, message, timestamp)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (commit_id) 
                DO UPDATE SET 
                    author = EXCLUDED.author,
                    message = EXCLUDED.message,
                    timestamp = EXCLUDED.timestamp
                RETURNING commit_id
            """
            
            commit_params = (
                commit_data['commit_id'],
                commit_data['author'],
                commit_data['message'],
                commit_data['timestamp']
            )
            
            result = self.execute_query(commit_query, commit_params)
            
            # Insert commit files
            if 'changed_files' in commit_data and commit_data['changed_files']:
                for file_info in commit_data['changed_files']:
                    file_query = """
                        INSERT INTO CraftNudge.Commit_Files (commit_id, file_name, change_type)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """
                    
                    file_params = (
                        commit_data['commit_id'],
                        file_info['file_name'],
                        file_info.get('change_type', 'modified')
                    )
                    
                    self.execute_query(file_query, file_params)
            
            return result
            
        except Exception as e:
            logger.error(f"Error upserting commit {commit_data.get('commit_id')}: {str(e)}")
            raise
    
    def get_all_commits(self, limit=100):
        """Get all commits with their files."""
        try:
            query = """
                SELECT 
                    c.commit_id,
                    c.author,
                    c.message,
                    c.timestamp,
                    c.created_at,
                    COALESCE(
                        json_agg(
                            json_build_object(
                                'file_id', cf.file_id,
                                'file_name', cf.file_name,
                                'change_type', cf.change_type
                            ) ORDER BY cf.file_name
                        ) FILTER (WHERE cf.file_id IS NOT NULL),
                        '[]'::json
                    ) as changed_files
                FROM CraftNudge.Commits c
                LEFT JOIN CraftNudge.Commit_Files cf ON c.commit_id = cf.commit_id
                GROUP BY c.commit_id, c.author, c.message, c.timestamp, c.created_at
                ORDER BY c.timestamp DESC
                LIMIT %s
            """
            
            return self.execute_query(query, (limit,))
            
        except Exception as e:
            logger.error(f"Error getting commits: {str(e)}")
            raise
    
    def get_commit_by_id(self, commit_id):
        """Get specific commit by ID."""
        try:
            query = """
                SELECT 
                    c.commit_id,
                    c.author,
                    c.message,
                    c.timestamp,
                    c.created_at,
                    COALESCE(
                        json_agg(
                            json_build_object(
                                'file_id', cf.file_id,
                                'file_name', cf.file_name,
                                'change_type', cf.change_type
                            ) ORDER BY cf.file_name
                        ) FILTER (WHERE cf.file_id IS NOT NULL),
                        '[]'::json
                    ) as changed_files
                FROM CraftNudge.Commits c
                LEFT JOIN CraftNudge.Commit_Files cf ON c.commit_id = cf.commit_id
                WHERE c.commit_id = %s
                GROUP BY c.commit_id, c.author, c.message, c.timestamp, c.created_at
            """
            
            result = self.execute_query(query, (commit_id,))
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error getting commit {commit_id}: {str(e)}")
            raise
    
    def get_commit_statistics(self):
        """Get commit statistics."""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_commits,
                    COUNT(DISTINCT author) as unique_authors,
                    COUNT(DISTINCT DATE(timestamp)) as active_days
                FROM CraftNudge.Commits
            """
            
            result = self.execute_query(query)
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Error getting commit statistics: {str(e)}")
            raise

    def clear_all_commits(self):
        """Clear all commits and related data from database."""
        try:
            # Clear commit files first (due to foreign key constraint)
            self.execute_query("DELETE FROM craftnudge.commit_files")
            
            # Clear commits
            self.execute_query("DELETE FROM craftnudge.commits")
            
            logger.info("✅ All commits cleared from database")
            
        except Exception as e:
            logger.error(f"Error clearing commits: {str(e)}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

# Global database service instance
db_service = DatabaseService()
