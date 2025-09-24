#!/bin/bash
set -e

# Docker entrypoint script for Validation LLM Service

echo "🚀 Starting Validation LLM Service..."
echo "Environment: ${FLASK_ENV:-production}"
echo "Host: ${VALIDATION_HOST:-0.0.0.0}:${VALIDATION_PORT:-5002}"
echo "Ollama: ${OLLAMA_HOST:-http://localhost:11434}"
echo "Qdrant: ${QDRANT_HOST:-localhost}:${QDRANT_PORT:-6333}"

# Wait for dependencies to be ready
echo "⏳ Waiting for dependencies..."

# Wait for Ollama
echo "Checking Ollama connection..."
OLLAMA_URL="${OLLAMA_HOST:-http://localhost:11434}"
for i in {1..30}; do
    if curl -sf "${OLLAMA_URL}/api/tags" > /dev/null 2>&1; then
        echo "✅ Ollama is ready at ${OLLAMA_URL}"
        break
    fi
    echo "⏳ Waiting for Ollama... (attempt $i/30)"
    sleep 5
done

# Wait for Qdrant
echo "Checking Qdrant connection..."
QDRANT_URL="http://${QDRANT_HOST:-localhost}:${QDRANT_PORT:-6333}"
for i in {1..30}; do
    if curl -sf "${QDRANT_URL}/collections" > /dev/null 2>&1; then
        echo "✅ Qdrant is ready at ${QDRANT_URL}"
        break
    fi
    echo "⏳ Waiting for Qdrant... (attempt $i/30)"
    sleep 5
done

# Test environment configuration
echo "🧪 Testing environment configuration..."
python test-docker-env.py

if [ $? -eq 0 ]; then
    echo "✅ Environment configuration test passed"
else
    echo "❌ Environment configuration test failed"
    echo "⚠️ Continuing anyway, but validation may not work properly"
fi

# Test imports
echo "🧪 Testing imports..."
python test_imports.py

if [ $? -eq 0 ]; then
    echo "✅ All imports successful"
else
    echo "❌ Import test failed"
    exit 1
fi

# Create necessary directories
mkdir -p /app/logs
mkdir -p /app/training_data/{exemplary,high_quality,acceptable,exports}

# Set permissions
chmod -R 755 /app/logs
chmod -R 755 /app/training_data

echo "🎉 Starting validation server..."

# Execute the main command
exec "$@"