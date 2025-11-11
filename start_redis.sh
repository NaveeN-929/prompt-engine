#!/bin/bash

# Start Redis for Token Storage
# Used by Pseudonymization and Repersonalization services

echo "🚀 Starting Redis for Token Storage..."

# Check if Redis is already running
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is already running on port 6379"
    redis-cli info | grep redis_version
    exit 0
fi

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is not installed"
    echo ""
    echo "Install Redis:"
    echo "  macOS:    brew install redis"
    echo "  Ubuntu:   sudo apt-get install redis-server"
    echo "  Docker:   docker run -d -p 6379:6379 --name redis-tokens redis:7-alpine"
    echo ""
    exit 1
fi

# Start Redis server
echo "Starting Redis server..."
redis-server --daemonize yes --port 6379 --maxmemory 256mb --maxmemory-policy allkeys-lru

# Wait for Redis to start
sleep 2

# Check if Redis started successfully
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis started successfully on port 6379"
    redis-cli info | grep redis_version
    echo ""
    echo "Redis Configuration:"
    echo "  - URL: redis://localhost:6379"
    echo "  - Max Memory: 256MB"
    echo "  - Policy: allkeys-lru (evict old keys when memory full)"
    echo ""
    echo "To stop Redis:"
    echo "  redis-cli shutdown"
else
    echo "❌ Failed to start Redis"
    exit 1
fi

