#!/bin/bash
# Script to start Qdrant Vector Database for local development

echo "🚀 Starting Qdrant Vector Database..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Check if Qdrant container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^qdrant$\|^paytechneodemo-qdrant$"; then
    echo "📦 Found existing Qdrant container..."
    
    # Check if it's running
    if docker ps --format '{{.Names}}' | grep -q "^qdrant$\|^paytechneodemo-qdrant$"; then
        echo "✅ Qdrant is already running!"
        echo ""
        echo "🌐 Qdrant is accessible at:"
        echo "   - REST API: http://localhost:6333"
        echo "   - Web UI: http://localhost:6333/dashboard"
        echo ""
        echo "Testing connection..."
        if curl -sf http://localhost:6333/collections > /dev/null 2>&1; then
            echo "✅ Connection successful!"
        else
            echo "⚠️ Connection failed. Restarting container..."
            docker restart qdrant 2>/dev/null || docker restart paytechneodemo-qdrant 2>/dev/null
            sleep 5
            echo "✅ Container restarted"
        fi
    else
        echo "🔄 Starting existing Qdrant container..."
        docker start qdrant 2>/dev/null || docker start paytechneodemo-qdrant 2>/dev/null
        sleep 5
        echo "✅ Qdrant started!"
    fi
else
    echo "📦 Creating new Qdrant container..."
    
    # Stop and remove any containers using ports 6333 or 6334
    echo "🧹 Cleaning up any conflicting containers..."
    docker ps -a -q --filter "publish=6333" | xargs -r docker stop 2>/dev/null
    docker ps -a -q --filter "publish=6333" | xargs -r docker rm 2>/dev/null
    docker ps -a -q --filter "publish=6334" | xargs -r docker stop 2>/dev/null
    docker ps -a -q --filter "publish=6334" | xargs -r docker rm 2>/dev/null
    
    # Create and start Qdrant container
    docker run -d \
        --name qdrant \
        -p 6333:6333 \
        -p 6334:6334 \
        -v "$(pwd)/qdrant_storage:/qdrant/storage" \
        qdrant/qdrant:latest
    
    echo "⏳ Waiting for Qdrant to be ready..."
    sleep 10
    
    # Wait for Qdrant to be healthy
    for i in {1..30}; do
        if curl -sf http://localhost:6333/collections > /dev/null 2>&1; then
            echo "✅ Qdrant is ready!"
            break
        fi
        echo "   Waiting... ($i/30)"
        sleep 2
    done
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Qdrant Vector Database Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Qdrant is running and accessible at:"
echo "   📡 REST API: http://localhost:6333"
echo "   🌐 Web UI:   http://localhost:6333/dashboard"
echo ""
echo "Test connection:"
echo "   curl http://localhost:6333/collections"
echo ""
echo "Now you can start your Python server:"
echo "   python3 server.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

