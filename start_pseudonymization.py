#!/usr/bin/env python3
"""
Start Pseudonymization Service (Port 5003) - Flask
Quick launcher from project root
Requires: Redis on port 6379
"""

import sys
import os
import redis

# Change to pseudonymization service directory
service_dir = os.path.join(os.path.dirname(__file__), 'pseudonymization-service')
os.chdir(service_dir)
sys.path.insert(0, service_dir)

def check_redis():
    """Check if Redis is available"""
    try:
        client = redis.from_url("redis://localhost:6379", decode_responses=True)
        client.ping()
        print("✅ Redis connected (localhost:6379)")
        return True
    except Exception as e:
        print("⚠️  Redis not available - will use in-memory fallback")
        print("   To start Redis: ./start_redis.sh")
        print(f"   Error: {str(e)}")
        return False

if __name__ == "__main__":
    from app.main import app
    
    print("=" * 70)
    print("🔒 Starting Pseudonymization Service (Flask)")
    print("=" * 70)
    print("Host: 0.0.0.0")
    print("Port: 5003")
    print("")
    
    # Check Redis
    check_redis()
    
    print("")
    print("✨ Features:")
    print("   - Automatic PII Detection (20+ types)")
    print("   - Type-specific Tokenization")
    print("   - Redis Token Storage (with in-memory fallback)")
    print("   - Field-level Security")
    print("   - GDPR Compliant")
    print("\n💡 Press Ctrl+C to stop")
    print("=" * 70)
    
    app.run(
        host="0.0.0.0",
        port=5003,
        debug=False
    )
