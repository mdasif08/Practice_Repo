#!/usr/bin/env python3
"""
CraftNudge Continuous Monitor Setup Script.
Complete setup for the continuous monitoring system with PostgreSQL, webhooks, and AI agents.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def print_banner():
    """Print setup banner."""
    print("=" * 80)
    print("🚀 CraftNudge Continuous Monitor Setup")
    print("=" * 80)
    print("This script will set up the complete continuous monitoring system")
    print("including PostgreSQL database, webhook server, and AI agent orchestration.")
    print("=" * 80)

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_git():
    """Check if Git is installed."""
    print("📦 Checking Git installation...")
    
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Git is installed: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git is not installed or not in PATH")
        return False

def check_postgresql():
    """Check PostgreSQL connection."""
    print("🗄️  Checking PostgreSQL connection...")
    
    try:
        # Try to import psycopg2
        import psycopg2
        
        # Try to connect to database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="newDB",
            user="postgres",
            password="root"
        )
        conn.close()
        print("✅ PostgreSQL connection successful")
        return True
    except ImportError:
        print("❌ psycopg2 is not installed")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {str(e)}")
        print("Please ensure PostgreSQL is running and accessible with:")
        print("  - Host: localhost")
        print("  - Port: 5432")
        print("  - Database: newDB")
        print("  - User: postgres")
        print("  - Password: root")
        return False

def check_ollama():
    """Check if Ollama is running."""
    print("🤖 Checking Ollama status...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running with {len(models)} models")
            return True
        else:
            print("❌ Ollama is not responding correctly")
            return False
    except Exception:
        print("❌ Ollama is not running")
        print("Please start Ollama with: ollama serve")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    
    try:
        # Try requirements.txt first
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                              capture_output=True, text=True, check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e.stderr}")
        
        # Try requirements-basic.txt as fallback
        try:
            print("🔄 Trying basic requirements...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-basic.txt'],
                                  capture_output=True, text=True, check=True)
            print("✅ Basic dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"❌ Failed to install basic dependencies: {e2.stderr}")
            return False

def initialize_database():
    """Initialize the PostgreSQL database."""
    print("🗄️  Initializing database...")
    
    try:
        from services.database_service import DatabaseService
        
        db = DatabaseService()
        stats = db.get_statistics()
        db.close()
        
        print(f"✅ Database initialized successfully")
        print(f"   - Total commits: {stats.get('total_commits', 0)}")
        print(f"   - Unique authors: {stats.get('unique_authors', 0)}")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

def test_services():
    """Test all services."""
    print("🧪 Testing services...")
    
    try:
        # Test database service
        from services.database_service import DatabaseService
        db = DatabaseService()
        db.close()
        print("✅ Database service: OK")
        
        # Test webhook handler
        from services.github_webhook_handler import GitHubWebhookHandler
        webhook_handler = GitHubWebhookHandler(database_service=db)
        webhook_handler.close()
        print("✅ Webhook handler: OK")
        
        # Test agent orchestrator
        from services.agent_orchestrator import AgentOrchestrator
        agent_orchestrator = AgentOrchestrator(database_service=db)
        agent_orchestrator.close()
        print("✅ Agent orchestrator: OK")
        
        # Test continuous monitor
        from services.continuous_monitor import ContinuousMonitor
        monitor = ContinuousMonitor()
        health = monitor.check_system_health()
        monitor.close()
        print("✅ Continuous monitor: OK")
        
        return True
    except Exception as e:
        print(f"❌ Service test failed: {str(e)}")
        return False

def create_config_files():
    """Create configuration files."""
    print("⚙️  Creating configuration files...")
    
    try:
        # Create .env file
        env_content = """# CraftNudge Continuous Monitor Configuration

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=newDB
DB_USER=postgres
DB_PASSWORD=root

# GitHub Webhook Configuration
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
CODE_LLAMA_MODEL=codellama:7b
OLLAMA_MODEL=llama2:7b

# Monitor Configuration
CHECK_INTERVAL=30
ENABLE_AGENTS=true
ENABLE_WEBHOOKS=true

