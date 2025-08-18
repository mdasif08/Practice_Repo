#!/usr/bin/env python3
"""
Example usage of CraftNudge Git Commit Logger

This script demonstrates how to use the microservice components
to track Git commits programmatically.
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from services.commit_tracker import CommitTrackerService
from services.data_storage import DataStorageService
from utils.error_handler import display_success_message, display_info_message


def main():
    """Demonstrate the Git commit logger functionality."""
    
    print("🚀 CraftNudge Git Commit Logger - Example Usage")
    print("=" * 50)
    
    try:
        # Initialize services
        print("\n1. Initializing services...")
        tracker = CommitTrackerService()
        storage = DataStorageService()
        
        # Get repository information
        print("\n2. Getting repository information...")
        repo_info = tracker.get_repository_info()
        print(f"   Repository: {repo_info['repository_path']}")
        print(f"   Branch: {repo_info['active_branch']}")
        print(f"   Total commits: {repo_info['total_commits']}")
        print(f"   Repository status: {'Clean' if not repo_info['is_dirty'] else 'Dirty'}")
        
        # Get tracking summary
        print("\n3. Getting tracking summary...")
        summary = tracker.get_tracking_summary()
        tracking_status = summary['tracking_status']
        print(f"   Logged commits: {tracking_status['total_logged_commits']}")
        print(f"   Coverage: {tracking_status['coverage_percentage']}%")
        
        # Track latest commit
        print("\n4. Tracking latest commit...")
        entry_id = tracker.track_latest_commit()
        if entry_id:
            print(f"   ✅ Successfully tracked commit with ID: {entry_id[:8]}")
        else:
            print("   ℹ️  No new commits to track")
        
        # Get statistics
        print("\n5. Getting commit statistics...")
        stats = storage.get_statistics()
        if stats['total_commits'] > 0:
            print(f"   Total commits logged: {stats['total_commits']}")
            print(f"   Unique authors: {stats['unique_authors']}")
            print(f"   Average files per commit: {stats['average_files_per_commit']}")
            if stats['most_active_author']:
                author = stats['most_active_author']
                print(f"   Most active author: {author['name']} ({author['commits']} commits)")
        else:
            print("   No commits logged yet")
        
        # Search for commits
        print("\n6. Searching commits...")
        commits = storage.load_commits(limit=5)
        if commits:
            print(f"   Found {len(commits)} recent commits:")
            for i, commit in enumerate(commits, 1):
                print(f"   {i}. {commit.commit_hash[:8]} - {commit.message[:50]}...")
        else:
            print("   No commits found")
        
        print("\n✅ Example completed successfully!")
        print("\n💡 Try running the CLI tools:")
        print("   python cli/track_commit.py --summary")
        print("   python cli/view_commits.py --detailed")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure you're running this from within a Git repository.")


if __name__ == '__main__':
    main()
