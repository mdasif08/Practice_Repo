#!/usr/bin/env python3
"""
Migration script to fix repository isolation issues.
Ensures each repository has its own individual commits and prevents mixing with Practice_Repo.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.database_service import DatabaseService
from services.repository_manager import RepositoryManager

def main():
    """Run the migration to fix repository isolation."""
    print("🔄 Starting repository isolation migration...")
    
    try:
        db_service = DatabaseService()
        repo_manager = RepositoryManager(db_service)
        
        # Step 1: Migrate existing commits to proper repository isolation
        print("📊 Migrating commits to repository isolation...")
        migration_result = db_service.migrate_commits_to_repositories()
        
        print(f"✅ Migrated {migration_result['migrated_commits']} commits")
        print(f"✅ Processed {migration_result['processed_repositories']} repositories")
        
        # Step 2: Get updated statistics
        print("📈 Getting updated statistics...")
        stats = repo_manager.get_repository_statistics()
        
        print(f"📁 Total repositories: {stats['total_repositories']}")
        print(f"📝 Total commits: {stats['total_commits']}")
        
        print("\n📋 Repository breakdown:")
        for repo in stats['repositories']:
            print(f"  • {repo['full_name']}: {repo['commit_count']} commits")
        
        # Step 3: Verify isolation
        print("\n🔍 Verifying repository isolation...")
        all_repos = repo_manager.get_all_repositories()
        
        for repo in all_repos:
            if repo['name'] != 'Practice_Repo':
                commits = repo_manager.get_commits_by_repository(repo['owner'], repo['name'], limit=5)
                print(f"  ✅ {repo['full_name']}: {len(commits)} commits (isolated)")
        
        print("\n✅ Migration completed successfully!")
        print("🎯 Each repository now has its own individual commits!")
        print("🚫 No more mixing with Practice_Repo!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

