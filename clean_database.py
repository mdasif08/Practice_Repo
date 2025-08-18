#!/usr/bin/env python3
"""
Script to clean the database and keep only commits from mdasif08.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.database_service import DatabaseService

def clean_database():
    """Remove all commits except those from mdasif08."""
    
    try:
        # Initialize database service
        db_service = DatabaseService()
        print("✅ Connected to PostgreSQL database")
        
        # Get all commits
        all_commits = db_service.get_recent_commits(limit=100)
        print(f"📊 Found {len(all_commits)} total commits in database")
        
        # Count commits by author
        author_counts = {}
        for commit in all_commits:
            author = commit['author']
            author_counts[author] = author_counts.get(author, 0) + 1
        
        print("\n📋 Current commits by author:")
        for author, count in author_counts.items():
            print(f"   {author}: {count} commits")
        
        # Keep only mdasif08 commits
        commits_to_keep = [commit for commit in all_commits if commit['author'] == 'mdasif08']
        commits_to_delete = [commit for commit in all_commits if commit['author'] != 'mdasif08']
        
        print(f"\n🗑️ Will delete {len(commits_to_delete)} commits from other authors")
        print(f"💾 Will keep {len(commits_to_keep)} commits from mdasif08")
        
        if commits_to_delete:
            print("\n📝 Commits to be deleted:")
            for commit in commits_to_delete:
                print(f"   - {commit['author']}: {commit['message'][:50]}...")
        
        if commits_to_keep:
            print("\n✅ Commits to keep:")
            for commit in commits_to_keep:
                print(f"   - {commit['author']}: {commit['message'][:50]}...")
        
        # Confirm deletion
        if commits_to_delete:
            print(f"\n⚠️ Are you sure you want to delete {len(commits_to_delete)} commits? (y/N): ", end="")
            confirm = input().strip().lower()
            
            if confirm == 'y':
                # Delete commits from other authors
                deleted_count = 0
                for commit in commits_to_delete:
                    try:
                        # Delete the commit
                        with db_service.conn.cursor() as cursor:
                            cursor.execute("DELETE FROM commits WHERE id = %s", (commit['id'],))
                        deleted_count += 1
                        print(f"🗑️ Deleted commit {commit['id']}: {commit['message'][:30]}...")
                    except Exception as e:
                        print(f"❌ Error deleting commit {commit['id']}: {str(e)}")
                
                # Commit the changes
                db_service.conn.commit()
                print(f"\n✅ Successfully deleted {deleted_count} commits")
            else:
                print("❌ Operation cancelled")
        else:
            print("\n✅ No commits to delete - only mdasif08 commits found")
        
        # Get final statistics
        final_commits = db_service.get_recent_commits(limit=100)
        final_stats = db_service.get_statistics()
        
        print(f"\n🎉 Final Database Status:")
        print(f"   Total commits: {final_stats['total_commits']}")
        print(f"   Unique authors: {final_stats['unique_authors']}")
        
        if final_commits:
            print(f"\n📋 Remaining commits:")
            for commit in final_commits:
                print(f"   - {commit['author']}: {commit['message']}")
        else:
            print("\n📋 No commits remaining in database")
        
        print("\n✅ Database cleaned successfully!")
        print("🖱️ Now click 'Track Now' in your frontend to see only mdasif08 commits!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    finally:
        if 'db_service' in locals():
            db_service.close()

if __name__ == '__main__':
    clean_database()
