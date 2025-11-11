# 🔐 Data Services Guide

Complete guide for Pseudonymization and Repersonalization Services

## 📋 Overview

This project includes two complementary microservices for secure data handling:

1. **Pseudonymization Service** (Port 8001) - Anonymizes sensitive data
2. **Repersonalization Service** (Port 8002) - Restores original data

Together, they enable secure data processing pipelines while maintaining compliance with privacy regulations like GDPR.

## 🎯 Use Cases

### 1. Secure Data Analytics
```
Original Data → Pseudonymize → Analyze Safely → Repersonalize → Report
```

### 2. Machine Learning Training
```
Customer Data → Pseudonymize → Train Model → Validate → Repersonalize Results
```

### 3. Third-Party Data Sharing
```
Internal Data → Pseudonymize → Share with Partner → Process → Return Pseudonymized → Repersonalize
```

### 4. Compliance Testing
```
Production Data → Pseudonymize → Test Environment → Development/QA → Cleanup
```

## 🚀 Quick Start

### Option 1: Start Both Services Together (Recommended)

```bash
# From project root
docker-compose -f docker-compose.data-services.yml up -d

# Check status
docker-compose -f docker-compose.data-services.yml ps

# View logs
docker-compose -f docker-compose.data-services.yml logs -f
```

### Option 2: Start Services Individually

```bash
# Start Pseudonymization Service
cd pseudonymization-service
docker-compose up -d

# Start Repersonalization Service (in another terminal)
cd repersonalization-service
docker-compose up -d
```

### Option 3: Local Development

```bash
# Terminal 1: Pseudonymization Service
cd pseudonymization-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Repersonalization Service
cd repersonalization-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## 📡 Service Endpoints

### Pseudonymization Service (Port 8001)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information |
| `/health` | GET | Health check |
| `/pseudonymize` | POST | Pseudonymize data |
| `/pseudonymize/bulk` | POST | Bulk pseudonymization |
| `/stats` | GET | Service statistics |
| `/key/rotate` | POST | Rotate encryption keys |
| `/docs` | GET | Interactive API documentation |

### Repersonalization Service (Port 8002)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information |
| `/health` | GET | Health check |
| `/repersonalize` | POST | Restore original data |
| `/repersonalize/bulk` | POST | Bulk repersonalization |
| `/cleanup/{id}` | DELETE | Clean up pseudonym |
| `/verify` | POST | Verify pseudonymization |
| `/stats` | GET | Service statistics |
| `/docs` | GET | Interactive API documentation |

## 💡 Complete Workflow Examples

### Example 1: Basic Pseudonymization and Repersonalization

```python
import requests
import json

# Original financial data
original_data = {
    "transactions": [
        {
            "date": "2025-11-10",
            "amount": 5000.00,
            "type": "credit",
            "description": "Monthly salary"
        },
        {
            "date": "2025-11-12",
            "amount": -150.00,
            "type": "debit",
            "description": "Grocery shopping"
        }
    ],
    "account_balance": 15000.00,
    "customer_id": "CUST_12345"
}

# Step 1: Pseudonymize
print("🔒 Step 1: Pseudonymizing data...")
pseudo_response = requests.post(
    'http://localhost:8001/pseudonymize',
    json=original_data
)

pseudo_result = pseudo_response.json()
pseudonym_id = pseudo_result['pseudonym_id']
pseudonymized_data = pseudo_result['pseudonymized_data']

print(f"✅ Pseudonymized successfully!")
print(f"   Pseudonym ID: {pseudonym_id}")
print(f"   Original Customer: {original_data['customer_id']}")
print(f"   Pseudonymized Customer: {pseudonymized_data['customer_id']}")
print(f"   Fields pseudonymized: {', '.join(pseudo_result['fields_pseudonymized'])}")

# Step 2: Process pseudonymized data safely
print("\n🔬 Step 2: Processing pseudonymized data...")
# Your analysis/ML/processing here
# The data is now safe to use in any environment
processed_results = {
    "analysis": "Safe to perform any analysis",
    "risk_score": 0.75,
    "category": "low_risk"
}
print(f"✅ Processing complete: {processed_results}")

# Step 3: Repersonalize when needed
print("\n🔓 Step 3: Repersonalizing data...")
repersonal_response = requests.post(
    'http://localhost:8002/repersonalize',
    json={
        'pseudonym_id': pseudonym_id,
        'verify': True
    }
)

