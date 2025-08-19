# 🚀 Beginner-Friendly Microservices Project

A simple, easy-to-understand microservices architecture for Git commit tracking and analysis.

## 🎯 What This Project Does

This project tracks Git commits from GitHub repositories and provides AI-powered analysis. It's built using a **microservices architecture** - meaning each part of the system is a separate, focused service.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Commit Tracker │    │ Repo Manager    │    │ Webhook Handler │    │  AI Analyzer    │
│   (Port 8001)   │    │  (Port 8002)    │    │   (Port 8003)   │    │   (Port 8004)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         └───────────────────────┼───────────────────────┼───────────────────────┘
                                 │                       │
                    ┌─────────────────┐    ┌─────────────────┐
                    │   PostgreSQL    │    │     Ollama      │
                    │   (Port 5432)   │    │   (Port 11434)  │
                    └─────────────────┘    └─────────────────┘
```

## 🎯 Services Explained (Simple!)

### 1. **Commit Tracker** (Port 8001)
- **What it does**: Saves and retrieves commit information
- **Like**: A librarian who keeps track of all books (commits)

### 2. **Repository Manager** (Port 8002)
- **What it does**: Manages repository information and statistics
- **Like**: A manager who organizes different sections of the library

### 3. **Webhook Handler** (Port 8003)
- **What it does**: Receives notifications when code is pushed to GitHub
- **Like**: A receptionist who gets phone calls about new deliveries

### 4. **AI Analyzer** (Port 8004)
- **What it does**: Uses AI to analyze commits and code changes
- **Like**: A smart assistant who reads and reviews the books

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

```bash
# 1. Start all services
docker-compose up -d

# 2. Check if everything is running
docker-compose ps

# 3. View logs
docker-compose logs -f
```

### Option 2: Running Services Individually

```bash
# 1. Install dependencies for each service
cd services/commit-tracker && pip install -r requirements.txt
cd services/repo-manager && pip install -r requirements.txt
cd services/webhook-handler && pip install -r requirements.txt
cd services/ai-analyzer && pip install -r requirements.txt

# 2. Start each service (in separate terminals)
cd services/commit-tracker && python app.py
cd services/repo-manager && python app.py
cd services/webhook-handler && python app.py
cd services/ai-analyzer && python app.py
```

## 🔑 GitHub Token Setup (Required for Real Commits)

**Important**: To fetch real commits from GitHub (instead of demo data), you need to configure a GitHub Personal Access Token.

### Quick Setup (Recommended)

```bash
# Run the automated setup script
python setup-github-token.py
```

### Manual Setup

1. **Get a GitHub Token**:
   - Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
   - Click "Generate new token (classic)"
   - Select scopes: `repo` and `read:user`
   - Copy the generated token

2. **Create Environment File**:
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env and replace 'your_github_token_here' with your actual token
   GITHUB_TOKEN=ghp_your_actual_token_here
   ```

3. **Test Configuration**:
   ```bash
   # Test GitHub connection
   curl http://localhost:8000/github/test
   ```

### What Happens Without a Token?

- The system will show an error message asking for a GitHub token
- No demo/static data will be displayed
- You'll need to configure the token to see real commits

## 🧪 Testing the Services

### 1. Check Service Health
```bash
# Commit Tracker
curl http://localhost:8001/health

# Repository Manager
curl http://localhost:8002/health

# Webhook Handler
curl http://localhost:8003/health

# AI Analyzer
curl http://localhost:8004/health
```

### 2. Add a Test Commit
```bash
curl -X POST http://localhost:8001/commits \
  -H "Content-Type: application/json" \
  -d '{
    "commit_hash": "abc123",
    "author": "john_doe",
    "message": "Fix login bug",
    "repository_name": "my-app"
  }'
```

### 3. Get All Commits
```bash
curl http://localhost:8001/commits
```

### 4. Analyze a Commit with AI
```bash
curl http://localhost:8004/analyze/commit/abc123
```

## 📊 API Endpoints

### Commit Tracker (Port 8001)
- `GET /health` - Service health check
- `GET /commits` - Get all commits
- `GET /commits/{hash}` - Get specific commit
- `POST /commits` - Add new commit
- `GET /commits/statistics` - Get commit statistics

### Repository Manager (Port 8002)
- `GET /health` - Service health check
- `GET /repos` - Get all repositories
- `GET /repos/{name}` - Get specific repository
- `GET /repos/statistics` - Get repository statistics

### Webhook Handler (Port 8003)
- `GET /health` - Service health check
- `POST /webhook/github` - Handle GitHub webhooks
- `POST /fetch-commits` - Fetch commits from GitHub
- `GET /webhook/events` - Get webhook events

### AI Analyzer (Port 8004)
- `GET /health` - Service health check
- `GET /analyze/commit/{hash}` - Analyze commit with AI
- `POST /analyze/code` - Analyze code changes
- `GET /status` - Get AI service status

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=newDB
DB_USER=postgres
DB_PASSWORD=root

# GitHub
GITHUB_TOKEN=your_github_token_here

# AI Models
OLLAMA_BASE_URL=http://localhost:11434
CODE_LLAMA_MODEL=codellama:7b
OLLAMA_MODEL=llama2:7b

# Service Ports
COMMIT_SERVICE_PORT=8001
REPO_SERVICE_PORT=8002
WEBHOOK_SERVICE_PORT=8003
AI_SERVICE_PORT=8004
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild services
docker-compose build

# Check service status
docker-compose ps
```

## 📁 Project Structure

```
MicroService/
├── services/
│   ├── commit-tracker/          # Handles commits
│   │   ├── app.py              # Flask application
│   │   ├── requirements.txt    # Dependencies
│   │   └── README.md           # Service documentation
│   ├── repo-manager/           # Handles repositories
│   ├── webhook-handler/        # Handles GitHub webhooks
│   └── ai-analyzer/            # Handles AI analysis
├── shared/                     # Shared code
│   ├── database.py            # Database connection
│   └── config.py              # Configuration
├── docker-compose.yml         # Orchestrates all services
└── README.md                  # This file
```

## 🎓 Learning Benefits

### Why Microservices?
1. **Easy to Understand**: Each service has one job
2. **Easy to Debug**: Problems are isolated
3. **Easy to Scale**: Add more of what you need
4. **Easy to Deploy**: Update one service at a time

### What You'll Learn
- ✅ **Service Communication**: How services talk to each other
- ✅ **API Design**: How to design REST APIs
- ✅ **Database Design**: How to structure data
- ✅ **Containerization**: How to use Docker
- ✅ **Orchestration**: How to manage multiple services

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check if port is already in use
netstat -tulpn | grep :8001

# Check Docker logs
docker-compose logs commit-tracker
```

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres
```

### AI Service Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull required models
ollama pull codellama:7b
ollama pull llama2:7b
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Need Help?

- Check the service-specific README files in each service directory
- Look at the logs: `docker-compose logs -f`
- Test individual endpoints to isolate issues
- Make sure all required services are running

---

**Happy Coding! 🎉**
