#!/usr/bin/env python3
"""
Check Redis connectivity and display stats
"""

import redis
import sys

def check_redis():
    """Check if Redis is running and accessible"""
    try:
        client = redis.from_url("redis://localhost:6379", decode_responses=True)
        
        # Test connection
        response = client.ping()
        if not response:
            print("❌ Redis connection failed - no response to PING")
            return False
        
        print("✅ Redis is connected and healthy")
        print()
        
        # Get info
        info = client.info()
        print("📊 Redis Information:")
        print(f"  - Version: {info.get('redis_version', 'unknown')}")
        print(f"  - Uptime: {info.get('uptime_in_days', 0)} days")
        print(f"  - Used Memory: {info.get('used_memory_human', 'unknown')}")
        print(f"  - Connected Clients: {info.get('connected_clients', 0)}")
        print(f"  - Total Keys: {client.dbsize()}")
        print()
        
        # Check for pseudonym keys
        pseudonym_keys = client.keys("pseudonym:*")
        if pseudonym_keys:
            print(f"🔑 Active Pseudonyms: {len(pseudonym_keys)}")
            print(f"  Example keys: {pseudonym_keys[:3]}")
        else:
            print("🔑 No pseudonym tokens stored yet")
        
        print()
        print("✅ Redis is ready for token storage")
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {str(e)}")
        print()
        print("To start Redis:")
        print("  ./start_redis.sh")
        print("  OR")
        print("  docker run -d -p 6379:6379 --name redis-tokens redis:7-alpine")
        return False
    except Exception as e:
        print(f"❌ Error checking Redis: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_redis()
    sys.exit(0 if success else 1)

