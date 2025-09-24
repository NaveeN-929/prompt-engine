# 🔗 Shared Infrastructure Setup Guide

This guide explains how to set up the validation system to share infrastructure (Ollama and Qdrant) with your existing prompt engine and autonomous agent projects.

## Overview

The validation system is designed to **share resources** with your existing setup:

- **Ollama Container**: Same instance, different models
- **Qdrant Database**: Same instance, different collections  
- **Port Configuration**: Non-conflicting ports

## Infrastructure Sharing

```
┌─────────────────────────────────────────────────────────────────┐
│                    Shared Infrastructure                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐              ┌─────────────────┐           │
│  │   Ollama LLM    │              │   Qdrant DB     │           │
│  │ (Port 11434)    │              │ (Port 6333)     │           │
│  │                 │              │                 │           │
│  │ • llama3.1:8b   │              │ Main Collections│           │
│  │ • llama3.2:3b   │◄─────────────┤ + Validation    │           │
│  │ • llama3.2:1b   │              │   Collections   │           │
│  └─────────────────┘              └─────────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Prompt Engine   │  │ Autonomous      │  │ Validation      │
│ (Port 5000)     │  │ Agent           │  │ System          │
│                 │  │ (Port 8000)     │  │ (Port 5002)     │
│ Uses:           │  │                 │  │                 │
│ • llama3.1:8b   │  │ Uses:           │  │ Uses:           │
│ • Main Qdrant   │  │ • Prompt Engine │  │ • llama3.2:3b   │
│   Collections   │  │ • Main LLM      │  │ • llama3.2:1b   │
└─────────────────┘  │ • Qdrant RAG    │  │ • Validation    │
                     └─────────────────┘  │   Collections   │
                                          └─────────────────┘
```

## Step-by-Step Setup

### 1. Verify Existing Infrastructure

First, check that your existing services are running:

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check Qdrant is running
curl http://localhost:6333/dashboard

# Check existing services
curl http://localhost:5000/health      # Prompt Engine
curl http://localhost:8000/agent/status # Autonomous Agent
```

### 2. Setup Validation Models

The validation system uses **different, smaller models** to avoid conflicts:

```bash
cd validation-llm

# For Docker-based Ollama (recommended)
python setup_docker_models.py

# For CLI-based Ollama
python setup_models.py
```

This will pull:
- `llama3.2:3b` - Primary validation model (smaller than main llama3.1:8b)
- `llama3.2:1b` - Speed validation model (very fast)

### 3. Configure Shared Resources

The configuration is already set up to share resources:

**Ollama Configuration:**
```python
VALIDATION_LLM_CONFIG = {
    "primary_validator": {
        "model_name": "llama3.2:3b",      # Different from main project
        "host": "http://localhost:11434",  # Same Ollama instance
        "temperature": 0.1,               # Low temp for consistency
    },
    "speed_validator": {
        "model_name": "llama3.2:1b",      # Fast validation model
        "host": "http://localhost:11434",  # Same Ollama instance
        "temperature": 0.2,
    }
}
```

**Qdrant Configuration:**
```python
VECTOR_DB_CONFIG = {
    "host": "localhost",
    "port": 6333,  # Same Qdrant instance
    "collections": {
        # Validation-specific collections (won't conflict with main project)
        "validated_responses": "validation_high_quality_responses",
        "validation_patterns": "validation_successful_patterns", 
        "training_data": "validation_training_dataset",
        "feedback_patterns": "validation_feedback_patterns"
    }
}
```

### 4. Start Validation System

```bash
cd validation-llm

# Test that everything is configured correctly
python test_imports.py

# Start the validation server
python simple_server.py
```

The server will start on **port 5002** (no conflict with existing services).

### 5. Verify Integration

Test that all systems work together:

```bash
# Test validation system
curl http://localhost:5002/health

