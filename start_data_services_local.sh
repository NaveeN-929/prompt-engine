#!/bin/bash

# Start Data Services Locally (without Docker)
# This script starts both Pseudonymization and Repersonalization services
# Requires: Redis on port 6379

echo "🚀 Starting Data Services (Local Mode)"
echo "======================================"
echo ""

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Check Redis first
echo "🔍 Checking Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running on port 6379"
    redis-cli info | grep redis_version
else
    echo "❌ Redis is NOT running!"
    echo ""
    echo "🚨 CRITICAL: Redis is required for token storage"
    echo ""
    echo "Start Redis with:"
    echo "  ./start_redis.sh"
    echo "  OR"
    echo "  docker run -d -p 6379:6379 --name redis-tokens redis:7-alpine"
    echo ""
    read -p "Continue without Redis (will use in-memory fallback)? [y/N]: " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
fi

echo ""

# Check and stop any existing processes
echo "📋 Checking for existing services..."
if check_port 5003; then
    echo "⚠️  Port 5003 is in use. Stopping existing Pseudonymization service..."
    pkill -f "start_pseudonymization.py" 2>/dev/null || true
    sleep 2
fi

if check_port 5004; then
    echo "⚠️  Port 5004 is in use. Stopping existing Repersonalization service..."
    pkill -f "start_repersonalization.py" 2>/dev/null || true
    sleep 2
fi

echo ""

# Create logs directory
mkdir -p logs

echo "🚀 Starting Pseudonymization Service (Port 5003)..."
python3 start_pseudonymization.py > logs/pseudonymization.log 2>&1 &
PSEUDO_PID=$!

echo "   PID: $PSEUDO_PID"
echo "   Log: logs/pseudonymization.log"

sleep 3

echo ""
echo "🚀 Starting Repersonalization Service (Port 5004)..."
python3 start_repersonalization.py > logs/repersonalization.log 2>&1 &
REPERSONAL_PID=$!

echo "   PID: $REPERSONAL_PID"
echo "   Log: logs/repersonalization.log"

# Wait for services to start
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
echo ""
echo "🔍 Checking service health..."

if check_port 5003; then
    PSEUDO_STATUS=$(curl -s http://localhost:5003/health 2>/dev/null | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "unreachable")
    if [ "$PSEUDO_STATUS" = "healthy" ]; then
        echo "✅ Pseudonymization Service: Healthy (Port 5003)"
    else
        echo "⚠️  Pseudonymization Service: $PSEUDO_STATUS"
    fi
else
    echo "❌ Pseudonymization Service: Not running"
fi

if check_port 5004; then
    REPERSONAL_STATUS=$(curl -s http://localhost:5004/health 2>/dev/null | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "unreachable")
    if [ "$REPERSONAL_STATUS" = "healthy" ]; then
        echo "✅ Repersonalization Service: Healthy (Port 5004)"
    else
        echo "⚠️  Repersonalization Service: $REPERSONAL_STATUS"
    fi
else
    echo "❌ Repersonalization Service: Not running"
fi

echo ""
echo "======================================"
echo "✅ Services started successfully!"
echo ""
echo "📍 Service Endpoints:"
echo "  • Redis:              redis://localhost:6379"
echo "  • Pseudonymization:   http://localhost:5003"
echo "  • Repersonalization:  http://localhost:5004"
echo ""
echo "🧪 Test the services:"
echo "  python3 check_redis.py           # Check Redis status"
echo "  python3 test_pii_detection.py    # Test PII detection"
echo ""
echo "📊 View logs:"
echo "  tail -f logs/pseudonymization.log"
echo "  tail -f logs/repersonalization.log"
echo ""
echo "🔍 Monitor Redis:"
echo "  redis-cli monitor"
echo "  redis-cli info"
echo "  redis-cli keys 'pseudonym:*'    # View tokens"
echo ""
echo "🛑 To stop services:"
echo "  pkill -f start_pseudonymization.py"
echo "  pkill -f start_repersonalization.py"
echo "  redis-cli shutdown    # Stop Redis"
echo ""

