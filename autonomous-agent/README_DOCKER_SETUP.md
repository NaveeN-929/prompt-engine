# Autonomous Agent Docker Model Setup

This directory contains a Docker-specific setup script for configuring Ollama models for the Autonomous Agent.

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
cd autonomous-agent
python setup_docker_models.py
```

### What it does

1. **Finds Ollama Container**: Automatically detects running Ollama containers
2. **Tests API Connection**: Verifies Ollama API is accessible on port 11434
3. **Checks Current Models**: Lists all currently available models
4. **Downloads Required Models**: 
   - Primary: `llama2` (default for autonomous agent)
   - Alternatives: `llama3.1:8b`, `llama3.2:3b`, `phi3:3.8b`
5. **Verifies Installation**: Confirms models are ready for use

### Expected Output

```
🤖 Autonomous Agent Docker Ollama Model Setup
==================================================
🔍 Looking for Ollama container...
   🐳 Found Ollama container: ollama

🔍 Testing Ollama API...
   ✅ Ollama API is accessible

📋 Checking current models...
   Currently available: 1 models
      • llama2

🎯 Required models for Autonomous Agent:
   • llama2

🎉 All required models are already available!

🎉 Autonomous Agent model setup completed!

Next steps:
1. Start autonomous agent: python run_agent.py
2. Test agent: curl http://localhost:8000/agent/status
3. Check integration: curl http://localhost:8000/analyze
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
- **Primary Model**: `llama2` (as defined in `config.py`)
- **Alternative Models**: `llama3.1:8b`, `llama3.2:3b`, `phi3:3.8b`

To change the default model, update `config.py`:
```python
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "your-preferred-model")
```
