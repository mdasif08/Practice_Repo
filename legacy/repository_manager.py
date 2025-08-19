"""
Repository Manager Service for CraftNudge Git Commit Logger.
Manages repository information and ensures proper commit isolation.
"""

import logging
import psycopg2.extras
from typing import Dict, Optional, Any, List
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database_service import DatabaseService
from utils.error_handler import DataStorageError

logger = logging.getLogger('RepositoryManager')


class RepositoryManager:
    """Manages repository information and ensures proper commit isolation."""
    
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
    
    def register_repository(self, owner: str, name: str, description: str = None, 
                          language: str = None, is_private: bool = False) -> int:
        """Register a new repository in the system."""
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO repositories (name, owner, full_name, description, language, is_private)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (full_name) DO UPDATE SET
                        description = EXCLUDED.description,
                        language = EXCLUDED.language,
                        is_private = EXCLUDED.is_private,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """, (name, owner, f"{owner}/{name}", description, language, is_private))
                
                repo_id = cursor.fetchone()[0]
                self.db.conn.commit()
                logger.info(f"Registered repository: {owner}/{name} (ID: {repo_id})")
                return repo_id
        except Exception as e:
            self.db.conn.rollback()
            raise DataStorageError(f"Failed to register repository: {str(e)}")
    
    def get_repository_id(self, owner: str, name: str) -> Optional[int]:
        """Get repository ID by owner and name."""
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM repositories WHERE owner = %s AND name = %s
                """, (owner, name))
                
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise DataStorageError(f"Failed to get repository ID: {str(e)}")
    
    def get_repository_by_id(self, repo_id: int) -> Optional[Dict[str, Any]]:
        """Get repository information by ID."""
        try:
            with self.db.conn.cursor(cursor_factory=self.db.conn.cursor_factory) as cursor:
                cursor.execute("""
                    SELECT * FROM repositories WHERE id = %s
                """, (repo_id,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            raise DataStorageError(f"Failed to get repository by ID: {str(e)}")
    
    def get_all_repositories(self) -> List[Dict[str, Any]]:
        """Get all registered repositories."""
        try:
            with self.db.conn.cursor(cursor_factory=self.db.conn.cursor_factory) as cursor:
                cursor.execute("""
                    SELECT * FROM repositories ORDER BY name
                """)
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise DataStorageError(f"Failed to get all repositories: {str(e)}")
    
    def get_commits_by_repository(self, owner: str, name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get commits for a specific repository with proper isolation."""
        try:
            return self.db.get_repository_commits(owner, name, limit)
        except Exception as e:
            raise DataStorageError(f"Failed to get commits by repository: {str(e)}")

    def ensure_repository_isolation(self, owner: str, name: str) -> int:
        """Ensure a repository is properly registered and isolated."""
        try:
            return self.db.ensure_repository_isolation(owner, name)
        except Exception as e:
            raise DataStorageError(f"Failed to ensure repository isolation: {str(e)}")

    def get_repository_statistics(self) -> Dict[str, Any]:
        """Get enhanced repository statistics with proper isolation."""
        try:
            with self.db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Get repository statistics with commit counts, excluding Practice_Repo
                cursor.execute("""
                    SELECT 
                        r.id,
                        r.name,
                        r.owner,
                        r.full_name,
                        r.language,
                        r.is_private,
                        COUNT(c.id) as commit_count
                    FROM repositories r
                    LEFT JOIN commits c ON r.id = c.repository_id
                    WHERE r.name != 'Practice_Repo'
                    GROUP BY r.id, r.name, r.owner, r.full_name, r.language, r.is_private
                    ORDER BY commit_count DESC
                """)
                
                repositories = [dict(row) for row in cursor.fetchall()]
                
                # Get total statistics (excluding Practice_Repo)
                cursor.execute("SELECT COUNT(*) as total_repositories FROM repositories WHERE name != 'Practice_Repo'")
                total_repositories = cursor.fetchone()['total_repositories']
                
                cursor.execute("""
                    SELECT COUNT(*) as total_commits 
                    FROM commits c
                    LEFT JOIN repositories r ON c.repository_id = r.id
                    WHERE (r.name IS NULL OR r.name != 'Practice_Repo') AND 
                          (c.repository_name IS NULL OR c.repository_name != 'Practice_Repo')
                """)
                total_commits = cursor.fetchone()['total_commits']
                
                return {
                    'repositories': repositories,
                    'total_repositories': total_repositories,
                    'total_commits': total_commits
                }
        except Exception as e:
            raise DataStorageError(f"Failed to get repository statistics: {str(e)}")

    def save_commit_with_repository(self, commit_data: Dict[str, Any], 
                                  owner: str, repo_name: str) -> int:
        """Save commit with proper repository association and isolation."""
        try:
            # Ensure repository is registered and isolated
            repo_id = self.ensure_repository_isolation(owner, repo_name)
            
            # Set the repository_id in commit data
            commit_data['repository_id'] = repo_id
            commit_data['repository_name'] = repo_name
            
            # Save the commit
            return self.db.save_commit(commit_data)
        except Exception as e:
            raise DataStorageError(f"Failed to save commit with repository: {str(e)}")
