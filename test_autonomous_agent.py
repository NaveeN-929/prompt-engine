#!/usr/bin/env python3
"""
Test script for the autonomous agent server on port 5001
"""

import requests
import json

def test_analyze_endpoint():
    """Test the /analyze endpoint with sample transaction data"""
    
    # Sample transaction data
    test_data = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": -5255, "type": "debit", "description": "Team Lunch"},
                {"date": "2024-01-01", "amount": 3123, "type": "credit", "description": "Invoice #30000 - Invoice Payment - Web Development"},
                {"date": "2024-01-01", "amount": -53, "type": "debit", "description": "Google Ads"},
                {"date": "2024-01-01", "amount": 6471, "type": "credit", "description": "Invoice #30001 - Invoice Payment - Consulting"},
                {"date": "2024-01-01", "amount": 6187, "type": "credit", "description": "Invoice #30002 - Invoice Payment - Subscription"},
                {"date": "2024-01-02", "amount": -2957, "type": "debit", "description": "Pantry Snacks"},
                {"date": "2024-01-02", "amount": -1404, "type": "debit", "description": "Warehouse Rent"},
                {"date": "2024-01-02", "amount": -3104, "type": "debit", "description": "Warehouse Rent"},
                {"date": "2024-01-02", "amount": -124, "type": "debit", "description": "Domain Renewals"},
                {"date": "2024-01-02", "amount": -4395, "type": "debit", "description": "SaaS - Email Marketing"}
            ],
            "account_balance": 19863
        }
    }
    
    print("🧪 Testing Autonomous Agent /analyze endpoint")
    print("=" * 60)
    
    try:
        response = requests.post(
            "http://localhost:5001/analyze", 
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Server responded successfully!")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print("\n📋 Analysis Result:")
                print("-" * 40)
                print(analysis)
                print("-" * 40)
                
                # Check if insights are generic (no specific dollar amounts)
                if "$" in analysis and any(char.isdigit() for char in analysis):
                    print("\n❌ Analysis still contains specific dollar amounts!")
                    print("🔍 Found specific amounts - needs to be more generic")
                    return False
                else:
                    print("\n✅ Analysis appears to use generic insights!")
                    return True
            else:
                print("❌ No analysis field in response")
                print(f"Response keys: {list(result.keys())}")
                return False
        else:
            print(f"❌ Server error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server on localhost:5001")
        print("Make sure the autonomous agent server is running")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_simple_endpoint():
    """Test if /simple endpoint exists"""
    
    print("\n🧪 Testing /simple endpoint")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5001/simple", timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ /simple endpoint is available!")
            return True
        else:
            print(f"❌ /simple endpoint returned: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server on localhost:5001")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Autonomous Agent Server (Port 5001)")
    print("=" * 60)
    
    # Test analyze endpoint
    analyze_success = test_analyze_endpoint()
    
    # Test simple endpoint  
    simple_success = test_simple_endpoint()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   /analyze endpoint: {'✅ PASS' if analyze_success else '❌ FAIL'}")
    print(f"   /simple endpoint:  {'✅ PASS' if simple_success else '❌ FAIL'}")
    
    if analyze_success:
        print("\n🎯 Generic insights are working correctly!")
        print("The server should now show generic observations instead of specific amounts.")
    else:
        print("\n🔧 Server may need additional configuration or restart.")
