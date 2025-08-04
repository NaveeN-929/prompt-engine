#!/bin/bash
# Setup script for Qdrant Vector Database

echo "🚀 Setting up Qdrant Vector Database for Agentic Prompt Engine..."

# Option 1: Docker setup (recommended)
echo "📦 Setting up Qdrant with Docker..."
docker pull qdrant/qdrant
docker run -d -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z --name qdrant qdrant/qdrant

echo "✅ Qdrant is running on:"
echo "   - REST API: http://localhost:6333"
echo "   - Web UI: http://localhost:6333/dashboard"

# Option 2: Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🎯 Setup complete! Your agentic prompt engine now has:"
echo "   ✅ Vector database for ultra-fast similarity search"
echo "   ✅ Sentence transformers for embeddings"
echo "   ✅ Pure agentic prompt generation"
echo ""
echo "🚀 Start the application with: python run.py"
echo "🌐 Access the interface at: http://localhost:5000"