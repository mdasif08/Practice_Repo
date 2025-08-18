#!/usr/bin/env python3
"""
Script to add test commit data to the database for frontend testing.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.database_service import DatabaseService
from datetime import datetime, timedelta
import random

def add_test_commits():
    """Add sample commit data to the database."""
    
    # Sample commit data
    test_commits = [
        {
            'commit_hash': 'a1b2c3d4e5f6789012345678901234567890abcd',
            'author': 'John Doe',
            'author_email': 'john.doe@example.com',
            'message': 'Add new feature: user authentication',
            'timestamp_commit': datetime.now() - timedelta(hours=2),
            'branch': 'main',
            'repository_name': 'test-repo',
            'files_changed': ['src/auth.py', 'tests/test_auth.py'],
            'lines_added': 45,
            'lines_deleted': 12
        },
        {
            'commit_hash': 'b2c3d4e5f6789012345678901234567890abcde1',
            'author': 'Jane Smith',
            'author_email': 'jane.smith@example.com',
            'message': 'Fix bug in data processing module',
            'timestamp_commit': datetime.now() - timedelta(hours=4),
            'branch': 'develop',
            'repository_name': 'test-repo',
            'files_changed': ['src/processor.py'],
            'lines_added': 8,
            'lines_deleted': 3
        },
        {
            'commit_hash': 'c3d4e5f6789012345678901234567890abcde12',
            'author': 'John Doe',
            'author_email': 'john.doe@example.com',
            'message': 'Update documentation and README',
            'timestamp_commit': datetime.now() - timedelta(hours=6),
            'branch': 'main',
            'repository_name': 'test-repo',
            'files_changed': ['README.md', 'docs/api.md'],
            'lines_added': 23,
            'lines_deleted': 5
        },
        {
            'commit_hash': 'd4e5f6789012345678901234567890abcde123',
            'author': 'Mike Johnson',
            'author_email': 'mike.johnson@example.com',
            'message': 'Implement caching mechanism',
            'timestamp_commit': datetime.now() - timedelta(hours=8),
            'branch': 'feature/caching',
            'repository_name': 'test-repo',
            'files_changed': ['src/cache.py', 'src/config.py'],
            'lines_added': 67,
            'lines_deleted': 0
        },
        {
            'commit_hash': 'e5f6789012345678901234567890abcde1234',
            'author': 'Jane Smith',
            'author_email': 'jane.smith@example.com',
            'message': 'Add unit tests for new features',
            'timestamp_commit': datetime.now() - timedelta(hours=10),
            'branch': 'develop',
            'repository_name': 'test-repo',
            'files_changed': ['tests/test_cache.py', 'tests/test_config.py'],
            'lines_added': 89,
            'lines_deleted': 0
        }
    ]
    
    try:
        # Initialize database service
        db_service = DatabaseService()
        
        print("Adding test commits to database...")
        
        for i, commit_data in enumerate(test_commits, 1):
            commit_id = db_service.save_commit(commit_data)
            print(f"Added commit {i}: {commit_data['message'][:50]}... (ID: {commit_id})")
        
        # Get statistics
        stats = db_service.get_statistics()
        print(f"\nDatabase statistics:")
        print(f"Total commits: {stats['total_commits']}")
        print(f"Unique authors: {stats['unique_authors']}")
        
        print("\n✅ Test data added successfully!")
        
    except Exception as e:
        print(f"❌ Error adding test data: {str(e)}")
        sys.exit(1)
    finally:
        if 'db_service' in locals():
            db_service.close()

if __name__ == '__main__':
    add_test_commits()
