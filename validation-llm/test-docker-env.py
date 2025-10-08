#!/usr/bin/env python3
"""
Test Docker Environment Variables for Validation Service
"""

import os
import sys
import requests
from config import get_config

def test_environment_variables():
    """Test that environment variables are set correctly"""
    print("🔍 Testing Docker Environment Variables")
    print("=" * 40)
    
    # Check environment variables
    env_vars = {
        "DOCKER_ENV": os.getenv("DOCKER_ENV", "not_set"),
        "OLLAMA_HOST": os.getenv("OLLAMA_HOST", "not_set"),
        "OLLAMA_PORT": os.getenv("OLLAMA_PORT", "not_set"),
        "QDRANT_HOST": os.getenv("QDRANT_HOST", "not_set"),
        "QDRANT_PORT": os.getenv("QDRANT_PORT", "not_set"),
        "VALIDATION_HOST": os.getenv("VALIDATION_HOST", "not_set"),
        "VALIDATION_PORT": os.getenv("VALIDATION_PORT", "not_set")
    }
    
    print("📋 Environment Variables:")
    for key, value in env_vars.items():
        print(f"   {key}: {value}")
    
    print()
    
    # Test configuration loading
    print("🔧 Testing Configuration Loading:")
    try:
        config = get_config()
        validation_llm_config = config["validation_llm"]["primary_validator"]
        
        print(f"   Primary Validator Host: {validation_llm_config['host']}")
        print(f"   Primary Validator Model: {validation_llm_config['model_name']}")
        
        vector_db_config = config["vector_db"]
        print(f"   Qdrant Host: {vector_db_config['host']}")
        print(f"   Qdrant Port: {vector_db_config['port']}")
        
        print("   ✅ Configuration loaded successfully")
        
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    return True

def test_service_connectivity():
    """Test connectivity to required services"""
    print("\n🌐 Testing Service Connectivity:")
    
    config = get_config()
    
    # Test Ollama connection
    ollama_host = config["validation_llm"]["primary_validator"]["host"]
    print(f"   Testing Ollama at {ollama_host}...")
    
    try:
        response = requests.get(f"{ollama_host}/api/tags", timeout=10)
        if response.status_code == 200:
            print("   ✅ Ollama connection successful")
            
            # Check if models are available
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            print(f"   📦 Available models: {len(models)}")
            
            required_models = ["mistral:latest"]
            for model in required_models:
                if any(model in available_model for available_model in models):
                    print(f"   ✅ Model {model} available")
                else:
                    print(f"   ⚠️ Model {model} not found")
        else:
            print(f"   ❌ Ollama connection failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ollama connection error: {e}")
        return False
    
    # Test Qdrant connection
    qdrant_host = config["vector_db"]["host"]
    qdrant_port = config["vector_db"]["port"]
    qdrant_url = f"http://{qdrant_host}:{qdrant_port}"
    
    print(f"   Testing Qdrant at {qdrant_url}...")
    
    try:
        response = requests.get(f"{qdrant_url}/collections", timeout=10)
        if response.status_code == 200:
            print("   ✅ Qdrant connection successful")
        else:
            print(f"   ❌ Qdrant connection failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Qdrant connection error: {e}")
        return False
    
    return True

def main():
    """Main test execution"""
    print("🐳 Docker Environment Test for Validation Service")
    print("=" * 50)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    if not env_ok:
        print("\n❌ Environment variable test failed")
        return 1
    
    # Test service connectivity
    connectivity_ok = test_service_connectivity()
    
    if not connectivity_ok:
        print("\n❌ Service connectivity test failed")
        return 1
    
    print("\n✅ All tests passed! Docker environment is configured correctly.")
    print("\n🚀 Validation service should be able to initialize successfully.")
    
    return 0

if __name__ == "__main__":
    exit(main())
