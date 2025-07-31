#!/usr/bin/env python3
"""
Test script for Banking Templates API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Ollama Status: {data.get('components', {}).get('ollama_llm')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_templates():
    """Test templates endpoint"""
    print("\n🔍 Testing templates endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/templates")
        if response.status_code == 200:
            data = response.json()
            templates = data.get("templates", [])
            print(f"✅ Templates endpoint passed - {len(templates)} templates found")
            for template in templates:
                print(f"   - {template['name']} ({template['category']})")
            return True
        else:
            print(f"❌ Templates endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Templates endpoint error: {e}")
        return False

def test_transaction_categorization():
    """Test transaction categorization template"""
    print("\n🔍 Testing transaction categorization...")
    
    test_data = {
        "context": "core_banking",
        "data_type": "transaction_history",
        "input_data": {
            "transaction_data": json.dumps({
                "transactions": [
                    {"id": "TXN001", "amount": 5000, "description": "Client payment", "date": "2024-01-15"},
                    {"id": "TXN002", "amount": -1200, "description": "Office rent", "date": "2024-01-20"},
                    {"id": "TXN003", "amount": -500, "description": "Credit card payment", "date": "2024-01-25"}
                ]
            })
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=test_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Transaction categorization passed")
            print(f"   Template used: {data.get('template_used')}")
            print(f"   Tokens used: {data.get('tokens_used')}")
            print(f"   Processing time: {data.get('processing_time', 0):.2f}s")
            print(f"   Prompt length: {len(data.get('prompt', ''))} chars")
            print(f"   Response length: {len(data.get('response', ''))} chars")
            return True
        else:
            print(f"❌ Transaction categorization failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Transaction categorization error: {e}")
        return False

def test_cash_flow_analysis():
    """Test cash flow analysis template"""
    print("\n🔍 Testing cash flow analysis...")
    
    test_data = {
        "context": "lending_decision",
        "data_type": "time_series_data",
        "input_data": {
            "time_series_data": json.dumps({
                "monthly_cash_flows": [
                    {"month": "2024-01", "cash_flow": 15000},
                    {"month": "2024-02", "cash_flow": 12000},
                    {"month": "2024-03", "cash_flow": 18000},
                    {"month": "2024-04", "cash_flow": 14000}
                ]
            }),
            "time_window": "120d"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=test_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Cash flow analysis passed")
            print(f"   Template used: {data.get('template_used')}")
            print(f"   Tokens used: {data.get('tokens_used')}")
            print(f"   Processing time: {data.get('processing_time', 0):.2f}s")
            print(f"   Prompt length: {len(data.get('prompt', ''))} chars")
            print(f"   Response length: {len(data.get('response', ''))} chars")
            return True
        else:
            print(f"❌ Cash flow analysis failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Cash flow analysis error: {e}")
        return False

def test_credit_assessment():
    """Test credit assessment template"""
    print("\n🔍 Testing credit assessment...")
    
    test_data = {
        "context": "loan_approval",
        "data_type": "transaction_analysis",
        "input_data": {
            "transaction_analysis": json.dumps({
                "total_revenue": 500000,
                "total_expenses": 350000,
                "net_profit": 150000,
                "debt_obligations": 50000
            }),
            "liability_data": json.dumps({
                "existing_loans": 200000,
                "credit_cards": 15000
            }),
            "industry_data": json.dumps({
                "industry": "technology",
                "average_dscr": 1.8
            })
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=test_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Credit assessment passed")
            print(f"   Template used: {data.get('template_used')}")
            print(f"   Tokens used: {data.get('tokens_used')}")
            print(f"   Processing time: {data.get('processing_time', 0):.2f}s")
            print(f"   Prompt length: {len(data.get('prompt', ''))} chars")
            print(f"   Response length: {len(data.get('response', ''))} chars")
            return True
        else:
            print(f"❌ Credit assessment failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Credit assessment error: {e}")
        return False

def test_feedback():
    """Test feedback endpoint"""
    print("\n🔍 Testing feedback endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/feedback")
        if response.status_code == 200:
            data = response.json()
            print("✅ Feedback endpoint passed")
            print(f"   Interaction count: {data.get('interaction_count')}")
            print(f"   Suggestions count: {len(data.get('suggestions', []))}")
            print("   Sample suggestions:")
            for i, suggestion in enumerate(data.get('suggestions', [])[:3], 1):
                print(f"     {i}. {suggestion}")
            return True
        else:
            print(f"❌ Feedback endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Feedback endpoint error: {e}")
        return False

def test_statistics():
    """Test statistics endpoint"""
    print("\n🔍 Testing statistics endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ Statistics endpoint passed")
            print(f"   Available contexts: {len(data.get('available_contexts', []))}")
            print(f"   Available data types: {len(data.get('available_data_types', []))}")
            print(f"   Total interactions: {data.get('usage_statistics', {}).get('total_interactions', 0)}")
            print(f"   Unique templates: {data.get('usage_statistics', {}).get('unique_templates', 0)}")
            return True
        else:
            print(f"❌ Statistics endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Statistics endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Banking Templates API Tests")
    print("=" * 60)
    
    tests = [
        test_health,
        test_templates,
        test_transaction_categorization,
        test_cash_flow_analysis,
        test_credit_assessment,
        test_feedback,
        test_statistics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"✅ {passed}/{total} tests passed!")
    
    if passed == total:
        print("🎉 All tests completed successfully!")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main() 