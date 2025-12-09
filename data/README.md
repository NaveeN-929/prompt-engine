# 💰 Financial Transaction Data Generator

## 🎉 What You Have

A **production-ready data generator** that creates realistic financial transaction datasets for testing your self-learning system!

---

## ✨ Features

✅ **18 Transaction Types** - Realistic categories (salary, rent, groceries, etc.)  
✅ **Realistic Amounts** - Category-appropriate price ranges  
✅ **Varied Descriptions** - Multiple description options per category  
✅ **Automatic Balance Calculation** - Maintains accurate account balances  
✅ **Flexible Generation** - 1 to 10,000+ datasets  
✅ **Two Output Formats** - Individual files or combined JSON  
✅ **Interactive & CLI** - Both modes supported  
✅ **Statistics Reporting** - Comprehensive generation stats  

---

## 🚀 Quick Start

### Generate 10 datasets (Interactive)

```bash
python3 data-script.py
# Then follow prompts
```

### Generate 100 datasets (Command Line)

```bash
python3 data-script.py 100 5 15
```

This creates 100 datasets with 5-15 transactions each in `generated_data/`

---

## 📊 Example Output

Here's what a generated dataset looks like:

```json
{
  "transactions": [
    {
      "date": "2024-11-10",
      "amount": 9916.15,
      "type": "credit",
      "description": "Annual bonus"
    },
    {
      "date": "2024-11-12",
      "amount": -140.57,
      "type": "debit",
      "description": "Dining out"
    },
    {
      "date": "2024-11-15",
      "amount": 7262.09,
      "type": "credit",
      "description": "Monthly salary"
    }
  ],
  "account_balance": 22435.05,
  "customer_id": "MEM_0001"
}
```

---

## 🧬 PAM Contextual Inputs

Each dataset now includes the signals PAM needs for bank-defined contexts.

- `transactions` include a `tags` array (e.g., `cross_border`, `high_value`, `card_spend`) that feeds eligibility checks.
- `customer_profile` captures income, products, propensities (`fx_lockup`, `credit_increase`, `card_to_loan`), risk, segments, channels, and utilisation.
- `contextual_signals` summarize recent behaviour (cross-border transfers, card spend, high-value transactions, average size).
- `bank_contexts` is a list of context cards (id, name, focus_area, priority, time_frame, incentive, description, eligibility rules, preview). These are the same structures the UI can send in an `/augment` request via the new `bank_contexts` body field.

You can reuse the sample context cards in `generated_data/dataset_0001.json` (and `pam-service/app/configs/bank_contexts.json`) to seeding the UI or API payloads.

Example augment request addition:

```json
{
  "input_data": { ... },
  "bank_contexts": [
    {
      "id": "fx_lockup",
      "priority": 1,
      "eligibility": {
        "min_recent_cross_border_transactions": 4,
        "propensity_score": { "key": "fx_lockup", "min": 0.65 }
      }
    }
  ]
}
```

---

## 💡 Common Use Cases

### 1. Train Self-Learning System

```bash
# Generate large training set
python3 data-script.py 500 8 15

# Each dataset will be processed by your self-learning system
# System learns patterns, improves quality predictions
```

### 2. Test Different Complexities

```bash
# Simple scenarios (5-8 transactions)
python3 data-script.py 100 5 8

# Complex scenarios (20-30 transactions)
python3 data-script.py 100 20 30
```

### 3. Benchmark Performance

```bash
# Generate consistent test set
python3 data-script.py 1000 10 10

# All datasets have exactly 10 transactions
# Perfect for consistent benchmarking
```

---

## 📈 Transaction Categories

### Income (Credit)
- **Salary**: $2,000 - $8,000
- **Freelance**: $500 - $5,000
- **Bonus**: $1,000 - $10,000
- **Refund**: $20 - $500
- **Interest**: $5 - $100
- **Investment**: $100 - $3,000

### Expenses (Debit)
- **Rent**: $800 - $2,500
- **Grocery**: $30 - $200
- **Utilities**: $50 - $300
- **Dining**: $15 - $150
- **Entertainment**: $10 - $100
- **Transportation**: $20 - $150
- **Shopping**: $50 - $500
- **Insurance**: $100 - $800
- **Healthcare**: $50 - $1,000
- **Subscription**: $10 - $50
- **Loan Payment**: $200 - $1,500
- **Phone Bill**: $30 - $100

---

## 🎯 Usage Modes

### Mode 1: Interactive (User-Friendly)

```bash
python3 data-script.py
```

**Prompts you for:**
- How many datasets?
- Min transactions per dataset?
- Max transactions per dataset?
- Save format (individual/combined)?
- Output directory?

### Mode 2: Command Line (Quick)

```bash
python3 data-script.py <count> [min_tx] [max_tx]
```

**Examples:**
```bash
python3 data-script.py 10          # 10 datasets, 5-15 tx each
python3 data-script.py 100 8 12    # 100 datasets, 8-12 tx each
python3 data-script.py 1000 5 20   # 1000 datasets, 5-20 tx each
```

### Mode 3: Programmatic (Advanced)

