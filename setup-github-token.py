#!/usr/bin/env python3
"""
GitHub Token Setup Script for CraftNudge Microservice Architecture
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with GitHub token configuration."""
    
    print("🚀 CraftNudge GitHub Token Setup")
    print("=" * 50)
    
    # Check if .env already exists
    env_file = Path('.env')
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("❌ Setup cancelled.")
            return False
    
    # Get GitHub token from user
    print("\n📋 GitHub Token Configuration")
    print("-" * 30)
    print("To use real GitHub commits, you need a GitHub Personal Access Token.")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Select scopes: 'repo' and 'read:user'")
    print("4. Copy the generated token")
    print()
    
    github_token = input("Enter your GitHub Personal Access Token: ").strip()
    
    if not github_token:
        print("❌ No token provided. Setup cancelled.")
        return False
    
    # Create .env file content
    env_content = f"""# Microservice Architecture Configuration
# =====================================

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=newDB
DB_USER=postgres
DB_PASSWORD=root

# GitHub API Configuration
GITHUB_TOKEN={github_token}

# Service Ports
GATEWAY_PORT=8000
COMMIT_SERVICE_PORT=8001
REPO_SERVICE_PORT=8002
WEBHOOK_SERVICE_URL=8003
AI_SERVICE_PORT=8004

# Service URLs (for inter-service communication)
COMMIT_SERVICE_URL=http://localhost:8001
REPO_SERVICE_URL=http://localhost:8002
WEBHOOK_SERVICE_URL=http://localhost:8003
AI_SERVICE_URL=http://localhost:8004

# Logging
LOG_LEVEL=INFO

# GitHub Webhook Secret (for webhook validation)
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# AI Service Configuration (if using Ollama)
OLLAMA_BASE_URL=http://localhost:11434
CODE_LLAMA_MODEL=codellama:7b
OLLAMA_MODEL=llama2:7b
"""
    
    try:
        # Write .env file
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n✅ .env file created successfully!")
        print("🔧 Next steps:")
        print("1. Start your microservices: docker-compose up -d")
        print("2. Test GitHub connection: curl http://localhost:8000/github/test")
        print("3. Open frontend: http://localhost:5173")
        print("4. Enter a repository owner and name to fetch real commits!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {str(e)}")
        return False

def test_github_connection():
    """Test GitHub API connection."""
    print("\n🧪 Testing GitHub API Connection")
    print("-" * 35)
    
    try:
        import requests
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("❌ No GitHub token found in .env file")
            return False
        
        # Test GitHub API
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CraftNudge-Microservice/1.0'
        }
        
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub API connection successful!")
            print(f"👤 Authenticated as: {user_data.get('login')}")
            print(f"📊 Rate limit remaining: {response.headers.get('X-RateLimit-Remaining')}")
            return True
        else:
            print(f"❌ GitHub API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("🔧 CraftNudge Microservice GitHub Setup")
    print("=" * 45)
    
    # Check if .env exists
    if Path('.env').exists():
        print("📁 .env file found!")
        response = input("Do you want to test the existing configuration? (Y/n): ").lower()
        if response != 'n':
            test_github_connection()
    else:
        print("📁 No .env file found.")
        response = input("Do you want to create one? (Y/n): ").lower()
        if response != 'n':
            if create_env_file():
                test_github_connection()
    
    print("\n�� Setup complete!")
