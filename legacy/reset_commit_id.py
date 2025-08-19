#!/usr/bin/env python3
"""
Script to reset the commit ID from 6 to 1.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.database_service import DatabaseService

def reset_commit_id():
    """Reset the commit ID from 6 to 1."""
    
    try:
        # Initialize database service
        db_service = DatabaseService()
        print("✅ Connected to PostgreSQL database")
        
        # Get current commit
        commits = db_service.get_recent_commits(limit=10)
        if not commits:
            print("❌ No commits found in database")
            return
        
        current_commit = commits[0]
        print(f"📋 Current commit:")
        print(f"   ID: {current_commit['id']}")
        print(f"   Author: {current_commit['author']}")
        print(f"   Message: {current_commit['message']}")
        print(f"   Hash: {current_commit['commit_hash']}")
        
        if current_commit['id'] == 1:
            print("✅ Commit ID is already 1, no changes needed!")
            return
        
        print(f"\n🔄 Resetting commit ID from {current_commit['id']} to 1...")
        
        # Step 1: Delete the current commit
        with db_service.conn.cursor() as cursor:
            cursor.execute("DELETE FROM commits WHERE id = %s", (current_commit['id'],))
            print(f"🗑️ Deleted commit with ID {current_commit['id']}")
        
        # Step 2: Reset the sequence to start from 1
        with db_service.conn.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE commits_id_seq RESTART WITH 1")
            print("🔄 Reset sequence to start from 1")
        
        # Step 3: Re-insert the commit (it will get ID 1)
        commit_data = {
            'commit_hash': current_commit['commit_hash'],
            'author': current_commit['author'],
            'author_email': current_commit.get('author_email', ''),
            'message': current_commit['message'],
            'timestamp_commit': current_commit['timestamp_commit'],
            'branch': current_commit.get('branch', 'main'),
            'repository_name': current_commit.get('repository_name', ''),
            'files_changed': current_commit.get('changed_files', []),
            'lines_added': current_commit.get('lines_added', 0),
            'lines_deleted': current_commit.get('lines_deleted', 0)
        }
        
        new_id = db_service.save_commit(commit_data)
        print(f"✅ Re-inserted commit with new ID: {new_id}")
        
        # Commit the changes
        db_service.conn.commit()
        
        # Verify the change
        final_commits = db_service.get_recent_commits(limit=10)
        if final_commits:
            final_commit = final_commits[0]
            print(f"\n🎉 Success! Commit ID is now: {final_commit['id']}")
            print(f"📋 Final commit details:")
            print(f"   ID: {final_commit['id']}")
            print(f"   Author: {final_commit['author']}")
            print(f"   Message: {final_commit['message']}")
            print(f"   Hash: {final_commit['commit_hash']}")
        else:
            print("❌ Error: No commits found after reset")
        
        print("\n✅ Commit ID successfully reset from 6 to 1!")
        print("🖱️ Now click 'Track Now' in your frontend to see the updated commit!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    finally:
        if 'db_service' in locals():
            db_service.close()

if __name__ == '__main__':
    reset_commit_id()
