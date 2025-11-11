# Service Management Guide

Complete guide for starting, stopping, and managing all services in the RAG-Enhanced Prompt Engine system.

## 📋 Overview

The system consists of 4 main components:
1. **Qdrant** (Docker) - Vector database (Port 6333)
2. **Prompt Engine** (Port 5000) - Dynamic prompt generation
3. **Validation Service** (Port 5002) - Response quality gates
4. **Autonomous Agent** (Port 5001) - RAG-enhanced analysis

## 🚀 Quick Start

### Start All Services
```bash
./start_all_services.sh
```

This will:
- ✅ Check and start Qdrant (if not running)
- ✅ Open 3 new terminal windows (one for each service)
- ✅ Start each service with its proper virtual environment
- ✅ Wait for each service to initialize before starting the next
- ✅ Verify all services are healthy

### Stop All Services
```bash
./stop_all_services.sh
```

This will:
- ✅ Stop all Python server processes
- ✅ Release ports 5000, 5001, and 5002
- ✅ Show final status of all ports

## 📊 Service Startup Flow

The services **must** be started in this order due to dependencies:

```
1. Qdrant (Vector DB)           ← Base requirement
   ↓ (wait 5s)
2. Prompt Engine (5000)          ← Required by Agent
   ↓ (wait 15s)
3. Validation Service (5002)     ← Required by Agent
   ↓ (wait 10s)
4. Autonomous Agent (5001)       ← Depends on all above
   ↓ (wait 20s)
   ✅ System Ready
```

### Timing Details
- **Prompt Engine**: 15 seconds to load vector DB and initialize
- **Validation Service**: 10 seconds to load LLM validation engine
- **Autonomous Agent**: 20 seconds to initialize RAG service and connect to dependencies

## 🔧 Manual Service Management

### Start Individual Services

#### 1. Start Prompt Engine
```bash
cd /Users/naveen/Pictures/prompt-engine
source prompt/bin/activate
python3 server.py
```
- **Port**: 5000
- **Virtual Env**: `prompt/` (Python 3.12)
- **Status**: http://localhost:5000/status

#### 2. Start Validation Service
```bash
cd /Users/naveen/Pictures/prompt-engine/validation-llm
source venv/bin/activate
python3 validation_server.py
```
- **Port**: 5002
- **Virtual Env**: `validation-llm/venv/` (Python 3.12)
- **Health**: http://localhost:5002/health

#### 3. Start Autonomous Agent
```bash
cd /Users/naveen/Pictures/prompt-engine/autonomous-agent
./start_agent.sh
```
- **Port**: 5001
- **Virtual Env**: `autonomous-agent/agent/` (Python 3.12)
- **Status**: http://localhost:5001/status
- **Interface**: http://localhost:5001/simple

### Start Qdrant (If Needed)
```bash
./start_qdrant.sh
```
Or manually:
```bash
docker start qdrant
# Or if container doesn't exist:
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

## 🔍 Health Check Commands

### Check All Services
```bash
# Prompt Engine
curl http://localhost:5000/status

# Validation Service
curl http://localhost:5002/health

# Autonomous Agent
curl http://localhost:5001/status

# Validation Integration
curl http://localhost:5001/validation/status
```

### Check Ports
```bash
# Check if ports are in use
lsof -i :5000  # Prompt Engine
lsof -i :5001  # Autonomous Agent
lsof -i :5002  # Validation Service
lsof -i :6333  # Qdrant
```

### Check Processes
```bash
# Show all service processes
ps aux | grep -E "server\.py|server_final\.py|validation_server\.py" | grep -v grep

# Show Qdrant container
docker ps | grep qdrant
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on specific port
lsof -ti :5000 | xargs kill -9  # Prompt Engine
lsof -ti :5001 | xargs kill -9  # Autonomous Agent
lsof -ti :5002 | xargs kill -9  # Validation Service

# Or use the stop script
./stop_all_services.sh
```

### Service Won't Start

#### Check Virtual Environment
```bash
# Verify venv exists and has correct Python version
source prompt/bin/activate && python --version  # Should be 3.12.x
source validation-llm/venv/bin/activate && python --version
source autonomous-agent/agent/bin/activate && python --version
```

#### Check Dependencies
```bash
# Prompt Engine
cd prompt-engine && source prompt/bin/activate
pip list | grep -E "flask|qdrant|sentence-transformers"

# Validation Service
cd validation-llm && source venv/bin/activate
pip list | grep -E "flask|qdrant|asgiref"

# Autonomous Agent
cd autonomous-agent && source agent/bin/activate
pip list | grep -E "flask|qdrant|sentence-transformers"
```

#### Check Qdrant
```bash
# Verify Qdrant is running
docker ps | grep qdrant

