# Prompt Engine Docker Model Setup

This directory contains a Docker-specific setup script for configuring Ollama models for the Prompt Engine.

## Files

- `setup_docker_models.py` - Main setup script for Docker-based Ollama model installation

## Usage

### Prerequisites

1. **Docker must be running**
2. **Ollama container must be running**:
   ```bash
   docker run -d -p 11434:11434 --name ollama ollama/ollama
   # or
   docker-compose up ollama
   ```

### Running the Setup

```bash
cd app
python setup_docker_models.py
```

### What it does

1. **Finds Ollama Container**: Automatically detects running Ollama containers
2. **Tests API Connection**: Verifies Ollama API is accessible on port 11434
3. **Checks Current Models**: Lists all currently available models
4. **Downloads Required Models**: 
   - Primary: `llama3.1:8b` (default for prompt engine)
   - Alternatives: `llama3.2:3b`, `llama2:7b`, `phi3:3.8b`
5. **Verifies Installation**: Confirms models are ready for use

### Expected Output

```
🚀 Prompt Engine Docker Ollama Model Setup
==================================================
🔍 Looking for Ollama container...
   🐳 Found Ollama container: ollama

🔍 Testing Ollama API...
   ✅ Ollama API is accessible

📋 Checking current models...
   Currently available: 1 models
      • llama3.1:8b

🎯 Required models for Prompt Engine:
   • llama3.1:8b

🎉 All required models are already available!

🎉 Prompt Engine model setup completed!

Next steps:
1. Start prompt engine: python main.py
2. Test prompt engine: curl http://localhost:5000/system/status
3. Test generation: curl -X POST http://localhost:5000/generate
```

### Troubleshooting

**No Ollama container found:**
```bash
docker run -d -p 11434:11434 --name ollama ollama/ollama
```

**API not accessible:**
```bash
# Check if port 11434 is exposed
docker ps
# Should show: 0.0.0.0:11434->11434/tcp
```

**Model download fails:**
```bash
# Check Docker logs
docker logs ollama
```

### Configuration

The script uses the following model configuration:
- **Primary Model**: `llama3.1:8b` (as defined in `config.py`)
- **Alternative Models**: `llama3.2:3b`, `llama2:7b`, `phi3:3.8b`

To change the default model, update `config.py`:
```python
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'your-preferred-model')
```

### Integration with Other Services

The Prompt Engine works with:
- **Autonomous Agent**: Uses prompt engine for response generation
- **Validation System**: Validates generated responses
- **Qdrant Vector DB**: Stores and retrieves knowledge embeddings

### Model Requirements

| Service | Primary Model | Purpose | Resource Usage |
|---------|---------------|---------|----------------|
| Prompt Engine | `llama3.1:8b` | Prompt generation | High accuracy |
| Autonomous Agent | `llama2` | Response generation | Via prompt engine |
| Validation System | `mistral:latest` | Response validation | Efficient resource |