```python
from data_script import TransactionDataGenerator

gen = TransactionDataGenerator()

# Generate datasets
datasets = gen.generate_multiple_datasets(
    count=100,
    min_transactions=5,
    max_transactions=15
)

# Save
gen.save_datasets(datasets, 'my_output', 'individual')
```

---

## 📁 Output Structure

### Individual Files (Default)

```
generated_data/
├── dataset_0001.json
├── dataset_0002.json
├── dataset_0003.json
├── ...
└── dataset_1000.json
```

**Pros:**
- Easy to process one-by-one
- Perfect for batch processing
- Can delete/modify individual files

### Combined File

```
generated_data/
└── all_datasets.json
```

**Pros:**
- Single file to manage
- Easy to load all at once
- Smaller total file size

---

## 📊 Statistics Output

After generation, you'll see:

```
============================================================
📊 DATASET GENERATION STATISTICS
============================================================
Total datasets: 100
Total transactions: 1,247
Average transactions per dataset: 12.5

Account Balances:
  Average: $5,432.18
  Minimum: $1,234.56
  Maximum: $9,876.54
============================================================
```

---

## 🔗 Integration with Self-Learning

### Step 1: Generate Test Data

```bash
python3 data-script.py 100
```

### Step 2: Feed to Self-Learning System

```bash
# Process each dataset through your API
for file in generated_data/*.json; do
    curl -X POST http://localhost:5000/generate \
         -H "Content-Type: application/json" \
         -d @$file
    sleep 0.5  # Rate limiting
done
```

### Step 3: Monitor Learning Progress

```bash
curl http://localhost:5000/self-learning/metrics
```

You'll see:
- Pattern count increasing
- Quality scores improving
- Success rate climbing

---

## 🎓 Best Practices

### 1. Start Small, Scale Up

```bash
# Test first
python3 data-script.py 10

# Then scale
python3 data-script.py 100
python3 data-script.py 1000
```

### 2. Mix Complexity Levels

```bash
# Simple
python3 data-script.py 200 3 8

# Medium
python3 data-script.py 200 8 15

# Complex
python3 data-script.py 200 15 25
```

### 3. Monitor Training Progress

- Track quality improvements with each batch
- Watch pattern recognition develop
- Observe prediction accuracy increase

### 4. Clean Up When Done

```bash
rm -rf generated_data/
```

---

## 🔧 Customization

### Add Custom Transaction Types

Edit `data-script.py`:

```python
'credit': {
    'my_income_type': {
        'min': 100, 
        'max': 1000, 
        'frequency': 'monthly'
    },
},
'debit': {
    'my_expense_type': {
        'min': 50, 
        'max': 500, 
        'frequency': 'weekly'
    },
}
```

### Adjust Balance Ranges

```python
# In generate_multiple_datasets()
base_balance = round(random.uniform(5000, 50000), 2)  # Higher range
```

### Change Date Ranges

```python
# In generate_dataset()
base_date = datetime.now() - timedelta(days=90)  # Last 90 days
```

---

## 📚 Documentation

- **DATA_GENERATOR_GUIDE.md** - Comprehensive usage guide
- **data-script.py** - The generator script (well-commented)
- **README.md** - This file

---

## 💡 Tips & Tricks

### Tip 1: Validate Generated Data

```bash
python3 -c "
import json, glob
for f in glob.glob('generated_data/*.json'):
    data = json.load(open(f))
    assert len(data['transactions']) > 0
    print(f'✓ {f}')
"
```

### Tip 2: Analyze Dataset Statistics

```bash
python3 -c "
import json, glob
files = glob.glob('generated_data/*.json')
balances = [json.load(open(f))['account_balance'] for f in files]
print(f'Average balance: ${sum(balances)/len(balances):,.2f}')
"
```

### Tip 3: Filter by Balance Range

```bash
# Find high-balance accounts
python3 -c "
import json, glob
for f in glob.glob('generated_data/*.json'):
    data = json.load(open(f))
    if data['account_balance'] > 10000:
        print(f'{f}: ${data[\"account_balance\"]:,.2f}')
"
```

---

## 🎉 Summary

You now have:

✅ **Realistic data generator** (302 lines)  
✅ **18 transaction categories** with proper ranges  
✅ **Flexible generation** (1 to unlimited datasets)  
✅ **Two output formats** (individual/combined)  
✅ **Interactive & CLI modes**  
✅ **Comprehensive documentation**  

---

## 🚀 Quick Command Reference

```bash
# Interactive mode
python3 data-script.py

# Quick generation
python3 data-script.py 100          # 100 datasets
python3 data-script.py 100 8 12     # 100 datasets, 8-12 tx each
python3 data-script.py 1000 5 20    # 1000 datasets, 5-20 tx each

# View generated file
cat generated_data/dataset_0001.json

# Count files
ls generated_data/*.json | wc -l

# Clean up
rm -rf generated_data/
```

---

**🎊 Ready to generate unlimited realistic financial datasets!**

**Use them to:**
- Train your self-learning system
- Test prediction accuracy
- Benchmark performance
- Validate quality improvements

*Perfect for testing your advanced self-learning system!*

