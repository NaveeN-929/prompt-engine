#!/usr/bin/env python3
"""
Test validation with no timeout settings
"""

import requests
import json
import time

def test_validation_no_timeout():
    """Test validation with no timeout constraints"""
    print("🧪 Testing Validation with No Timeout")
    print("=" * 40)
    
    # Simple test data
    test_data = {
        "response_data": {
            "analysis": "Simple financial analysis for testing.",
            "status": "success"
        },
        "input_data": {
            "transactions": [{"amount": -25.00, "description": "test"}],
            "account_balance": 500.00
        },
        "validation_config": {
            "fast_mode": True,
            "criteria": {
                "content_accuracy": {"weight": 1.0, "threshold": 0.5}
            }
        }
    }
    
    print("📡 Sending validation request (no timeout)...")
    print("⏰ This may take a while - please wait...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:5002/validate/response",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=None  # No client-side timeout
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n⏱️ Request completed in {elapsed:.3f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Validation completed!")
            print(f"📊 Status: {result.get('status', 'unknown')}")
            print(f"💯 Overall Score: {result.get('overall_score', 0):.3f}")
            print(f"🏆 Quality Level: {result.get('quality_level', 'unknown')}")
            
            if 'criteria_scores' in result:
                print("📋 Criteria Scores:")
                for criterion, score in result['criteria_scores'].items():
                    print(f"   - {criterion}: {score:.3f}")
            
            print(f"\n🎉 Validation is working! Response time: {elapsed:.1f}s")
            return True
            
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"📄 Response: {response.text[:300]}...")
            return False
            
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n⏹️ Test interrupted after {elapsed:.1f}s")
        return False
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ ERROR after {elapsed:.1f}s: {e}")
        return False

def main():
    """Run the no-timeout test"""
    print("🔧 VALIDATION NO-TIMEOUT TEST")
    print("=" * 50)
    print("This test removes all timeout constraints to see if")
    print("validation can complete given unlimited time.")
    print("\nNOTE: You may need to restart the validation service")
    print("for the timeout changes to take effect.")
    print("\nPress Ctrl+C to cancel if it takes too long.")
    print("=" * 50)
    
    success = test_validation_no_timeout()
    
    if success:
        print("\n✅ VALIDATION IS WORKING!")
        print("The issue was timeout-related. You can now:")
        print("1. Adjust timeouts to a reasonable value (e.g., 30-60s)")
        print("2. Optimize the validation process further")
        print("3. Test with the UI to see validation scores")
    else:
        print("\n❌ VALIDATION STILL FAILING")
        print("The issue is not just timeout-related.")
        print("Check validation service logs for other errors.")

if __name__ == "__main__":
    main()
