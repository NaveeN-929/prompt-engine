# Redis Setup for Pseudonymization Services

## 🚨 Critical: Why Redis is Required

The Pseudonymization and Repersonalization services use **Redis** for persistent token storage. Without Redis:

❌ **Problems:**
- Tokens are lost on service restart
- Cannot scale horizontally (multiple instances)
- No TTL/expiration support
- Not production-ready
- Data loss risk

✅ **With Redis:**
- Persistent token storage across restarts
- Horizontal scaling support
- Automatic token expiration (TTL)
- Production-ready architecture
- Shared state between services

---

## 🔧 Installation Options

### Option 1: Install Redis Locally (Recommended for Development)

#### macOS
```bash
# Install via Homebrew
brew install redis

# Start Redis
./start_redis.sh

# Or manually
redis-server --daemonize yes --port 6379 --maxmemory 256mb
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### Windows
```bash
# Use WSL2 or Docker (see Option 2)
```

### Option 2: Docker (Recommended for Production)

```bash
# Quick start
docker run -d \
  --name redis-tokens \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru

# Check status
docker ps | grep redis-tokens
docker logs redis-tokens
```

### Option 3: Docker Compose (Automatic)

Redis is automatically started when using:
```bash
docker-compose -f docker-compose.data-services.yml up -d
```

---

## ✅ Verify Redis is Running

```bash
# Quick check
redis-cli ping
# Should return: PONG

# Full check with stats
python3 check_redis.py

# Manual check
redis-cli info | grep redis_version
```

---

## 🚀 Starting Services with Redis

### Local Mode (Python)
```bash
# 1. Start Redis first
./start_redis.sh

# 2. Start both services
./start_data_services_local.sh

# OR start individually
python3 start_pseudonymization.py
python3 start_repersonalization.py
```

### Docker Mode
```bash
# Redis starts automatically
docker-compose -f docker-compose.data-services.yml up -d
```

---

## 📊 Monitoring Redis

### View Stored Tokens
```bash
# Count pseudonym tokens
redis-cli DBSIZE

# List all pseudonym keys
redis-cli KEYS "pseudonym:*"

# View a specific token (example)
redis-cli GET "pseudonym:a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

### Monitor Real-time Operations
```bash
# Watch all Redis commands in real-time
redis-cli MONITOR

# Get Redis statistics
redis-cli INFO

# Check memory usage
redis-cli INFO memory
```

### Check Token TTL
```bash
# Check time-to-live for a specific token
redis-cli TTL "pseudonym:<your-pseudonym-id>"

# Returns:
#   Positive number: seconds remaining
#   -1: no expiration set
#   -2: key doesn't exist
```

---

## ⚙️ Configuration

### Environment Variables

**Pseudonymization Service:**
```bash
REDIS_URL=redis://localhost:6379    # Redis connection URL
REDIS_TTL=86400                      # Token TTL in seconds (24 hours)
```

**Docker Compose:**
```yaml
environment:
  - REDIS_URL=redis://redis:6379
  - REDIS_TTL=86400
```

### Recommended TTL Values

| Use Case | TTL | Setting |
|----------|-----|---------|
| Development | 1 hour | `REDIS_TTL=3600` |
| Testing | 24 hours | `REDIS_TTL=86400` |
| Production | 7 days | `REDIS_TTL=604800` |
| Long-term | 30 days | `REDIS_TTL=2592000` |

---

## 🔒 Security Best Practices

### 1. Password Protection (Production)
```bash
# Start Redis with password
redis-server --requirepass YOUR_STRONG_PASSWORD

# Update connection URL
REDIS_URL=redis://:YOUR_STRONG_PASSWORD@localhost:6379
```

### 2. Bind to Localhost Only (Development)
```bash
redis-server --bind 127.0.0.1
```

### 3. Disable Dangerous Commands (Production)
```bash
redis-server --rename-command FLUSHDB "" --rename-command FLUSHALL ""
```

### 4. Use TLS (Production)
```bash
REDIS_URL=rediss://localhost:6380  # Note: rediss:// with TLS
```

---

## 🛠️ Troubleshooting

