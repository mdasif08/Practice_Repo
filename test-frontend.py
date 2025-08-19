#!/usr/bin/env python3
"""
Frontend Testing Script for CraftNudge Microservice Architecture
"""

import requests
import time
import sys
from pathlib import Path

def test_frontend():
    """Test if the frontend is running and accessible."""
    
    print("🧪 Testing Frontend Application")
    print("=" * 40)
    
    # Test 1: Check if frontend server is running
    print("1. Testing frontend server...")
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend server is running on port 5173")
        else:
            print(f"   ❌ Frontend server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Frontend server is not running on port 5173")
        print("   💡 Start the frontend with: cd frontend && npm run dev")
        return False
    except Exception as e:
        print(f"   ❌ Error testing frontend: {str(e)}")
        return False
    
    # Test 2: Check if React app is loading
    print("2. Testing React application...")
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        content = response.text
        
        if "React App Running" in content or "CraftNudge" in content:
            print("   ✅ React application is loading")
        elif "root" in content and "main.jsx" in content:
            print("   ✅ React application structure detected")
        else:
            print("   ⚠️  React application may not be rendering properly")
            print("   💡 Check browser console for JavaScript errors")
        
    except Exception as e:
        print(f"   ❌ Error testing React app: {str(e)}")
        return False
    
    # Test 3: Check API gateway
    print("3. Testing API gateway...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API gateway is running on port 8000")
        else:
            print(f"   ❌ API gateway returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ API gateway is not running on port 8000")
        print("   💡 Start microservices with: docker-compose up -d")
    except Exception as e:
        print(f"   ❌ Error testing API gateway: {str(e)}")
    
    print("\n🎯 Next Steps:")
    print("1. Open your browser and go to: http://localhost:5173")
    print("2. You should see a loading spinner, then the CraftNudge interface")
    print("3. If you see a white page, check the browser console (F12) for errors")
    print("4. Configure GitHub token: python setup-github-token.py")
    
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    
    print("📦 Checking Dependencies")
    print("=" * 25)
    
    # Check if frontend directory exists
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if package.json exists
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json not found in frontend directory")
        return False
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("⚠️  node_modules not found - run 'npm install' in frontend directory")
        return False
    
    print("✅ Frontend dependencies look good")
    return True

if __name__ == "__main__":
    print("🔧 CraftNudge Frontend Test")
    print("=" * 30)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependencies check failed")
        sys.exit(1)
    
    # Test frontend
    if test_frontend():
        print("\n🎉 Frontend test completed successfully!")
    else:
        print("\n❌ Frontend test failed")
        sys.exit(1)
