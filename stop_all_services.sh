#!/bin/bash
# Stop All Services Script
# Stops PAM Service (5005), Prompt Engine (5000), Autonomous Agent (5001), and Validation Service (5002)

echo "🛑 Stopping All Services..."
echo "============================================================"

# Function to kill process on specific port
kill_port() {
    local port=$1
    local service_name=$2
    
    echo ""
    echo "🔍 Checking port $port ($service_name)..."
    
    # Find process using the port
    pid=$(lsof -ti :$port 2>/dev/null)
    
    if [ -n "$pid" ]; then
        echo "   Found process(es) on port $port: $pid"
        echo "   Stopping $service_name..."
        kill -15 $pid 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if lsof -ti :$port >/dev/null 2>&1; then
            echo "   Force killing $service_name..."
            kill -9 $pid 2>/dev/null
            sleep 1
        fi
        
        # Verify port is released
        if lsof -ti :$port >/dev/null 2>&1; then
            echo "   ❌ Failed to release port $port"
        else
            echo "   ✅ Port $port released"
        fi
    else
        echo "   ✓ Port $port is already free"
    fi
}

# Function to kill process by name
kill_by_name() {
    local process_name=$1
    local display_name=$2
    
    echo ""
    echo "🔍 Checking for $display_name processes..."
    
    pids=$(pgrep -f "$process_name" 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "   Found process(es): $pids"
        echo "   Stopping $display_name..."
        pkill -15 -f "$process_name" 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if pgrep -f "$process_name" >/dev/null 2>&1; then
            echo "   Force killing $display_name..."
            pkill -9 -f "$process_name" 2>/dev/null
            sleep 1
        fi
        
        # Verify stopped
        if pgrep -f "$process_name" >/dev/null 2>&1; then
            echo "   ❌ Some $display_name processes may still be running"
        else
            echo "   ✅ All $display_name processes stopped"
        fi
    else
        echo "   ✓ No $display_name processes found"
    fi
}

# Stop services by port
echo ""
echo "📍 Stopping services by port..."
kill_port 5005 "PAM Service"
kill_port 5000 "Prompt Engine"
kill_port 5001 "Autonomous Agent"
kill_port 5002 "Validation Service"

# Stop services by process name (backup method)
echo ""
echo "📍 Stopping services by process name..."
kill_by_name "pam-service/run_service.py" "PAM Service"
kill_by_name "server.py" "Prompt Engine (server.py)"
kill_by_name "server_final.py" "Autonomous Agent (server_final.py)"
kill_by_name "validation_server.py" "Validation Service"
kill_by_name "simple_server.py" "Simple Validation Server"
kill_by_name "start_agent.sh" "Agent Startup Script"

# Final verification
echo ""
echo "============================================================"
echo "🔍 Final Port Status:"
echo ""

for port in 5005 5000 5001 5002; do
    if lsof -ti :$port >/dev/null 2>&1; then
        echo "   Port $port: ❌ STILL IN USE"
    else
        echo "   Port $port: ✅ FREE"
    fi
done

echo ""
echo "🔍 Running Python Server Processes:"
echo ""
python_servers=$(ps aux | grep -E "server\.py|server_final\.py|validation_server\.py|simple_server\.py" | grep -v grep | grep -v "stop_all_services")

if [ -z "$python_servers" ]; then
    echo "   ✅ No server processes running"
else
    echo "$python_servers"
    echo ""
    echo "   ⚠️  Warning: Some processes are still running"
fi

echo ""
echo "============================================================"
echo "✅ Stop script completed!"
echo ""
echo "To start services again:"
echo "   • PAM Service:        cd pam-service && source pam/bin/activate && python3 run_service.py"
echo "   • Prompt Engine:      cd prompt-engine && source prompt/bin/activate && python3 server.py"
echo "   • Validation Service: cd validation-llm && source venv/bin/activate && python3 validation_server.py"
echo "   • Autonomous Agent:   cd autonomous-agent && ./start_agent.sh"
echo ""
echo "Or use: ./start_all_services.sh"
echo ""

