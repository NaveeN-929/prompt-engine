#!/usr/bin/env python3
"""
Simple test to check if environment variables are being read correctly
"""

import os

print("Environment Variable Test")
print("=" * 30)

# Check if we're in Docker
print(f"DOCKER_ENV: {os.getenv('DOCKER_ENV', 'NOT_SET')}")
print(f"PROMPT_ENGINE_HOST: {os.getenv('PROMPT_ENGINE_HOST', 'NOT_SET')}")
print(f"PROMPT_ENGINE_PORT: {os.getenv('PROMPT_ENGINE_PORT', 'NOT_SET')}")

# Manual URL construction
host = os.getenv('PROMPT_ENGINE_HOST', 'localhost')
port = os.getenv('PROMPT_ENGINE_PORT', '5000')
manual_url = f"http://{host}:{port}"
print(f"Manual URL: {manual_url}")

# Test config import
try:
    from config import PROMPT_ENGINE_URL
    print(f"Config URL: {PROMPT_ENGINE_URL}")
except Exception as e:
    print(f"Config import error: {e}")
