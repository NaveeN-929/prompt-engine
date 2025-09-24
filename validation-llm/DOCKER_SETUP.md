# 🐳 Docker Setup for Validation LLM Service

## 📋 Overview

This document provides comprehensive Docker setup instructions for the Validation LLM Service, including standalone deployment and integration with the PaytechNeoDemo stack.

## 🏗️ Docker Files Structure

```
validation-llm/
├── Dockerfile                     # Main container definition
├── .dockerignore                 # Files to exclude from build context
├── docker-compose.yml            # Standalone deployment (removed)
├── requirements.txt              # Python dependencies
└── DOCKER_SETUP.md              # This documentation
```

## 🐳 Dockerfile Features

### Multi-Stage Build
- **Builder Stage**: Compiles dependencies with build tools
- **Runtime Stage**: Minimal production image without build dependencies
- **Size Optimization**: Reduces final image size significantly

### Security Features
- **Non-root User**: Runs as `validator` user (UID 1001)
- **Minimal Base**: Uses `python:3.11-slim` for security
- **Read-only Mounts**: Application code mounted read-only in development

### Environment Variables
```dockerfile
ENV VALIDATION_HOST=0.0.0.0
ENV VALIDATION_PORT=5002
ENV OLLAMA_HOST=http://ollama:11434
ENV QDRANT_HOST=qdrant
ENV QDRANT_PORT=6333
```

## 🚀 Integration with PaytechNeoDemo Stack

The validation service has been integrated into the main `docker-compose.paytechneodemo.yml`:

### Service Configuration
```yaml
validator:
  image: paytechneodemo/validator:latest
  container_name: paytechneodemo-validator
  ports:
    - "5002:5002"
  environment:
    - DOCKER_ENV=true
    - VALIDATION_HOST=0.0.0.0
    - VALIDATION_PORT=5002
    - OLLAMA_HOST=ollama
    - OLLAMA_PORT=11434
    - QDRANT_HOST=qdrant
    - QDRANT_PORT=6333
  depends_on:
    - ollama
    - qdrant
  volumes:
    - validator_training_data:/app/training_data
    - validator_logs:/app/logs
```

### Updated Autonomous Agent
The autonomous agent now includes validation service configuration:
```yaml
environment:
  - VALIDATION_HOST=validator
  - VALIDATION_PORT=5002
depends_on:
  - validator  # Added dependency
```

## 🏃‍♂️ Running the Stack

### 1. Build and Deploy
```bash
# Build the validator image
docker build -t paytechneodemo/validator:latest ./validation-llm/

# Start the complete stack
docker-compose -f docker-compose.paytechneodemo.yml up -d
```

### 2. Verify Services
```bash
# Check all services
docker-compose -f docker-compose.paytechneodemo.yml ps

# Check validator logs
docker logs paytechneodemo-validator

# Test validator health
curl http://localhost:5002/health
```

### 3. Service URLs
- **Autonomous Agent**: http://localhost:5001
- **Prompt Engine**: http://localhost:5000
- **Validator Service**: http://localhost:5002
- **Ollama**: http://localhost:11434
- **Qdrant**: http://localhost:6333

## 📊 Service Dependencies

```
┌─────────────────┐    ┌─────────────────┐
│ Autonomous      │───▶│ Validator       │
│ Agent           │    │ Service         │
│ (port 5001)     │    │ (port 5002)     │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ Prompt Engine   │    │ Ollama LLM      │
│ (port 5000)     │    │ (port 11434)    │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
         ┌─────────────────────────┐
         │ Qdrant Vector DB        │
         │ (ports 6333, 6334)     │
         └─────────────────────────┘
```

## 💾 Data Persistence

### Volumes Created
- `validator_training_data`: Stores training data and exports
- `validator_logs`: Application logs
- `ollama_data`: Shared LLM models
- `qdrant_data`: Shared vector database storage

### Data Locations
```
/app/training_data/
├── exemplary/          # High-quality training samples
├── high_quality/       # Good training samples
├── acceptable/         # Acceptable training samples
└── exports/           # Training data exports

/app/logs/             # Application logs
```

## 🔧 Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `VALIDATION_HOST` | `0.0.0.0` | Bind address |
| `VALIDATION_PORT` | `5002` | Service port |
| `OLLAMA_HOST` | `ollama` | Ollama service host |
| `QDRANT_HOST` | `qdrant` | Qdrant service host |
| `DOCKER_ENV` | `false` | Docker environment flag |
| `FLASK_DEBUG` | `false` | Flask debug mode |

### Health Checks
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3
- **Start Period**: 60 seconds (allows for model loading)
- **Endpoint**: `http://localhost:5002/health`

## 🐛 Troubleshooting

### Common Issues

#### 1. Service Not Starting
```bash
# Check logs
docker logs paytechneodemo-validator

# Check dependencies
docker-compose -f docker-compose.paytechneodemo.yml ps
```

#### 2. Model Loading Issues
```bash
# Check Ollama connection
curl http://localhost:11434/api/tags

# Verify models are available
docker exec paytechneodemo-ollama ollama list
```

#### 3. Validation Service Unavailable
```bash
# Test validation endpoint
curl http://localhost:5002/health

# Check network connectivity
docker exec paytechneodemo-autonomous-agent ping validator
```

### Debug Mode
Enable debug logging:
```yaml
environment:
  - FLASK_DEBUG=true
  - LOG_LEVEL=DEBUG
```

## 📈 Monitoring

### Health Endpoints
- **Validator**: `GET /health`
- **Detailed Status**: `GET /validation/status`
- **System Status**: `GET /system/status`

### Metrics
- Validation success/failure rates
- Response times
- Training data collection stats
- Service availability

## 🔄 Updates and Maintenance

### Updating the Service
```bash
# Pull latest image
docker pull paytechneodemo/validator:latest

# Restart service
docker-compose -f docker-compose.paytechneodemo.yml restart validator
```

### Backup Training Data
```bash
# Backup training data volume
docker run --rm -v validator_training_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/validator-training-data-backup.tar.gz -C /data .
```

### Log Rotation
Logs are automatically rotated by Docker. Configure in compose file:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🎯 Production Considerations

### Resource Limits
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 1G
```

### Security
- Run as non-root user ✅
- Use secrets for sensitive data
- Enable TLS for external access
- Regular security updates

### Scaling
- Horizontal scaling supported
- Load balancer configuration needed
- Shared storage for training data

## ✅ Verification Checklist

- [ ] Validator service starts successfully
- [ ] Health check passes
- [ ] Can connect to Ollama
- [ ] Can connect to Qdrant
- [ ] Autonomous agent can reach validator
- [ ] Validation endpoints respond
- [ ] Training data persists
- [ ] Logs are written
- [ ] Service restarts on failure

## 🎉 Success!

The validation service is now fully dockerized and integrated with the PaytechNeoDemo stack! The complete system provides:

- 🔒 **Blocking Validation**: Quality gates for all responses
- 📊 **Real-time Monitoring**: Health checks and status endpoints
- 💾 **Data Persistence**: Training data and logs preserved
- 🔄 **Auto-restart**: Service resilience and reliability
- 🏗️ **Production Ready**: Multi-stage builds and security hardening
