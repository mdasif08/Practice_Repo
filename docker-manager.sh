#!/bin/bash

# Docker Manager Script for CraftNudge Microservices
# Usage: ./docker-manager.sh [start|stop|restart|status|logs|build]

set -e

COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop first."
        exit 1
    fi
}

# Function to start services
start_services() {
    print_info "Starting CraftNudge Microservices..."
    docker-compose -f $COMPOSE_FILE up -d
    print_status "All services started successfully!"
    
    echo ""
    print_info "Service URLs:"
    echo "  🌐 Frontend: http://localhost:3000"
    echo "  🔌 API Gateway: http://localhost:8000"
    echo "  📊 Commit Tracker: http://localhost:8001"
    echo "  📁 Repo Manager: http://localhost:8002"
    echo "  🔗 Webhook Handler: http://localhost:8003"
    echo "  🤖 AI Analyzer: http://localhost:8004"
    echo "  🗄️  Database: localhost:5432"
    echo "  🧠 Ollama: http://localhost:11434"
}

# Function to stop services
stop_services() {
    print_info "Stopping CraftNudge Microservices..."
    docker-compose -f $COMPOSE_FILE down
    print_status "All services stopped successfully!"
}

# Function to restart services
restart_services() {
    print_info "Restarting CraftNudge Microservices..."
    docker-compose -f $COMPOSE_FILE down
    docker-compose -f $COMPOSE_FILE up -d
    print_status "All services restarted successfully!"
}

# Function to show status
show_status() {
    print_info "CraftNudge Microservices Status:"
    echo ""
    docker-compose -f $COMPOSE_FILE ps
}

# Function to show logs
show_logs() {
    print_info "Showing logs for all services..."
    docker-compose -f $COMPOSE_FILE logs -f
}

# Function to build services
build_services() {
    print_info "Building CraftNudge Microservices..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    print_status "All services built successfully!"
}

# Function to show help
show_help() {
    echo "CraftNudge Docker Manager"
    echo "========================"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start all microservices"
    echo "  stop      - Stop all microservices"
    echo "  restart   - Restart all microservices"
    echo "  status    - Show status of all services"
    echo "  logs      - Show logs from all services"
    echo "  build     - Build all services (no cache)"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start all services"
    echo "  $0 status   # Check service status"
    echo "  $0 logs     # View service logs"
}

# Main script logic
case "${1:-help}" in
    start)
        check_docker
        start_services
        ;;
    stop)
        check_docker
        stop_services
        ;;
    restart)
        check_docker
        restart_services
        ;;
    status)
        check_docker
        show_status
        ;;
    logs)
        check_docker
        show_logs
        ;;
    build)
        check_docker
        build_services
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
