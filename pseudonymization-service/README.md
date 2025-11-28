# 🔒 Pseudonymization Service

A secure microservice for anonymizing sensitive financial data while maintaining data utility for analysis and processing.

## 🎯 Overview

The Pseudonymization Service provides secure anonymization of financial transaction data, customer information, and other sensitive data. It uses cryptographic techniques to ensure:

- **Reversibility**: Data can be restored by the Repersonalization Service
- **Consistency**: Same inputs always produce same pseudonyms
- **Security**: Uses HMAC-SHA256 for identifier pseudonymization
- **Data Utility**: Preserves data relationships and statistical properties

## ✨ Features

✅ **Secure Pseudonymization** - HMAC-based identifier anonymization  
✅ **Amount Obfuscation** - Adds deterministic noise while preserving magnitude  
✅ **Date Shifting** - Temporal relationships preserved with date offsets  
✅ **Text Categorization** - Transaction descriptions converted to categories  
✅ **Bulk Processing** - Process multiple datasets in one request  
✅ **Key Management** - Secure key storage and rotation  
✅ **RESTful API** - FastAPI with automatic OpenAPI documentation  
✅ **Docker Support** - Containerized deployment ready  

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

# Run the service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# When done, deactivate virtual environment
deactivate
```

### Option 2: Docker

```bash
# Build the image
docker build -t pseudonymization-service .

# Run the container
docker run -p 8001:8001 \
  -v $(pwd)/keys:/app/keys \
  pseudonymization-service
```

### Option 3: Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f
```

## 📡 API Endpoints

### 1. Pseudonymize Data

**POST** `/pseudonymize`

Anonymize financial transaction data.

**Request:**
```json
{
  "transactions": [
    {
      "date": "2025-11-10",
      "amount": 5000.00,
      "type": "credit",
      "description": "Monthly salary"
    }
  ],
  "account_balance": 15000.00,
  "customer_id": "CUST_001",
  "metadata": {}
}
```

**Response:**
```json
{
  "pseudonymized_data": {
    "transactions": [
      {
        "date": "2025-11-15",
        "amount": 5125.50,
        "type": "credit",
        "description": "INCOME_CAT_A_a1b2c3d4e5f6"
      }
    ],
    "account_balance": 15375.00,
    "customer_id": "PSEUDO_A7F3E9D2B1C4F6E8"
  },
  "pseudonym_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-11-11T10:30:00.000000",
  "fields_pseudonymized": [
    "customer_id",
    "transaction.amount",
    "transaction.date",
    "transaction.description",
    "account_balance"
  ],
  "processing_time_ms": 12.5
}
```

### 2. Bulk Pseudonymization

**POST** `/pseudonymize/bulk`

Process multiple datasets at once.

**Request:**
```json
{
  "datasets": [
    {
      "transactions": [...],
      "account_balance": 15000.00,
      "customer_id": "CUST_001"
    },
    {
      "transactions": [...],
      "account_balance": 25000.00,
      "customer_id": "CUST_002"
    }
  ],
  "batch_id": "batch_20251111"
}
```

### 3. Health Check

**GET** `/health`

Check service health and status.

**Response:**
```json
{
  "status": "healthy",
  "service": "pseudonymization-service",
  "version": "1.0.0",
  "timestamp": "2025-11-11T10:30:00.000000",
  "key_manager_status": "operational"
}
```

### 4. Statistics

**GET** `/stats`

Get service usage statistics.

**Response:**
```json
{
  "service": "pseudonymization",
  "statistics": {
    "total_pseudonymized": 150,
    "total_fields_processed": 750,
    "last_pseudonymization": "2025-11-11T10:30:00.000000",
    "active_pseudonyms": 150
  },
  "timestamp": "2025-11-11T10:30:00.000000"
}
```

### 5. Key Rotation

**POST** `/key/rotate`

Rotate encryption keys (admin operation).

⚠️ **Warning**: Coordinate with Repersonalization Service before rotating keys.

## 🔐 Pseudonymization Methods

### 1. Identifier Pseudonymization
- Uses HMAC-SHA256 with secret key
- Consistent: Same ID → Same pseudonym
- Format: `PSEUDO_XXXXXXXXXXXXXXXX`

### 2. Amount Obfuscation
- Adds deterministic ±10% noise
- Preserves sign and magnitude
- Maintains statistical properties

### 3. Date Shifting
- Shifts dates by ±30 days deterministically
- Preserves temporal relationships
- Maintains time series patterns

