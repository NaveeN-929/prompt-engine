#!/bin/bash

# Docker Setup Script for Prompt Engine
# This script helps you quickly set up and run the Prompt Engine with Docker

set -e  # Exit on error

echo "🚀 Prompt Engine Docker Setup"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Setup environment file
setup_env() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp env.template .env
        print_success ".env file created"
        print_warning "Please review and modify .env file with your settings"
    else
        print_warning ".env file already exists, skipping creation"
    fi
}

# Pull required images
pull_images() {
    print_status "Pulling Docker images..."
    docker-compose pull
    print_success "Images pulled successfully"
}

# Start services
start_services() {
    print_status "Starting services..."
    docker-compose up -d
    print_success "Services started"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for Qdrant
    print_status "Waiting for Qdrant..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -sf http://localhost:6333/collections &>/dev/null; then
            break
        fi
        sleep 1
        ((timeout--))
    done
    
    if [ $timeout -eq 0 ]; then
        print_warning "Qdrant may not be ready yet"
    else
        print_success "Qdrant is ready"
    fi
    
    # Wait for Prompt Engine
    print_status "Waiting for Prompt Engine..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -sf http://localhost:5000/system/status &>/dev/null; then
            break
        fi
        sleep 1
        ((timeout--))
    done
    
    if [ $timeout -eq 0 ]; then
        print_warning "Prompt Engine may not be ready yet"
    else
        print_success "Prompt Engine is ready"
    fi
}

# Setup Ollama model
setup_ollama() {
    print_status "Setting up Ollama model..."
    
    # Get model from .env or use default
    MODEL=$(grep OLLAMA_MODEL .env | cut -d '=' -f2 | tr -d '"' || echo "llama3.1:8b")
    
    print_status "Pulling model: $MODEL"
    docker exec -it prompt-engine-ollama ollama pull $MODEL || {
        print_warning "Failed to pull model automatically. You can do this manually later:"
        echo "docker exec -it prompt-engine-ollama ollama pull $MODEL"
    }
}

# Show status
show_status() {
    echo ""
    echo "🏃 Service Status"
    echo "=================="
    docker-compose ps
    
    echo ""
    echo "🌐 Access URLs"
    echo "=============="
    echo "Web UI:        http://localhost:5000"
    echo "System Status: http://localhost:5000/system/status"
    echo "Qdrant:        http://localhost:6333"
    echo "Ollama:        http://localhost:11434"
    
    echo ""
    echo "📋 Useful Commands"
    echo "=================="
    echo "View logs:           docker-compose logs -f"
    echo "Stop services:       docker-compose down"
    echo "Restart services:    docker-compose restart"
    echo "Update images:       docker-compose pull && docker-compose up -d"
    
    # Test API
    echo ""
    print_status "Testing API..."
    if curl -sf http://localhost:5000/system/status | jq . &>/dev/null; then
        print_success "API is responding correctly"
    else
        print_warning "API test failed or jq not installed"
    fi
}

# Main setup process
main() {
    echo "Starting setup process..."
    echo ""
    
    # Parse command line arguments
    SKIP_OLLAMA=false
    DEVELOPMENT=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-ollama)
                SKIP_OLLAMA=true
                shift
                ;;
            --dev)
                DEVELOPMENT=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-ollama    Skip Ollama model setup"
                echo "  --dev           Start in development mode"
                echo "  --help          Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Run setup steps
    check_docker
    setup_env
    pull_images
    
    if [ "$DEVELOPMENT" = true ]; then
        print_status "Starting in development mode..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    else
        start_services
    fi
    
    wait_for_services
    
    if [ "$SKIP_OLLAMA" = false ]; then
        setup_ollama
    else
        print_warning "Skipping Ollama model setup"
    fi
    
    show_status
    
    print_success "Setup complete! 🎉"
    echo ""
    print_status "Open http://localhost:5000 in your browser to get started"
}

# Run main function
main "$@"