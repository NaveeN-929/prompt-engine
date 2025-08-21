#!/usr/bin/env python3
"""
Test script to verify Docker network connectivity
Run this inside the autonomous-agent container to test connections
"""

import os
import requests
import time
from config import PROMPT_ENGINE_URL, OLLAMA_HOST, OLLAMA_PORT, QDRANT_HOST, QDRANT_PORT

def test_service_connectivity():
    """Test connectivity to all required services"""
    
    print("🔍 Testing Docker Network Connectivity")
    print("=" * 50)
    
    # Test environment variables
    print(f"📋 Environment Variables:")
    print(f"   PROMPT_ENGINE_HOST: {os.getenv('PROMPT_ENGINE_HOST', 'NOT SET')}")
    print(f"   PROMPT_ENGINE_PORT: {os.getenv('PROMPT_ENGINE_PORT', 'NOT SET')}")
    print(f"   PROMPT_ENGINE_URL: {PROMPT_ENGINE_URL}")
    print(f"   OLLAMA_HOST: {OLLAMA_HOST}")
    print(f"   QDRANT_HOST: {QDRANT_HOST}")
    print()
    
    services = [
        ("Prompt Engine", f"{PROMPT_ENGINE_URL}/system/status"),
        ("Prompt Engine Health", f"{PROMPT_ENGINE_URL}/health"), 
        ("Ollama", f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags"),
        ("Qdrant", f"http://{QDRANT_HOST}:{QDRANT_PORT}/dashboard"),
    ]
    
    for service_name, url in services:
        try:
            print(f"🔗 Testing {service_name}: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {service_name}: Connected (Status: {response.status_code})")
            else:
                print(f"   ⚠️  {service_name}: HTTP {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ {service_name}: Connection refused - {e}")
        except requests.exceptions.Timeout:
            print(f"   ⏰ {service_name}: Timeout after 5 seconds")
        except Exception as e:
            print(f"   💥 {service_name}: Error - {e}")
        
        time.sleep(0.5)
    
    print()
    print("🏁 Connectivity test completed")

if __name__ == "__main__":
    test_service_connectivity()
