#!/usr/bin/env python3
"""
Test validation service directly
"""

import requests
import json

def test_validation_service_direct():
    """Test the validation service directly with correct format"""
    
    print("🔍 Testing Validation Service Directly")
    print("=" * 40)
    
    # Test data in the correct format
    test_data = {
        "response_data": {
            "analysis": "This is a comprehensive financial analysis. The customer shows good spending patterns with regular transactions. Recommendations include setting up automatic savings and monitoring monthly expenses.",
            "status": "success",
            "processing_time": 1.5
        },
        "input_data": {
            "transactions": [
                {
                    "amount": -50.00,
                    "description": "Coffee Shop",
                    "category": "dining"
                }
            ],
            "account_balance": 1000.00
        }
    }
    
    print("1. Testing validation service health...")
    try:
        response = requests.get("http://localhost:5002/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Health: {health.get('status', 'unknown')}")
            print(f"   🔧 Engine initialized: {health.get('validation_engine_initialized', False)}")
        else:
            print(f"   ❌ Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    print("\n2. Testing direct validation request...")
    try:
        response = requests.post(
            "http://localhost:5002/validate/response",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        print(f"   📡 Response status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Validation successful!")
            print(f"   📊 Status: {result.get('status', 'unknown')}")
            print(f"   💯 Overall score: {result.get('overall_score', 0):.2f}")
            print(f"   🏆 Quality level: {result.get('quality_level', 'unknown')}")
            
            if 'criteria_scores' in result:
                print(f"   📋 Criteria scores:")
                for criterion, score in result['criteria_scores'].items():
                    print(f"      - {criterion}: {score:.2f}")
            
            return True
        else:
            print(f"   ❌ Validation failed: HTTP {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Validation request error: {e}")
        return False

if __name__ == "__main__":
    success = test_validation_service_direct()
    if success:
        print("\n✅ Validation service is working correctly!")
    else:
        print("\n❌ Validation service has issues!")
