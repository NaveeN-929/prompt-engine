#!/usr/bin/env python3
"""
Quick verification of the fixes applied
"""

import requests
import json

def test_services():
    """Test all services quickly"""
    print("🔍 VERIFYING SYSTEM FIXES")
    print("=" * 40)
    
    # Test 1: Validation Service
    print("\n1. Testing Validation Service...")
    try:
        response = requests.get("http://localhost:5002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Validation Service: Connected")
        else:
            print(f"❌ Validation Service: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Validation Service: {e}")
    
    # Test 2: Prompt Engine
    print("\n2. Testing Prompt Engine...")
    try:
        response = requests.get("http://localhost:5000/system/status", timeout=5)
        if response.status_code == 200:
            print("✅ Prompt Engine: Connected (using /system/status)")
        else:
            print(f"❌ Prompt Engine: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Prompt Engine: {e}")
    
    # Test 3: Autonomous Agent
    print("\n3. Testing Autonomous Agent...")
    try:
        response = requests.get("http://localhost:5001/agent/status", timeout=5)
        if response.status_code == 200:
            print("✅ Autonomous Agent: Connected")
        else:
            print(f"❌ Autonomous Agent: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Autonomous Agent: {e}")
    
    # Test 4: Quick Validation Test
    print("\n4. Testing Validation Integration...")
    try:
        validation_data = {
            "response_data": {
                "analysis": "=== SECTION 1: INSIGHTS ===\nGood analysis.\n=== SECTION 2: RECOMMENDATIONS ===\nGood recommendations."
            },
            "input_data": {
                "transactions": [{"date": "2024-01-15", "amount": 1500.00, "type": "credit"}]
            }
        }
        
        response = requests.post(
            "http://localhost:5002/validate/response",
            json=validation_data,
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            score = result.get('overall_score', 0)
            print(f"✅ Validation Test: Working (Score: {score:.2%})")
        else:
            print(f"❌ Validation Test: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Validation Test: {e}")
    
    print("\n" + "=" * 40)
    print("✅ Fix Verification Complete")

if __name__ == "__main__":
    test_services()
