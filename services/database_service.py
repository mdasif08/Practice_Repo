"""
PostgreSQL Database Service for CraftNudge Git Commit Logger.
Handles all database operations for storing commits and agent interactions.
"""

import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import List, Dict, Optional, Any
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.error_handler import DataStorageError


class DatabaseService:
    """PostgreSQL database service for storing commit data and agent interactions."""
    
    def __init__(self, host: str = "localhost", port: int = 5432, 
                 database: str = "newDB", user: str = "postgres", password: str = "root"):
        """Initialize database connection."""
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables if they don't exist."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self._create_tables()
        except Exception as e:
            raise DataStorageError(f"Failed to initialize database: {str(e)}")
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        with self.conn.cursor() as cursor:
            # Commits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commits (
                    id SERIAL PRIMARY KEY,
                    commit_hash VARCHAR(40) UNIQUE NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    timestamp_commit TIMESTAMP NOT NULL,
                    timestamp_logged TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    branch VARCHAR(255),
                    repository_path TEXT,
                    changed_files JSONB,
                    metadata JSONB
                )
            """)
            
            # Agent interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_interactions (
                    id SERIAL PRIMARY KEY,
                    commit_id INTEGER REFERENCES commits(id),
                    agent_type VARCHAR(50) NOT NULL,
                    interaction_type VARCHAR(50) NOT NULL,
                    input_data JSONB,
                    output_data JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'pending'
                )
            """)
            
            # GitHub webhook events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS github_events (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(50) NOT NULL,
                    repository VARCHAR(255) NOT NULL,
                    commit_hash VARCHAR(40),
                    event_data JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Agent configurations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_configs (
                    id SERIAL PRIMARY KEY,
                    agent_name VARCHAR(100) UNIQUE NOT NULL,
                    agent_type VARCHAR(50) NOT NULL,
                    model_name VARCHAR(100),
                    configuration JSONB,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
    
    def save_commit(self, commit_data: Dict[str, Any]) -> int:
        """Save a commit to the database."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO commits (commit_hash, author, message, timestamp_commit, 
                                       branch, repository_path, changed_files, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (commit_hash) DO UPDATE SET
                        author = EXCLUDED.author,
                        message = EXCLUDED.message,
                        timestamp_commit = EXCLUDED.timestamp_commit,
                        branch = EXCLUDED.branch,
                        repository_path = EXCLUDED.repository_path,
                        changed_files = EXCLUDED.changed_files,
                        metadata = EXCLUDED.metadata
                    RETURNING id
                """, (
                    commit_data['commit_hash'],
                    commit_data['author'],
                    commit_data['message'],
                    commit_data['timestamp_commit'],
                    commit_data.get('branch'),
                    commit_data.get('repository_path'),
                    json.dumps(commit_data.get('changed_files', [])),
                    json.dumps(commit_data.get('metadata', {}))
                ))
                
                commit_id = cursor.fetchone()[0]
                self.conn.commit()
                return commit_id
        except Exception as e:
            self.conn.rollback()
            raise DataStorageError(f"Failed to save commit: {str(e)}")
    
    def get_commit_by_hash(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """Get a commit by its hash."""
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM commits WHERE commit_hash = %s
                """, (commit_hash,))
                
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return None
        except Exception as e:
            raise DataStorageError(f"Failed to get commit: {str(e)}")
    
    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits."""
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM commits 
                    ORDER BY timestamp_commit DESC 
                    LIMIT %s
                """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise DataStorageError(f"Failed to get recent commits: {str(e)}")
    
    def save_agent_interaction(self, commit_id: int, agent_type: str, 
                              interaction_type: str, input_data: Dict[str, Any], 
                              output_data: Dict[str, Any], status: str = "completed") -> int:
        """Save an agent interaction."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO agent_interactions 
                    (commit_id, agent_type, interaction_type, input_data, output_data, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    commit_id,
                    agent_type,
                    interaction_type,
                    json.dumps(input_data),
                    json.dumps(output_data),
                    status
                ))
                
                interaction_id = cursor.fetchone()[0]
                self.conn.commit()
                return interaction_id
        except Exception as e:
            self.conn.rollback()
            raise DataStorageError(f"Failed to save agent interaction: {str(e)}")
    
    def save_github_event(self, event_type: str, repository: str, 
                         commit_hash: Optional[str], event_data: Dict[str, Any]) -> int:
        """Save a GitHub webhook event."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO github_events (event_type, repository, commit_hash, event_data)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (
                    event_type,
                    repository,
                    commit_hash,
                    json.dumps(event_data)
                ))
                
                event_id = cursor.fetchone()[0]
                self.conn.commit()
                return event_id
        except Exception as e:
            self.conn.rollback()
            raise DataStorageError(f"Failed to save GitHub event: {str(e)}")
    
    def get_unprocessed_github_events(self) -> List[Dict[str, Any]]:
        """Get unprocessed GitHub events."""
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM github_events 
                    WHERE processed = FALSE 
                    ORDER BY timestamp ASC
                """)
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise DataStorageError(f"Failed to get unprocessed events: {str(e)}")
    
    def mark_event_processed(self, event_id: int):
        """Mark a GitHub event as processed."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE github_events SET processed = TRUE WHERE id = %s
                """, (event_id,))
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise DataStorageError(f"Failed to mark event as processed: {str(e)}")
    
    def save_agent_config(self, agent_name: str, agent_type: str, 
                         model_name: str, configuration: Dict[str, Any]) -> int:
        """Save or update agent configuration."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO agent_configs (agent_name, agent_type, model_name, configuration)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (agent_name) DO UPDATE SET
                        agent_type = EXCLUDED.agent_type,
                        model_name = EXCLUDED.model_name,
                        configuration = EXCLUDED.configuration,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """, (
                    agent_name,
                    agent_type,
                    model_name,
                    json.dumps(configuration)
                ))
                
                config_id = cursor.fetchone()[0]
                self.conn.commit()
                return config_id
        except Exception as e:
            self.conn.rollback()
            raise DataStorageError(f"Failed to save agent config: {str(e)}")
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent configuration."""
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM agent_configs WHERE agent_name = %s AND is_active = TRUE
                """, (agent_name,))
                
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return None
        except Exception as e:
            raise DataStorageError(f"Failed to get agent config: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Total commits
                cursor.execute("SELECT COUNT(*) as total_commits FROM commits")
                total_commits = cursor.fetchone()['total_commits']
                
                # Unique authors
                cursor.execute("SELECT COUNT(DISTINCT author) as unique_authors FROM commits")
                unique_authors = cursor.fetchone()['unique_authors']
                
                # Total agent interactions
                cursor.execute("SELECT COUNT(*) as total_interactions FROM agent_interactions")
                total_interactions = cursor.fetchone()['total_interactions']
                
                # Unprocessed events
                cursor.execute("SELECT COUNT(*) as unprocessed_events FROM github_events WHERE processed = FALSE")
                unprocessed_events = cursor.fetchone()['unprocessed_events']
                
                return {
                    'total_commits': total_commits,
                    'unique_authors': unique_authors,
                    'total_interactions': total_interactions,
                    'unprocessed_events': unprocessed_events
                }
        except Exception as e:
            raise DataStorageError(f"Failed to get statistics: {str(e)}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
