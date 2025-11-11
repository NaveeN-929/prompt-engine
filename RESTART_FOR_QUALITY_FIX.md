# 🔄 CRITICAL: Restart Required for Quality Improvement

## The Problem

The services are running **OLD CODE** from before the quality improvement integration. The score is staying the same because:

❌ Quality Improvement Engine not loaded  
❌ Learning feedback not integrated  
❌ Improved prompts not being retrieved  

## The Solution: RESTART SERVICES

### Step 1: Stop All Services

```bash
cd /Users/naveen/Pictures/prompt-engine
./stop_all_services.sh
```

**Wait for all services to stop completely** (about 10-15 seconds)

### Step 2: Verify Everything Stopped

```bash
# These should all FAIL (return connection errors):
curl http://localhost:5000/health  # Should fail
curl http://localhost:5001/health  # Should fail
```

### Step 3: Start All Services with NEW CODE

```bash
./start_all_services.sh
```

**Wait 30-60 seconds for services to fully initialize**

### Step 4: Verify New Code is Loaded

Check the Prompt Engine startup logs for this CRITICAL line:

```bash
# Look at the logs when starting
# You should see:
🧠 Quality Improvement Engine enabled - prompts will improve over time
```

If you DON'T see this line, the quality improvement isn't loaded!

### Step 5: Run Verification Again

```bash
./verify_quality_improvement.sh
```

---

## Expected Behavior After Restart

### First Run:
```
Validation score: 0.79
(System learns and generates improvements)
```

### Second Run:
```
Validation score: 0.85+ ← HIGHER!
🎯 Using quality-improved prompt
```

---

## How to Monitor the Logs

### Terminal 1: Prompt Engine Logs
```bash
cd /Users/naveen/Pictures/prompt-engine

# Start and watch logs
python3 -m app.main 2>&1 | tee logs/prompt_engine_live.log
```

**Look for:**
- ✅ `🧠 Quality Improvement Engine enabled`
- ✅ `🎯 Using quality-improved prompt` (on 2nd run)
- ✅ `📚 Quality improvement learning complete`

### Terminal 2: Autonomous Agent Logs
```bash
cd /Users/naveen/Pictures/prompt-engine/autonomous-agent

python3 server_final.py 2>&1 | tee ../logs/agent_live.log
```

**Look for:**
- ✅ `Phase 7: Submitting learning feedback`
- ✅ Validation results being sent

---

## Quick Restart Commands

```bash
cd /Users/naveen/Pictures/prompt-engine

# Full restart
./stop_all_services.sh && sleep 10 && ./start_all_services.sh

# Wait for services to be ready
sleep 30

# Verify services are up
curl http://localhost:5000/health
curl http://localhost:5001/health

# Run verification
./verify_quality_improvement.sh
```

---

## Troubleshooting

### Issue: "Quality Improvement Engine" not showing in logs

**This means the code isn't loaded!**

1. Make sure you're in the correct directory:
   ```bash
   cd /Users/naveen/Pictures/prompt-engine
   ```

2. Check the updated code is there:
   ```bash
   grep -n "self_learning_manager" app/generators/agentic_prompt_generator.py | head -5
   ```
   
   Should show lines with `self_learning_manager`

3. Ensure Python is using the correct files:
   ```bash
   # Clear Python cache
   find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
   find . -name "*.pyc" -delete 2>/dev/null
   ```

4. Restart services again

### Issue: Services won't stop

```bash
# Force kill if needed
pkill -f "python3 -m app.main"
pkill -f "python3 server_final.py"

# Check nothing is running
ps aux | grep python3 | grep -E "app.main|server_final"
```

### Issue: Port already in use

```bash
# Find what's using the ports
lsof -i :5000  # Prompt Engine
lsof -i :5001  # Autonomous Agent

# Kill if needed
kill -9 <PID>
```

---

## Verification Checklist

Before running the test:

- [ ] Services stopped completely
- [ ] Services restarted with new code
- [ ] Prompt Engine shows "🧠 Quality Improvement Engine enabled"
- [ ] Both health checks pass
- [ ] Waited 30+ seconds for full initialization

Then run:
```bash
./verify_quality_improvement.sh
```

---

## What Success Looks Like

```
╔═══════════════════════════════════════════════════════════════╗
║  Quality Improvement Verification Script                      ║
╚═══════════════════════════════════════════════════════════════╝

Step 3: Running FIRST analysis...
✓ First run complete
  Validation score: 0.79

Step 4: Running SECOND analysis...
✓ Second run complete
  Validation score: 0.85

═══════════════════════════════════════════════════════════════
✓ SUCCESS: Score IMPROVED by 0.06 (+7.6%)

Quality improvement is WORKING! 🎉
```

---

## Why This Happened

When services are running, they load code into memory. Changes to Python files **don't take effect** until services restart. 

We added quality improvement code AFTER services started, so they're running old code.

**Solution:** Always restart after code changes!

---

## Quick Fix Command

Run this single command:

```bash
cd /Users/naveen/Pictures/prompt-engine && \
./stop_all_services.sh && \
sleep 15 && \
echo "Clearing Python cache..." && \
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && \
find . -name "*.pyc" -delete 2>/dev/null && \
echo "Starting services with updated code..." && \
./start_all_services.sh && \
sleep 30 && \
echo "Running verification..." && \
./verify_quality_improvement.sh
```

This will:
1. Stop services
2. Clear Python cache
3. Start services (loading new code)
4. Wait for initialization
5. Run verification test