repersonal_result = repersonal_response.json()
restored_data = repersonal_result['original_data']

print(f"✅ Repersonalized successfully!")
print(f"   Restored Customer: {restored_data['customer_id']}")
print(f"   Verified: {repersonal_result['verified']}")
print(f"   Processing time: {repersonal_result['processing_time_ms']:.2f}ms")

# Step 4: Clean up (GDPR compliance)
print("\n🧹 Step 4: Cleaning up...")
cleanup_response = requests.delete(
    f'http://localhost:8002/cleanup/{pseudonym_id}'
)
print("✅ Pseudonym cleaned up!")

print("\n🎉 Complete workflow finished!")
```

### Example 2: Bulk Processing

```python
import requests
from pathlib import Path
import json

# Load multiple datasets from your data directory
data_files = list(Path('data/generated_data').glob('dataset_*.json'))
datasets = []

for file in data_files[:10]:  # Process first 10
    with open(file) as f:
        datasets.append(json.load(f))

# Bulk pseudonymize
print(f"🔒 Pseudonymizing {len(datasets)} datasets...")
pseudo_response = requests.post(
    'http://localhost:8001/pseudonymize/bulk',
    json={
        'datasets': datasets,
        'batch_id': 'batch_001'
    }
)

bulk_result = pseudo_response.json()
print(f"✅ Bulk pseudonymization complete!")
print(f"   Successful: {bulk_result['successful']}")
print(f"   Failed: {bulk_result['failed']}")

# Extract pseudonym IDs
pseudonym_ids = [
    r['pseudonym_id'] for r in bulk_result['results'] 
    if r['success']
]

# Process the pseudonymized data...
# ... your analysis here ...

# Bulk repersonalize
print(f"\n🔓 Repersonalizing {len(pseudonym_ids)} datasets...")
repersonal_response = requests.post(
    'http://localhost:8002/repersonalize/bulk',
    json={
        'pseudonym_ids': pseudonym_ids,
        'batch_id': 'batch_001',
        'continue_on_error': True
    }
)

repersonal_result = repersonal_response.json()
print(f"✅ Bulk repersonalization complete!")
print(f"   Successful: {repersonal_result['successful']}")
print(f"   Failed: {repersonal_result['failed']}")
```

### Example 3: Integration with Existing Data Pipeline

```python
import requests

def secure_data_pipeline(input_data):
    """
    Secure data processing pipeline
    """
    # 1. Pseudonymize
    pseudo_response = requests.post(
        'http://localhost:8001/pseudonymize',
        json=input_data
    )
    
    if pseudo_response.status_code != 200:
        raise Exception("Pseudonymization failed")
    
    pseudo_result = pseudo_response.json()
    pseudonym_id = pseudo_result['pseudonym_id']
    safe_data = pseudo_result['pseudonymized_data']
    
    # 2. Process (your existing logic)
    processed_results = your_analysis_function(safe_data)
    
    # 3. Repersonalize results if needed
    if needs_original_data:
        repersonal_response = requests.post(
            'http://localhost:8002/repersonalize',
            json={'pseudonym_id': pseudonym_id}
        )
        
        original_data = repersonal_response.json()['original_data']
        
        # Combine results with original data
        final_results = combine_results(original_data, processed_results)
    else:
        final_results = processed_results
    
    # 4. Cleanup
    requests.delete(f'http://localhost:8002/cleanup/{pseudonym_id}')
    
    return final_results

# Use in your pipeline
from pathlib import Path
import json

for data_file in Path('data/generated_data').glob('dataset_*.json'):
    with open(data_file) as f:
        data = json.load(f)
    
    results = secure_data_pipeline(data)
    print(f"Processed {data_file}: {results}")
