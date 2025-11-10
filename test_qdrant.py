#!/usr/bin/env python3
"""
Quick test script to verify Qdrant connection
"""

import sys
import requests
from qdrant_client import QdrantClient
from config import QDRANT_HOST, QDRANT_PORT

def test_qdrant_connection():
    """Test Qdrant connection"""
    print("🔍 Testing Qdrant Connection...")
    print(f"   Host: {QDRANT_HOST}")
    print(f"   Port: {QDRANT_PORT}")
    print(f"   URL: http://{QDRANT_HOST}:{QDRANT_PORT}")
    print()
    
    # Test 1: HTTP Connection
    print("1️⃣ Testing HTTP connection...")
    try:
        response = requests.get(f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections", timeout=5)
        if response.status_code == 200:
            print("   ✅ HTTP connection successful!")
            collections = response.json()
            print(f"   📦 Collections: {collections}")
        else:
            print(f"   ❌ HTTP connection failed with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection refused: {e}")
        print()
        print("💡 Qdrant is not running or not accessible at localhost:6333")
        print()
        print("🔧 To fix this, run:")
        print("   ./start_qdrant.sh")
        print()
        print("Or manually start Qdrant with Docker:")
        print("   docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant:latest")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Qdrant Client Connection
    print()
    print("2️⃣ Testing Qdrant client connection...")
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        collections = client.get_collections()
        print("   ✅ Qdrant client connected successfully!")
        print(f"   📦 Collections: {[c.name for c in collections.collections]}")
    except Exception as e:
        print(f"   ❌ Qdrant client error: {e}")
        return False
    
    # Test 3: Check collections
    print()
    print("3️⃣ Checking required collections...")
    required_collections = ['agentic_prompts', 'successful_patterns', 'data_insights']
    for collection_name in required_collections:
        exists = any(col.name == collection_name for col in collections.collections)
        if exists:
            print(f"   ✅ Collection '{collection_name}' exists")
        else:
            print(f"   ℹ️  Collection '{collection_name}' will be created on first use")
    
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ Qdrant is ready for use!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("🌐 Qdrant Dashboard: http://localhost:6333/dashboard")
    print()
    return True

if __name__ == "__main__":
    success = test_qdrant_connection()
    sys.exit(0 if success else 1)