# Test a validation request
curl -X POST http://localhost:5002/validate/response \
  -H "Content-Type: application/json" \
  -d '{
    "response_data": {
      "analysis": "=== SECTION 1: INSIGHTS ===\nTest insights\n=== SECTION 2: RECOMMENDATIONS ===\nTest recommendations"
    },
    "input_data": {
      "transactions": [{"amount": 100, "type": "credit"}]
    }
  }'
```

## Resource Usage

### Model Usage by Service

| Service | Primary Model | Purpose | Resource Usage |
|---------|---------------|---------|----------------|
| Prompt Engine | `llama3.1:8b` | Prompt generation | High accuracy |
| Autonomous Agent | Uses Prompt Engine | Response generation | Via prompt engine |
| Validation System | `llama3.2:3b` | Response validation | Lower resource |
| Speed Validation | `llama3.2:1b` | Fast validation | Minimal resource |

### Qdrant Collections

| Project | Collection Prefix | Purpose |
|---------|------------------|---------|
| Main Project | `prompts_*`, `analysis_*` | Prompt patterns, analysis data |
| Validation System | `validation_*` | Validation patterns, training data |

Collections are **completely separate** - no conflicts or data mixing.

### Port Usage

| Service | Port | Purpose |
|---------|------|---------|
| Prompt Engine | 5000 | Main prompt generation |
| Validation System | 5002 | Response validation |
| Autonomous Agent | 8000 | Analysis endpoint |
| Ollama | 11434 | LLM API (shared) |
| Qdrant | 6333 | Vector DB (shared) |

## Benefits of Shared Infrastructure

### 1. **Resource Efficiency**
- Single Ollama instance serves multiple models
- Single Qdrant instance with separate collections
- Reduced memory and CPU usage

### 2. **Cost Savings**
- No need for additional containers
- Shared GPU resources (if using GPU acceleration)
- Lower infrastructure costs

### 3. **Simplified Management**
- Single point of management for LLM models
- Unified vector database administration
- Consistent backup and monitoring

### 4. **Performance**
- Models stay loaded in memory
- Faster switching between models
- Shared caching benefits

## Troubleshooting Shared Setup

### Model Conflicts
If you get model loading issues:

```bash
# Check which models are loaded
curl http://localhost:11434/api/tags

# For Docker-based Ollama, check container logs
docker logs <ollama_container_name>

# For CLI-based Ollama, unload a model if needed (frees memory)
curl -X DELETE http://localhost:11434/api/generate -d '{"model": "model_name", "keep_alive": 0}'

# For Docker-based Ollama, restart container if needed
docker restart <ollama_container_name>
```

### Collection Conflicts
If you get Qdrant collection issues:

```bash
# List all collections
curl http://localhost:6333/collections

# Check collection details
curl http://localhost:6333/collections/validation_high_quality_responses
```

### Port Conflicts
If port 5002 is in use:

```bash
# Check what's using the port
netstat -an | grep 5002

# Change port in config.py if needed
```

## Monitoring Shared Resources

### Ollama Resource Usage
```bash
# Check loaded models and memory usage
curl http://localhost:11434/api/tags | jq '.models[] | {name: .name, size: .size}'
```

### Qdrant Resource Usage
```bash
# Check database statistics
curl http://localhost:6333/metrics
```

### System Resource Usage
```bash
# Monitor CPU and memory
htop

# Check GPU usage (if applicable)
nvidia-smi
```

## Integration Testing

Test the complete pipeline:

```bash
cd validation-llm

# Run integration example
python examples/integration_example.py
```

This will test:
1. Autonomous agent response generation
2. Validation system assessment  
3. Training data storage
4. Feedback loop integration

## Next Steps

1. **Monitor Resource Usage**: Keep an eye on Ollama and Qdrant performance
2. **Tune Model Selection**: Adjust models based on performance needs
3. **Scale as Needed**: Add more models or increase resources if needed
4. **Backup Strategy**: Include validation data in your backup procedures

---

*The shared infrastructure approach maximizes efficiency while maintaining complete separation of concerns between your main project and the validation system.*
