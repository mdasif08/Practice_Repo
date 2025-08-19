# 🚀 Microservices Architecture - CraftNudge Git Commit Logger

Your project has been successfully transformed into a **true microservices architecture**! This document explains the new structure and how to use it.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │  Service Mesh   │
│   (React)       │◄──►│   (Port 8000)   │◄──►│  (Docker Net)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Commit Service │    │ Repository Svc  │    │  Webhook Svc    │
│   (Port 8001)   │    │   (Port 8002)   │    │   (Port 8003)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Service    │    │  Database Svc   │    │  Monitor Svc    │
│   (Port 8004)   │    │   (Port 8005)   │    │   (Port 8006)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 New Project Structure

```
MicroService/
├── services/
│   ├── commit-service/          # Git commit tracking
│   │   ├── app.py              # Service entry point
│   │   └── Dockerfile          # Service container
│   ├── repository-service/      # Repository management
│   │   ├── app.py
│   │   └── Dockerfile
│   ├── webhook-service/         # GitHub webhook handling
│   │   ├── app.py
│   │   └── Dockerfile
│   ├── ai-service/             # AI agent orchestration
│   │   ├── app.py
│   │   └── Dockerfile
│   ├── database-service/       # Database operations
│   │   ├── app.py
│   │   └── Dockerfile
│   ├── monitor-service/        # Continuous monitoring
│   │   ├── app.py
│   │   └── Dockerfile
│   └── api-gateway/            # Central API gateway
│       ├── app.py
│       └── Dockerfile
├── docker-compose.yml          # Service orchestration
├── start-microservices.sh      # Quick start script
├── MICROSERVICES_README.md     # This file
└── [existing files remain unchanged]
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- At least 4GB RAM available

### 1. Start All Services
```bash
# Option 1: Use the startup script
./start-microservices.sh

# Option 2: Manual start
docker-compose up -d
```

### 2. Check Service Health
```bash
# Check API Gateway
curl http://localhost:8000/health

# Check all services health
curl http://localhost:8000/api/health
```

### 3. Access Services
- **API Gateway**: http://localhost:8000
- **Commit Service**: http://localhost:8001
- **Repository Service**: http://localhost:8002
- **Webhook Service**: http://localhost:8003
- **AI Service**: http://localhost:8004
- **Database Service**: http://localhost:8005
- **Monitor Service**: http://localhost:8006

## 📋 Service Details

### API Gateway (Port 8000)
**Purpose**: Central routing and request handling
- Routes requests to appropriate services
- Handles cross-cutting concerns
- Provides unified API interface
- Health monitoring for all services

**Key Endpoints**:
- `GET /health` - Gateway health check
- `GET /api/health` - All services health check
- `GET /api/commits` - Get all commits
- `POST /api/repositories` - Register repository
- `POST /api/webhook/github` - GitHub webhook handler

### Commit Service (Port 8001)
**Purpose**: Git commit tracking and management
- Track new commits
- Retrieve commit information
- Commit statistics and analytics
- Commit history management

**Key Endpoints**:
- `GET /commits` - Get all commits
- `GET /commits/<hash>` - Get specific commit
- `POST /commits` - Track new commit
- `GET /commits/statistics` - Get commit statistics

### Repository Service (Port 8002)
**Purpose**: Repository management and operations
- Register new repositories
- Repository information management
- Repository-specific commit retrieval
- Repository statistics

**Key Endpoints**:
- `GET /repositories` - Get all repositories
- `POST /repositories` - Register repository
- `GET /repositories/<owner>/<name>` - Get specific repository
- `GET /repositories/<owner>/<name>/commits` - Get repository commits

### Webhook Service (Port 8003)
**Purpose**: GitHub webhook handling and event processing
- Process GitHub webhooks
- Event queue management
- Webhook event statistics
- Event processing status

**Key Endpoints**:
- `POST /webhook/github` - GitHub webhook handler
- `GET /webhook/events` - Get all webhook events
- `GET /webhook/events/unprocessed` - Get unprocessed events
- `GET /webhook/statistics` - Get webhook statistics

### AI Service (Port 8004)
**Purpose**: AI agent orchestration and analysis
- Code analysis using Code Llama
- Commit analysis using Ollama
- AI agent status monitoring
- Analysis result management

**Key Endpoints**:
- `GET /agents/status` - Get AI agents status
- `POST /agents/analyze/commit` - Analyze commit
- `POST /agents/analyze/code` - Analyze code changes
- `GET /agents/interactions` - Get agent interactions

### Database Service (Port 8005)
**Purpose**: Database operations and management
- Database health monitoring
- Database statistics
- Backup and restore operations
- Database maintenance tasks

**Key Endpoints**:
- `GET /database/statistics` - Get database statistics
- `GET /database/tables` - Get database tables
- `POST /database/backup` - Create database backup
- `POST /database/cleanup` - Clean up old data

### Monitor Service (Port 8006)
**Purpose**: Continuous monitoring and background tasks
- Start/stop monitoring
- Monitor status and statistics
- Background task management
- System health monitoring

**Key Endpoints**:
- `POST /monitor/start` - Start monitoring
- `POST /monitor/stop` - Stop monitoring
- `GET /monitor/status` - Get monitor status
- `POST /monitor/run-once` - Run single monitoring cycle

## 🔧 Configuration

### Environment Variables
Each service can be configured using environment variables:

```bash
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=newDB
DB_USER=postgres
DB_PASSWORD=root