### Problem: "Redis connection failed"

**Solution 1: Check if Redis is running**
```bash
redis-cli ping
# If error, start Redis: ./start_redis.sh
```

**Solution 2: Check port**
```bash
lsof -i :6379
# Should show redis-server
```

**Solution 3: Check logs**
```bash
# If using Docker
docker logs redis-tokens

# If using system Redis
sudo journalctl -u redis-server
```

### Problem: "Connection refused"

**Cause:** Redis not started or wrong URL

**Solution:**
```bash
# Check Redis process
ps aux | grep redis-server

# Check connection
redis-cli -h localhost -p 6379 ping

# Restart Redis
redis-cli shutdown
./start_redis.sh
```

### Problem: "Out of memory" errors

**Solution 1: Increase memory limit**
```bash
redis-cli CONFIG SET maxmemory 512mb
```

**Solution 2: Check eviction policy**
```bash
redis-cli CONFIG GET maxmemory-policy
# Should be: allkeys-lru (least recently used)
```

**Solution 3: Clear old tokens**
```bash
# Manual cleanup
redis-cli FLUSHDB

# Restart services to regenerate
```

### Problem: Services work but tokens not persisting

**Check:** Verify Redis is actually being used
```bash
# Check storage type
curl http://localhost:5003/stats | jq '.storage.storage_type'
# Should return: "redis"
# If "memory", Redis connection failed
```

---

## 🧪 Testing Redis Integration

### Test Script
```bash
# Full system test
python3 test_pii_detection.py

# Redis-specific test
python3 check_redis.py
```

### Manual Test
```python
import redis
import requests

# 1. Check Redis connection
client = redis.from_url("redis://localhost:6379")
print(f"Redis ping: {client.ping()}")

# 2. Pseudonymize some data
data = {
    "customer_id": "CUST_12345",
    "name": "John Doe",
    "email": "john@example.com"
}
response = requests.post("http://localhost:5003/pseudonymize", json=data)
pseudonym_id = response.json()["pseudonym_id"]

# 3. Check if token is in Redis
key = f"pseudonym:{pseudonym_id}"
exists = client.exists(key)
print(f"Token in Redis: {exists}")

# 4. Check TTL
ttl = client.ttl(key)
print(f"Token TTL: {ttl} seconds")
```

---

## 📈 Performance Tuning

### For High-Volume Workloads

**1. Increase connections**
```python
# In redis_storage.py
client = redis.from_url(
    redis_url,
    decode_responses=True,
    max_connections=50  # Increase pool size
)
```

**2. Use Redis Cluster** (for very high scale)
```bash
# Start Redis cluster
redis-cli --cluster create \
  localhost:7000 localhost:7001 localhost:7002 \
  --cluster-replicas 1
```

**3. Enable persistence**
```bash
# RDB snapshots
redis-server --save 60 1000

# AOF (append-only file)
redis-server --appendonly yes
```

---

## 🛑 Stopping Redis

```bash
# Graceful shutdown
redis-cli shutdown

# If using Docker
docker stop redis-tokens
docker rm redis-tokens

# If using system service
sudo systemctl stop redis-server
```

---

## 📚 Additional Resources

- **Redis Documentation:** https://redis.io/documentation
- **Redis Commands:** https://redis.io/commands
- **Redis Best Practices:** https://redis.io/docs/manual/patterns/
- **Redis Python Client:** https://redis-py.readthedocs.io/

---

## ✅ Quick Start Checklist

- [ ] Redis installed (Homebrew/apt/Docker)
- [ ] Redis running (`redis-cli ping` returns `PONG`)
- [ ] Port 6379 accessible
- [ ] `check_redis.py` passes
- [ ] Services started with `./start_data_services_local.sh`
- [ ] Test passed: `python3 test_pii_detection.py`
- [ ] Token storage type is "redis" (check `/stats` endpoint)

---

## 🔗 Related Files

- `start_redis.sh` - Quick Redis startup script
- `check_redis.py` - Redis health check utility
- `pseudonymization-service/app/core/redis_storage.py` - Redis integration
- `docker-compose.data-services.yml` - Docker configuration with Redis

