#!/usr/bin/env python3
"""
Test the new /test/generic-insights endpoint
"""

import requests
import json

def test_generic_insights_endpoint():
    """Test the generic insights endpoint"""
    
    test_data = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": -5255, "type": "debit", "description": "Team Lunch"},
                {"date": "2024-01-01", "amount": 3123, "type": "credit", "description": "Invoice Payment - Web Development"},
                {"date": "2024-01-01", "amount": -53, "type": "debit", "description": "Google Ads"},
                {"date": "2024-01-01", "amount": 6471, "type": "credit", "description": "Invoice Payment - Consulting"},
                {"date": "2024-01-01", "amount": 6187, "type": "credit", "description": "Invoice Payment - Subscription"}
            ],
            "account_balance": 19863
        }
    }
    
    print("🧪 Testing /test/generic-insights endpoint")
    print("=" * 60)
    
    try:
        response = requests.post(
            "http://localhost:5001/test/generic-insights", 
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test endpoint responded successfully!")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print("\n📋 Analysis Result:")
                print("-" * 50)
                print(analysis)
                print("-" * 50)
                
                # Check if insights are generic (no specific dollar amounts)
                if "$" in analysis and "," in analysis and any(char.isdigit() for char in analysis):
                    # Look for patterns like $1,234.56
                    import re
                    dollar_amounts = re.findall(r'\$[\d,]+\.?\d*', analysis)
                    if dollar_amounts:
                        print(f"\n❌ Analysis still contains specific dollar amounts: {dollar_amounts}")
                        print("🔍 The insights should be generic observations without specific amounts")
                        return False
                
                print("\n✅ Analysis appears to use generic insights!")
                print("🎯 No specific dollar amounts found - using broad observations")
                return True
            else:
                print("❌ No analysis field in response")
                return False
        else:
            print(f"❌ Test endpoint error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server on localhost:5001")
        print("Make sure the autonomous agent server is running")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Generic Insights Endpoint")
    print("=" * 60)
    
    success = test_generic_insights_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 SUCCESS: Generic insights are working correctly!")
        print("The server is now generating generic observations instead of specific amounts.")
        print("This should fix the issue you saw in the /simple web interface.")
    else:
        print("❌ FAILED: Generic insights still need work.")
        print("The server may still be generating specific amounts instead of generic observations.")
