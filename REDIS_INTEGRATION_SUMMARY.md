# Redis Integration Summary

## 🎯 What Was Fixed

### Critical Issue Identified
- **Problem:** Services were using **in-memory storage** (`dict`), NOT Redis
- **Impact:** Token loss on restart, no TTL, not production-ready
- **Status:** ✅ **FIXED** - Full Redis integration complete

---

## 📦 Changes Made

### 1. New Files Created

#### `/pseudonymization-service/app/core/redis_storage.py`
- Redis-based token storage with TTL support
- Automatic fallback to in-memory if Redis unavailable
- Connection pooling and error handling
- Token statistics and monitoring

#### `/start_redis.sh`
- Quick Redis startup script for local development
- Checks if Redis already running
- Configures memory limits and eviction policy

#### `/check_redis.py`
- Redis health check utility
- Displays connection status, memory usage, and active tokens
- Tests connectivity before starting services

#### `/start_data_services_local.sh`
- Start both services locally (without Docker)
- Checks Redis availability before starting
- Provides clear error messages and logs

#### `/REDIS_SETUP.md`
- Complete Redis setup guide
- Installation instructions (macOS/Linux/Docker)
- Troubleshooting guide
- Security best practices

---

### 2. Updated Files

#### `requirements.txt` (both services)
```diff
+ redis==5.0.1
```

#### `pseudonymization-service/app/config.py`
```python
# New Redis configuration
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_TTL: int = int(os.getenv("REDIS_TTL", "86400"))  # 24 hours
```

#### `pseudonymization-service/app/core/pseudonymizer.py`
```python
# Before (IN-MEMORY ❌)
self.pseudonym_map = {}

# After (REDIS ✅)
from .redis_storage import RedisStorage
self.storage = RedisStorage(redis_url=redis_url, ttl=redis_ttl)
```

Key changes:
- Replaced `self.pseudonym_map[pseudonym_id] = data` with `self.storage.store(pseudonym_id, data)`
- Replaced `self.pseudonym_map[pseudonym_id]` with `self.storage.retrieve(pseudonym_id)`
- Replaced `del self.pseudonym_map[pseudonym_id]` with `self.storage.delete(pseudonym_id)`
- Added Redis stats to `/stats` endpoint

#### `docker-compose.data-services.yml`
```yaml
services:
  redis:  # NEW SERVICE
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --maxmemory 256mb
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
  
  pseudonymization-service:
    environment:
      - REDIS_URL=redis://redis:6379
      - REDIS_TTL=86400
    depends_on:
      redis:
        condition: service_healthy
  
  repersonalization-service:
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      redis:
        condition: service_healthy

volumes:
  redis-data:  # Persistent storage
```

#### `start_pseudonymization.py` & `start_repersonalization.py`
- Added Redis connectivity check on startup
- Shows warning if Redis unavailable (uses fallback)

---

## 🚀 How to Use

### Quick Start (Local Development)

```bash
# 1. Start Redis
./start_redis.sh

# 2. Check Redis
python3 check_redis.py

# 3. Start both services
./start_data_services_local.sh

# 4. Test PII detection
python3 test_pii_detection.py
```

### Using Docker (Production)

```bash
# Starts Redis + both services automatically
docker-compose -f docker-compose.data-services.yml up -d

# Check logs
docker-compose -f docker-compose.data-services.yml logs -f

# View Redis data
docker exec -it redis-tokens redis-cli
> KEYS pseudonym:*
> DBSIZE
```

---

## ✅ Verification

### Check Redis is Being Used

```bash
# 1. Start services
./start_data_services_local.sh

# 2. Check storage type
curl http://localhost:5003/stats | jq '.storage.storage_type'
# Should return: "redis"

# 3. Pseudonymize some data
curl -X POST http://localhost:5003/pseudonymize \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# 4. Check Redis
redis-cli KEYS "pseudonym:*"
# Should show keys

# 5. Check TTL
redis-cli TTL "pseudonym:<your-id>"
# Should show ~86400 seconds (24 hours)
```

### Check Persistence Across Restarts

```bash
# 1. Pseudonymize data
curl -X POST http://localhost:5003/pseudonymize \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User"}' | jq -r '.pseudonym_id'
# Save the pseudonym_id

# 2. Restart service
pkill -f start_pseudonymization.py
python3 start_pseudonymization.py &

# 3. Try to repersonalize (should still work!)
curl -X POST http://localhost:5004/repersonalize \
  -H "Content-Type: application/json" \
  -d '{"pseudonym_id": "<your-saved-id>"}'
# Should return original data (because it's in Redis!)
```

---

## 📊 Monitoring

