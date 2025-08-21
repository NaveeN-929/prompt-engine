#!/usr/bin/env python3
"""
Debug script to check environment variable resolution
"""

import os
import sys
sys.path.append('/app')  # Add app directory to path for Docker

print("🔍 Environment Variable Debug")
print("=" * 40)

# Check raw environment variables
print("📋 Raw Environment Variables:")
env_vars = [
    'DOCKER_ENV',
    'PROMPT_ENGINE_HOST', 
    'PROMPT_ENGINE_PORT',
    'OLLAMA_HOST',
    'OLLAMA_PORT', 
    'QDRANT_HOST',
    'QDRANT_PORT'
]

for var in env_vars:
    value = os.getenv(var, 'NOT SET')
    print(f"   {var}: {value}")

print()

# Check config resolution
try:
    from config import PROMPT_ENGINE_URL, PROMPT_ENGINE_HOST, PROMPT_ENGINE_PORT
    print("✅ Config import successful:")
    print(f"   PROMPT_ENGINE_HOST: {PROMPT_ENGINE_HOST}")
    print(f"   PROMPT_ENGINE_PORT: {PROMPT_ENGINE_PORT}")
    print(f"   PROMPT_ENGINE_URL: {PROMPT_ENGINE_URL}")
except Exception as e:
    print(f"❌ Config import failed: {e}")

print()

# Test the actual URL that would be used
try:
    from core.prompt_consumer import PromptConsumerService
    consumer = PromptConsumerService()
    print(f"🔗 Default PromptConsumerService URL: {consumer.prompt_engine_url}")
    
    # Test with explicit URL
    consumer_explicit = PromptConsumerService(PROMPT_ENGINE_URL)
    print(f"🔗 Explicit PromptConsumerService URL: {consumer_explicit.prompt_engine_url}")
except Exception as e:
    print(f"❌ PromptConsumerService test failed: {e}")

print("\n🏁 Debug complete")
