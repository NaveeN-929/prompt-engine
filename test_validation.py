#!/usr/bin/env python3
"""
Test script to verify validation functionality
"""

import requests
import json
import time

def test_validation_integration():
    """Test that validation is working in the pipeline endpoints"""
    
    print("🧪 Testing Validation Integration")
    print("=" * 40)
    
    # Test data
    test_data = {
        "input_data": {
            "transactions": [
                {
                    "amount": -50.00,
                    "description": "Coffee Shop Purchase",
                    "category": "dining",
                    "date": "2024-01-15"
                },
                {
                    "amount": -120.00,
                    "description": "Grocery Store",
                    "category": "groceries", 
                    "date": "2024-01-14"
                }
            ],
            "account_balance": 1500.00,
            "customer_id": "TEST_001"
        }
    }
    
    # Test validation service status first
    print("1. Checking validation service status...")
    try:
        response = requests.get("http://localhost:5001/validation/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Validation service status: {status.get('status', 'unknown')}")
            print(f"   🔗 Service connected: {status.get('service_connected', False)}")
            print(f"   📊 Total validations: {status.get('integration_stats', {}).get('validation_stats', {}).get('total_validations', 0)}")
        else:
            print(f"   ❌ Failed to get validation status: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking validation status: {e}")
        return False
    
    # Test agentic pipeline with validation
    print("\n2. Testing Agentic Pipeline with validation...")
    try:
        response = requests.post(
            "http://localhost:5001/pipeline/agentic",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Pipeline request successful")
            print(f"   ⏱️ Processing time: {result.get('processing_time', 0):.3f}s")
            
            # Check if validation data is present
            validation = result.get('validation')
            if validation:
                print(f"   🔒 Validation present: YES")
                print(f"   📊 Quality level: {validation.get('quality_level', 'unknown')}")
                print(f"   💯 Quality score: {validation.get('quality_score', 0):.2f}")
                print(f"   ✅ Quality approved: {validation.get('quality_approved', False)}")
                print(f"   📋 Validation status: {validation.get('validation_status', 'unknown')}")
            else:
                print(f"   🔒 Validation present: NO")
                
        else:
            print(f"   ❌ Pipeline request failed: HTTP {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing agentic pipeline: {e}")
        return False
    
    # Check validation stats after the request
    print("\n3. Checking validation stats after request...")
    try:
        response = requests.get("http://localhost:5001/validation/status")
        if response.status_code == 200:
            status = response.json()
            stats = status.get('integration_stats', {}).get('validation_stats', {})
            print(f"   📊 Total validations: {stats.get('total_validations', 0)}")
            print(f"   ✅ Passed validations: {stats.get('passed_validations', 0)}")
            print(f"   ❌ Failed validations: {stats.get('failed_validations', 0)}")
            print(f"   ⚠️ Validation errors: {stats.get('validation_errors', 0)}")
            print(f"   ⏱️ Average validation time: {stats.get('average_validation_time', 0):.3f}s")
            
            if stats.get('total_validations', 0) > 0:
                print("\n   🎉 SUCCESS: Validations are being performed!")
                return True
            else:
                print("\n   ⚠️ WARNING: No validations performed yet")
                return False
        else:
            print(f"   ❌ Failed to get updated validation status: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking updated validation status: {e}")
        return False

def main():
    """Main test execution"""
    print("🔒 Validation Integration Test")
    print("=" * 50)
    
    success = test_validation_integration()
    
    if success:
        print("\n✅ All tests passed! Validation is working correctly.")
        return 0
    else:
        print("\n❌ Tests failed! Validation needs to be fixed.")
        return 1

if __name__ == "__main__":
    exit(main())