# Check Qdrant logs
docker logs qdrant

# Restart Qdrant
docker restart qdrant

# Test Qdrant connection
curl http://localhost:6333/collections
```

### Validation Not Working

If you see "⚠️ Validation Unavailable" in the interface:

1. **Check validation service is running**:
   ```bash
   curl http://localhost:5002/health
   ```

2. **Check agent can reach validation service**:
   ```bash
   curl http://localhost:5001/validation/status
   ```

3. **Restart in correct order**:
   ```bash
   ./stop_all_services.sh
   ./start_all_services.sh
   ```

### NumPy Compatibility Issues

If you see NumPy 2.x errors:
```bash
# Fix for each service
cd prompt-engine && source prompt/bin/activate
pip install "numpy<2" --force-reinstall

cd validation-llm && source venv/bin/activate
pip install "numpy<2" --force-reinstall

cd autonomous-agent && source agent/bin/activate
pip install "numpy<2" --force-reinstall
```

## 📝 Service Configuration

### Environment Variables

#### Prompt Engine
- `QDRANT_HOST=localhost`
- `QDRANT_PORT=6333`

#### Validation Service
- None required (uses Flask defaults)

#### Autonomous Agent
- `VALIDATOR_HOST=localhost`
- `VALIDATOR_PORT=5002`
- `QDRANT_HOST=localhost`
- `QDRANT_PORT=6333`
- `PROMPT_ENGINE_HOST=localhost`
- `PROMPT_ENGINE_PORT=5000`

These are set automatically by `start_agent.sh`.

## 🎯 Testing the System

### 1. Quick Smoke Test
```bash
# After starting all services, run:
curl http://localhost:5000/status  # Should return JSON
curl http://localhost:5002/health  # Should return {"status":"healthy"}
curl http://localhost:5001/status  # Should return JSON with validation status
```

### 2. Full Pipeline Test
1. Open http://localhost:5001/simple
2. Click "Load Example"
3. Click "Full RAG Pipeline"
4. Check for:
   - ✅ Analysis results with insights and recommendations
   - ✅ Validation results showing quality score
   - ✅ No "Validation Unavailable" warning

### 3. Validation Integration Test
```bash
curl -s http://localhost:5001/validation/status | python3 -m json.tool
```
Should show:
- `"integration_initialized": true`
- `"blocking_validation_enabled": true`
- `"validation_service_available": true`

## 📊 Service Logs

When using `start_all_services.sh`, logs are saved to:
```
logs/
├── prompt_engine.log
├── validation_service.log
└── autonomous_agent.log
```

View logs:
```bash
tail -f logs/prompt_engine.log
tail -f logs/validation_service.log
tail -f logs/autonomous_agent.log
```

## 🔐 Python Virtual Environments

All services use Python 3.12 with isolated virtual environments:

| Service | Virtual Environment | Location |
|---------|-------------------|----------|
| Prompt Engine | `prompt/` | `/Users/naveen/Pictures/prompt-engine/prompt/` |
| Validation Service | `venv/` | `/Users/naveen/Pictures/prompt-engine/validation-llm/venv/` |
| Autonomous Agent | `agent/` | `/Users/naveen/Pictures/prompt-engine/autonomous-agent/agent/` |

## 🚨 Common Issues

### "Port already in use"
**Solution**: Run `./stop_all_services.sh` first

### "Connection refused" to Qdrant
**Solution**: Start Qdrant with `./start_qdrant.sh`

### "Validation Unavailable"
**Solution**: 
1. Check validation service: `curl http://localhost:5002/health`
2. Restart in order: Validation → Agent

### Services start but won't respond
**Solution**: 
1. Check the terminal windows for error messages
2. Verify virtual environments are activated
3. Check logs in `logs/` directory

## 📚 Additional Resources

- **Architecture**: See `techincal-archi.md`
- **Qdrant Setup**: See `QUICKSTART_QDRANT.md`
- **Validation Integration**: See `BLOCKING_VALIDATION_INTEGRATION.md`
- **Testing Guide**: See `TESTING_GUIDE.md`

## ⚙️ Script Reference

### start_all_services.sh
- Opens 3 new terminal windows
- Starts services with proper venvs
- Waits for each service to be ready
- Validates full system health
- **Use when**: Starting fresh or after system restart

### stop_all_services.sh
- Stops all Python server processes
- Kills processes by port and name
- Releases all service ports
- Shows final cleanup status
- **Use when**: Need to restart or shutdown system

### start_agent.sh
- Starts only the autonomous agent
- Sets environment variables for local development
- Connects to localhost services
- **Use when**: Restarting just the agent

---

**Last Updated**: 2025-11-10  
**Python Version**: 3.12.11  
**System**: macOS (Darwin 24.6.0)