# Webhook Server Configuration
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5000
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        # Create systemd service file
        service_content = """[Unit]
Description=CraftNudge Continuous Monitor
After=network.target postgresql.service

[Service]
Type=simple
User=postgres
WorkingDirectory=/path/to/craftnudge
Environment=PATH=/path/to/craftnudge/venv/bin
ExecStart=/path/to/craftnudge/venv/bin/python -m services.continuous_monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        with open('craftnudge-monitor.service', 'w') as f:
            f.write(service_content)
        
        print("✅ Configuration files created:")
        print("   - .env (environment variables)")
        print("   - craftnudge-monitor.service (systemd service)")
        return True
    except Exception as e:
        print(f"❌ Failed to create config files: {str(e)}")
        return False

def create_startup_scripts():
    """Create startup scripts."""
    print("📜 Creating startup scripts...")
    
    try:
        # Create start script
        start_script = """#!/bin/bash
# CraftNudge Continuous Monitor Startup Script

echo "Starting CraftNudge Continuous Monitor..."

# Start webhook server in background
python webhook_server.py --host 0.0.0.0 --port 5000 &
WEBHOOK_PID=$!

# Start continuous monitor
python -m services.continuous_monitor --interval 30

# Cleanup on exit
kill $WEBHOOK_PID
"""
        
        with open('start_monitor.sh', 'w') as f:
            f.write(start_script)
        
        # Make executable
        os.chmod('start_monitor.sh', 0o755)
        
        # Create stop script
        stop_script = """#!/bin/bash
# CraftNudge Continuous Monitor Stop Script

echo "Stopping CraftNudge Continuous Monitor..."

# Stop webhook server
pkill -f webhook_server.py

# Stop continuous monitor
pkill -f continuous_monitor

echo "Monitor stopped"
"""
        
        with open('stop_monitor.sh', 'w') as f:
            f.write(stop_script)
        
        # Make executable
        os.chmod('stop_monitor.sh', 0o755)
        
        print("✅ Startup scripts created:")
        print("   - start_monitor.sh")
        print("   - stop_monitor.sh")
        return True
    except Exception as e:
        print(f"❌ Failed to create startup scripts: {str(e)}")
        return False

def show_next_steps():
    """Show next steps for the user."""
    print("\n" + "=" * 80)
    print("🎉 Setup completed successfully!")
    print("=" * 80)
    print("\nNext steps:")
    print("\n1. 🔧 Configure GitHub Webhook:")
    print("   - Go to your GitHub repository")
    print("   - Settings > Webhooks > Add webhook")
    print("   - Payload URL: http://your-server:5000/webhook/github")
    print("   - Content type: application/json")
    print("   - Events: Just the push event")
    print("   - Secret: (use the one in .env file)")
    
    print("\n2. 🚀 Start the monitoring system:")
    print("   Option A - Using scripts:")
    print("   ./start_monitor.sh")
    print("   ")
    print("   Option B - Using CLI:")
    print("   python cli/manage_monitor.py start --daemon")
    print("   python webhook_server.py --host 0.0.0.0 --port 5000")
    
    print("\n3. 📊 Monitor the system:")
    print("   python cli/manage_monitor.py status")
    print("   python cli/manage_monitor.py health")
    
    print("\n4. 📝 View recent commits:")
    print("   python cli/manage_monitor.py recent-commits")
    
    print("\n5. 🔍 Check webhook server:")
    print("   curl http://localhost:5000/health")
    
    print("\n📚 Documentation:")
    print("   - README.md: Basic usage")
    print("   - cli/manage_monitor.py --help: CLI commands")
    print("   - webhook_server.py --help: Webhook server options")
    
    print("\n🆘 Troubleshooting:")
    print("   - Check logs: continuous_monitor.log")
    print("   - Database issues: Verify PostgreSQL connection")
    print("   - Ollama issues: Ensure ollama serve is running")
    print("   - Webhook issues: Check firewall and port accessibility")

def main():
    """Main setup function."""
    print_banner()
    
    # Check prerequisites
    checks = [
        ("Python Version", check_python_version),
        ("Git Installation", check_git),
        ("PostgreSQL Connection", check_postgresql),
        ("Ollama Status", check_ollama),
    ]
    
    failed_checks = []
    for check_name, check_func in checks:
        if not check_func():
            failed_checks.append(check_name)
    
    if failed_checks:
        print(f"\n❌ Setup cannot continue. Failed checks: {', '.join(failed_checks)}")
        print("Please fix the issues above and run the setup again.")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return False
    
    # Initialize database
    if not initialize_database():
        print("\n❌ Failed to initialize database")
        return False
    
    # Test services
    if not test_services():
        print("\n❌ Failed to test services")
        return False
    
    # Create configuration files
    if not create_config_files():
        print("\n❌ Failed to create configuration files")
        return False
    
    # Create startup scripts
    if not create_startup_scripts():
        print("\n❌ Failed to create startup scripts")
        return False
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
