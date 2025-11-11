# 🔒 Enhanced PII Detection & Pseudonymization

## ✨ What's New

The Pseudonymization and Repersonalization services have been significantly enhanced with comprehensive PII detection capabilities.

### 🎯 Key Enhancements

#### 1. **Automatic PII Detection (20+ Types)**
The service now automatically identifies and pseudonymizes various types of Personally Identifiable Information:

**Personal Identifiers:**
- Full names
- Social Security Numbers (SSN)
- Passport numbers
- Driver's licenses
- National ID numbers

**Contact Information:**
- Email addresses
- Phone numbers
- Physical addresses
- Postal/ZIP codes
- IP addresses

**Financial Data:**
- Credit card numbers
- Bank account numbers
- Routing numbers
- IBAN codes
- SWIFT codes

**Other Sensitive Data:**
- Biometric data
- GPS coordinates (latitude/longitude)
- Usernames
- Customer IDs
- Employee IDs
- Medical record numbers
- Vehicle Identification Numbers (VIN)

#### 2. **Field-Level Security**
Granular control over which fields get pseudonymized based on:
- Field name patterns
- Content patterns (regex-based)
- Data type detection
- Context-aware analysis

#### 3. **Reversible Tokenization**
Type-specific pseudonym generation that maintains data utility:

| PII Type | Original | Pseudonymized | Format |
|----------|----------|---------------|---------|
| **Name** | John Doe | USER_A7B3C9 | USER_{token} |
| **Email** | john@email.com | EMAIL_X4Y2Z8@anon.email.com | EMAIL_{token}@anon.{domain} |
| **Phone** | 555-123-4567 | PHONE_N3P7Q1 | PHONE_{token} |
| **SSN** | 123-45-6789 | SSN_K5M8P2Q9R | SSN_{token} |
| **Account** | 1234-5678-9012 | ACCT_K9L2M5N8P3 | ACCT_{token} |
| **Credit Card** | 4532-1234-5678 | CARD_T7U9V2W5X8Y1 | CARD_{token} |
| **Address** | 123 Main St | ADDR_F3G6H9J2K5 | ADDR_{token} |
| **IP Address** | 192.168.1.1 | IP_M4N7P1Q8 | IP_{token} |

#### 4. **Enhanced Data Structure**
Updated input format to support comprehensive customer data:

```json
{
  "customer_id": "CUST_12345",
  "name": "John Doe",
  "email": "john.doe@email.com",
  "phone": "555-123-4567",
  "transactions": [
    {
      "date": "2025-10-16",
      "amount": 5000.00,
      "type": "credit",
      "description": "Monthly salary"
    }
  ],
  "account_info": {
    "account_number": "1234-5678-9012",
    "routing_number": "021000021",
    "bank_name": "Example Bank"
  },
  "account_balance": 15000.00,
  "timestamp": "2025-10-16T10:30:00Z"
}
```

#### 5. **PII Detection Response**
Enhanced API response with comprehensive PII information:

```json
{
  "pseudonymized_data": {
    "customer_id": "CUST_A7F3E9D2B1C4",
    "name": "USER_8F2B4A6C",
    "email": "EMAIL_X4Y2Z8@anon.email.com",
    ...
  },
  "pseudonym_id": "550e8400-e29b-41d4-a716-446655440000",
  "fields_pseudonymized": ["customer_id", "name", "email", "phone"],
  "pii_detected": [
    {
      "field": "name",
      "type": "name",
      "original_preview": "John Doe",
      "pseudonymized": "USER_8F2B4A6C"
    }
  ],
  "pii_summary": {
    "total_pii_fields": 8,
    "high_confidence_count": 8,
    "pii_types_found": {
      "name": 1,
      "email": 1,
      "phone": 1,
      "customer_id": 1,
      "bank_account": 1
    },
    "fields_affected": ["name", "email", "phone", "customer_id", "account_info.account_number"]
  },
  "processing_time_ms": 15.3
}
```

## 🚀 Updated Service Ports

**Breaking Change:** Ports have been updated for better organization:

- **Pseudonymization Service:** Port **5003** (was 8001)
- **Repersonalization Service:** Port **5004** (was 8002)

### Service URLs

```bash
# Pseudonymization API
http://localhost:5003

# Repersonalization API
http://localhost:5004

# API Documentation
http://localhost:5003/docs
http://localhost:5004/docs
```

## 📡 API Examples

### Example 1: Pseudonymize with PII Detection

```bash
curl -X POST http://localhost:5003/pseudonymize \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_12345",
    "name": "John Doe",
    "email": "john.doe@email.com",
    "phone": "555-123-4567",
    "transactions": [
      {
        "date": "2025-10-16",
        "amount": 5000.00,
        "type": "credit",
        "description": "Monthly salary"
      }
    ],
    "account_info": {
      "account_number": "1234-5678-9012"
    },
    "account_balance": 15000.00,
    "timestamp": "2025-10-16T10:30:00Z"
  }'
```

### Example 2: Python Client

