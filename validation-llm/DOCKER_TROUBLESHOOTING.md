# 🔧 Docker Troubleshooting Guide for Validation Service

## 🚨 Common Issue: "Connection refused to localhost:11434"

### Problem
The validation service is trying to connect to `localhost:11434` instead of the Docker service `ollama:11434`.

### Root Cause
The environment variable `OLLAMA_HOST` is not being set correctly or the service is not using it properly.

### ✅ Solution

#### 1. Check Environment Variables
```bash
# Verify environment variables in the container
docker exec paytechneodemo-validator env | grep OLLAMA
```

Should show:
```
OLLAMA_HOST=http://ollama:11434
OLLAMA_PORT=11434
```

#### 2. Fixed Docker Compose Configuration
The `docker-compose.yml` has been updated to include the full URL:
```yaml
environment:
  - OLLAMA_HOST=http://ollama:11434  # Full URL with protocol
```

#### 3. Test Network Connectivity
```bash
# Test if validator can reach ollama
docker exec paytechneodemo-validator curl -sf http://ollama:11434/api/tags

# Test if validator can reach qdrant
docker exec paytechneodemo-validator curl -sf http://qdrant:6333/collections
```

## 🔍 Diagnostic Tools

### 1. Environment Test Script
Run inside the container:
```bash
docker exec paytechneodemo-validator python test-docker-env.py
```

### 2. Debug Script
Run from host:
```bash
cd validation-llm
chmod +x debug-docker.sh
./debug-docker.sh
```

### 3. Manual Model Setup
If models are missing:
```bash
cd validation-llm
chmod +x setup-models-docker.sh
./setup-models-docker.sh
```

## 🚀 Step-by-Step Resolution

### Step 1: Rebuild the Validator Image
```bash
cd validation-llm
./build-docker.sh
```

### Step 2: Restart the Stack
```bash
docker-compose down
docker-compose up -d
```

### Step 3: Wait for Services to Initialize
```bash
# Watch the logs
docker logs -f paytechneodemo-validator
```

### Step 4: Verify Services
```bash
# Check all services are up
docker-compose ps

# Test validator health
curl http://localhost:5002/health

# Test validation endpoint
curl http://localhost:5001/validation/status
```

## 📋 Verification Checklist

- [ ] All containers are running (`docker-compose ps`)
- [ ] Ollama is accessible from validator container
- [ ] Qdrant is accessible from validator container
- [ ] Environment variables are set correctly
- [ ] Required models are installed in Ollama
- [ ] Validator service health check passes
- [ ] Autonomous agent can reach validator service

## 🔧 Advanced Troubleshooting

### Check Container Logs
```bash
# Validator logs
docker logs paytechneodemo-validator

# Ollama logs
docker logs paytechneodemo-ollama

# Qdrant logs
docker logs paytechneodemo-qdrant
```

### Network Inspection
```bash
# List networks
docker network ls

# Inspect the network
docker network inspect paytechneodemo-network
```

### Manual Service Testing
```bash
# Enter validator container
docker exec -it paytechneodemo-validator bash

# Test connections manually
curl http://ollama:11434/api/tags
curl http://qdrant:6333/collections

# Check environment
env | grep -E "(OLLAMA|QDRANT|VALIDATION)"
```

## 🆘 Emergency Recovery

### Complete Reset
```bash
# Stop everything
docker-compose down -v

# Remove old images (optional)
docker rmi paytechneodemo/validator:latest

# Rebuild and restart
cd validation-llm
./build-docker.sh
cd ..
docker-compose up -d
```

### Model Reinstallation
```bash
# Access Ollama container directly
docker exec -it paytechneodemo-ollama ollama pull llama3.2:3b
docker exec -it paytechneodemo-ollama ollama pull llama3.2:1b

# Verify models
docker exec paytechneodemo-ollama ollama list
```

## 📊 Expected Behavior

### Successful Startup Logs
```
🚀 Starting Validation LLM Service...
⏳ Waiting for dependencies...
✅ Ollama is ready at http://ollama:11434
✅ Qdrant is ready at http://qdrant:6333
✅ Environment configuration test passed
✅ All imports successful
🎉 Starting validation server...
```

### Working Health Check
```bash
$ curl http://localhost:5002/health
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "llm_validator": "active",
    "vector_db": "connected"
  }
}
```

## 💡 Prevention Tips

1. **Always use full URLs** in environment variables (including `http://`)
2. **Wait for dependencies** before starting dependent services
3. **Use health checks** to ensure services are ready
4. **Test environment** configuration before starting main application
5. **Monitor logs** during startup for early error detection

## 🎯 Quick Fix Commands

```bash
# Quick restart
docker-compose restart validator

# Force rebuild and restart
docker-compose up -d --build validator

# Check if models are available
docker exec paytechneodemo-ollama ollama list

# Test validator connectivity
docker exec paytechneodemo-validator python test-docker-env.py
```

## 📞 Still Having Issues?

If the problem persists:

1. **Check the logs** first: `docker logs paytechneodemo-validator`
2. **Run the debug script**: `./validation-llm/debug-docker.sh`
3. **Verify network connectivity** between containers
4. **Ensure models are properly installed** in Ollama
5. **Try a complete reset** with `docker-compose down -v` and restart

The issue should now be resolved with the updated Docker configuration! 🎉
