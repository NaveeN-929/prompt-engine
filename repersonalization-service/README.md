# 🔓 Repersonalization Service

A secure microservice for restoring original data from pseudonymized versions, completing the secure data processing pipeline.

## 🎯 Overview

The Repersonalization Service works in tandem with the Pseudonymization Service to enable secure data processing workflows. It:

- **Restores Original Data**: Converts pseudonymized data back to original form
- **Verifies Integrity**: Ensures data consistency throughout the process
- **Maintains Security**: Uses same cryptographic keys as Pseudonymization Service
- **Supports Compliance**: Enables GDPR-compliant data handling

## ✨ Features

✅ **Secure Data Restoration** - Retrieve original data using pseudonym IDs  
✅ **Integrity Verification** - Verify data consistency and completeness  
✅ **Bulk Processing** - Restore multiple datasets in one request  
✅ **Service Integration** - Seamless communication with Pseudonymization Service  
✅ **Audit Support** - Track all repersonalization operations  
✅ **RESTful API** - FastAPI with automatic OpenAPI documentation  
✅ **Docker Support** - Containerized deployment ready  
✅ **GDPR Compliance** - Support for data cleanup and retention policies  

## 🚀 Quick Start

### Option 1: Direct Python (with Virtual Environment)

**Requirements:** Python 3.12

```bash
# Create virtual environment (using Python 3.12)
python3.12 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Ensure Pseudonymization Service is running
# (it needs to be accessible at http://localhost:8001)

# Run the service
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# When done, deactivate virtual environment
deactivate
```

### Option 2: Docker

```bash
# Build the image
docker build -t repersonalization-service .

# Run the container (ensure shared keys volume)
docker run -p 8002:8002 \
  -v $(pwd)/keys:/app/keys \
  -e PSEUDONYMIZATION_SERVICE_URL=http://pseudonymization-service:8001 \
  repersonalization-service
```

### Option 3: Docker Compose (Recommended)

```bash
# Start both services together
docker-compose up -d

# View logs
docker-compose logs -f repersonalization-service
```

## 📡 API Endpoints

### 1. Repersonalize Data

**POST** `/repersonalize`

Restore original data from a pseudonymized version.

**Request:**
```json
{
  "pseudonym_id": "550e8400-e29b-41d4-a716-446655440000",
  "verify": true
}
```

**Response:**
```json
{
  "original_data": {
    "transactions": [
      {
        "date": "2025-11-10",
        "amount": 5000.00,
        "type": "credit",
        "description": "Monthly salary"
      }
    ],
    "account_balance": 15000.00,
    "customer_id": "CUST_001"
  },
  "pseudonym_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-11-11T10:30:00.000000",
  "processing_time_ms": 8.3,
  "verified": true
}
```

### 2. Bulk Repersonalization

**POST** `/repersonalize/bulk`

Restore multiple datasets at once.

**Request:**
```json
{
  "pseudonym_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ],
  "batch_id": "batch_20251111",
  "continue_on_error": true
}
```

**Response:**
```json
{
  "batch_id": "batch_20251111",
  "total_requests": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "index": 0,
      "success": true,
      "pseudonym_id": "550e8400-e29b-41d4-a716-446655440000",
      "original_data": {...},
      "verified": true
    }
  ],
  "processing_time_ms": 25.6,
  "timestamp": "2025-11-11T10:30:00.000000"
}
```

### 3. Health Check

**GET** `/health`

Check service health and connectivity.

**Response:**
```json
{
  "status": "healthy",
  "service": "repersonalization-service",
  "version": "1.0.0",
  "timestamp": "2025-11-11T10:30:00.000000",
  "key_manager_status": "operational",
  "pseudonymization_service_status": "connected"
}
```

### 4. Statistics

**GET** `/stats`

Get service usage statistics.

**Response:**
```json
{
  "service": "repersonalization",
  "statistics": {
    "total_repersonalized": 250,
    "total_failed": 5,
    "last_repersonalization": "2025-11-11T10:30:00.000000",
    "success_rate": 98.04
  },
  "timestamp": "2025-11-11T10:30:00.000000"
}
```