```python
import requests

# Original data
data = {
    "customer_id": "CUST_12345",
    "name": "John Doe",
    "email": "john.doe@email.com",
    "phone": "555-123-4567",
    "transactions": [...],
    "account_info": {...},
    "account_balance": 15000.00,
    "timestamp": "2025-10-16T10:30:00Z"
}

# Pseudonymize
response = requests.post('http://localhost:5003/pseudonymize', json=data)
result = response.json()

print(f"PII Detected: {result['pii_summary']['total_pii_fields']} fields")
print(f"Types Found: {list(result['pii_summary']['pii_types_found'].keys())}")
print(f"Pseudonym ID: {result['pseudonym_id']}")

# Get pseudonymized data
safe_data = result['pseudonymized_data']

# Process safely...

# Repersonalize when needed
restore_response = requests.post(
    'http://localhost:5004/repersonalize',
    json={'pseudonym_id': result['pseudonym_id']}
)

original_data = restore_response.json()['original_data']
```

## 🔍 Detection Methods

### 1. Field Name Pattern Matching
Identifies PII based on field names:
- `name`, `full_name`, `first_name`, `last_name` → Name
- `email`, `email_address` → Email
- `phone`, `telephone`, `mobile` → Phone
- `ssn`, `social_security` → SSN

### 2. Content Pattern Matching
Uses regex patterns to detect:
- Email format: `xxx@yyy.zzz`
- Phone format: `(XXX) XXX-XXXX` or `XXX-XXX-XXXX`
- SSN format: `XXX-XX-XXXX`
- Credit card format: `XXXX-XXXX-XXXX-XXXX`
- IP address format: `XXX.XXX.XXX.XXX`

### 3. Context-Aware Analysis
Analyzes data structure and context for accurate detection

## 📊 Statistics & Monitoring

Enhanced statistics tracking:

```bash
curl http://localhost:5003/stats
```

Response:
```json
{
  "service": "pseudonymization",
  "statistics": {
    "total_pseudonymized": 150,
    "total_fields_processed": 750,
    "total_pii_detected": 1200,
    "pii_types_processed": {
      "name": 150,
      "email": 150,
      "phone": 120,
      "customer_id": 150,
      "bank_account": 100
    },
    "last_pseudonymization": "2025-11-11T10:30:00.000000",
    "active_pseudonyms": 150
  }
}
```

## 🧪 Testing

### Run PII Detection Tests

```bash
# Test the enhanced PII detection
python3 test_pii_detection.py
```

This will demonstrate:
- Automatic PII detection across 20+ types
- Type-specific tokenization
- Field-level pseudonymization
- Repersonalization with verification
- PII detection summary and statistics

## 🔧 Migration Guide

### Updating from Previous Version

#### 1. Update Port References

**Old:**
```python
PSEUDO_URL = "http://localhost:8001"
REPERSONAL_URL = "http://localhost:8002"
```

**New:**
```python
PSEUDO_URL = "http://localhost:5003"
REPERSONAL_URL = "http://localhost:5004"
```

#### 2. Update Data Structure

**Old:**
```json
{
  "transactions": [...],
  "account_balance": 15000.00,
  "customer_id": "CUST_001"
}
```

**New (Recommended):**
```json
{
  "customer_id": "CUST_12345",
  "name": "John Doe",
  "email": "john.doe@email.com",
  "transactions": [...],
  "account_info": {...},
  "account_balance": 15000.00,
  "timestamp": "2025-10-16T10:30:00Z"
}
```

#### 3. Handle New Response Fields

The response now includes:
- `pii_detected`: List of detected PII items
- `pii_summary`: Statistical summary of PII detection

Update your code to utilize or ignore these new fields as needed.

## 🎯 Use Cases

### 1. Secure Development & Testing
```python
# Use production data in dev environment
prod_data = get_production_data()  # Contains real PII
pseudo_result = pseudonymize(prod_data)
test_with_safe_data(pseudo_result['pseudonymized_data'])  # Safe!
```

### 2. GDPR Compliance
```python
# Detect and protect all PII automatically
customer_data = get_customer_data()
result = pseudonymize(customer_data)

print(f"Protected {result['pii_summary']['total_pii_fields']} PII fields")
print(f"Types: {list(result['pii_summary']['pii_types_found'].keys())}")
```

### 3. Data Sharing with Partners
```python
# Share data safely with third parties
internal_data = get_internal_data()
pseudo_result = pseudonymize(internal_data)

# Send pseudonymized data to partner
send_to_partner(pseudo_result['pseudonymized_data'])

# Partner processes and returns
processed = receive_from_partner()

# Repersonalize results
final_data = repersonalize(pseudo_result['pseudonym_id'])
```

## 📚 Documentation

- **API Documentation**: http://localhost:5003/docs & http://localhost:5004/docs
- **Complete Guide**: [DATA_SERVICES_GUIDE.md](DATA_SERVICES_GUIDE.md)
- **Quick Start**: [DATA_SERVICES_README.md](DATA_SERVICES_README.md)

## 🚀 Get Started

```bash
# Start services (new ports 5003 & 5004)
./start_data_services.sh

# Run PII detection tests
python3 test_pii_detection.py

# View API documentation
open http://localhost:5003/docs
```

---

**🎉 Enhanced PII Protection Ready!**

Automatically detect and protect 20+ types of sensitive data with field-level granular control.

