#!/usr/bin/env python3
"""
Start Repersonalization Service (Port 5004) - Flask
Quick launcher from project root
Requires: Pseudonymization Service on port 5003
"""

import sys
import os
import redis
import requests

# Change to repersonalization service directory
service_dir = os.path.join(os.path.dirname(__file__), 'repersonalization-service')
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
        print("⚠️  Redis not available")
        return False

def check_pseudonymization_service():
    """Check if Pseudonymization service is running"""
    try:
        response = requests.get("http://localhost:5003/health", timeout=2)
        if response.status_code == 200:
            print("✅ Pseudonymization service is running (localhost:5003)")
            return True
        else:
            print("⚠️  Pseudonymization service responded but not healthy")
            return False
    except Exception as e:
        print("⚠️  Pseudonymization service not available (localhost:5003)")
        print("   Start it with: python3 start_pseudonymization.py")
        return False

if __name__ == "__main__":
    from app.main import app
    
    print("=" * 70)
    print("🔓 Starting Repersonalization Service (Flask)")
    print("=" * 70)
    print("Host: 0.0.0.0")
    print("Port: 5004")
    print("")
    
    # Check dependencies
    check_redis()
    check_pseudonymization_service()
    
    print("")
    print("✨ Features:")
    print("   - Secure Data Restoration")
    print("   - Integrity Verification")
    print("   - Bulk Repersonalization")
    print("   - GDPR Cleanup Support")
    print("\n💡 Press Ctrl+C to stop")
    print("=" * 70)
    
    app.run(
        host="0.0.0.0",
        port=5004,
        debug=False
    )