### 5. Cleanup

**DELETE** `/cleanup/{pseudonym_id}`

Remove pseudonym mapping after successful repersonalization (GDPR compliance).

**Response:**
```json
{
  "message": "Pseudonym cleaned up successfully",
  "pseudonym_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-11-11T10:30:00.000000"
}
```

### 6. Verify Pseudonymization

**POST** `/verify`

Verify pseudonymization integrity for auditing.

**Request:**
```json
{
  "pseudonym_id": "550e8400-e29b-41d4-a716-446655440000",
  "pseudonymized_data": {...}
}
```

## 🏗️ Architecture

```
repersonalization-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   └── core/
│       ├── __init__.py
│       ├── repersonalizer.py      # Core repersonalization logic
│       └── key_manager.py         # Key management (synced with pseudo service)
├── keys/                          # Shared key storage (gitignored)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔗 Complete Workflow Example

### Python Integration

```python
import requests

# Step 1: Pseudonymize data
pseudo_response = requests.post(
    'http://localhost:8001/pseudonymize',
    json={
        'transactions': [
            {
                'date': '2025-11-10',
                'amount': 5000.00,
                'type': 'credit',
                'description': 'Monthly salary'
            }
        ],
        'account_balance': 15000.00,
        'customer_id': 'CUST_001'
    }
)

pseudo_result = pseudo_response.json()
pseudonym_id = pseudo_result['pseudonym_id']
pseudonymized_data = pseudo_result['pseudonymized_data']

print(f"Data pseudonymized with ID: {pseudonym_id}")
print(f"Pseudonymized customer: {pseudonymized_data['customer_id']}")

# Step 2: Process the pseudonymized data safely
# ... do your analysis, ML, etc. on pseudonymized_data ...

# Step 3: Repersonalize when needed
repersonal_response = requests.post(
    'http://localhost:8002/repersonalize',
    json={
        'pseudonym_id': pseudonym_id,
        'verify': True
    }
)

repersonal_result = repersonal_response.json()
original_data = repersonal_result['original_data']

print(f"Data restored: {original_data['customer_id']}")
print(f"Verified: {repersonal_result['verified']}")

# Step 4: Clean up (optional, for GDPR compliance)
cleanup_response = requests.delete(
    f'http://localhost:8002/cleanup/{pseudonym_id}'
)

print("Pseudonym cleaned up")
```

### cURL Examples

```bash
# Repersonalize data
curl -X POST http://localhost:8002/repersonalize \
  -H "Content-Type: application/json" \
  -d '{
    "pseudonym_id": "550e8400-e29b-41d4-a716-446655440000",
    "verify": true
  }'

# Bulk repersonalization
curl -X POST http://localhost:8002/repersonalize/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "pseudonym_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "660e8400-e29b-41d4-a716-446655440001"
    ],
    "continue_on_error": true
  }'

# Check health
curl http://localhost:8002/health

# Get statistics
curl http://localhost:8002/stats

# Cleanup pseudonym
curl -X DELETE http://localhost:8002/cleanup/550e8400-e29b-41d4-a716-446655440000
```

## 🔐 Security Features

### Key Synchronization
- Shares encryption keys with Pseudonymization Service
- Uses same key version for consistency
- Supports key rotation (coordinated with pseudo service)

### Data Verification
- Validates data structure and completeness
- Checks all required fields are present
- Verifies numeric and date fields

### Audit Trail
- Logs all repersonalization operations
- Tracks success/failure rates
- Provides statistics for compliance reporting

## 🛠️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REPERSONAL_HOST` | `0.0.0.0` | Service host |
| `REPERSONAL_PORT` | `8002` | Service port |
| `DEBUG` | `false` | Debug mode |
| `KEY_STORE_PATH` | `./keys/keystore.json` | Key storage path (shared) |
| `PSEUDONYMIZATION_SERVICE_URL` | `http://localhost:8001` | Pseudonymization service URL |
| `LOG_LEVEL` | `INFO` | Logging level |

### Key Sharing

The Repersonalization Service must share keys with the Pseudonymization Service:

```bash
# Option 1: Shared volume (Docker)
docker-compose up  # keys automatically shared

# Option 2: Manual sync
cp ../pseudonymization-service/keys/* ./keys/
```

## 📊 Monitoring

### Health Monitoring

```bash
# Check service health
curl http://localhost:8002/health

# Check connectivity to Pseudonymization Service
curl http://localhost:8002/health | jq '.pseudonymization_service_status'

# Get performance statistics
curl http://localhost:8002/stats
```

### Logging

Important events logged:
- Successful repersonalizations
- Failed attempts with reasons
- Data verification results
- Service connectivity issues

## 🧪 Testing

### Test Repersonalization Flow

```bash
# 1. First, pseudonymize some data
PSEUDO_ID=$(curl -X POST http://localhost:8001/pseudonymize \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [{
      "date": "2025-11-10",
      "amount": 5000.00,
      "type": "credit",
      "description": "Test transaction"
    }],
    "account_balance": 15000.00,
    "customer_id": "TEST_001"
  }' | jq -r '.pseudonym_id')

echo "Pseudonym ID: $PSEUDO_ID"

# 2. Now repersonalize it
curl -X POST http://localhost:8002/repersonalize \
  -H "Content-Type: application/json" \
  -d "{
    \"pseudonym_id\": \"$PSEUDO_ID\",
    \"verify\": true
  }" | jq '.'
```

### API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

## 🚀 Production Deployment

### Docker Compose (Both Services)

```yaml
version: '3.8'

services:
  pseudonymization-service:
    build: ./pseudonymization-service
    ports:
      - "8001:8001"
    volumes:
      - shared-keys:/app/keys
    environment:
      - KEY_STORE_PATH=/app/keys/keystore.json

  repersonalization-service:
    build: ./repersonalization-service
    ports:
      - "8002:8002"
    volumes:
      - shared-keys:/app/keys
    environment:
      - KEY_STORE_PATH=/app/keys/keystore.json
      - PSEUDONYMIZATION_SERVICE_URL=http://pseudonymization-service:8001
    depends_on:
      - pseudonymization-service

volumes:
  shared-keys:
```

### Kubernetes Deployment

- Use Kubernetes Secrets for key management
- Deploy both services in same namespace
- Use Service mesh for secure communication
- Implement pod-to-pod encryption

### High Availability

- Deploy multiple replicas
- Use Redis/database for shared state
- Implement circuit breakers
- Add health check probes

## 🔒 Compliance Features

### GDPR Compliance

- **Right to Erasure**: Use `/cleanup` endpoint
- **Data Minimization**: Only store necessary mappings
- **Audit Trail**: Complete logging of operations
- **Data Verification**: Integrity checks at each step

### Data Retention

```python
# Implement TTL for pseudonym mappings
# In production, use Redis with expiration

PSEUDONYM_TTL = 24 * 60 * 60  # 24 hours

# Or implement scheduled cleanup
@app.on_event("startup")
async def schedule_cleanup():
    # Clean up pseudonyms older than TTL
    pass
```

## 🤝 Service Dependencies

### Required Services
- **Pseudonymization Service**: Must be running and accessible
- **Shared Key Storage**: Both services must access same keys

### Optional Enhancements
- **Redis**: For distributed pseudonym storage
- **PostgreSQL**: For audit logging
- **Vault**: For secure key management
- **Prometheus**: For metrics collection

## 📚 Additional Resources

- [Pseudonymization Service Documentation](../pseudonymization-service/README.md)
- [GDPR Compliance Guidelines](https://gdpr.eu/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤔 Troubleshooting

### Service Unreachable

```bash
# Check health
curl http://localhost:8002/health

# Check Pseudonymization Service connectivity
curl http://localhost:8001/health
```

### Key Synchronization Issues

```bash
# Verify keys are shared
ls -la keys/

# Check key manager status
curl http://localhost:8002/health | jq '.key_manager_status'
```

### Failed Repersonalization

```bash
# Check logs
docker-compose logs repersonalization-service

# Verify pseudonym ID exists
curl http://localhost:8001/stats
```

---

**🎊 Secure Repersonalization Service Ready!**

Complete the secure data processing pipeline with confidence.

