#!/usr/bin/env python3
"""
Test script for the pipeline endpoints on the autonomous agent server
"""

import requests
import json

def test_pipeline_full():
    """Test the /pipeline/full endpoint"""
    
    test_data = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": -5255, "type": "debit", "description": "Team Lunch"},
                {"date": "2024-01-01", "amount": 3123, "type": "credit", "description": "Invoice #30000 - Invoice Payment - Web Development"},
                {"date": "2024-01-01", "amount": -53, "type": "debit", "description": "Google Ads"},
                {"date": "2024-01-01", "amount": 6471, "type": "credit", "description": "Invoice #30001 - Invoice Payment - Consulting"},
                {"date": "2024-01-01", "amount": 6187, "type": "credit", "description": "Invoice #30002 - Invoice Payment - Subscription"}
            ],
            "account_balance": 19863
        }
    }
    
    print("🧪 Testing /pipeline/full endpoint")
    print("=" * 50)
    
    try:
        response = requests.post(
            "http://localhost:5001/pipeline/full", 
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Pipeline responded successfully!")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print("\n📋 Analysis Result:")
                print("-" * 40)
                print(analysis)
                print("-" * 40)
                
                # Check if insights are generic (no specific dollar amounts)
                if "$" in analysis and any(char.isdigit() for char in analysis if analysis[analysis.index(char)-1:analysis.index(char)+2].count('$') > 0):
                    print("\n❌ Analysis still contains specific dollar amounts!")
                    print("🔍 Found specific amounts - needs to be more generic")
                    return False
                else:
                    print("\n✅ Analysis appears to use generic insights!")
                    return True
            else:
                print("❌ No analysis field in response")
                return False
        else:
            print(f"❌ Pipeline error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_pipeline_agentic():
    """Test the /pipeline/agentic endpoint"""
    
    test_data = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": -5255, "type": "debit", "description": "Team Lunch"},
                {"date": "2024-01-01", "amount": 3123, "type": "credit", "description": "Invoice Payment - Web Development"},
                {"date": "2024-01-01", "amount": -53, "type": "debit", "description": "Google Ads"}
            ],
            "account_balance": 19863
        }
    }
    
    print("\n🧪 Testing /pipeline/agentic endpoint")
    print("=" * 50)
    
    try:
        response = requests.post(
            "http://localhost:5001/pipeline/agentic", 
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Agentic pipeline responded successfully!")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print("\n📋 Analysis Result:")
                print("-" * 40)
                print(analysis)
                print("-" * 40)
                
                # Check if insights are generic
                if "$" in analysis and "," in analysis:
                    print("\n❌ Analysis still contains specific dollar amounts!")
                    return False
                else:
                    print("\n✅ Analysis appears to use generic insights!")
                    return True
            else:
                print("❌ No analysis field in response")
                return False
        else:
            print(f"❌ Agentic pipeline error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Pipeline Endpoints on Autonomous Agent Server")
    print("=" * 70)
    
    # Test both pipeline endpoints
    full_success = test_pipeline_full()
    agentic_success = test_pipeline_agentic()
    
    print("\n" + "=" * 70)
    print("📊 Test Summary:")
    print(f"   /pipeline/full:    {'✅ PASS' if full_success else '❌ FAIL'}")
    print(f"   /pipeline/agentic: {'✅ PASS' if agentic_success else '❌ FAIL'}")
    
    if full_success and agentic_success:
        print("\n🎯 Both pipelines are working with generic insights!")
        print("The /simple web interface should now show generic observations.")
    else:
        print("\n🔧 Some pipelines may need additional fixes or dependencies.")
