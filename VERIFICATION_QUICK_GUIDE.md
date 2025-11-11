# 🧪 Quality Improvement Verification Guide

## What Was Fixed

The verification script now properly wraps the dataset in the required format:

**Before (Wrong):**
```json
{
  "transactions": [...],
  "account_balance": 718391.91,
  "customer_id": "BIZ_0001"
}
```

**After (Correct):**
```json
{
  "input_data": {
    "transactions": [...],
    "account_balance": 718391.91,
    "customer_id": "BIZ_0001"
  }
}
```

---

## How to Run

### Step 1: Ensure Services Are Running

```bash
cd /Users/naveen/Pictures/prompt-engine

# Check if services are up
curl http://localhost:5000/health  # Prompt Engine
curl http://localhost:5001/health  # Autonomous Agent

# If not running, start them:
./start_all_services.sh
```

### Step 2: Run the Verification Script

```bash
./verify_quality_improvement.sh
```

---

## Expected Output

### Successful Run:

```
╔═══════════════════════════════════════════════════════════════╗
║  Quality Improvement Verification Script                      ║
║  Tests that validation scores IMPROVE for repeated datasets   ║
╚═══════════════════════════════════════════════════════════════╝

Step 1: Checking if services are running...
✓ Services are running

Step 2: Checking for test data...
✓ Test data available

Step 3: Running FIRST analysis (learning phase)...
  This will establish a baseline score

✓ First run complete
  Validation score: 0.71

Waiting 3 seconds for learning to complete...

Step 4: Running SECOND analysis (improvement phase)...
  This should use improved prompt and get higher score

✓ Second run complete
  Validation score: 0.82

═══════════════════════════════════════════════════════════════
                        RESULTS
═══════════════════════════════════════════════════════════════

  First Run:  0.71
  Second Run: 0.82

✓ SUCCESS: Score IMPROVED by 0.11 (+15.5%)

  Quality improvement is WORKING! 🎉
  The system learned from the first run and generated
  a better prompt for the second run.
```

---

## Manual Test (Alternative)

If you want to test manually:

```bash
cd /Users/naveen/Pictures/prompt-engine

# Wrap the data properly
cat data/generated_data/dataset_0001.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
wrapped = {'input_data': data}
print(json.dumps(wrapped))
" > /tmp/wrapped_data.json

# First run
echo "=== FIRST RUN ==="
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d @/tmp/wrapped_data.json \
  | python3 -m json.tool | grep -A 5 "overall_score"

# Wait for learning
sleep 5

# Second run
echo ""
echo "=== SECOND RUN (Should be improved) ==="
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d @/tmp/wrapped_data.json \
  | python3 -m json.tool | grep -A 5 "overall_score"
```

---

## What to Look For

### In the Script Output:

✅ **First run score**: Around 0.70-0.72  
✅ **Second run score**: Around 0.80-0.85 (HIGHER!)  
✅ **Improvement message**: "Score IMPROVED by..."

### In the Logs:

**Prompt Engine logs:**
```
🎯 Using quality-improved prompt (learned from past validation feedback)
```

**Autonomous Agent logs:**
```
Phase 7: Submitting learning feedback
✓ Feedback submitted successfully
```

---

## Troubleshooting

### Issue: "Services not running"

```bash
./start_all_services.sh
# Wait 30 seconds for services to initialize
```

### Issue: "Could not extract validation score"

The script will now show the response preview. Check for:
- Error messages in the response
- Service unavailability
- Missing dependencies

### Issue: Score not improving

1. Check logs for "🧠 Quality Improvement Engine enabled"
2. Verify first run completes successfully
3. Wait longer between runs (5 seconds instead of 3)
4. Check that validation_result is being passed

### Issue: "RAG service not available"

Make sure Qdrant and Ollama are running:
```bash
docker ps | grep qdrant
docker ps | grep ollama
```

If not:
```bash
./setup_qdrant.sh
# Start Ollama separately if needed
```

---

## Quick Test Commands

### Check Services:
```bash
curl http://localhost:5000/health && echo " - Prompt Engine ✓"
curl http://localhost:5001/health && echo " - Autonomous Agent ✓"
curl http://localhost:6333 && echo " - Qdrant ✓"
curl http://localhost:11434 && echo " - Ollama ✓"
```

### Test Data Wrapping:
```bash
# This should work now:
cat data/generated_data/dataset_0001.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(json.dumps({'input_data': data}))" | \
curl -s -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d @- | python3 -m json.tool | head -50
```

---

## Success Criteria

Your quality improvement is working if:

1. ✅ Script runs without errors
2. ✅ First run score extracted successfully (~0.71)
3. ✅ Second run score is higher (~0.82+)
4. ✅ Improvement percentage > 10%
5. ✅ Logs show "quality-improved prompt" being used

---

## Next Steps After Success

Once verified working:

1. **Test with different datasets:**
   ```bash
   # Modify script to use dataset_0002.json or dataset_0003.json
   ```

2. **Monitor over time:**
   ```bash
   # Run multiple times to see continued improvement
   for i in {1..5}; do
     echo "Run $i:"
     curl -X POST http://localhost:5001/analyze \
       -H "Content-Type: application/json" \
       -d @/tmp/wrapped_data.json | \
       python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('validation_result',{}).get('overall_score','N/A'))"
     sleep 3
   done
   ```

3. **Check improvement metrics:**
   ```bash
   curl http://localhost:5000/self-learning/metrics
   ```

---

## Summary

The verification script now:
- ✅ Properly wraps data in `input_data` field
- ✅ Extracts validation scores correctly
- ✅ Shows response preview on errors
- ✅ Calculates improvement percentage
- ✅ Provides clear success/failure messages

**Run it now:** `./verify_quality_improvement.sh`

