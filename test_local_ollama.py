#!/usr/bin/env python3
"""
Test script for local Ollama integration
"""

import requests
import json

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Ollama Status: {data['components']['ollama_llm']}")
            print(f"   Current Model: {data['ollama_config']['model']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_simple_transaction():
    """Test transaction categorization with simple data"""
    url = "http://localhost:8000/generate"
    
    payload = {
        "context": "core_banking",
        "data_type": "transaction_history",
        "input_data": {
            "transaction_data": json.dumps({
                "transactions": [
                    {
                        "id": "TXN001",
                        "date": "2024-01-15",
                        "amount": 5000.00,
                        "description": "Payment from ABC Corp",
                        "type": "credit"
                    },
                    {
                        "id": "TXN002", 
                        "date": "2024-01-16",
                        "amount": -1200.00,
                        "description": "Office Rent Payment",
                        "type": "debit"
                    }
                ]
            })
        }
    }
    
    try:
        print("\n🔍 Testing transaction categorization...")
        print("   (No timeout - waiting for model to complete...)")
        response = requests.post(url, json=payload)  # No timeout
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Transaction categorization successful!")
            print(f"   Template used: {data['template_used']}")
            print(f"   Tokens used: {data['tokens_used']}")
            print(f"   Processing time: {data['processing_time']:.2f}s")
            print(f"   Response length: {len(data['response'])} characters")
            print(f"   Response preview: {data['response'][:200]}...")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    print("🚀 Testing Local Ollama Integration")
    print("=" * 50)
    
    # Test health first
    if not test_health():
        print("\n❌ Health check failed. Make sure the server is running.")
        return
    
    # Test simple transaction
    test_simple_transaction()

if __name__ == "__main__":
    main() 