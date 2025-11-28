# 📋 Data Structure Update - PII Enhanced

## ✅ What Changed

The data generator now produces **PII-enhanced datasets** compatible with the new Pseudonymization Service.

---

## 🆕 New Data Structure

### Before
```json
{
  "transactions": [...],
  "account_balance": 150000.00,
  "customer_id": "BIZ_0001"
}
```

### After (PII-Enhanced)
```json
{
  "customer_id": "BIZ_0001",
  "name": "Tech Solutions Inc",
  "email": "info@techsolutionsinc.business.com",
  "phone": "555-234-5678",
  "transactions": [
    {
      "date": "2025-10-16",
      "amount": 50000.00,
      "type": "credit",
      "description": "Customer payment received - Invoice #INV12345"
    }
  ],
  "account_info": {
    "account_number": "1234-5678-9012",
    "routing_number": "021000021",
    "bank_name": "First National Bank",
    "account_type": "business_checking"
  },
  "account_balance": 150000.00,
  "timestamp": "2025-11-11T10:30:00.000000Z"
}
```

---

## 🔍 New PII Fields

### 1. **name** (Business Name)
- Realistic business names
- Examples: "Tech Solutions Inc", "Global Logistics Ltd"
- 20+ predefined names with variations

### 2. **email** (Business Email)
- Business email addresses
- Format: `info@company.domain.com`
- Multiple formats: info, contact, accounts, finance

### 3. **phone** (Business Phone)
- Business phone numbers
- Format: `XXX-XXX-XXXX`
- Area codes 200-999

### 4. **account_info** (Account Details)
Contains:
- `account_number`: Format `XXXX-XXXX-XXXX`
- `routing_number`: 9-digit routing number
- `bank_name`: 8+ realistic bank names
- `account_type`: business_checking, business_savings, commercial_account

### 5. **timestamp**
- ISO format timestamp
- Marks when data was generated
- Format: `YYYY-MM-DDTHH:MM:SS.000000Z`

---

## 🚀 Usage

### Generate PII-Enhanced Data

```bash
# Interactive mode
python3 data-script.py

# Command line (10 datasets, 5-15 transactions each)
python3 data-script.py 10 5 15

# Large batch (100 datasets)
python3 data-script.py 100 8 12
```

### Sample Output

```bash
$ python3 data-script.py 1 3 5

🏢 BUSINESS BANKING TRANSACTION DATA GENERATOR
   For SME Business Accounts (PII-Enhanced)
============================================================
✨ Generates data with:
   - Business names, emails, phone numbers
   - Account information (account #, routing #)
   - Transaction history
   - Ready for PII detection testing
============================================================

🔄 Generating 1 datasets...
   Transactions per dataset: 3-5

📊 DATASET GENERATION STATISTICS
============================================================
Total datasets: 1
Total transactions: 4
Average transactions per dataset: 4.0

Account Balances:
  Average: $352,450.25
  Minimum: $352,450.25
  Maximum: $352,450.25
============================================================

📋 Sample Dataset (first one):
------------------------------------------------------------
{
  "customer_id": "BIZ_0001",
  "name": "Tech Solutions Inc",
  "email": "info@techsolutionsinc.business.com",
  "phone": "555-234-5678",
  "transactions": [...],
  "account_info": {
    "account_number": "1234-5678-9012",
    "routing_number": "021000021",
    "bank_name": "First National Bank",
    "account_type": "business_checking"
  },
  "account_balance": 352450.25,
  "timestamp": "2025-11-11T10:30:00.000000Z"
}
```

---

## 🔒 PII Detection Ready

The new structure is **perfect for testing PII detection**:

### PII Types That Will Be Detected

| Field | PII Type | Detection Method |
|-------|----------|------------------|
| `customer_id` | Customer ID | Field name + pattern |
| `name` | Business Name | Field name |
| `email` | Email Address | Field name + email pattern |
| `phone` | Phone Number | Phone number pattern |
| `account_info.account_number` | Bank Account | Field name + pattern |
| `account_info.routing_number` | Routing Number | Field name + pattern |

