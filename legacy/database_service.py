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
            # Repositories table (NEW - for better organization)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repositories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    owner VARCHAR(255) NOT NULL,
                    full_name VARCHAR(500) UNIQUE NOT NULL,
                    description TEXT,
                    language VARCHAR(100),
                    is_private BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Commits table (ENHANCED with repository_id)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commits (
                    id SERIAL PRIMARY KEY,
                    commit_hash VARCHAR(40) NOT NULL,
                    repository_id INTEGER REFERENCES repositories(id),
                    author VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    timestamp_commit TIMESTAMP NOT NULL,
                    timestamp_logged TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    branch VARCHAR(255),
                    repository_path TEXT,
                    repository_name TEXT,
                    changed_files JSONB,
                    metadata JSONB,
                    UNIQUE(commit_hash, repository_id)
                )
            """)
            
            # Add repository_id column if it doesn't exist (for backward compatibility)
            cursor.execute("ALTER TABLE commits ADD COLUMN IF NOT EXISTS repository_id INTEGER REFERENCES repositories(id);")
            
            # Add repository_name column if it doesn't exist (for backward compatibility)
            cursor.execute("ALTER TABLE commits ADD COLUMN IF NOT EXISTS repository_name TEXT;")
            
            # Add indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_commits_repository_id ON commits(repository_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_commits_author ON commits(author);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_commits_timestamp ON commits(timestamp_commit);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_repositories_full_name ON repositories(full_name);")
            
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
                    INSERT INTO commits (commit_hash, repository_id, author, message, timestamp_commit, 
                                       branch, repository_path, repository_name, changed_files, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (commit_hash, repository_id) DO UPDATE SET
                        author = EXCLUDED.author,
                        message = EXCLUDED.message,
                        timestamp_commit = EXCLUDED.timestamp_commit,
                        branch = EXCLUDED.branch,
                        repository_path = EXCLUDED.repository_path,
                        repository_name = EXCLUDED.repository_name,
                        changed_files = EXCLUDED.changed_files,
                        metadata = EXCLUDED.metadata
                    RETURNING id
                """, (
                    commit_data['commit_hash'],
                    commit_data.get('repository_id'),
                    commit_data['author'],
                    commit_data['message'],
                    commit_data['timestamp_commit'],
                    commit_data.get('branch'),
                    commit_data.get('repository_path'),
                    commit_data.get('repository_name'),
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
    
    def get_recent_commits(self, limit: int = 10, repository_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent commits with proper repository filtering."""
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                if repository_name:
                    # Enhanced query to get commits for specific repository with proper isolation
                    cursor.execute("""
                        SELECT c.*, r.name as repo_name, r.owner as repo_owner, r.full_name as repo_full_name
                        FROM commits c
                        LEFT JOIN repositories r ON c.repository_id = r.id
                        WHERE (r.name = %s AND r.name != 'Practice_Repo') OR 
                              (c.repository_name = %s AND c.repository_name != 'Practice_Repo')
                        ORDER BY c.timestamp_commit DESC 
                        LIMIT %s
                    """, (repository_name, repository_name, limit))
                else:
                    # Get all commits with repository info, excluding Practice_Repo unless specifically requested
                    cursor.execute("""
                        SELECT c.*, r.name as repo_name, r.owner as repo_owner, r.full_name as repo_full_name
                        FROM commits c
                        LEFT JOIN repositories r ON c.repository_id = r.id
                        WHERE (r.name IS NULL OR r.name != 'Practice_Repo') OR 
                              (c.repository_name IS NULL OR c.repository_name != 'Practice_Repo')
                        ORDER BY c.timestamp_commit DESC 
                        LIMIT %s
                    """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise DataStorageError(f"Failed to get recent commits: {str(e)}")

    def get_repository_commits(self, repo_owner: str, repo_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get commits for a specific repository with proper isolation."""
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT c.*, r.name as repo_name, r.owner as repo_owner, r.full_name as repo_full_name
                    FROM commits c
                    LEFT JOIN repositories r ON c.repository_id = r.id
                    WHERE (r.owner = %s AND r.name = %s) OR 
                          (c.repository_name = %s AND c.repository_name != 'Practice_Repo')
                    ORDER BY c.timestamp_commit DESC 
                    LIMIT %s
                """, (repo_owner, repo_name, repo_name, limit))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise DataStorageError(f"Failed to get repository commits: {str(e)}")

    def migrate_commits_to_repositories(self) -> Dict[str, int]:
        """Migrate existing commits to proper repository isolation."""
        try:
            with self.conn.cursor() as cursor:
                # Get all unique repository names from commits (excluding Practice_Repo)
                cursor.execute("""
                    SELECT DISTINCT repository_name 
                    FROM commits 
                    WHERE repository_name IS NOT NULL 
                    AND repository_name != 'Practice_Repo'
                """)
                
                repo_names = [row[0] for row in cursor.fetchall()]
                migrated_count = 0
                
                for repo_name in repo_names:
                    # Create repository entry if it doesn't exist
                    cursor.execute("""
                        INSERT INTO repositories (name, owner, full_name, description, language, is_private)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (full_name) DO NOTHING
                        RETURNING id
                    """, (repo_name, 'mdasif08', f'mdasif08/{repo_name}', None, None, False))
                    
                    result = cursor.fetchone()
                    if result:
                        repo_id = result[0]
                        
                        # Update commits to use this repository_id
                        cursor.execute("""
                            UPDATE commits 
                            SET repository_id = %s 
                            WHERE repository_name = %s AND repository_id IS NULL
                        """, (repo_id, repo_name))
                        
                        migrated_count += cursor.rowcount
                
                self.conn.commit()
                return {
                    'migrated_commits': migrated_count,
                    'processed_repositories': len(repo_names)
                }
        except Exception as e:
            self.conn.rollback()
            raise DataStorageError(f"Failed to migrate commits: {str(e)}")

    def ensure_repository_isolation(self, owner: str, repo_name: str) -> int:
        """Ensure a repository is properly registered and isolated."""
        try:
            with self.conn.cursor() as cursor:
                # Register repository if it doesn't exist
                cursor.execute("""
                    INSERT INTO repositories (name, owner, full_name, description, language, is_private)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (full_name) DO UPDATE SET
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """, (repo_name, owner, f"{owner}/{repo_name}", None, None, False))
                
                repo_id = cursor.fetchone()[0]
                
                # Update any existing commits to use this repository_id
                cursor.execute("""
                    UPDATE commits 
                    SET repository_id = %s 
                    WHERE repository_name = %s AND repository_id IS NULL
                """, (repo_id, repo_name))
                
                self.conn.commit()
                return repo_id
        except Exception as e:
            self.conn.rollback()
            raise DataStorageError(f"Failed to ensure repository isolation: {str(e)}")
    
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
    
    def get_repository_statistics(self) -> Dict[str, Any]:
        """Get repository-specific statistics."""
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Get commits by repository
                cursor.execute("""
                    SELECT repository_name, COUNT(*) as commit_count 
                    FROM commits 
                    WHERE repository_name IS NOT NULL 
                    GROUP BY repository_name 
                    ORDER BY commit_count DESC
                """)
                repo_stats = [dict(row) for row in cursor.fetchall()]
                
                # Get commits with NULL repository_name
                cursor.execute("SELECT COUNT(*) as null_repo_count FROM commits WHERE repository_name IS NULL")
                null_repo_count = cursor.fetchone()['null_repo_count']
                
                return {
                    'repository_stats': repo_stats,
                    'null_repository_count': null_repo_count,
                    'total_repositories': len(repo_stats)
                }
        except Exception as e:
            raise DataStorageError(f"Failed to get repository statistics: {str(e)}")
    
    def fix_null_repository_names(self, default_repo_name: str = "Practice_Repo") -> int:
        """Fix commits with NULL repository_name by setting them to a default value."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE commits 
                    SET repository_name = %s 
                    WHERE repository_name IS NULL
                """, (default_repo_name,))
                
                updated_count = cursor.rowcount
                self.conn.commit()
                return updated_count
        except Exception as e:
            self.conn.rollback()
            raise DataStorageError(f"Failed to fix null repository names: {str(e)}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
