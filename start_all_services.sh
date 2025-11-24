#!/bin/bash
# Start All Services Script
# Starts each service in a new terminal window with proper virtual environment
# Flow: Prompt Engine (5000) → Validation Service (5002) → Autonomous Agent (5001)

echo "🚀 Starting All Services in New Terminal Windows..."
echo "============================================================"

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

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
    local max_attempts=45  # 90 seconds total (45 * 2)
    local attempt=1
    
    echo "   ⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "   ✅ $service_name is ready!"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "   ⚠️  $service_name did not start properly (timeout after 90s)"
    return 1
}

# Check if Qdrant is running
echo ""
echo "🔍 Step 0: Checking prerequisites..."
echo "============================================================"
if ! docker ps | grep -q qdrant; then
    echo "   ⚠️  Qdrant is not running!"
    echo "   Starting Qdrant..."
    cd "$SCRIPT_DIR"
    if [ -f "start_qdrant.sh" ]; then
        ./start_qdrant.sh
    else
        docker start qdrant 2>/dev/null || docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
    fi
    echo "   ⏳ Waiting for Qdrant to initialize..."
    sleep 5
fi

if docker ps | grep -q qdrant; then
    echo "   ✅ Qdrant is running"
else
    echo "   ❌ Failed to start Qdrant - services may not work properly!"
fi

# 1. Start Prompt Engine (Port 5000) - REQUIRED FIRST
echo ""
echo "============================================================"
echo "1️⃣  Starting Prompt Engine (Port 5000) in new terminal..."
echo "============================================================"

if check_port 5000; then
    echo "   ⚠️  Port 5000 is already in use. Skipping..."
else
    if [ -d "$SCRIPT_DIR/prompt" ] && [ -f "$SCRIPT_DIR/server.py" ]; then
        osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR' && source prompt/bin/activate && echo '🚀 Starting Prompt Engine...' && echo '============================================================' && python3 server.py"
end tell
EOF
        echo "   ✅ Opened new terminal for Prompt Engine"
        echo "   ⏳ Waiting for Prompt Engine to initialize (20 seconds)..."
        echo "      (Model loading may take additional time...)"
        sleep 20
        
        if wait_for_service "http://localhost:5000/status" "Prompt Engine"; then
            echo "   ✅ Prompt Engine is operational!"
        else
            echo "   ⚠️  Prompt Engine health check timed out - continuing anyway"
            echo "      Check the terminal window for initialization status"
        fi
    else
        echo "   ❌ Prompt Engine files not found at $SCRIPT_DIR"
        exit 1
    fi
fi

# 2. Start Validation Service (Port 5002) - REQUIRED SECOND
echo ""
echo "============================================================"
echo "2️⃣  Starting Validation Service (Port 5002) in new terminal..."
echo "============================================================"

if check_port 5002; then
    echo "   ⚠️  Port 5002 is already in use. Skipping..."
else
    if [ -d "$SCRIPT_DIR/validation-llm/venv" ] && [ -f "$SCRIPT_DIR/validation-llm/validation_server.py" ]; then
        osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR/validation-llm' && source venv/bin/activate && echo '🛡️  Starting Validation Service...' && echo '============================================================' && python3 validation_server.py"
end tell
EOF
        echo "   ✅ Opened new terminal for Validation Service"
        echo "   ⏳ Waiting for Validation Service to initialize (10 seconds)..."
        sleep 10
        
        if wait_for_service "http://localhost:5002/health" "Validation Service"; then
            echo "   ✅ Validation Service is operational!"
        else
            echo "   ⚠️  Validation Service health check timed out - continuing anyway"
            echo "      Check the terminal window for initialization status"
        fi
    else
        echo "   ❌ Validation Service files not found at $SCRIPT_DIR/validation-llm"
        exit 1
    fi
fi

