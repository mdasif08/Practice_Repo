# 🐳 Docker Deployment Guide

## Overview

This guide explains how to deploy the CraftNudge Microservices architecture using Docker. All services, including the frontend, are now containerized and can be managed with simple commands.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git (to clone the repository)

### 1. Start All Services
```bash
# Using the management script (recommended)
./docker-manager.sh start

# Or using docker-compose directly
docker-compose up -d
```

### 2. Access the Application
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Database**: localhost:5432

## 📋 Service Architecture

| Service | Port | Description | Container Name |
|---------|------|-------------|----------------|
| **Frontend** | 3000 | React app with nginx | microservice-frontend |
| **API Gateway** | 8000 | Routes requests to services | microservice-api-gateway |
| **Commit Tracker** | 8001 | Handles commit operations | microservice-commit-tracker |
| **Repository Manager** | 8002 | Manages repositories | microservice-repo-manager |
| **Webhook Handler** | 8003 | Processes GitHub webhooks | microservice-webhook-handler |
| **AI Analyzer** | 8004 | AI analysis service | microservice-ai-analyzer |
| **PostgreSQL** | 5432 | Database | microservice-postgres |
| **Ollama** | 11434 | AI models | microservice-ollama |

## 🛠️ Management Commands

### Using the Management Script
```bash
# Start all services
./docker-manager.sh start

# Stop all services
./docker-manager.sh stop

# Restart all services
./docker-manager.sh restart

# Check service status
./docker-manager.sh status

# View service logs
./docker-manager.sh logs

# Rebuild all services
./docker-manager.sh build

# Show help
./docker-manager.sh help
```

### Using Docker Compose Directly
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild services
docker-compose build --no-cache

# Check status
docker-compose ps
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
# GitHub Token (required for real commits)
GITHUB_TOKEN=your_github_token_here

# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=newDB
DB_USER=postgres
DB_PASSWORD=root

# Service Ports
GATEWAY_PORT=8000
COMMIT_SERVICE_PORT=8001
REPO_SERVICE_PORT=8002
WEBHOOK_SERVICE_PORT=8003
AI_SERVICE_PORT=8004
```

### Frontend Configuration
The frontend automatically proxies API calls to the backend services through nginx. No additional configuration is needed.

## 📊 Monitoring

### Check Service Health
```bash
# API Gateway health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000/health

# Individual service health
curl http://localhost:8001/health  # Commit Tracker
curl http://localhost:8002/health  # Repo Manager
curl http://localhost:8003/health  # Webhook Handler
curl http://localhost:8004/health  # AI Analyzer
```

### View Service Logs
```bash
# All services
./docker-manager.sh logs

# Specific service
docker-compose logs -f frontend
docker-compose logs -f api-gateway
docker-compose logs -f commit-tracker
```

## 🔄 Development Workflow

### Making Changes
1. **Frontend Changes**: Edit files in `frontend/` directory
2. **Backend Changes**: Edit files in `services/` directory
3. **Rebuild**: `./docker-manager.sh build`
4. **Restart**: `./docker-manager.sh restart`

### Hot Reload (Development)
For development with hot reload, you can run the frontend separately:
```bash
# Stop frontend container
docker-compose stop frontend

# Run frontend in development mode
cd frontend && npm run dev
```

## 🗄️ Database Management

### Access Database
```bash
# Connect to PostgreSQL container
docker exec -it microservice-postgres psql -U postgres -d newDB

# View tables
\dt

# View commits
SELECT * FROM "CraftNudge".Commits LIMIT 10;
```

### Backup Database
```bash
# Create backup
docker exec microservice-postgres pg_dump -U postgres newDB > backup.sql

# Restore backup
docker exec -i microservice-postgres psql -U postgres newDB < backup.sql
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :3000

# Kill the process or change port in docker-compose.yml
```

#### 2. Docker Not Running
```bash
# Start Docker Desktop
# Then run:
./docker-manager.sh start
```

#### 3. Frontend Not Loading
```bash
# Check if frontend container is running
docker-compose ps

# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

#### 4. API Connection Issues
```bash
# Check if API Gateway is running
curl http://localhost:8000/health

# Check nginx configuration
docker exec microservice-frontend nginx -t
```

### Reset Everything
```bash
# Stop and remove all containers
docker-compose down

# Remove all images
docker-compose down --rmi all

# Remove volumes (WARNING: This will delete all data)
docker-compose down -v

# Start fresh
./docker-manager.sh start
```

## 📈 Performance

### Resource Usage
Monitor resource usage:
```bash
# View container resource usage
docker stats

# View specific container
docker stats microservice-frontend
```

### Scaling
To scale specific services:
```bash
# Scale commit tracker to 3 instances
docker-compose up -d --scale commit-tracker=3
```

## 🔒 Security

### Production Considerations
1. **Change default passwords** in `.env` file
2. **Use HTTPS** by configuring SSL certificates
3. **Restrict network access** using Docker networks
4. **Regular security updates** for base images
5. **Monitor logs** for suspicious activity

### Network Security
```bash
# View network configuration
docker network ls
docker network inspect microservice_microservice-network
```

## 📝 Logs and Debugging

### Log Locations
- **Application logs**: `docker-compose logs -f`
- **Nginx logs**: Inside frontend container at `/var/log/nginx/`
- **Database logs**: Inside postgres container

### Debug Mode
```bash
# Run in debug mode
docker-compose up -d --build
docker-compose logs -f
```

## 🎯 Next Steps

1. **Set up GitHub webhooks** for automatic commit detection
2. **Configure AI models** in Ollama
3. **Set up monitoring** and alerting
4. **Implement CI/CD** pipeline
5. **Add load balancing** for production

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review service logs: `./docker-manager.sh logs`
3. Check service status: `./docker-manager.sh status`
4. Rebuild services: `./docker-manager.sh build`

---

**🎉 Your CraftNudge Microservices are now fully containerized and ready for production!**
