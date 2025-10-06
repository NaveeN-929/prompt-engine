#!/usr/bin/env python3
"""
Quick fix for validation timeout - patch the running service
"""

import requests
import json
import time

def test_ollama_keep_alive():
    """Test if we can keep models loaded in memory"""
    print("🔧 Testing Ollama Keep-Alive Configuration")
    print("-" * 40)
    
    # Test with keep_alive option to keep model in memory
    payload = {
        "model": "llama3.2:1b",
        "prompt": "Test response for validation.",
        "options": {
            "num_predict": 50,
            "temperature": 0.1
        },
        "keep_alive": "5m",  # Keep model loaded for 5 minutes
        "stream": False
    }
    
    print("   📡 Testing with keep_alive option...")
    
    # Make multiple requests to see if subsequent ones are faster
    for i in range(3):
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
                response_text = result.get("response", "")[:50]
                print(f"   Request {i+1}: {elapsed:.3f}s - '{response_text}...'")
                
                if i == 0 and elapsed > 8:
                    print(f"   ⚠️ First request slow ({elapsed:.3f}s) - model loading")
                elif i > 0 and elapsed < 3:
                    print(f"   ✅ Subsequent request fast ({elapsed:.3f}s) - model cached")
            else:
                print(f"   ❌ Request {i+1} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request {i+1} error: {e}")
        
        time.sleep(1)  # Small delay between requests

def create_optimized_validation_config():
    """Create an optimized validation configuration"""
    print("\n⚙️ Creating Optimized Validation Configuration")
    print("-" * 40)
    
    # Ultra-fast validation config
    fast_config = {
        "response_data": {
            "analysis": "Test financial analysis with basic insights and recommendations.",
            "status": "success"
        },
        "input_data": {
            "transactions": [{"amount": -50, "description": "test"}],
            "account_balance": 1000
        },
        "validation_config": {
            "fast_mode": True,
            "use_speed_model": True,  # Force use of 1B model
            "criteria": {
                "content_accuracy": {"weight": 1.0, "threshold": 0.5}
            },
            "llm_options": {
                "num_predict": 100,  # Very short responses
                "temperature": 0.1,
                "keep_alive": "10m"  # Keep model loaded
            }
        }
    }
    
    return fast_config

def test_optimized_validation():
    """Test validation with optimized configuration"""
    print("\n🚀 Testing Optimized Validation")
    print("-" * 40)
    
    config = create_optimized_validation_config()
    
    try:
        print("   📡 Sending optimized validation request...")
        start = time.time()
        
        response = requests.post(
            "http://localhost:5002/validate/response",
            headers={"Content-Type": "application/json"},
            json=config,
            timeout=45
        )
        
        elapsed = time.time() - start
        print(f"   ⏱️ Request completed in {elapsed:.3f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Validation successful!")
            print(f"   📊 Status: {result.get('status', 'unknown')}")
            print(f"   💯 Score: {result.get('overall_score', 0):.3f}")
            print(f"   🏆 Quality: {result.get('quality_level', 'unknown')}")
            return True
        else:
            print(f"   ❌ Validation failed: HTTP {response.status_code}")
            error_text = response.text[:300] if response.text else "No error details"
            print(f"   📄 Error: {error_text}...")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"   ❌ Request timed out after {elapsed:.3f}s")
        return False
    except Exception as e:
        elapsed = time.time() - start
        print(f"   ❌ Request error after {elapsed:.3f}s: {e}")
        return False

def suggest_immediate_fixes():
    """Suggest immediate fixes for the timeout issue"""
    print("\n💡 IMMEDIATE FIX RECOMMENDATIONS")
    print("=" * 40)
    
    print("🔧 OPTION 1: Restart Validation Service (Recommended)")
    print("   1. Stop the validation service (Ctrl+C)")
    print("   2. Restart with: python validation_server.py")
    print("   3. The async fixes will be applied")
    
    print("\n⚡ OPTION 2: Use Faster Model Only")
    print("   - Edit validation-llm/config.py")
    print("   - Change primary_validator model to 'llama3.2:1b'")
    print("   - Reduce timeout to 10 seconds")
    
    print("\n🚀 OPTION 3: Pre-warm Models")
    print("   - Run: ollama run llama3.2:1b")
    print("   - Run: ollama run llama3.2:3b")
    print("   - This keeps models loaded in memory")
    
    print("\n📊 EXPECTED RESULTS AFTER FIX:")
    print("   ✅ Validation completes in 3-8 seconds")
    print("   ✅ No more timeout errors")
    print("   ✅ UI shows validation scores")
    print("   ✅ Statistics show successful validations")

def main():
    """Run quick timeout fix diagnostics"""
    print("🔧 VALIDATION TIMEOUT QUICK FIX")
    print("=" * 50)
    
    # Test Ollama optimization
    test_ollama_keep_alive()
    
    # Test optimized validation
    success = test_optimized_validation()
    
    # Provide recommendations
    suggest_immediate_fixes()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 VALIDATION IS WORKING WITH CURRENT CODE!")
        print("The timeout might be intermittent or resolved.")
    else:
        print("🔧 VALIDATION SERVICE NEEDS RESTART")
        print("Apply the fixes by restarting the service.")

if __name__ == "__main__":
    main()
