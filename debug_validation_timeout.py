#!/usr/bin/env python3
"""
Comprehensive validation service timeout debugging
"""

import requests
import json
import time
import asyncio
import threading

def test_basic_connectivity():
    """Test basic service connectivity"""
    print("🔍 Testing Basic Connectivity")
    print("-" * 30)
    
    endpoints = [
        ("Health", "http://localhost:5002/health"),
        ("Status", "http://localhost:5002/status"),
        ("Root", "http://localhost:5002/")
    ]
    
    for name, url in endpoints:
        try:
            start = time.time()
            response = requests.get(url, timeout=5)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                print(f"   ✅ {name}: {response.status_code} ({elapsed:.3f}s)")
            else:
                print(f"   ❌ {name}: {response.status_code} ({elapsed:.3f}s)")
        except Exception as e:
            print(f"   ❌ {name}: {e}")

def test_ollama_connectivity():
    """Test Ollama connectivity"""
    print("\n🤖 Testing Ollama Connectivity")
    print("-" * 30)
    
    try:
        # Test basic Ollama connection
        start = time.time()
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]
            print(f"   ✅ Ollama connection: {elapsed:.3f}s")
            print(f"   📦 Available models: {len(models)}")
            
            required_models = ["mistral:latest"]
            for model in required_models:
                if any(model in m for m in models):
                    print(f"   ✅ Model {model}: Available")
                else:
                    print(f"   ❌ Model {model}: Missing")
        else:
            print(f"   ❌ Ollama connection failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ollama error: {e}")

def test_simple_ollama_request():
    """Test a simple Ollama request to see response time"""
    print("\n⚡ Testing Simple Ollama Request")
    print("-" * 30)
    
    payload = {
        "model": "mistral:latest",
        "prompt": "Say 'OK' and nothing else.",
        "options": {"num_predict": 5, "temperature": 0.1},
        "stream": False
    }
    
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            print(f"   ✅ Simple request: {elapsed:.3f}s")
            print(f"   📝 Response: '{response_text.strip()}'")
            
            if elapsed > 10:
                print(f"   ⚠️ WARNING: Slow response time ({elapsed:.3f}s)")
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Request error: {e}")

def test_validation_request_minimal():
    """Test minimal validation request"""
    print("\n🔬 Testing Minimal Validation Request")
    print("-" * 30)
    
    minimal_data = {
        "response_data": {
            "analysis": "Simple test analysis.",
            "status": "success"
        },
        "input_data": {
            "test": True
        },
        "validation_config": {
            "fast_mode": True,
            "criteria": {
                "content_accuracy": {"weight": 1.0, "threshold": 0.5}
            }
        }
    }
    
    try:
        print("   📡 Sending minimal validation request...")
        start = time.time()
        
        response = requests.post(
            "http://localhost:5002/validate/response",
            headers={"Content-Type": "application/json"},
            json=minimal_data,
            timeout=60  # Longer timeout for debugging
        )
        
        elapsed = time.time() - start
        print(f"   ⏱️ Request completed in {elapsed:.3f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Validation successful!")
            print(f"   📊 Status: {result.get('status', 'unknown')}")
            print(f"   💯 Score: {result.get('overall_score', 0):.3f}")
            return True
        else:
            print(f"   ❌ Validation failed: HTTP {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"   ❌ Request timed out after {elapsed:.3f}s")
        return False
    except Exception as e:
        elapsed = time.time() - start
        print(f"   ❌ Request error after {elapsed:.3f}s: {e}")
        return False

def test_async_behavior():
    """Test if the issue is related to async behavior"""
    print("\n🔄 Testing Async Behavior")
    print("-" * 30)
    
    def make_request(request_id):
        try:
            start = time.time()
            response = requests.get("http://localhost:5002/health", timeout=10)
            elapsed = time.time() - start
            print(f"   Request {request_id}: {elapsed:.3f}s - {response.status_code}")
        except Exception as e:
            elapsed = time.time() - start
            print(f"   Request {request_id}: {elapsed:.3f}s - ERROR: {e}")
    
    # Make multiple concurrent requests
    threads = []
    for i in range(3):
        thread = threading.Thread(target=make_request, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

def check_validation_engine_status():
    """Check detailed validation engine status"""
    print("\n🔧 Checking Validation Engine Status")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:5002/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            
            print(f"   🏥 System status: {status.get('system', {}).get('status', 'unknown')}")
            
            engine_status = status.get('validation_engine', {})
            print(f"   🤖 Engine initialized: {engine_status.get('initialized', False)}")
            print(f"   🤖 Engine status: {engine_status.get('status', 'unknown')}")
            
            server_stats = status.get('server_statistics', {})
            print(f"   📊 Total requests: {server_stats.get('total_requests', 0)}")
            print(f"   ✅ Successful: {server_stats.get('successful_validations', 0)}")
            print(f"   ❌ Failed: {server_stats.get('failed_validations', 0)}")
            
            uptime = server_stats.get('uptime', 0)
            print(f"   ⏰ Uptime: {uptime:.1f}s")
            
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Status error: {e}")

def main():
    """Run comprehensive validation debugging"""
    print("🔍 COMPREHENSIVE VALIDATION SERVICE DEBUGGING")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    test_basic_connectivity()
    
    # Test 2: Ollama connectivity
    test_ollama_connectivity()
    
    # Test 3: Simple Ollama request
    test_simple_ollama_request()
    
    # Test 4: Validation engine status
    check_validation_engine_status()
    
    # Test 5: Async behavior
    test_async_behavior()
    
    # Test 6: Minimal validation request
    success = test_validation_request_minimal()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ VALIDATION SERVICE IS WORKING!")
        print("The timeout issue has been resolved.")
    else:
        print("❌ VALIDATION SERVICE STILL HAS ISSUES")
        print("Further investigation needed.")
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Check validation service terminal for error logs")
    print("2. Restart validation service if needed")
    print("3. Verify Ollama models are properly loaded")
    print("4. Check system resources (CPU/Memory)")

if __name__ == "__main__":
    main()
