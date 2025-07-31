#!/usr/bin/env python3
"""
Very simple test with minimal data
"""

import requests
import json

def test_minimal():
    """Test with minimal transaction data"""
    url = "http://localhost:8000/generate"
    
    payload = {
        "context": "core_banking",
        "data_type": "transaction_history", 
        "input_data": {
            "transaction_data": json.dumps({
                "transactions": [
                    {
                        "id": "T1",
                        "amount": 100,
                        "description": "Test payment"
                    }
                ]
            })
        }
    }
    
    print("🔍 Testing minimal transaction data...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        print("   (No timeout - waiting for model to complete...)")
        response = requests.post(url, json=payload)  # No timeout
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Template: {data.get('template_used')}")
            print(f"Tokens: {data.get('tokens_used')}")
            print(f"Time: {data.get('processing_time'):.2f}s")
            print(f"Response: {data.get('response', '')[:100]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_minimal() 