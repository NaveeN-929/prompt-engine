#!/bin/bash
# Start Autonomous Agent with proper environment variables

cd "$(dirname "$0")"

# Source the virtual environment
source agent/bin/activate

# Set environment variables for local development
export VALIDATOR_HOST="localhost"
export VALIDATOR_PORT="5002"
export VALIDATION_HOST="0.0.0.0"
export VALIDATION_PORT="5002"
export QDRANT_HOST="localhost"
export QDRANT_PORT="6333"
export PROMPT_ENGINE_HOST="localhost"
export PROMPT_ENGINE_PORT="5000"

echo "🚀 Starting Autonomous Agent with validation integration..."
echo "   Validation Service: http://$VALIDATOR_HOST:$VALIDATOR_PORT"
echo "   Qdrant: $QDRANT_HOST:$QDRANT_PORT"
echo "   Prompt Engine: http://$PROMPT_ENGINE_HOST:$PROMPT_ENGINE_PORT"

# Start the server
python3 server_final.py

