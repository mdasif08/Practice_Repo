#!/usr/bin/env python3
"""
Environment Setup Script
Helps users configure their environment variables for the CraftNudge system.
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with user input."""
    
    print("🔧 CraftNudge Environment Setup")
    print("=" * 40)
    print("This script will help you create a .env file with your configuration.")
    print("Your tokens and passwords will be stored securely and won't be committed to Git.\n")
    
    # Check if .env already exists
    env_path = Path('.env')
    if env_path.exists():
        print("⚠️ .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Setup cancelled.")
            return
    
    # Get user input
    print("\n📋 Database Configuration:")
    db_host = input("Database Host (default: localhost): ").strip() or "localhost"
    db_port = input("Database Port (default: 5432): ").strip() or "5432"
    db_name = input("Database Name (default: newDB): ").strip() or "newDB"
    db_user = input("Database User (default: postgres): ").strip() or "postgres"
    db_password = input("Database Password (default: root): ").strip() or "root"
    
    print("\n🔑 GitHub Configuration:")
    github_token = input("GitHub Personal Access Token: ").strip()
    if not github_token:
        print("⚠️ Warning: No GitHub token provided. Some features may not work.")
    
    webhook_secret = input("GitHub Webhook Secret (optional): ").strip() or ""
    
    print("\n🤖 Ollama Configuration:")
    ollama_url = input("Ollama Base URL (default: http://localhost:11434): ").strip() or "http://localhost:11434"
    code_llama_model = input("Code Llama Model (default: codellama:7b): ").strip() or "codellama:7b"
    ollama_model = input("Ollama Model (default: llama2:7b): ").strip() or "llama2:7b"
    
    print("\n⚙️ Server Configuration:")
    webhook_host = input("Webhook Host (default: 0.0.0.0): ").strip() or "0.0.0.0"
    webhook_port = input("Webhook Port (default: 5000): ").strip() or "5000"
    check_interval = input("Check Interval in seconds (default: 30): ").strip() or "30"
    
    # Create .env content
    env_content = f"""# Database Configuration
DB_HOST={db_host}
DB_PORT={db_port}
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}

# GitHub Configuration
GITHUB_TOKEN={github_token}
GITHUB_WEBHOOK_SECRET={webhook_secret}

# Ollama Configuration
OLLAMA_BASE_URL={ollama_url}
CODE_LLAMA_MODEL={code_llama_model}
OLLAMA_MODEL={ollama_model}

# Webhook Server Configuration
WEBHOOK_HOST={webhook_host}
WEBHOOK_PORT={webhook_port}

# Monitor Configuration
CHECK_INTERVAL={check_interval}
ENABLE_AGENTS=true
ENABLE_WEBHOOKS=true
"""
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    # Create frontend .env
    frontend_env_content = f"""REACT_APP_GITHUB_TOKEN={github_token}
"""
    
    frontend_env_path = Path('frontend/.env')
    frontend_env_path.parent.mkdir(exist_ok=True)
    with open(frontend_env_path, 'w') as f:
        f.write(frontend_env_content)
    
    print("\n✅ Environment files created successfully!")
    print("📁 .env (backend configuration)")
    print("📁 frontend/.env (frontend configuration)")
    print("\n🔒 These files are automatically ignored by Git for security.")
    print("🚀 You can now run the system without hardcoded tokens!")

def validate_env():
    """Validate the current .env configuration."""
    
    print("🔍 Validating Environment Configuration")
    print("=" * 40)
    
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Run 'python setup_env.py' to create it.")
        return False
    
    # Load and validate
    try:
        from config.env_manager import env_manager
        env_manager.print_config()
        
        if env_manager.validate_config():
            print("\n✅ Configuration is valid!")
            return True
        else:
            print("\n⚠️ Configuration has issues. Please check your .env file.")
            return False
            
    except Exception as e:
        print(f"❌ Error validating configuration: {str(e)}")
        return False

def main():
    """Main function."""
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        validate_env()
    else:
        create_env_file()

if __name__ == '__main__':
    main()
