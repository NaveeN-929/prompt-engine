# 🚀 Starting Data Services (Without Docker)

## Quick Start Guide

### Prerequisites

Make sure you have Python 3.12 and dependencies installed:

```bash
# For Pseudonymization Service
cd pseudonymization-service
source pseudo/bin/activate  # or: source venv/bin/activate
pip install -r requirements.txt

# For Repersonalization Service (in another terminal)
cd repersonalization-service
source repersonal/bin/activate  # or: source venv/bin/activate
pip install -r requirements.txt
```

---

## 🎯 Method 1: From Project Root (Recommended)

### Start Pseudonymization Service (Port 5003)

**Terminal 1:**
```bash
python3 start_pseudonymization.py
```

### Start Repersonalization Service (Port 5004)

**Terminal 2:**
```bash
python3 start_repersonalization.py
```

---

## 🎯 Method 2: From Service Directories

### Start Pseudonymization Service

**Terminal 1:**
```bash
cd pseudonymization-service
source pseudo/bin/activate
python3 run_service.py
```

### Start Repersonalization Service

**Terminal 2:**
```bash
cd repersonalization-service
source repersonal/bin/activate
python3 run_service.py
```

---

## 🎯 Method 3: Using Uvicorn Directly

### Start Pseudonymization Service

**Terminal 1:**
```bash
cd pseudonymization-service
source pseudo/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 5003 --reload
```

### Start Repersonalization Service

**Terminal 2:**
```bash
cd repersonalization-service
source repersonal/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 5004 --reload
```

---

## ✅ Verify Services are Running

### Check Health

```bash
# Pseudonymization Service
curl http://localhost:5003/health

# Repersonalization Service
curl http://localhost:5004/health
```

### View API Documentation

Open in your browser:
- **Pseudonymization:** http://localhost:5003/docs
- **Repersonalization:** http://localhost:5004/docs

---

## 📊 Service Startup Order

**Important:** Start services in this order:

1. **First:** Pseudonymization Service (Port 5003)
2. **Then:** Repersonalization Service (Port 5004)

*Reason: Repersonalization service needs to connect to Pseudonymization service*

---

## 🧪 Test the Services

Once both services are running:

```bash
# Run the test suite
python3 test_pii_detection.py
```

---

## 🛑 Stopping Services

Press `Ctrl+C` in each terminal to stop the services gracefully.

---

## 📝 Quick Reference

### Service Ports
| Service | Port | URL |
|---------|------|-----|
| Pseudonymization | 5003 | http://localhost:5003 |
| Repersonalization | 5004 | http://localhost:5004 |

### API Documentation
| Service | Docs URL |
|---------|----------|
| Pseudonymization | http://localhost:5003/docs |
| Repersonalization | http://localhost:5004/docs |

### Launcher Scripts
| Script | Description |
|--------|-------------|
| `start_pseudonymization.py` | Start from project root |
| `start_repersonalization.py` | Start from project root |
| `pseudonymization-service/run_service.py` | Start from service dir |
| `repersonalization-service/run_service.py` | Start from service dir |

---

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :5003
lsof -i :5004

# Kill the process if needed
kill -9 <PID>
```

### Module Not Found Error

```bash
# Make sure virtual environment is activated
cd pseudonymization-service
source pseudo/bin/activate
pip install -r requirements.txt
```

### Cannot Connect to Pseudonymization Service

Make sure Pseudonymization service (5003) is running before starting Repersonalization service (5004).

---

## 💡 Development Tips

### Auto-Reload Mode

Use `--reload` flag for development:

```bash
cd pseudonymization-service
source pseudo/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 5003 --reload
```

Changes to code will automatically restart the server.

### View Logs

Logs will display in the terminal where you started each service.

### Custom Port

To use different ports, edit the config files:
- `pseudonymization-service/app/config.py`
- `repersonalization-service/app/config.py`

---

## 🎉 Example Session

```bash
# Terminal 1: Start Pseudonymization
$ python3 start_pseudonymization.py
======================================================================
🔒 Starting Pseudonymization Service
======================================================================
Host: 0.0.0.0
Port: 5003
API Documentation: http://localhost:5003/docs
======================================================================

✨ Features:
   - Automatic PII Detection (20+ types)
   - Type-specific Tokenization
   - Field-level Security
   - GDPR Compliant

💡 Press Ctrl+C to stop
======================================================================
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5003

# Terminal 2: Start Repersonalization
$ python3 start_repersonalization.py
======================================================================
🔓 Starting Repersonalization Service
======================================================================
Host: 0.0.0.0
Port: 5004
API Documentation: http://localhost:5004/docs
======================================================================

✨ Features:
   - Secure Data Restoration
   - Integrity Verification
   - Bulk Repersonalization
   - GDPR Cleanup Support

💡 Press Ctrl+C to stop
⚠️  Note: Pseudonymization Service must be running (port 5003)
======================================================================
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5004

# Terminal 3: Test
$ python3 test_pii_detection.py
======================================================================
  🔐 PII Detection & Pseudonymization Test Suite
  Enhanced with 20+ PII Types
======================================================================
✅ All tests passed!
```

---

## 📚 Additional Resources

- **Feature Guide:** [PII_DETECTION_FEATURES.md](PII_DETECTION_FEATURES.md)
- **Complete Guide:** [DATA_SERVICES_GUIDE.md](DATA_SERVICES_GUIDE.md)
- **Changelog:** [CHANGELOG_PII_ENHANCEMENT.md](CHANGELOG_PII_ENHANCEMENT.md)

---

**🚀 Ready to start! Choose your preferred method above.**

