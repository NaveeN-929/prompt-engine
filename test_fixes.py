#!/usr/bin/env python3
"""
Quick test to verify the fixes for the system issues
"""

import requests
import time

def test_prompt_engine():
    """Test Prompt Engine with correct endpoint"""
    print("🔍 Testing Prompt Engine...")
    try:
        response = requests.get("http://localhost:5000/system/status", timeout=5)
        if response.status_code == 200:
            print("✅ Prompt Engine: Connected (using /system/status)")
            return True
        else:
            print(f"❌ Prompt Engine: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Prompt Engine: {e}")
        return False

def test_ollama_quick():
    """Test Ollama with shorter timeout"""
    print("🔍 Testing Ollama...")
    try:
        # Test connection
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama: Connected")
            
            # Test model with short timeout
            test_prompt = {
                "model": "mistral:latest",
                "prompt": "Hi",
                "options": {"temperature": 0.1, "num_predict": 5},
                "keep_alive": "1m",
                "stream": False
            }
            
            start_time = time.time()
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=test_prompt,
                timeout=10  # Short timeout
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Ollama Model: Working ({end_time - start_time:.2f}s)")
                return True
            else:
                print(f"❌ Ollama Model: HTTP {response.status_code}")
                return False
        else:
            print(f"❌ Ollama: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama: {e}")
        return False

def test_validation_speed():
    """Test Validation System with optimized settings"""
    print("🔍 Testing Validation System...")
    try:
        # Test health
        response = requests.get("http://localhost:5002/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Validation System: HTTP {response.status_code}")
            return False
        
        print("✅ Validation System: Connected")
        
        # Test validation with optimized settings
        validation_data = {
            "response_data": {
                "analysis": "=== SECTION 1: INSIGHTS ===\nGood analysis.\n=== SECTION 2: RECOMMENDATIONS ===\nGood recommendations."
            },
            "input_data": {
                "transactions": [{"date": "2024-01-15", "amount": 1500.00, "type": "credit"}]
            }
        }
        
        start_time = time.time()
        response = requests.post(
            "http://localhost:5002/validate/response",
            json=validation_data,
            timeout=25  # Optimized timeout
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            score = result.get('overall_score', 0)
            print(f"✅ Validation: Working ({end_time - start_time:.2f}s, Score: {score:.2%})")
            return True
        else:
            print(f"❌ Validation: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Validation System: {e}")
        return False

def main():
    print("🚀 TESTING SYSTEM FIXES")
    print("=" * 40)
    
    results = []
    results.append(test_prompt_engine())
    results.append(test_ollama_quick())
    results.append(test_validation_speed())
    
    print("\n" + "=" * 40)
    print("📊 RESULTS SUMMARY")
    
    if all(results):
        print("🎉 All fixes working! System is operational.")
    else:
        print("⚠️  Some issues remain. Check individual test results above.")
    
    print(f"✅ Passed: {sum(results)}/3 tests")

if __name__ == "__main__":
    main()