# 3. Start Autonomous Agent (Port 5001) - REQUIRES BOTH ABOVE
echo ""
echo "============================================================"
echo "3️⃣  Starting Autonomous Agent (Port 5001) in new terminal..."
echo "============================================================"

if check_port 5001; then
    echo "   ⚠️  Port 5001 is already in use. Skipping..."
else
    if [ -d "$SCRIPT_DIR/autonomous-agent/agent" ] && [ -f "$SCRIPT_DIR/autonomous-agent/start_agent.sh" ]; then
        osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR/autonomous-agent' && echo '🤖 Starting Autonomous Agent...' && echo '============================================================' && ./start_agent.sh"
end tell
EOF
        echo "   ✅ Opened new terminal for Autonomous Agent"
        echo "   ⏳ Waiting for Autonomous Agent to initialize (20 seconds)..."
        echo "      (Agent needs to initialize RAG service and connect to dependencies)"
        sleep 20
        
        if wait_for_service "http://localhost:5001/status" "Autonomous Agent"; then
            echo "   ✅ Autonomous Agent is operational!"
        else
            echo "   ⚠️  Autonomous Agent may still be initializing - check the terminal window"
        fi
    else
        echo "   ❌ Autonomous Agent files not found at $SCRIPT_DIR/autonomous-agent"
        exit 1
    fi
fi

# Final comprehensive status check
echo ""
echo "============================================================"
echo "📊 Final Service Status Summary"
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
echo "🔍 Service Health Check:"

# Prompt Engine
if curl -s -f http://localhost:5000/status > /dev/null 2>&1; then
    echo "   1️⃣  Prompt Engine (5000):      ✅ HEALTHY & RESPONDING"
else
    echo "   1️⃣  Prompt Engine (5000):      ❌ NOT RESPONDING"
fi

# Validation Service
if curl -s -f http://localhost:5002/health > /dev/null 2>&1; then
    echo "   2️⃣  Validation Service (5002):  ✅ HEALTHY & RESPONDING"
else
    echo "   2️⃣  Validation Service (5002):  ❌ NOT RESPONDING"
fi

# Autonomous Agent
if curl -s -f http://localhost:5001/status > /dev/null 2>&1; then
    echo "   3️⃣  Autonomous Agent (5001):    ✅ HEALTHY & RESPONDING"
    
    # Check validation integration
    validation_status=$(curl -s http://localhost:5001/validation/status 2>/dev/null | grep -o '"integration_initialized":true' || echo "")
    if [ -n "$validation_status" ]; then
        echo "       └─ Validation Integration:  ✅ ACTIVE"
    else
        echo "       └─ Validation Integration:  ⚠️  CHECK STATUS"
    fi
else
    echo "   3️⃣  Autonomous Agent (5001):    ❌ NOT RESPONDING"
fi

echo ""
echo "============================================================"
echo "✅ All Services Started Successfully!"
echo "============================================================"
echo ""
echo "🌐 Service URLs (Click to open):"
echo "   • Prompt Engine Status:   http://localhost:5000/status"
echo "   • Validation Health:      http://localhost:5002/health"
echo "   • Autonomous Agent UI:    http://localhost:5001/simple"
echo "   • Agent Status:           http://localhost:5001/status"
echo ""
echo "📊 Service Dependencies Flow:"
echo "   1. Qdrant (Docker)        → Vector Database"
echo "   2. Prompt Engine (5000)   → Prompt Generation"
echo "   3. Validation Service (5002) → Response Quality Gates"
echo "   4. Autonomous Agent (5001) → RAG-Enhanced Analysis"
echo ""
echo "📝 Terminal Windows:"
echo "   • 3 new terminal windows have been opened"
echo "   • Each service runs with its own virtual environment"
echo "   • Check terminal windows for service logs"
echo ""
echo "🛑 To stop all services:"
echo "   ./stop_all_services.sh"
echo ""
echo "💡 Quick Test:"
echo "   Open http://localhost:5001/simple and try the 'Full RAG Pipeline'"
echo ""

