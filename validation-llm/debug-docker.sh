#!/bin/bash

# Debug script for Docker validation service issues

echo "🔍 Debugging Validation Service Docker Issues"
echo "============================================="

# Check if containers are running
echo "📊 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(validator|ollama|qdrant)"

echo ""
echo "🌐 Network Connectivity Tests:"

# Test from validator container to ollama
echo "Testing validator → ollama connection:"
docker exec paytechneodemo-validator curl -sf http://ollama:11434/api/tags > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Validator can reach Ollama"
else
    echo "   ❌ Validator cannot reach Ollama"
fi

# Test from validator container to qdrant
echo "Testing validator → qdrant connection:"
docker exec paytechneodemo-validator curl -sf http://qdrant:6333/collections > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Validator can reach Qdrant"
else
    echo "   ❌ Validator cannot reach Qdrant"
fi

echo ""
echo "🔧 Environment Variables in Validator Container:"
docker exec paytechneodemo-validator env | grep -E "(OLLAMA|QDRANT|VALIDATION)"

echo ""
echo "📋 Validation Service Logs (last 20 lines):"
docker logs paytechneodemo-validator --tail 20

echo ""
echo "🧪 Running Environment Test in Container:"
docker exec paytechneodemo-validator python test-docker-env.py

echo ""
echo "💡 Troubleshooting Tips:"
echo "   1. Ensure all services are up: docker-compose ps"
echo "   2. Check Ollama models: docker exec paytechneodemo-ollama ollama list"
echo "   3. Restart validator: docker-compose restart validator"
echo "   4. Check full logs: docker logs paytechneodemo-validator"
