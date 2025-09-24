#!/bin/bash

# Setup models for validation service in Docker environment

echo "🤖 Setting up Validation Models in Docker Environment"
echo "====================================================="

# Check if Ollama is accessible
OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
echo "Testing Ollama connection at ${OLLAMA_HOST}..."

if ! curl -sf "${OLLAMA_HOST}/api/tags" > /dev/null 2>&1; then
    echo "❌ Cannot connect to Ollama at ${OLLAMA_HOST}"
    echo "💡 Make sure Ollama service is running and accessible"
    exit 1
fi

echo "✅ Ollama is accessible"

# Models needed for validation
MODELS=(
    "llama3.2:3b"
    "llama3.2:1b"
)

echo ""
echo "📦 Installing validation models..."

for model in "${MODELS[@]}"; do
    echo "Installing ${model}..."
    
    # Use curl to pull model via Ollama API
    curl -X POST "${OLLAMA_HOST}/api/pull" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"${model}\"}" \
        --max-time 600
    
    if [ $? -eq 0 ]; then
        echo "✅ ${model} installed successfully"
    else
        echo "❌ Failed to install ${model}"
    fi
    
    echo ""
done

echo "🔍 Verifying installed models..."
curl -s "${OLLAMA_HOST}/api/tags" | python3 -m json.tool

echo ""
echo "✅ Model setup complete!"
echo ""
echo "💡 You can now restart the validation service:"
echo "   docker-compose restart validator"