# GitHub Configuration
GITHUB_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# AI Configuration
OLLAMA_BASE_URL=http://ollama:11434
CODE_LLAMA_MODEL=codellama:7b
OLLAMA_MODEL=llama2:7b

# Monitor Configuration
CHECK_INTERVAL=30
ENABLE_AGENTS=true
ENABLE_WEBHOOKS=true
```

## 🐳 Docker Commands

### Start Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d commit-service

# Start with logs
docker-compose up
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs commit-service

# Follow logs
docker-compose logs -f
```

### Rebuild Services
```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build commit-service

# Rebuild and start
docker-compose up --build
```

## 🔍 Monitoring and Debugging

### Health Checks
```bash
# Check API Gateway
curl http://localhost:8000/health

# Check all services
curl http://localhost:8000/api/health

# Check individual services
curl http://localhost:8001/health  # Commit Service
curl http://localhost:8002/health  # Repository Service
curl http://localhost:8003/health  # Webhook Service
curl http://localhost:8004/health  # AI Service
curl http://localhost:8005/health  # Database Service
curl http://localhost:8006/health  # Monitor Service
```

### Service Discovery
The API Gateway maintains a service registry:
```python
SERVICE_URLS = {
    'commit': 'http://localhost:8001',
    'repository': 'http://localhost:8002',
    'webhook': 'http://localhost:8003',
    'ai': 'http://localhost:8004',
    'database': 'http://localhost:8005',
    'monitor': 'http://localhost:8006'
}
```

## 🚀 Development

### Adding New Services
1. Create service directory in `services/`
2. Create `app.py` with Flask application
3. Create `Dockerfile`
4. Add service to `docker-compose.yml`
5. Update API Gateway routing

### Service Communication
Services communicate via HTTP REST APIs:
```python
# Example: Commit service calling repository service
import requests

response = requests.get('http://repository-service:8002/repositories')
repositories = response.json()
```

### Testing Services
```bash
# Test individual service
curl http://localhost:8001/commits

# Test through API Gateway
curl http://localhost:8000/api/commits
```

## 📊 Benefits of Microservices Architecture

### ✅ Advantages
- **Independent Deployment**: Each service can be deployed separately
- **Technology Diversity**: Different services can use different technologies
- **Scalability**: Scale individual services based on load
- **Fault Isolation**: Failure in one service doesn't affect others
- **Team Autonomy**: Different teams can work on different services
- **Better Testing**: Services can be tested in isolation

### ⚠️ Considerations
- **Complexity**: More moving parts to manage
- **Network Latency**: Inter-service communication overhead
- **Data Consistency**: Distributed data management challenges
- **Monitoring**: More complex monitoring and debugging

## 🔄 Migration from Monolithic

This microservices architecture maintains compatibility with the original monolithic codebase:

- **Same Business Logic**: All original functionality preserved
- **Same Database**: Uses the same PostgreSQL database
- **Same Configuration**: Compatible with existing `.env` files
- **Gradual Migration**: Can run alongside monolithic version

## 📈 Next Steps

### Phase 1: Current State ✅
- ✅ Service separation
- ✅ API Gateway implementation
- ✅ Docker containerization
- ✅ Basic service communication

### Phase 2: Future Enhancements
- 🔄 Database per service
- 🔄 Message queue integration
- 🔄 Service discovery (Consul)
- 🔄 Load balancing
- 🔄 Circuit breakers
- 🔄 Centralized logging (ELK)
- 🔄 Monitoring (Prometheus/Grafana)

## 🆘 Troubleshooting

### Common Issues

**Service Not Starting**
```bash
# Check logs
docker-compose logs <service-name>

# Check if port is in use
netstat -tlnp | grep <port>
```

**Database Connection Issues**
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Test connection
docker exec -it <postgres-container> psql -U postgres -d newDB
```

**Service Communication Issues**
```bash
# Check network connectivity
docker network ls
docker network inspect microservice_microservices-network
```

## 📞 Support

For issues and questions:
1. Check service logs: `docker-compose logs <service-name>`
2. Verify health endpoints: `curl http://localhost:<port>/health`
3. Check Docker network: `docker network inspect microservice_microservices-network`

## 🎯 What Changed

### Before (Monolithic)
- Single `webhook_server.py` file
- All services in one process
- Shared database connection
- Direct imports between services

### After (Microservices)
- Separate service directories
- Independent service processes
- API Gateway for routing
- Service-specific endpoints
- Containerized deployment
- Health monitoring
- Service discovery

---

**🎉 Congratulations!** Your project is now running as a true microservices architecture!

## 🚀 Quick Commands

```bash
# Start all services
./start-microservices.sh

# Check health
curl http://localhost:8000/api/health

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

Your microservices architecture is ready for production use! 🚀
