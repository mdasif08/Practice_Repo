#!/usr/bin/env python3
"""
Complete System Test - CraftNudge Microservice Architecture
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_api_gateway_health():
    """Test API Gateway health check."""
    print_header("Testing API Gateway Health")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success("API Gateway is healthy!")
            print_info(f"Service: {data['service']}")
            print_info(f"Timestamp: {data['timestamp']}")
            print_info("Connected Services:")
            for service, url in data['services'].items():
                print(f"  - {service}: {url}")
            return True
        else:
            print_error(f"API Gateway health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"API Gateway health check error: {str(e)}")
        return False

def test_github_connection():
    """Test GitHub API connection."""
    print_header("Testing GitHub API Connection")
    
    try:
        response = requests.get(f"{API_BASE_URL}/github/test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('demo_mode'):
                print_success("GitHub service is running in demo mode")
                print_info(data.get('message', 'Demo mode active'))
            elif data.get('authenticated'):
                print_success("GitHub API is authenticated!")
                print_info(f"Username: {data.get('username')}")
                print_info(f"Rate limit remaining: {data.get('rate_limit_remaining')}")
            else:
                print_error(f"GitHub API error: {data.get('error')}")
            return True
        else:
            print_error(f"GitHub test failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"GitHub test error: {str(e)}")
        return False

def test_track_commits():
    """Test commit tracking functionality."""
    print_header("Testing Commit Tracking")
    
    test_data = {
        "owner": "demo",
        "repo": "test-repo",
        "max_commits": 3
    }
    
    try:
        print_info("Sending track-commits request...")
        response = requests.post(
            f"{API_BASE_URL}/track-commits",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Commit tracking successful!")
            print_info(f"Repository: {data['repository']}")
            print_info(f"Commits fetched: {data['commits_fetched']}")
            print_info(f"Commits stored: {data['commits_stored']}")
            print_info(f"Message: {data['message']}")
            
            # Display commit details
            if data.get('commits'):
                print_info(f"\n📝 Commit Details:")
                for i, commit in enumerate(data['commits'], 1):
                    print(f"  {i}. {commit['message']}")
                    print(f"     Author: {commit['author']}")
                    print(f"     Files changed: {len(commit.get('changed_files', []))}")
                    print(f"     Timestamp: {commit['timestamp']}")
                    print()
            
            return True
        else:
            print_error(f"Commit tracking failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Commit tracking error: {str(e)}")
        return False

def test_get_commits():
    """Test retrieving commits from database."""
    print_header("Testing Commit Retrieval")
    
    try:
        response = requests.get(f"{API_BASE_URL}/commits?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success("Commits retrieved successfully!")
            print_info(f"Total commits: {data.get('count', 0)}")
            
            if data.get('commits'):
                print_info(f"\n📊 Recent Commits:")
                for i, commit in enumerate(data['commits'][:3], 1):
                    print(f"  {i}. {commit['message'][:50]}...")
                    print(f"     Author: {commit['author']}")
                    print(f"     Files: {len(commit.get('changed_files', []))}")
            
            return True
        else:
            print_error(f"Commit retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Commit retrieval error: {str(e)}")
        return False

def test_statistics():
    """Test statistics endpoint."""
    print_header("Testing Statistics")
    
    try:
        response = requests.get(f"{API_BASE_URL}/commits/statistics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            print_success("Statistics retrieved successfully!")
            print_info(f"Total commits: {stats.get('total_commits', 0)}")
            print_info(f"Total files changed: {stats.get('total_files_changed', 0)}")
            print_info(f"Unique authors: {stats.get('unique_authors', 0)}")
            print_info(f"Recent commits (24h): {stats.get('recent_commits', 0)}")
            return True
        else:
            print_error(f"Statistics failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Statistics error: {str(e)}")
        return False

def test_frontend():
    """Test frontend accessibility."""
    print_header("Testing Frontend")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print_success("Frontend is accessible!")
            print_info(f"URL: {FRONTEND_URL}")
            print_info("You can now open this URL in your browser to use the UI")
            return True
        else:
            print_error(f"Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Frontend test error: {str(e)}")
        print_info("Make sure the frontend is running with: cd frontend && npm run dev")
        return False

def main():
    """Run all tests."""
    print_header("CraftNudge Microservice System - Complete Test")
    print_info(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("API Gateway Health", test_api_gateway_health),
        ("GitHub Connection", test_github_connection),
        ("Commit Tracking", test_track_commits),
        ("Commit Retrieval", test_get_commits),
        ("Statistics", test_statistics),
        ("Frontend", test_frontend)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print_error(f"Test '{test_name}' failed with exception: {str(e)}")
    
    print_header("Test Results Summary")
    print_info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print_success("🎉 ALL TESTS PASSED! Your CraftNudge system is fully operational!")
        print_info("\n🌐 Next Steps:")
        print_info("1. Open your browser and go to: http://localhost:5173")
        print_info("2. Enter a repository owner and name")
        print_info("3. Click 'Track Commits' to test the complete workflow")
        print_info("4. View statistics and commit details in the UI")
    else:
        print_error(f"❌ {total - passed} test(s) failed. Please check the errors above.")
    
    print_info("\n📚 System Architecture:")
    print_info("- Frontend: React + Vite (Port 5173)")
    print_info("- API Gateway: Flask (Port 8000)")
    print_info("- Commit Tracker: Flask (Port 8001)")
    print_info("- Database: PostgreSQL (Port 5432)")
    print_info("- Containerization: Docker + Docker Compose")

if __name__ == "__main__":
    main()
