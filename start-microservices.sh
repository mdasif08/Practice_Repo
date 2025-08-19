#!/bin/bash

echo "🚀 CraftNudge Microservice Architecture"
echo "======================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "📋 To get real GitHub commits (instead of demo data), you need to configure a GitHub token."
    echo ""
    echo "🔧 Quick setup:"
    echo "   python setup-github-token.py"
    echo ""
    echo "📖 Manual setup:"
    echo "   1. Copy env.example to .env"
    echo "   2. Edit .env and add your GitHub token"
    echo "   3. Get token from: https://github.com/settings/tokens"
    echo ""
    read -p "Do you want to continue without GitHub token? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. Please configure GitHub token first."
        exit 1
    fi
    echo "⚠️  Running without GitHub token - only demo data will be available."
else
    echo "✅ .env file found"
fi

echo ""
echo "🐳 Starting microservices with Docker Compose..."
echo ""

# Start services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
echo "=================="

services=("api-gateway:8000" "commit-tracker:8001" "repo-manager:8002" "webhook-handler:8003" "ai-analyzer:8004")

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ $name (port $port) - Running"
    else
        echo "❌ $name (port $port) - Not responding"
    fi
done

echo ""
echo "🎉 Microservices started!"
echo ""
echo "📱 Frontend: http://localhost:5173"
echo "🔗 API Gateway: http://localhost:8000"
echo ""
echo "🧪 Test GitHub connection:"
echo "   curl http://localhost:8000/github/test"
echo ""
echo "📋 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