---

## 🧪 Testing with Pseudonymization

### Step 1: Generate Test Data

```bash
cd data
python3 data-script.py 5 5 10
```

### Step 2: Test with Pseudonymization Service

```bash
# Start service (if not running)
python3 start_pseudonymization.py

# Test with generated data
curl -X POST http://localhost:5003/pseudonymize \
  -H "Content-Type: application/json" \
  -d @generated_data/dataset_0001.json
```

### Expected PII Detection

The service will detect and pseudonymize:
- ✅ Customer ID → `CUST_XXXXXXXXXX`
- ✅ Business Name → `USER_XXXXXXXX`
- ✅ Email → `EMAIL_XXXXXXXX@anon.domain.com`
- ✅ Phone → `PHONE_XXXXXX`
- ✅ Account Number → `ACCT_XXXXXXXXXX`

---

## 📊 Data Characteristics

### Business Names
- 20 predefined realistic business names
- Automatic variations for larger datasets
- Industries: Tech, Logistics, Energy, Manufacturing, etc.

### Email Addresses
- 8 business email domains
- 4 email format types (info, contact, accounts, finance)
- Derived from business names

### Phone Numbers
- Format: `XXX-XXX-XXXX`
- Area codes: 200-999
- Business phone number ranges

### Account Information
- Account numbers: 12 digits (XXXX-XXXX-XXXX)
- Routing numbers: 9 digits (valid format)
- 8 realistic bank names
- 3 business account types

---

## 🔄 Backward Compatibility

The old data files still work, but **new files include PII fields**.

### Migration

No migration needed! New structure is additive:
- All old fields remain
- New PII fields added
- Services handle both formats

---

## 💡 Use Cases

### 1. PII Detection Testing
```bash
# Generate data with various PII types
python3 data-script.py 50 5 15

# Test detection accuracy
python3 ../test_pii_detection.py
```

### 2. Pseudonymization Testing
```bash
# Generate business data
python3 data-script.py 10

# Pseudonymize all files
for file in generated_data/*.json; do
    curl -X POST http://localhost:5003/pseudonymize \
         -H "Content-Type: application/json" \
         -d @$file
done
```

### 3. End-to-End Pipeline
```bash
# Generate → Pseudonymize → Process → Repersonalize
python3 data-script.py 1 5 10
python3 ../test_pii_detection.py
```

---

## 📝 Example Complete Dataset

```json
{
  "customer_id": "SME_0042",
  "name": "Digital Marketing Agency",
  "email": "contact@digitalmarketingagency.corp.com",
  "phone": "723-456-7890",
  "transactions": [
    {
      "date": "2025-10-18",
      "amount": 45000.00,
      "type": "credit",
      "description": "Service contract revenue"
    },
    {
      "date": "2025-10-22",
      "amount": -8500.00,
      "type": "debit",
      "description": "Marketing campaign"
    },
    {
      "date": "2025-10-25",
      "amount": -12000.00,
      "type": "debit",
      "description": "Monthly payroll processing"
    }
  ],
  "account_info": {
    "account_number": "5678-9012-3456",
    "routing_number": "123456789",
    "bank_name": "Commerce Bank",
    "account_type": "business_checking"
  },
  "account_balance": 224500.00,
  "timestamp": "2025-11-11T14:23:45.123456Z"
}
```

---

## 🎯 Benefits

✅ **Realistic PII** - Business names, emails, phone numbers  
✅ **Comprehensive Testing** - All PII types covered  
✅ **Service Ready** - Works with Pseudonymization Service  
✅ **Production-Like** - SME business banking scenarios  
✅ **Automated** - Generate unlimited test data  

---

## 🚀 Quick Start

```bash
# Generate 10 PII-enhanced datasets
cd data
python3 data-script.py 10 5 10

# View generated data
cat generated_data/dataset_0001.json | jq '.'

# Test with services
cd ..
python3 test_pii_detection.py
```

---

**✨ Your data generator now creates production-ready PII-enhanced datasets!**

Perfect for testing the Pseudonymization Service with realistic business banking data.

