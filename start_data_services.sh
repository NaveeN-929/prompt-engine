#!/bin/bash

# Start Data Services - Pseudonymization and Repersonalization
# This script starts both services together with shared key storage

echo "🚀 Starting Data Services..."
echo "======================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

echo "✅ docker-compose is available"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.data-services.yml down

echo ""
echo "🔨 Building and starting services..."
echo ""

# Build and start services
docker-compose -f docker-compose.data-services.yml up -d --build

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check Pseudonymization Service
echo ""
echo "Checking Pseudonymization Service..."
PSEUDO_STATUS=$(curl -s http://localhost:5003/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo "unreachable")

if [ "$PSEUDO_STATUS" = "healthy" ]; then
    echo "✅ Pseudonymization Service: Healthy (Port 5003)"
else
    echo "⚠️  Pseudonymization Service: $PSEUDO_STATUS"
    echo "   Check logs: docker-compose -f docker-compose.data-services.yml logs pseudonymization-service"
fi

# Check Repersonalization Service
echo ""
echo "Checking Repersonalization Service..."
REPERSONAL_STATUS=$(curl -s http://localhost:5004/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo "unreachable")

if [ "$REPERSONAL_STATUS" = "healthy" ]; then
    echo "✅ Repersonalization Service: Healthy (Port 5004)"
else
    echo "⚠️  Repersonalization Service: $REPERSONAL_STATUS"
    echo "   Check logs: docker-compose -f docker-compose.data-services.yml logs repersonalization-service"
fi

echo ""
echo "======================================"
echo "🎉 Data Services Started!"
echo ""
echo "📡 Service Endpoints:"
echo "   Pseudonymization:    http://localhost:5003"
echo "   Repersonalization:   http://localhost:5004"
echo ""
echo "📚 API Documentation:"
echo "   Pseudonymization:    http://localhost:5003/docs"
echo "   Repersonalization:   http://localhost:5004/docs"
echo ""
echo "🔒 PII Detection: Automatic detection of 20+ PII types"
echo "   Test it: python3 test_pii_detection.py"
echo ""
echo "🔍 View logs:"
echo "   docker-compose -f docker-compose.data-services.yml logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose -f docker-compose.data-services.yml down"
echo ""