```

## 🔒 Security Best Practices

### 1. Key Management

```bash
# Ensure keys are properly secured
chmod 600 pseudonymization-service/keys/*
chmod 600 repersonalization-service/keys/*

# In production, use proper key management services
# - AWS KMS
# - HashiCorp Vault
# - Azure Key Vault
```

### 2. Network Security

```bash
# Use internal networks for service communication
# Add to docker-compose.data-services.yml:
networks:
  internal:
    internal: true  # No external access
```

### 3. Authentication

```python
# Add API key authentication (example)
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = "your-secure-api-key"
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

### 4. Data Retention

```python
# Implement automatic cleanup after TTL
import asyncio
from datetime import datetime, timedelta

async def cleanup_old_pseudonyms():
    """Clean up pseudonyms older than 24 hours"""
    while True:
        # Get old pseudonym IDs
        old_pseudonyms = get_pseudonyms_older_than(hours=24)
        
        for pseudonym_id in old_pseudonyms:
            await cleanup_pseudonym(pseudonym_id)
        
        await asyncio.sleep(3600)  # Run every hour
```

## 📊 Monitoring and Health Checks

### Health Check Script

```bash
#!/bin/bash
# health_check.sh

echo "🏥 Checking Data Services Health..."

# Check Pseudonymization Service
PSEUDO_HEALTH=$(curl -s http://localhost:8001/health | jq -r '.status')
if [ "$PSEUDO_HEALTH" = "healthy" ]; then
    echo "✅ Pseudonymization Service: Healthy"
else
    echo "❌ Pseudonymization Service: Unhealthy"
fi

# Check Repersonalization Service
REPERSONAL_HEALTH=$(curl -s http://localhost:8002/health | jq -r '.status')
if [ "$REPERSONAL_HEALTH" = "healthy" ]; then
    echo "✅ Repersonalization Service: Healthy"
else
    echo "❌ Repersonalization Service: Unhealthy"
fi

# Check service connectivity
CONNECTIVITY=$(curl -s http://localhost:8002/health | jq -r '.pseudonymization_service_status')
if [ "$CONNECTIVITY" = "connected" ]; then
    echo "✅ Service Connectivity: Connected"
else
    echo "⚠️  Service Connectivity: $CONNECTIVITY"
fi
```

### Statistics Monitoring

```python
import requests
import time

def monitor_services():
    """Monitor service statistics"""
    while True:
        # Pseudonymization stats
        pseudo_stats = requests.get('http://localhost:8001/stats').json()
        print(f"Pseudonymization: {pseudo_stats['statistics']['total_pseudonymized']} total")
        
        # Repersonalization stats
        repersonal_stats = requests.get('http://localhost:8002/stats').json()
        print(f"Repersonalization: {repersonal_stats['statistics']['total_repersonalized']} total")
        print(f"Success Rate: {repersonal_stats['statistics']['success_rate']:.2f}%")
        
        time.sleep(60)  # Every minute
```

## 🧪 Testing

### Unit Tests

```bash
# Run tests for both services
cd pseudonymization-service
pytest tests/

cd ../repersonalization-service
pytest tests/
```

### Integration Tests

```bash
# Test complete workflow
python tests/integration/test_full_workflow.py
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8001
```

## 📚 Documentation Links

- [Pseudonymization Service README](pseudonymization-service/README.md)
- [Repersonalization Service README](repersonalization-service/README.md)
- [API Documentation](http://localhost:8001/docs) (Pseudonymization)
- [API Documentation](http://localhost:8002/docs) (Repersonalization)

## 🛠️ Troubleshooting

### Services Not Starting

```bash
# Check Docker logs
docker-compose -f docker-compose.data-services.yml logs

# Check ports
netstat -an | grep 8001
netstat -an | grep 8002
```

### Key Synchronization Issues

```bash
# Verify shared keys volume
docker volume inspect prompt-engine_shared-keys

# Check key files
docker exec pseudonymization-service ls -la /app/keys
docker exec repersonalization-service ls -la /app/keys
```

### Service Connectivity Issues

```bash
# Test from inside container
docker exec repersonalization-service \
  curl http://pseudonymization-service:8001/health

# Check network
docker network inspect prompt-engine_data-services
```

## 🚀 Production Deployment Checklist

- [ ] Configure proper key management service (KMS, Vault)
- [ ] Set up HTTPS/TLS for API endpoints
- [ ] Implement API authentication and authorization
- [ ] Configure logging and monitoring (Prometheus, Grafana)
- [ ] Set up automated backups for key storage
- [ ] Implement rate limiting
- [ ] Configure firewall rules
- [ ] Set up automated health checks
- [ ] Implement circuit breakers
- [ ] Configure horizontal pod autoscaling (Kubernetes)
- [ ] Set up audit logging for compliance
- [ ] Implement data retention policies
- [ ] Configure alerting for failures

## 📞 Support

For issues:
1. Check service health: `curl http://localhost:8001/health && curl http://localhost:8002/health`
2. Review logs: `docker-compose logs -f`
3. Check API documentation: http://localhost:8001/docs and http://localhost:8002/docs

---

**🎊 Secure Data Services Ready!**

Process sensitive data with confidence and compliance.

