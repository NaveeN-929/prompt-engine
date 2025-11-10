#!/bin/bash
# Start All Services Script
# Starts Prompt Engine (5000), Validation Service (5002), and Autonomous Agent (5001)

echo "🚀 Starting All Services..."
echo "============================================================"

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if Qdrant is running
echo ""
echo "🔍 Checking prerequisites..."
if ! docker ps | grep -q qdrant; then
    echo "   ⚠️  Qdrant is not running!"
    echo "   Starting Qdrant..."
    cd "$SCRIPT_DIR"
    if [ -f "start_qdrant.sh" ]; then
        ./start_qdrant.sh
    else
        docker start qdrant 2>/dev/null || docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
    fi
    sleep 3
fi

if docker ps | grep -q qdrant; then
    echo "   ✅ Qdrant is running"
else
    echo "   ❌ Failed to start Qdrant - continuing anyway..."
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -ti :$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=15
    local attempt=1
    
    echo "   ⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "   ✅ $service_name is ready!"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo "   ⚠️  $service_name may not be fully ready (timeout)"
    return 1
}

# 1. Start Prompt Engine (Port 5000)
echo ""
echo "============================================================"
echo "1️⃣  Starting Prompt Engine (Port 5000)..."
echo "============================================================"

if check_port 5000; then
    echo "   ⚠️  Port 5000 is already in use. Skipping..."
else
    cd "$SCRIPT_DIR"
    if [ -d "prompt" ] && [ -f "server.py" ]; then
        source prompt/bin/activate
        nohup python3 server.py > logs/prompt_engine.log 2>&1 &
        echo "   Started Prompt Engine (PID: $!)"
        wait_for_service "http://localhost:5000/status" "Prompt Engine"
    else
        echo "   ❌ Prompt Engine files not found"
    fi
fi

# 2. Start Validation Service (Port 5002)
echo ""
echo "============================================================"
echo "2️⃣  Starting Validation Service (Port 5002)..."
echo "============================================================"

if check_port 5002; then
    echo "   ⚠️  Port 5002 is already in use. Skipping..."
else
    cd "$SCRIPT_DIR/validation-llm"
    if [ -d "venv" ] && [ -f "validation_server.py" ]; then
        source venv/bin/activate
        nohup python3 validation_server.py > ../logs/validation_service.log 2>&1 &
        echo "   Started Validation Service (PID: $!)"
        wait_for_service "http://localhost:5002/health" "Validation Service"
    else
        echo "   ❌ Validation Service files not found"
    fi
fi

# 3. Start Autonomous Agent (Port 5001)
echo ""
echo "============================================================"
echo "3️⃣  Starting Autonomous Agent (Port 5001)..."
echo "============================================================"

if check_port 5001; then
    echo "   ⚠️  Port 5001 is already in use. Skipping..."
else
    cd "$SCRIPT_DIR/autonomous-agent"
    if [ -d "agent" ] && [ -f "start_agent.sh" ]; then
        nohup ./start_agent.sh > ../logs/autonomous_agent.log 2>&1 &
        echo "   Started Autonomous Agent (PID: $!)"
        sleep 5  # Give it more time to initialize
        wait_for_service "http://localhost:5001/status" "Autonomous Agent"
    else
        echo "   ❌ Autonomous Agent files not found"
    fi
fi

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Final status check
echo ""
echo "============================================================"
echo "📊 Service Status Summary"
echo "============================================================"
echo ""

# Check each service
echo "🔍 Port Status:"
for port in 5000 5001 5002; do
    if check_port $port; then
        echo "   Port $port: ✅ IN USE"
    else
        echo "   Port $port: ❌ FREE (service may not have started)"
    fi
done

echo ""
echo "🔍 Service Health:"

# Prompt Engine
if curl -s -f http://localhost:5000/status > /dev/null 2>&1; then
    echo "   Prompt Engine (5000):    ✅ HEALTHY"
else
    echo "   Prompt Engine (5000):    ❌ NOT RESPONDING"
fi

# Validation Service
if curl -s -f http://localhost:5002/health > /dev/null 2>&1; then
    echo "   Validation Service (5002): ✅ HEALTHY"
else
    echo "   Validation Service (5002): ❌ NOT RESPONDING"
fi

# Autonomous Agent
if curl -s -f http://localhost:5001/status > /dev/null 2>&1; then
    echo "   Autonomous Agent (5001):  ✅ HEALTHY"
else
    echo "   Autonomous Agent (5001):  ❌ NOT RESPONDING"
fi

echo ""
echo "============================================================"
echo "✅ Startup script completed!"
echo ""
echo "🌐 Service URLs:"
echo "   • Prompt Engine:      http://localhost:5000"
echo "   • Autonomous Agent:   http://localhost:5001/simple"
echo "   • Validation Service: http://localhost:5002/health"
echo ""
echo "📝 Logs are available in: $SCRIPT_DIR/logs/"
echo ""
echo "To stop all services:"
echo "   ./stop_all_services.sh"
echo ""

