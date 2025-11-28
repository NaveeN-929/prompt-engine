# 🔐 Data Services - Quick Start Guide

## 📦 What's Been Created

Two new microservices have been added to your project:

### 1. Pseudonymization Service (Port 8001)
Securely anonymizes sensitive financial data while maintaining data utility.

**Location:** `pseudonymization-service/`

**Features:**
- HMAC-based identifier pseudonymization
- Deterministic amount obfuscation
- Date shifting while preserving relationships
- Transaction description categorization
- Bulk processing support
- Key management and rotation

### 2. Repersonalization Service (Port 8002)
Restores original data from pseudonymized versions.

**Location:** `repersonalization-service/`

**Features:**
- Secure data restoration
- Integrity verification
- Bulk repersonalization
- GDPR-compliant cleanup
- Audit trail support
- Service connectivity monitoring

## 🚀 Quick Start (3 Steps)

### Step 1: Start the Services

```bash
# From project root
./start_data_services.sh
```

This will:
- Build Docker images for both services
- Start services with shared key storage
- Perform health checks
- Display service endpoints

### Step 2: Test the Services

```bash
# Run the test suite
python3 test_data_services.py
```

This will demonstrate:
- Single pseudonymization workflow
- Bulk processing
- Data integrity verification
- Service statistics

### Step 3: Explore the APIs

Open in your browser:
- **Pseudonymization API**: http://localhost:8001/docs
- **Repersonalization API**: http://localhost:8002/docs

## 📁 Project Structure

```
prompt-engine/
├── pseudonymization-service/
│   ├── app/
│   │   ├── main.py                    # FastAPI application
│   │   ├── config.py                  # Configuration
│   │   └── core/
│   │       ├── pseudonymizer.py       # Core logic
│   │       └── key_manager.py         # Key management
│   ├── keys/                          # Secure key storage (shared)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .gitignore
│   └── README.md
│
├── repersonalization-service/
│   ├── app/
│   │   ├── main.py                    # FastAPI application
│   │   ├── config.py                  # Configuration
│   │   └── core/
│   │       ├── repersonalizer.py      # Core logic
│   │       └── key_manager.py         # Key management
│   ├── keys/                          # Secure key storage (shared)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .gitignore
│   └── README.md
│
├── docker-compose.data-services.yml   # Combined deployment
├── start_data_services.sh             # Startup script
├── stop_data_services.sh              # Shutdown script
├── test_data_services.py              # Test suite
├── DATA_SERVICES_GUIDE.md             # Complete documentation
└── DATA_SERVICES_README.md            # This file
```

## 💡 Usage Examples

### Example 1: Python Integration

```python
import requests

# 1. Pseudonymize sensitive data
original_data = {
    "transactions": [{"date": "2025-11-10", "amount": 5000.00, ...}],
    "account_balance": 15000.00,
    "customer_id": "CUST_001"
}

response = requests.post(
    'http://localhost:8001/pseudonymize',
    json=original_data
)

result = response.json()
pseudonym_id = result['pseudonym_id']
safe_data = result['pseudonymized_data']

# 2. Process the safe data
# ... your analysis/ML/processing ...

# 3. Restore original data when needed
response = requests.post(
    'http://localhost:8002/repersonalize',
    json={'pseudonym_id': pseudonym_id}
)

original = response.json()['original_data']
```

### Example 2: With Your Generated Data

```python
import json
from pathlib import Path
import requests

# Process your generated datasets
for data_file in Path('data/generated_data').glob('dataset_*.json'):
    with open(data_file) as f:
        data = json.load(f)
    
    # Pseudonymize
    response = requests.post(
        'http://localhost:8001/pseudonymize',
        json=data
    )
    
    pseudonymized = response.json()['pseudonymized_data']
    
    # Your processing here...
    print(f"Processed {data_file.name} safely")
```

### Example 3: cURL Commands

```bash
# Pseudonymize
curl -X POST http://localhost:8001/pseudonymize \
  -H "Content-Type: application/json" \
  -d @data/generated_data/dataset_0001.json

# Repersonalize (use pseudonym_id from above)
curl -X POST http://localhost:8002/repersonalize \
  -H "Content-Type: application/json" \
  -d '{"pseudonym_id": "your-pseudonym-id-here"}'
```

## 🔧 Management Commands

### Start Services
```bash
./start_data_services.sh
```

### Stop Services
```bash
./stop_data_services.sh
```

### View Logs
```bash
docker-compose -f docker-compose.data-services.yml logs -f

# Or for individual service:
docker-compose -f docker-compose.data-services.yml logs pseudonymization-service
docker-compose -f docker-compose.data-services.yml logs repersonalization-service
```

