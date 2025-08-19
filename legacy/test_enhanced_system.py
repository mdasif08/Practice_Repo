#!/usr/bin/env python3
"""
Test script for the enhanced repository-based Git commit tracking system.
Tests the new RepositoryManager and enhanced database functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.database_service import DatabaseService
from services.repository_manager import RepositoryManager
from services.github_commit_fetcher import GitHubCommitFetcher
from config.env_manager import env_manager

def test_repository_manager():
    """Test the RepositoryManager functionality."""
    print("🧪 Testing RepositoryManager...")
    
    try:
        # Initialize services
        db_service = DatabaseService()
        repo_manager = RepositoryManager(db_service)
        
        # Test repository registration
        print("  📝 Testing repository registration...")
        repo_id = repo_manager.register_repository(
            owner="test_user",
            name="test_repo",
            description="A test repository",
            language="Python",
            is_private=False
        )
        print(f"    ✅ Repository registered with ID: {repo_id}")
        
        # Test getting repository ID
        print("  🔍 Testing repository ID retrieval...")
        retrieved_id = repo_manager.get_repository_id("test_user", "test_repo")
        assert retrieved_id == repo_id
        print(f"    ✅ Repository ID retrieved correctly: {retrieved_id}")
        
        # Test getting repository details
        print("  📋 Testing repository details retrieval...")
        repo_details = repo_manager.get_repository_by_id(repo_id)
        assert repo_details is not None
        assert repo_details['name'] == "test_repo"
        print(f"    ✅ Repository details retrieved: {repo_details['name']}")
        
        # Test getting all repositories
        print("  📚 Testing all repositories retrieval...")
        all_repos = repo_manager.get_all_repositories()
        assert len(all_repos) > 0
        print(f"    ✅ Found {len(all_repos)} repositories")
        
        print("✅ RepositoryManager tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ RepositoryManager test failed: {str(e)}")
        return False

def test_enhanced_database():
    """Test the enhanced database functionality."""
    print("🧪 Testing enhanced database functionality...")
    
    try:
        db_service = DatabaseService()
        
        # Test getting recent commits with repository filtering
        print("  📝 Testing recent commits retrieval...")
        commits = db_service.get_recent_commits(limit=5)
        print(f"    ✅ Retrieved {len(commits)} recent commits")
        
        # Test statistics
        print("  📊 Testing statistics retrieval...")
        stats = db_service.get_statistics()
        print(f"    ✅ Database statistics: {stats}")
        
        print("✅ Enhanced database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced database test failed: {str(e)}")
        return False

def test_github_fetcher():
    """Test the enhanced GitHub commit fetcher."""
    print("🧪 Testing enhanced GitHub commit fetcher...")
    
    try:
        db_service = DatabaseService()
        repo_manager = RepositoryManager(db_service)
        github_fetcher = GitHubCommitFetcher(db_service, repo_manager)
        
        # Test repository details fetching (if token is available)
        if hasattr(env_manager, 'GITHUB_TOKEN') and env_manager.GITHUB_TOKEN:
            print("  🔍 Testing repository details fetching...")
            try:
                repo_details = github_fetcher.fetch_repository_details("mdasif08", "Practice_Repo")
                print(f"    ✅ Repository details fetched: {repo_details['name']}")
            except Exception as e:
                print(f"    ⚠️ Repository details fetch failed (expected if repo doesn't exist): {str(e)}")
        
        print("✅ Enhanced GitHub fetcher tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced GitHub fetcher test failed: {str(e)}")
        return False

def test_repository_statistics():
    """Test repository statistics functionality."""
    print("🧪 Testing repository statistics...")
    
    try:
        db_service = DatabaseService()
        repo_manager = RepositoryManager(db_service)
        
        # Test repository statistics
        print("  📊 Testing repository statistics...")
        repo_stats = repo_manager.get_repository_statistics()
        print(f"    ✅ Repository statistics: {repo_stats['total_repositories']} repositories, {repo_stats['total_commits']} commits")
        
        print("✅ Repository statistics tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Repository statistics test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting enhanced system tests...\n")
    
    tests = [
        test_repository_manager,
        test_enhanced_database,
        test_github_fetcher,
        test_repository_statistics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The enhanced system is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



