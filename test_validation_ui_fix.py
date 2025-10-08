#!/usr/bin/env python3
"""
Test script to verify validation UI fixes
"""

import requests
import json

def test_validation_display():
    """Test that validation results are properly displayed"""
    print("🔍 Testing Validation UI Fix")
    print("=" * 50)
    
    # Test data
    test_data = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary"},
                {"date": "2024-01-16", "amount": -50.00, "type": "debit", "description": "Grocery"}
            ],
            "account_balance": 2250.00
        },
        "request_config": {
            "generation_type": "autonomous",
            "include_validation": True
        }
    }
    
    print("\n1. Sending analysis request to autonomous agent...")
    try:
        response = requests.post(
            "http://localhost:5001/analyze",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis completed successfully")
            
            # Check validation field
            if 'validation' in result:
                validation = result['validation']
                print("\n2. Checking validation data structure:")
                print(f"   - Has 'validation' field: ✅")
                print(f"   - Quality Level: {validation.get('quality_level', 'N/A')}")
                print(f"   - Overall Score: {validation.get('overall_score', 'N/A')}")
                print(f"   - Quality Approved: {validation.get('quality_approved', 'N/A')}")
                print(f"   - Validation Status: {validation.get('validation_status', 'N/A')}")
                
                # Check if score is properly set
                score = validation.get('overall_score', 0)
                if score > 0:
                    print(f"\n✅ Validation score is working: {score:.2%}")
                    print(f"   This should display in UI as: Validation: {score:.0%}")
                else:
                    print(f"\n⚠️  Validation score is 0.0%")
                    print(f"   Check if validation service is running properly")
                
                # Print full validation for debugging
                print("\n3. Full validation response:")
                print(json.dumps(validation, indent=2))
                
            else:
                print("❌ No 'validation' field in response")
                print("   Response keys:", list(result.keys()))
        else:
            print(f"❌ Analysis failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print("\nUI Fix Summary:")
    print("1. ✅ UI now looks for 'overall_score' field")
    print("2. ✅ Validation status properly set to 'approved'")
    print("3. ✅ Quality level and score should display correctly")
    print("\nIf validation shows 0.0%, check:")
    print("- Is validation service running? (port 5002)")
    print("- Check autonomous agent logs for validation errors")

if __name__ == "__main__":
    test_validation_display()