### View Active Tokens
```bash
# Count tokens
redis-cli DBSIZE

# List all pseudonym keys
redis-cli KEYS "pseudonym:*"

# Get specific token
redis-cli GET "pseudonym:abc123..."
```

### Monitor Real-time
```bash
# Watch all Redis operations
redis-cli MONITOR

# Check memory usage
redis-cli INFO memory

# View stats from service
curl http://localhost:5003/stats | jq '.storage'
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `REDIS_TTL` | `86400` (24h) | Token time-to-live in seconds |

### TTL Recommendations

| Environment | TTL | Setting |
|-------------|-----|---------|
| Development | 1 hour | `REDIS_TTL=3600` |
| Staging | 24 hours | `REDIS_TTL=86400` |
| Production | 7 days | `REDIS_TTL=604800` |

---

## 🛠️ Troubleshooting

### Services start but use "memory" storage

**Problem:** Redis not available when services start

**Solution:**
```bash
# 1. Check Redis
redis-cli ping

# 2. If not running
./start_redis.sh

# 3. Restart services
pkill -f start_pseudonymization.py
python3 start_pseudonymization.py &
```

### "Redis connection failed"

**Solutions:**
```bash
# Check if Redis is running
redis-cli ping

# Check port is accessible
lsof -i :6379

# Start Redis
./start_redis.sh

# Or use Docker
docker run -d -p 6379:6379 --name redis-tokens redis:7-alpine
```

### Tokens not expiring

**Check TTL:**
```bash
# View TTL for a token
redis-cli TTL "pseudonym:<your-id>"

# Should return positive number (seconds remaining)
# -1 means no expiration (bug)
# -2 means key doesn't exist
```

**Fix:**
```bash
# Restart service with correct TTL
REDIS_TTL=86400 python3 start_pseudonymization.py
```

---

## 🔒 Security

### Production Checklist

- [ ] Redis password enabled (`--requirepass`)
- [ ] Redis bound to private network only
- [ ] TLS enabled for Redis connections
- [ ] Firewall rules restrict Redis access
- [ ] Redis persistence enabled (AOF/RDB)
- [ ] Regular backups of Redis data
- [ ] Monitor Redis memory usage
- [ ] Set appropriate TTL values

### Enable Password Protection
```bash
# Start Redis with password
redis-server --requirepass YOUR_STRONG_PASSWORD

# Update connection URL
export REDIS_URL="redis://:YOUR_STRONG_PASSWORD@localhost:6379"
```

---

## 📈 Performance

### Current Configuration
- **Max Memory:** 256MB
- **Eviction Policy:** allkeys-lru (evict least recently used)
- **Persistence:** AOF (append-only file)

### For High-Volume Workloads
```bash
# Increase memory
redis-server --maxmemory 1gb

# Increase connection pool
# Edit redis_storage.py:
client = redis.from_url(redis_url, max_connections=50)
```

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `start_redis.sh` | Start Redis locally |
| `check_redis.py` | Check Redis health |
| `REDIS_SETUP.md` | Complete setup guide |
| `REDIS_INTEGRATION_SUMMARY.md` | This document |
| `start_data_services_local.sh` | Start services locally |
| `pseudonymization-service/app/core/redis_storage.py` | Redis integration |
| `docker-compose.data-services.yml` | Docker config with Redis |

---

## ✅ Testing

### Run Full Test Suite
```bash
# 1. Check Redis
python3 check_redis.py

# 2. Test PII detection with Redis storage
python3 test_pii_detection.py

# 3. Check stats
curl http://localhost:5003/stats | jq
```

### Expected Output
```json
{
  "storage": {
    "storage_type": "redis",
    "connected": true,
    "ttl_seconds": 86400,
    "active_pseudonyms": 5,
    "redis_info": {
      "used_memory_human": "1.2M",
      "connected_clients": 3,
      "uptime_in_days": 0
    }
  }
}
```

---

## 🎉 Benefits Achieved

✅ **Persistence** - Tokens survive service restarts  
✅ **TTL Support** - Automatic token expiration  
✅ **Scalability** - Multiple service instances can share tokens  
✅ **Production Ready** - Industry-standard architecture  
✅ **Monitoring** - Full visibility into token storage  
✅ **Fallback** - Graceful degradation if Redis unavailable  
✅ **Security** - Centralized token management  

---

## 🔗 Next Steps

1. ✅ Install Redis: `./start_redis.sh`
2. ✅ Verify connection: `python3 check_redis.py`
3. ✅ Start services: `./start_data_services_local.sh`
4. ✅ Test integration: `python3 test_pii_detection.py`
5. 📖 Read full guide: `REDIS_SETUP.md`
6. 🚀 Deploy to production with Docker Compose