### 4. Text Categorization
- Maps descriptions to categories
- Format: `CATEGORY_HASH`
- Categories: INCOME_CAT_A, EXPENSE_CAT_B, etc.

## 🏗️ Architecture

```
pseudonymization-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   └── core/
│       ├── __init__.py
│       ├── pseudonymizer.py    # Core pseudonymization logic
│       └── key_manager.py      # Key management
├── keys/                       # Key storage (gitignored)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔗 Integration Example

### Python Client

```python
import requests

# Pseudonymize data
response = requests.post(
    'http://localhost:8001/pseudonymize',
    json={
        'transactions': [...],
        'account_balance': 15000.00,
        'customer_id': 'CUST_001'
    }
)

result = response.json()
pseudonym_id = result['pseudonym_id']
pseudonymized_data = result['pseudonymized_data']

# Process the anonymized data...

# Later, use pseudonym_id with Repersonalization Service
# to restore original data
```

### cURL

```bash
curl -X POST http://localhost:8001/pseudonymize \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [{
      "date": "2025-11-10",
      "amount": 5000.00,
      "type": "credit",
      "description": "Monthly salary"
    }],
    "account_balance": 15000.00,
    "customer_id": "CUST_001"
  }'
```

## 🔒 Security Considerations

### Key Management
- Keys stored with 600 permissions (read/write owner only)
- Uses 256-bit keys for HMAC operations
- Support for key rotation with version tracking
- In production: Use AWS KMS, HashiCorp Vault, or similar

### Data Storage
- Pseudonym mappings stored in-memory (demo)
- Production: Use encrypted Redis or secure database
- Implement TTL for automatic cleanup
- Consider GDPR compliance requirements

### API Security
- Add authentication (JWT, API keys)
- Implement rate limiting
- Use HTTPS in production
- Audit logging for compliance

## 🛠️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PSEUDO_HOST` | `0.0.0.0` | Service host |
| `PSEUDO_PORT` | `8001` | Service port |
| `DEBUG` | `false` | Debug mode |
| `KEY_STORE_PATH` | `./keys/keystore.json` | Key storage path |
| `REPERSONALIZATION_SERVICE_URL` | `http://localhost:8002` | Repersonalization service URL |
| `LOG_LEVEL` | `INFO` | Logging level |

## 📊 Monitoring

### Health Checks

```bash
# Check service health
curl http://localhost:8001/health

# Get statistics
curl http://localhost:8001/stats
```

### Logging

The service logs important events:
- Pseudonymization operations
- Key rotations
- Errors and warnings

## 🧪 Testing

```bash
# Test pseudonymization
curl -X POST http://localhost:8001/pseudonymize \
  -H "Content-Type: application/json" \
  -d @test_data.json

# Check the API documentation
# Open browser: http://localhost:8001/docs
```

## 🔄 Integration with Repersonalization Service

The services work together:

1. **Pseudonymization Service**: Anonymizes data → Returns `pseudonym_id`
2. **Process**: Work with pseudonymized data safely
3. **Repersonalization Service**: Uses `pseudonym_id` → Restores original data

```python
# Full workflow
pseudo_response = requests.post(
    'http://localhost:8001/pseudonymize',
    json=original_data
)

pseudonym_id = pseudo_response.json()['pseudonym_id']
pseudonymized_data = pseudo_response.json()['pseudonymized_data']

# ... process pseudonymized_data ...

# Restore original
repersonal_response = requests.post(
    'http://localhost:8002/repersonalize',
    json={'pseudonym_id': pseudonym_id}
)

original_data = repersonal_response.json()['original_data']
```

## 📝 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 🚀 Production Deployment

### Docker Compose with Both Services

See main `docker-compose.yml` in project root for deploying both Pseudonymization and Repersonalization services together.

### Scaling Considerations

- Stateless design allows horizontal scaling
- Use Redis/database for pseudonym storage
- Implement distributed key management
- Add load balancer for high availability

## 📚 Additional Resources

- [GDPR Pseudonymization Guidelines](https://gdpr.eu/pseudonymization/)
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Support

For issues or questions:
1. Check the logs: `docker-compose logs pseudonymization-service`
2. Verify health: `curl http://localhost:8001/health`
3. Review API docs: http://localhost:8001/docs

---

**🎊 Secure Pseudonymization Service Ready!**

Protect sensitive data while maintaining analytical utility.

