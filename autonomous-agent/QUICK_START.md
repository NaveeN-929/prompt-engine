# 🚀 Quick Start Guide

## Fix the "No module named 'flask'" Error

The error indicates that Flask and other dependencies are not installed in your Python environment. Here's how to fix it:

### Option 1: Automated Setup (Recommended)

**On Windows:**
```cmd
# Run the automated setup script
install.bat
```

**On Linux/Mac:**
```bash
# Run the automated setup script
python setup.py
```

### Option 2: Manual Installation

```bash
# Navigate to the autonomous-agent directory
cd autonomous-agent

# Install all dependencies
pip install -r requirements.txt

# Create environment file
copy env.template .env   # Windows
cp env.template .env     # Linux/Mac

# Create logs directory
mkdir logs
```

### Option 3: Using Virtual Environment (Best Practice)

```bash
# Create virtual environment
python -m venv agent_env

# Activate virtual environment
# Windows:
agent_env\Scripts\activate
# Linux/Mac:
source agent_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy env.template .env   # Windows
cp env.template .env     # Linux/Mac
```

## Start the Agent

Once dependencies are installed:

```bash
# Start the autonomous agent
python run_agent.py
```

## Access the Web Interface

Open your browser and go to:
```
http://localhost:5001
```

## Test the Agent

```bash
# Run comprehensive tests
python test_agent.py
```

## Configuration

Edit the `.env` file to configure:
- Prompt engine connection (default: localhost:5000)
- LLM provider settings (Ollama, OpenAI, etc.)
- Vector database connection
- Agent behavior settings

## Troubleshooting

### Common Issues:

1. **"No module named 'flask'"**
   - Solution: Run `pip install -r requirements.txt`

2. **"Prompt engine not available"**
   - Ensure your prompt-engine is running on port 5000
   - Check the PROMPT_ENGINE_HOST and PROMPT_ENGINE_PORT in .env

3. **"LLM provider not available"**
   - Ensure Ollama is running on port 11434
   - Or configure OpenAI/Anthropic API keys in .env

4. **Port already in use**
   - Change FLASK_PORT in .env to a different port (e.g., 5002)

### Environment Check:

```bash
# Check Python version (should be 3.8+)
python --version

# Check if Flask is installed
python -c "import flask; print('Flask version:', flask.__version__)"

# List installed packages
pip list
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure .env file
3. ✅ Start the prompt-engine (if not already running)
4. ✅ Start the autonomous agent
5. ✅ Access the web interface
6. ✅ Test with sample financial data

The autonomous agent will then provide sophisticated financial analysis with anti-hallucination mechanisms!

## Fix the "No module named 'flask'" Error

The error indicates that Flask and other dependencies are not installed in your Python environment. Here's how to fix it:

### Option 1: Automated Setup (Recommended)

**On Windows:**
```cmd
# Run the automated setup script
install.bat
```

**On Linux/Mac:**
```bash
# Run the automated setup script
python setup.py
```

### Option 2: Manual Installation

```bash
# Navigate to the autonomous-agent directory
cd autonomous-agent

# Install all dependencies
pip install -r requirements.txt

# Create environment file
copy env.template .env   # Windows
cp env.template .env     # Linux/Mac

# Create logs directory
mkdir logs
```

### Option 3: Using Virtual Environment (Best Practice)

```bash
# Create virtual environment
python -m venv agent_env

# Activate virtual environment
# Windows:
agent_env\Scripts\activate
# Linux/Mac:
source agent_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy env.template .env   # Windows
cp env.template .env     # Linux/Mac
```

## Start the Agent

Once dependencies are installed:

```bash
# Start the autonomous agent
python run_agent.py
```

## Access the Web Interface

Open your browser and go to:
```
http://localhost:5001
```

## Test the Agent

```bash
# Run comprehensive tests
python test_agent.py
```

## Configuration

Edit the `.env` file to configure:
- Prompt engine connection (default: localhost:5000)
- LLM provider settings (Ollama, OpenAI, etc.)
- Vector database connection
- Agent behavior settings

## Troubleshooting

### Common Issues:

1. **"No module named 'flask'"**
   - Solution: Run `pip install -r requirements.txt`

2. **"Prompt engine not available"**
   - Ensure your prompt-engine is running on port 5000
   - Check the PROMPT_ENGINE_HOST and PROMPT_ENGINE_PORT in .env

3. **"LLM provider not available"**
   - Ensure Ollama is running on port 11434
   - Or configure OpenAI/Anthropic API keys in .env

4. **Port already in use**
   - Change FLASK_PORT in .env to a different port (e.g., 5002)

### Environment Check:

```bash
# Check Python version (should be 3.8+)
python --version

# Check if Flask is installed
python -c "import flask; print('Flask version:', flask.__version__)"

# List installed packages
pip list
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure .env file
3. ✅ Start the prompt-engine (if not already running)
4. ✅ Start the autonomous agent
5. ✅ Access the web interface
6. ✅ Test with sample financial data

The autonomous agent will then provide sophisticated financial analysis with anti-hallucination mechanisms!