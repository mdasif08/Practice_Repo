#!/usr/bin/env python3
"""
Migration script to associate existing commits with repositories.
This script will update existing commits to have proper repository_id values.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.database_service import DatabaseService
from services.repository_manager import RepositoryManager

def migrate_commits_to_repositories():
    """Migrate existing commits to be associated with repositories."""
    print("🔄 Starting commit migration...")
    
    try:
        db_service = DatabaseService()
        repo_manager = RepositoryManager(db_service)
        
        # Get all commits that don't have repository_id
        with db_service.conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, repository_name, commit_hash 
                FROM commits 
                WHERE repository_id IS NULL
                ORDER BY timestamp_commit DESC
            """)
            commits_to_migrate = cursor.fetchall()
        
        print(f"📝 Found {len(commits_to_migrate)} commits to migrate")
        
        migrated_count = 0
        for commit_id, repo_name, commit_hash in commits_to_migrate:
            if repo_name:
                try:
                    # Try to find the repository by name
                    repo_id = repo_manager.get_repository_id("mdasif08", repo_name)
                    
                    if repo_id:
                        # Update the commit with the repository_id
                        with db_service.conn.cursor() as cursor:
                            cursor.execute("""
                                UPDATE commits 
                                SET repository_id = %s 
                                WHERE id = %s
                            """, (repo_id, commit_id))
                        
                        migrated_count += 1
                        print(f"  ✅ Migrated commit {commit_hash[:8]} to repository {repo_name}")
                    else:
                        print(f"  ⚠️ Repository {repo_name} not found for commit {commit_hash[:8]}")
                        
                except Exception as e:
                    print(f"  ❌ Error migrating commit {commit_hash[:8]}: {str(e)}")
            else:
                print(f"  ⚠️ Commit {commit_hash[:8]} has no repository_name")
        
        db_service.conn.commit()
        print(f"\n🎉 Migration completed! Migrated {migrated_count} commits")
        
        # Show updated statistics
        print("\n📊 Updated statistics:")
        stats = repo_manager.get_repository_statistics()
        for repo in stats['repositories']:
            print(f"  📁 {repo['name']}: {repo['commit_count']} commits")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def create_missing_repositories():
    """Create repositories for commits that don't have associated repositories."""
    print("\n🔍 Creating missing repositories...")
    
    try:
        db_service = DatabaseService()
        repo_manager = RepositoryManager(db_service)
        
        # Get unique repository names from commits
        with db_service.conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT repository_name 
                FROM commits 
                WHERE repository_name IS NOT NULL 
                AND repository_name != ''
            """)
            repo_names = [row[0] for row in cursor.fetchall()]
        
        print(f"📝 Found {len(repo_names)} unique repository names")
        
        created_count = 0
        for repo_name in repo_names:
            try:
                # Check if repository already exists
                existing_id = repo_manager.get_repository_id("mdasif08", repo_name)
                
                if not existing_id:
                    # Create the repository
                    repo_id = repo_manager.register_repository(
                        owner="mdasif08",
                        name=repo_name,
                        description=f"Repository for {repo_name}",
                        language="Unknown",
                        is_private=False
                    )
                    created_count += 1
                    print(f"  ✅ Created repository: {repo_name}")
                else:
                    print(f"  ℹ️ Repository {repo_name} already exists")
                    
            except Exception as e:
                print(f"  ❌ Error creating repository {repo_name}: {str(e)}")
        
        print(f"\n🎉 Created {created_count} new repositories")
        return True
        
    except Exception as e:
        print(f"❌ Repository creation failed: {str(e)}")
        return False

def main():
    """Run the complete migration process."""
    print("🚀 Starting complete migration process...\n")
    
    # Step 1: Create missing repositories
    if not create_missing_repositories():
        print("❌ Repository creation failed")
        return False
    
    # Step 2: Migrate commits to repositories
    if not migrate_commits_to_repositories():
        print("❌ Commit migration failed")
        return False
    
    print("\n🎉 Complete migration successful!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



