# 🔒 Strict Validation Requirements

The Response Validation LLM System operates with **NO FALLBACKS** or mock responses. All services must be properly configured and running for the system to function.

## Required Services

### 1. Ollama LLM Service
**Status**: REQUIRED - No fallbacks
**Purpose**: Provides validation LLM models

```bash
# Must be running
ollama serve

# Required models must be available
ollama pull mistral:latest  # Primary validation model
```

**Verification**:
```bash
curl http://localhost:11434/api/tags
# Should return list including mistral:latest
```

### 2. Qdrant Vector Database
**Status**: REQUIRED - No fallbacks
**Purpose**: Stores validation patterns and training data

```bash
# Must be running
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

**Verification**:
```bash
curl http://localhost:6333/dashboard
# Should return Qdrant dashboard
```

### 3. All Core Components
**Status**: REQUIRED - No fallbacks

- **LLM Validator**: Must connect to Ollama successfully
- **Quality Assessor**: Must complete all quality checks
- **Training Data Manager**: Must access Qdrant database
- **Feedback Manager**: Must communicate with other services

## Failure Modes

### ❌ **Service Unavailable**
If any required service is unavailable:

```json
{
  "error": "Validation engine not properly initialized",
  "details": "Please ensure all required services (Ollama, Qdrant) are running",
  "status": "service_unavailable"
}
```

### ❌ **Model Not Available**
If required models are not loaded:

```json
{
  "error": "Cannot connect to validation LLM",
  "details": "Please ensure Ollama is running and models are available",
  "status": "llm_unavailable"
}
```

### ❌ **Validation Failed**
If validation process encounters errors:

```json
{
  "error": "Validation processing failed",
  "details": "Specific error details",
  "status": "processing_error"
}
```

## No Mock Responses

The system will **NEVER**:
- ❌ Provide mock validation scores
- ❌ Generate fake quality assessments  
- ❌ Return placeholder training data
- ❌ Use fallback validation logic
- ❌ Continue with degraded functionality

## Strict Validation Process

### 1. **LLM Connection Check**
```python
# REQUIRED - No fallbacks
connection_test = await self._test_llm_connection()
if not connection_test["available"]:
    raise RuntimeError(f"Cannot connect to validation LLM: {connection_test['error']}")
```

### 2. **All Criteria Must Pass**
```python
# If ANY criterion fails, entire validation fails
for criterion_name, result in validation_results:
    if isinstance(result, Exception):
        raise RuntimeError(f"Validation failed for {criterion_name}: {result}")
```

### 3. **Quality Assessment Required**
```python
# Quality assessment must complete successfully
try:
    quality_result = await self.quality_assessor.assess_quality(...)
except Exception as e:
    raise RuntimeError(f"Quality assessment failed: {e}")
```

### 4. **Training Data Storage**
```python
# Database must be accessible for training data
if not self.training_data_manager.is_initialized:
    raise RuntimeError("Training data manager not initialized")
```

## Pre-Flight Checks

Before starting the validation server, run:

```bash
cd validation-llm

# 1. Test imports
python test_imports.py

# 2. Setup models (if not done)
python setup_models.py

# 3. Verify services
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:6333/dashboard  # Qdrant
```

## Error Handling Strategy

### **Fail Fast**
- Detect service issues immediately
- Provide clear error messages
- Stop processing rather than continue with degraded service

### **Clear Diagnostics**
- Specific error details
- Service status information
- Resolution steps

### **No Silent Failures**
- All errors are logged
- HTTP status codes reflect actual status
- No hidden fallback behavior

## Monitoring Requirements

### **Health Checks**
```bash
# System health
curl http://localhost:5002/health

# Detailed status
curl http://localhost:5002/status
```

### **Service Dependencies**
The validation system requires:
1. **Ollama**: Models loaded and responsive
2. **Qdrant**: Database accessible and responsive
3. **Network**: All services can communicate

### **Performance Monitoring**
- Validation request success rate must be monitored
- Service availability must be tracked
- Error rates should trigger alerts

## Troubleshooting

### **Common Issues**

1. **"Validation engine not properly initialized"**
   ```bash
   # Check Ollama
   ollama serve
   ollama list
   
   # Check Qdrant
   docker ps | grep qdrant
   ```

2. **"Cannot connect to validation LLM"**
   ```bash
   # Pull required models
   ollama pull mistral:latest
   ```

3. **"Validation processing failed"**
   ```bash
   # Check logs
   tail -f validation.log
   
   # Test individual components
   python test_imports.py
   ```

## Configuration Validation

The system validates configuration at startup:

```python
# All required models must be specified
VALIDATION_LLM_CONFIG = {
    "primary_validator": {
        "model_name": "mistral:latest",  # MUST exist
        "host": "http://localhost:11434",  # MUST be accessible
    }
}

# All collections must be accessible
VECTOR_DB_CONFIG = {
    "host": "localhost",
    "port": 6333,  # MUST be accessible
    "collections": {...}  # MUST be creatable
}
```

## Success Criteria

✅ **Fully Operational**: All services running, all validations working
❌ **Partially Operational**: NOT SUPPORTED - System fails completely
❌ **Degraded Mode**: NOT SUPPORTED - No fallback operation

---

*The validation system is designed for reliability and accuracy. It will not compromise on quality by providing fallback responses when proper validation cannot be performed.*

