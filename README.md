# CraftNudge - Git Commit Logger with Continuous Monitoring

A comprehensive Git commit tracking and analysis system that automatically monitors your repositories, stores commit data in PostgreSQL, and provides AI-powered insights using Code Llama and Ollama.

## 🚀 Features

### Core Functionality
- **Git Commit Tracking**: Automatically logs every Git commit with metadata
- **PostgreSQL Storage**: Robust database storage for commit history and analysis
- **GitHub Webhook Integration**: Real-time commit detection via GitHub webhooks
- **AI-Powered Analysis**: Code quality and commit pattern analysis using Code Llama and Ollama
- **Continuous Monitoring**: Background service that processes commits automatically

### AI Agent Integration
- **Code Llama**: Analyzes code changes for quality, security, and best practices
- **Ollama**: Provides insights on commit patterns and development habits
- **Automated Processing**: Agents run automatically on new commits
- **Configurable Models**: Support for different AI models and configurations

### Monitoring & Management
- **Webhook Server**: Flask-based server for handling GitHub webhooks
- **Continuous Monitor**: Background service for automatic processing
- **CLI Management**: Comprehensive command-line interface for system management
- **Health Monitoring**: Real-time system health and status checking
- **Statistics & Analytics**: Detailed metrics and reporting

## 📋 Prerequisites

### Required Software
- **Python 3.8+**: Core runtime environment
- **PostgreSQL**: Database server (pgAdmin for management)
- **Git**: Version control system
- **Ollama**: Local AI model server

### Database Configuration
- **Database Name**: `newDB`
- **Username**: `postgres`
- **Password**: `root`
- **Host**: `localhost`
- **Port**: `5432`

### AI Models
- **Code Llama**: `codellama:7b` (for code analysis)
- **Ollama**: `llama2:7b` (for commit analysis)

## 🛠️ Installation

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd MicroService

# Run the comprehensive setup script
python setup_continuous_monitor.py
```

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# For Python 3.13+ compatibility issues, use:
pip install -r requirements-basic.txt

# Initialize the system
python cli/manage_monitor.py setup
```

## 🚀 Getting Started

### 1. Start the Monitoring System

**Option A: Using startup scripts**
```bash
./start_monitor.sh
```

**Option B: Using CLI**
```bash
# Start continuous monitor as daemon
python cli/manage_monitor.py start --daemon

# Start webhook server
python webhook_server.py --host 0.0.0.0 --port 5000
```

### 2. Configure GitHub Webhook

1. Go to your GitHub repository
2. Navigate to **Settings > Webhooks**
3. Click **Add webhook**
4. Configure:
   - **Payload URL**: `http://your-server:5000/webhook/github`
   - **Content type**: `application/json`
   - **Events**: Select "Just the push event"
   - **Secret**: Use the secret from your `.env` file

### 3. Verify System Status

```bash
# Check overall status
python cli/manage_monitor.py status

# Detailed health check
python cli/manage_monitor.py health

# View recent commits
python cli/manage_monitor.py recent-commits
```

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  Webhook Server  │───▶│  PostgreSQL DB  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Continuous       │    │ AI Agents       │
                       │ Monitor          │    │ (Code Llama &   │
                       │                  │    │  Ollama)        │
                       └──────────────────┘    └─────────────────┘
```

## 🎯 Usage Examples

### Basic Commit Tracking
```bash
# Track latest commit
python cli/track_commit.py

# Track all commits
python cli/track_commit.py --all

# Track specific range
python cli/track_commit.py --range HEAD~5..HEAD
```

### View Commit History
```bash
# View recent commits
python cli/view_commits.py

# Filter by author
python cli/view_commits.py --author "John Doe"

# Export as JSON
python cli/view_commits.py --json
```

### System Management
```bash
# Start monitoring
python cli/manage_monitor.py start

# Check status
python cli/manage_monitor.py status

# Run single cycle
python cli/manage_monitor.py run-once

# Stop monitoring
python cli/manage_monitor.py stop
```

### Webhook Server Management
```bash
# Start webhook server
python webhook_server.py --host 0.0.0.0 --port 5000

# Check webhook status
python cli/manage_monitor.py webhook-status

# Test webhook endpoint
curl http://localhost:5000/health
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with your configuration:

```env
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
```

### AI Model Configuration
The system automatically configures AI agents with optimized prompts:

- **Code Llama**: Focuses on code quality, security, and best practices
- **Ollama**: Analyzes commit patterns and development habits

## 📈 Monitoring & Analytics

### Database Statistics
```bash
# Get system statistics
python cli/manage_monitor.py health
```

The system tracks:
- Total commits processed
- Unique authors
- Agent interactions
- Webhook events
- System health metrics

### AI Analysis Results
Each commit is automatically analyzed for:
- **Code Quality**: Best practices, potential issues
- **Security**: Vulnerabilities, security concerns
- **Performance**: Optimization opportunities
- **Patterns**: Development habits and trends

## 🛠️ Troubleshooting

### Common Issues

**PostgreSQL Connection Failed**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Verify connection
psql -h localhost -U postgres -d newDB
```

**Ollama Not Running**
```bash
# Start Ollama
ollama serve

# Check available models
ollama list
```

**Webhook Server Issues**
```bash
# Check if port is accessible
netstat -tlnp | grep 5000

# Test webhook endpoint
curl http://localhost:5000/health
```

**Monitor Not Processing**
```bash
# Check logs
tail -f continuous_monitor.log

# Run manual cycle
python cli/manage_monitor.py run-once
```

### Log Files
- `continuous_monitor.log`: Main monitoring service logs
- `webhook_server.log`: Webhook server logs (if configured)

## 🔄 Continuous Integration

### GitHub Actions Integration
The system can be integrated with GitHub Actions for automated deployment:

```yaml
name: Deploy CraftNudge Monitor
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          # Your deployment script
```

### Docker Support
The system can be containerized for easy deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "webhook_server.py"]
```

## 📚 API Reference

### Webhook Server Endpoints

- `POST /webhook/github`: Handle GitHub webhook events
- `GET /webhook/status`: Get webhook processing statistics
- `GET /health`: Health check endpoint
- `POST /process/events`: Manually process unprocessed events
- `POST /pull/latest`: Manually pull latest commits

### CLI Commands

```bash
# Monitor management
python cli/manage_monitor.py start [--daemon] [--interval 30]
python cli/manage_monitor.py stop
python cli/manage_monitor.py status
python cli/manage_monitor.py health

# Webhook management
python cli/manage_monitor.py start-webhook-server
python cli/manage_monitor.py webhook-status

# Data viewing
python cli/manage_monitor.py recent-commits [--limit 10]
python cli/manage_monitor.py run-once
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Open an issue on GitHub
4. Check the documentation

---

**CraftNudge** - Transform your Git commits into actionable insights with AI-powered analysis and continuous monitoring.