### Check Health
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
```

### View Statistics
```bash
curl http://localhost:8001/stats
curl http://localhost:8002/stats
```

### Restart Services
```bash
docker-compose -f docker-compose.data-services.yml restart
```

## 📊 Service Features

### Pseudonymization Methods

1. **Identifier Pseudonymization**
   - HMAC-SHA256 based
   - Consistent mapping
   - Format: `PSEUDO_XXXXXXXXXXXXXXXX`

2. **Amount Obfuscation**
   - Deterministic ±10% noise
   - Preserves magnitude and sign
   - Maintains statistical properties

3. **Date Shifting**
   - ±30 days offset
   - Preserves temporal relationships
   - Deterministic transformation

4. **Text Categorization**
   - Maps descriptions to categories
   - Format: `CATEGORY_HASH`
   - Maintains analytical utility

### Security Features

- **Encryption Keys**: 256-bit keys with HMAC
- **Key Storage**: Secure file permissions (600)
- **Key Rotation**: Coordinated rotation support
- **Audit Logging**: Complete operation tracking
- **GDPR Compliance**: Data cleanup endpoints

## 🔗 Integration with Existing Services

These data services can be integrated with your existing prompt-engine:

```python
# In your existing code
from your_module import process_data

def secure_pipeline(customer_data):
    # 1. Pseudonymize before processing
    pseudo_resp = requests.post(
        'http://localhost:8001/pseudonymize',
        json=customer_data
    )
    
    safe_data = pseudo_resp.json()['pseudonymized_data']
    pseudonym_id = pseudo_resp.json()['pseudonym_id']
    
    # 2. Process safely
    results = process_data(safe_data)
    
    # 3. Repersonalize if needed for reporting
    if needs_original:
        repersonal_resp = requests.post(
            'http://localhost:8002/repersonalize',
            json={'pseudonym_id': pseudonym_id}
        )
        original = repersonal_resp.json()['original_data']
        return combine_results(original, results)
    
    return results
```

## 📚 Documentation

- **Complete Guide**: [DATA_SERVICES_GUIDE.md](DATA_SERVICES_GUIDE.md)
- **Pseudonymization Details**: [pseudonymization-service/README.md](pseudonymization-service/README.md)
- **Repersonalization Details**: [repersonalization-service/README.md](repersonalization-service/README.md)
- **API Docs (Interactive)**:
  - Pseudonymization: http://localhost:8001/docs
  - Repersonalization: http://localhost:8002/docs

## 🔒 Security Considerations

### Development
- Keys are auto-generated on first start
- Stored in `keys/` directory (gitignored)
- Shared between services via Docker volume

### Production
- Use proper key management service (AWS KMS, HashiCorp Vault)
- Implement API authentication (JWT, API keys)
- Enable HTTPS/TLS
- Add rate limiting
- Implement audit logging
- Configure firewall rules

## 🧪 Testing

### Run Test Suite
```bash
python3 test_data_services.py
```

### Manual Testing
```bash
# Test with your generated data
curl -X POST http://localhost:8001/pseudonymize \
  -H "Content-Type: application/json" \
  -d @data/generated_data/dataset_0001.json | jq '.'
```

### Load Testing
```bash
# Install locust
pip install locust

# Create locustfile.py (example provided in docs)
locust -f locustfile.py --host=http://localhost:8001
```

## 🆘 Troubleshooting

### Services Won't Start
```bash
# Check Docker
docker ps

# Check logs
docker-compose -f docker-compose.data-services.yml logs

# Rebuild
docker-compose -f docker-compose.data-services.yml up -d --build
```

### Port Conflicts
```bash
# Check if ports are in use
lsof -i :8001
lsof -i :8002

# Change ports in docker-compose.data-services.yml if needed
```

### Key Synchronization Issues
```bash
# Check shared volume
docker volume inspect prompt-engine_shared-keys

# Verify keys exist
docker exec pseudonymization-service ls -la /app/keys
docker exec repersonalization-service ls -la /app/keys
```

## 🎯 Next Steps

1. **Start the services**: `./start_data_services.sh`
2. **Run the tests**: `python3 test_data_services.py`
3. **Explore the APIs**: http://localhost:8001/docs
4. **Read the complete guide**: [DATA_SERVICES_GUIDE.md](DATA_SERVICES_GUIDE.md)
5. **Integrate with your app**: Add pseudonymization to your data pipeline

## 💬 Common Questions

**Q: Do I need both services?**
A: Yes, they work together. Pseudonymization anonymizes data, Repersonalization restores it.

**Q: Can I use just Pseudonymization?**
A: Yes, if you don't need to restore original data. But you won't be able to repersonalize later.

**Q: How secure is this?**
A: Uses industry-standard HMAC-SHA256. For production, integrate with proper key management services.

**Q: Does this affect my existing services?**
A: No, these are independent microservices that run on different ports (8001, 8002).

**Q: Can I scale these services?**
A: Yes, they're stateless. Use Redis/database for shared state in production.

## 🎉 You're Ready!

Your data services are ready to use. Start protecting sensitive data while maintaining analytical utility!

```bash
# Start now
./start_data_services.sh

# Test it
python3 test_data_services.py

# Explore
open http://localhost:8001/docs
```

---

**Built with FastAPI, Docker, and Security Best Practices**

