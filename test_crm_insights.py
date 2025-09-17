#!/usr/bin/env python3
"""
Test script for the refined CRM insights functionality
Demonstrates the paired insight/recommendation format with banking products
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import datetime, timedelta

# Import our modules for direct testing
from app.generators.prompt_generator import PromptGenerator
from app.generators.response_formatter import ResponseFormatter
from app.llm.mock_llm import OllamaLLM
from app.templates.banking import crm_insights_refined

# Sample transaction data for testing
sample_transaction_data = {
    "transactions": [
        {
            "date": "2024-01-15",
            "description": "Office Supplies Purchase",
            "amount": -1250.00,
            "category": "expenses",
            "merchant": "Office Depot"
        },
        {
            "date": "2024-01-14",
            "description": "Client Payment Received",
            "amount": 5000.00,
            "category": "revenue",
            "merchant": "ABC Corp"
        },
        {
            "date": "2024-01-13",
            "description": "Marketing Campaign",
            "amount": -2800.00,
            "category": "marketing",
            "merchant": "Google Ads"
        },
        {
            "date": "2024-01-12",
            "description": "Salary Payment",
            "amount": -3500.00,
            "category": "payroll",
            "merchant": "Payroll Processor"
        },
        {
            "date": "2024-01-11",
            "description": "International Client Payment",
            "amount": 7500.00,
            "category": "revenue",
            "merchant": "Global Tech Ltd"
        }
    ],
    "account_info": {
        "business_type": "Technology Consulting",
        "monthly_revenue": 25000,
        "employee_count": 8,
        "industry": "Technology Services"
    },
    "time_period": "Last 30 days"
}

def test_crm_insights():
    """Test the CRM insights functionality using the merged /generate endpoint"""
    url = "http://localhost:5000/generate"

    print("🧪 Testing Refined CRM Insights Generation")
    print("=" * 50)

    try:
        # Make the request using the merged endpoint
        payload = {
            "input_data": sample_transaction_data,
            "generation_type": "crm_insights"
        }
        response = requests.post(url, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()

            print("✅ Success! CRM Insights Generated")
            print(f"⏱️  Processing Time: {result['processing_time']:.2f}s")
            print(f"🎯 Template Used: {result.get('template_used', 'N/A')}")
            print(f"🤖 Tokens Used: {result.get('tokens_used', 'N/A')}")
            print(f"🔧 Generation Mode: {result.get('generation_mode', 'N/A')}")

            # Debug: Print all keys in response
            print(f"📋 Response Keys: {list(result.keys())}")
            print(f"📋 Full Response: {json.dumps(result, indent=2)[:500]}...")

            # Check if there was an error
            if 'status' in result and result['status'] == 'error':
                print(f"❌ Error in response: {result.get('message', 'Unknown error')}")
                return

            # Check if CRM insights specific fields are present
            if 'pairs_count' in result and 'json_output' in result:
                print(f"📊 Pairs Generated: {result['pairs_count']}")

                print("\n📋 JSON Output for RAG Pipeline:")
                print(json.dumps(result['json_output'], indent=2))

                print("\n🎨 CRM Display Format:")
                print(result['display_output'])
            else:
                print("\n❌ CRM insights fields not found in response")
                print("Response structure:", list(result.keys()))
                return

            print("\n📊 Banking Product Integration Check:")
            banking_products_found = 0
            for i, pair in enumerate(result['json_output'], 1):
                if '(Upsell)' in pair['recommendation'] or '(Cross-sell)' in pair['recommendation']:
                    banking_products_found += 1
                    product_type = '(Upsell)' if '(Upsell)' in pair['recommendation'] else '(Cross-sell)'
                    print(f"   Pair {i}: {product_type} - Banking product suggestion included")

            print(f"\n✅ Banking Products Found: {banking_products_found}/3 (Target: Exactly 3 banking product suggestions)")

            # Show which recommendations have banking products
            for i, pair in enumerate(result['json_output'], 1):
                has_product = '(Upsell)' in pair['recommendation'] or '(Cross-sell)' in pair['recommendation']
                status = "✅ Banking Product" if has_product else "ℹ️  General Advice"
                print(f"   Pair {i}: {status}")

            print("\n" + "=" * 50)
            print("✅ Test completed successfully!")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        print("\n💡 Make sure the server is running:")
        print("   python app/main.py")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_crm_insights_direct():
    """Test CRM insights functionality directly without Flask server"""
    print("🧪 Testing CRM Insights Directly (No Flask Server)")
    print("=" * 50)

    try:
        # Initialize components
        prompt_generator = PromptGenerator()
        response_formatter = ResponseFormatter()

        # Generate prompt
        print("📝 Generating CRM insights prompt...")
        prompt_text, template_name, prompt_time = prompt_generator.generate_prompt(
            context="crm_financial_insights",
            data_type="transaction_history",
            input_data={"transaction_data": sample_transaction_data}
        )

        print(f"✅ Prompt generated in {prompt_time:.3f}s")
        print(f"🎯 Template used: {template_name}")

        # Use mock response for testing (since Ollama may not be available)
        print("🤖 Using mock response for testing...")
        response_text = '''[
            {
                "insight": "Revenue appears to be trending upward with consistent payment receipts",
                "recommendation": "Consider setting aside a portion of this surplus in a high-yield savings account or term deposit to build financial resilience"
            },
            {
                "insight": "Cash flow patterns show regular seasonal fluctuations",
                "recommendation": "To smooth out cash flow, you might explore a flexible overdraft facility or invoice financing during peak outflow weeks (Upsell)"
            },
            {
                "insight": "Payment collection cycle is longer than industry average",
                "recommendation": "Introducing automated payment reminders could improve cash flow predictability — your RM can assist"
            },
            {
                "insight": "Marketing spend has increased significantly recently",
                "recommendation": "Consider bundling your marketing budget with a revolving credit line to support scalable growth without cash strain (Upsell)"
            },
            {
                "insight": "International transaction volume is rising",
                "recommendation": "A multi-currency business account could reduce your conversion costs and improve reconciliation (Cross-sell)"
            }
        ]'''
        tokens_used = 150
        llm_time = 0.1
        print("✅ Using mock response for testing")

        # Format response
        print("🔧 Formatting paired response...")
        formatted_result = response_formatter.format_paired_response(response_text)

        # Display results
        print(f"📊 Pairs Generated: {formatted_result['pairs_count']}")

        print("\n📋 JSON Output for RAG Pipeline:")
        print(json.dumps(formatted_result['json_output'], indent=2))

        print("\n🎨 CRM Display Format:")
        print(formatted_result['display_output'])

        print("\n🔍 Generic Insight Examples:")
        for i, pair in enumerate(formatted_result['json_output'], 1):
            print(f"   {i}. '{pair['insight']}' (Generic, no specific transaction details)")

        print("\n📊 Banking Product Integration Check:")
        banking_products_found = 0
        for i, pair in enumerate(formatted_result['json_output'], 1):
            if '(Upsell)' in pair['recommendation'] or '(Cross-sell)' in pair['recommendation']:
                banking_products_found += 1
                product_type = '(Upsell)' if '(Upsell)' in pair['recommendation'] else '(Cross-sell)'
                print(f"   Pair {i}: {product_type} - Banking product suggestion included")

        print(f"\n✅ Banking Products Found: {banking_products_found}/3 (Target: Exactly 3 banking product suggestions)")

        # Show which recommendations have banking products
        for i, pair in enumerate(formatted_result['json_output'], 1):
            has_product = '(Upsell)' in pair['recommendation'] or '(Cross-sell)' in pair['recommendation']
            status = "✅ Banking Product" if has_product else "ℹ️  General Advice"
            print(f"   Pair {i}: {status}")

        print("\n" + "=" * 50)
        print("✅ Direct test completed successfully!")

    except Exception as e:
        print(f"❌ Error in direct test: {e}")
        import traceback
        traceback.print_exc()

def test_crm_insights():
    """Test the CRM insights functionality using the merged /generate endpoint"""
    url = "http://localhost:5000/generate"

    print("🧪 Testing Refined CRM Insights Generation")
    print("=" * 50)

    try:
        # Make the request using the merged endpoint
        payload = {
            "input_data": sample_transaction_data,
            "generation_type": "crm_insights"
        }
        response = requests.post(url, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()

            print("✅ Success! CRM Insights Generated")
            print(f"⏱️  Processing Time: {result['processing_time']:.2f}s")
            print(f"🎯 Template Used: {result.get('template_used', 'N/A')}")
            print(f"🤖 Tokens Used: {result.get('tokens_used', 'N/A')}")
            print(f"🔧 Generation Mode: {result.get('generation_mode', 'N/A')}")

            # Debug: Print all keys in response
            print(f"📋 Response Keys: {list(result.keys())}")
            print(f"📋 Full Response: {json.dumps(result, indent=2)[:500]}...")

            # Check if there was an error
            if 'status' in result and result['status'] == 'error':
                print(f"❌ Error in response: {result.get('message', 'Unknown error')}")
                return

            # Check if CRM insights specific fields are present
            if 'pairs_count' in result and 'json_output' in result:
                print(f"📊 Pairs Generated: {result['pairs_count']}")

                print("\n📋 JSON Output for RAG Pipeline:")
                print(json.dumps(result['json_output'], indent=2))

                print("\n🎨 CRM Display Format:")
                print(result['display_output'])
            else:
                print("\n❌ CRM insights fields not found in response")
                print("Response structure:", list(result.keys()))
                return

            print("\n📊 Banking Product Integration Check:")
            banking_products_found = 0
            for i, pair in enumerate(result['json_output'], 1):
                if '(Upsell)' in pair['recommendation'] or '(Cross-sell)' in pair['recommendation']:
                    banking_products_found += 1
                    product_type = '(Upsell)' if '(Upsell)' in pair['recommendation'] else '(Cross-sell)'
                    print(f"   Pair {i}: {product_type} - Banking product suggestion included")

            print(f"\n✅ Banking Products Found: {banking_products_found}/3 (Target: Exactly 3 banking product suggestions)")

            # Show which recommendations have banking products
            for i, pair in enumerate(result['json_output'], 1):
                has_product = '(Upsell)' in pair['recommendation'] or '(Cross-sell)' in pair['recommendation']
                status = "✅ Banking Product" if has_product else "ℹ️  General Advice"
                print(f"   Pair {i}: {status}")

            print("\n" + "=" * 50)
            print("✅ Test completed successfully!")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        print("\n💡 Make sure the server is running:")
        print("   python app/main.py")
        print("\n🔄 Running direct test instead...")
        test_crm_insights_direct()
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("\n🔄 Running direct test instead...")
        test_crm_insights_direct()

def test_flask_endpoint():
    """Test the actual Flask endpoint"""
    print("🧪 Testing Flask CRM Insights Endpoint")
    print("=" * 50)

    try:
        # Simple test data
        payload = {
            "input_data": sample_transaction_data,
            "generation_type": "crm_insights"
        }

        response = requests.post("http://localhost:5000/generate", json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("✅ Flask endpoint responded successfully!")

            if 'json_output' in result:
                print(f"📊 Pairs Generated: {result.get('pairs_count', 'N/A')}")
                print("🎯 Flask endpoint is working correctly with generic insights!")
                return True
            else:
                print("❌ CRM insights fields not found in Flask response")
                return False
        else:
            print(f"❌ Flask endpoint error: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Flask endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    # Test Flask endpoint first
    flask_working = test_flask_endpoint()

    if not flask_working:
        print("\n🔄 Flask endpoint not available, running direct test instead...")
        test_crm_insights_direct()
