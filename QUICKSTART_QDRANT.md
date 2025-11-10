# Quick Start: Fixing Qdrant Connection Issue

## Problem
Your Python server is getting "Connection refused" when trying to connect to Qdrant at `localhost:6333`.

```
❌ Could not connect to Qdrant at localhost:6333: [Errno 61] Connection refused
```

## Root Cause
The Python server (`server.py`) is running **locally** (outside Docker), but Qdrant needs to be running in a Docker container and accessible on port 6333.

## Solution: Start Qdrant Container

### Option 1: Quick Start Script (Recommended)

Run the automated startup script:

```bash
cd /Users/naveen/Pictures/prompt-engine
./start_qdrant.sh
```

This script will:
- ✅ Check if Docker is running
- ✅ Check if Qdrant container exists
- ✅ Start or create the Qdrant container
- ✅ Verify connection
- ✅ Show you the dashboard URL

### Option 2: Manual Docker Commands

If you prefer manual control:

```bash
# Stop any existing Qdrant containers
docker stop qdrant 2>/dev/null || docker stop paytechneodemo-qdrant 2>/dev/null
docker rm qdrant 2>/dev/null || docker rm paytechneodemo-qdrant 2>/dev/null

# Start fresh Qdrant container
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Wait a few seconds for Qdrant to start
sleep 5

# Test connection
curl http://localhost:6333/collections
```

### Option 3: Using Docker Compose

If you want to run the entire stack with Docker Compose:

```bash
cd /Users/naveen/Pictures/prompt-engine
docker-compose up -d qdrant

# Wait for Qdrant to be ready
sleep 10

# Test connection
curl http://localhost:6333/collections
```

## Verification Steps

### 1. Check if Qdrant is Running

```bash
# Check if container is running
docker ps | grep qdrant

# Should show something like:
# CONTAINER ID   IMAGE                  STATUS         PORTS
# abc123def456   qdrant/qdrant:latest   Up 2 minutes   0.0.0.0:6333->6333/tcp
```

### 2. Test Connection

Run the test script:

```bash
cd /Users/naveen/Pictures/prompt-engine
python3 test_qdrant.py
```

Or test manually:

```bash
# Test HTTP endpoint
curl http://localhost:6333/collections

# Should return JSON like:
# {"result":{"collections":[]}}
```

### 3. Check Qdrant Dashboard

Open in your browser:
```
http://localhost:6333/dashboard
```

You should see the Qdrant web interface.

## Start Your Python Server

Once Qdrant is running and verified:

```bash
cd /Users/naveen/Pictures/prompt-engine
python3 server.py
```

You should now see:

```
✅ Connected to Qdrant at localhost:6333
Starting Fixed UI Server on http://localhost:5000
```

## Troubleshooting

### Issue: "Docker is not running"

**Solution:** Start Docker Desktop application

```bash
# On macOS, you can open Docker Desktop with:
open -a Docker
```

Wait for Docker to fully start (the whale icon in the menu bar should be stable).

### Issue: "Port 6333 already in use"

**Solution:** Find and stop the conflicting process

```bash
# Find what's using port 6333
lsof -i :6333

# Stop the Qdrant container if it's already running
docker stop qdrant
docker rm qdrant

# Or use docker-compose
docker-compose stop qdrant
docker-compose rm -f qdrant
```

### Issue: "Cannot connect even though container is running"

**Solution:** Restart the container

```bash
# Restart Qdrant
docker restart qdrant

# Or recreate it
docker stop qdrant
docker rm qdrant
./start_qdrant.sh
```

### Issue: Container runs but connection still fails

**Solution:** Check if port forwarding is correct

```bash
# Check port mapping
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep qdrant

# Should show:
# qdrant    0.0.0.0:6333->6333/tcp, 0.0.0.0:6334->6334/tcp
```

If ports are not mapped correctly:

```bash
docker stop qdrant
docker rm qdrant
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

## Environment Variables

The connection uses these environment variables (defined in `config.py`):

```python
QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')  # For local development
QDRANT_PORT = int(os.getenv('QDRANT_PORT', '6333'))
```

If you need to change these, create a `.env` file:

```bash
# .env file
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Docker Compose vs Standalone

### Running Python Server Locally (Current Setup)

```
Your Computer
├── Python server.py (localhost:5000) ← Running locally
└── Docker Containers
    └── Qdrant (localhost:6333) ← Accessible via localhost
```

Configuration:
```python
QDRANT_HOST = "localhost"  # ✅ Correct
QDRANT_PORT = 6333
```

### Running Everything in Docker

If you want to run everything in Docker (using `docker-compose.yml`):

```bash
docker-compose up -d
```

Configuration would be:
```python
QDRANT_HOST = "qdrant"  # ✅ Container name in Docker network
QDRANT_PORT = 6333
```

## Quick Commands Reference

```bash
# Start Qdrant
./start_qdrant.sh

# Test connection
python3 test_qdrant.py

# Check Qdrant status
docker ps | grep qdrant

# View Qdrant logs
docker logs qdrant

# Restart Qdrant
docker restart qdrant

# Stop Qdrant
docker stop qdrant

# Remove Qdrant container
docker rm qdrant

# Start your server
python3 server.py

# View Qdrant dashboard
open http://localhost:6333/dashboard
```

## Summary

1. **Start Qdrant**: `./start_qdrant.sh`
2. **Verify**: `python3 test_qdrant.py`
3. **Start Server**: `python3 server.py`
4. **Access App**: Open `http://localhost:5000`

That's it! Your agentic prompt engine should now work with vector database acceleration. 🚀

