#!/usr/bin/env python3
"""
Test script for the Prompting Engine Demo API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json()['status']}")
            print(f"   Version: {response.json()['version']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_templates():
    """Test the templates endpoint"""
    print("\n🔍 Testing templates endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/templates")
        if response.status_code == 200:
            templates = response.json()['templates']
            print(f"✅ Templates endpoint passed - {len(templates)} templates found")
            for template in templates:
                print(f"   - {template['name']} ({template['category']})")
        else:
            print(f"❌ Templates endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Templates endpoint error: {e}")

def test_generate_customer_service():
    """Test customer service prompt generation"""
    print("\n🔍 Testing customer service prompt generation...")
    
    test_data = {
        "context": "customer_service",
        "data_type": "complaint",
        "input_data": {
            "customer_name": "John Doe",
            "issue_description": "Product arrived damaged",
            "order_number": "ORD-12345",
            "product_name": "Wireless Headphones"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Customer service generation passed")
            print(f"   Template used: {result['template_used']}")
            print(f"   Tokens used: {result['tokens_used']}")
            print(f"   Processing time: {result['processing_time']:.2f}s")
            print(f"   Prompt length: {len(result['prompt'])} chars")
            print(f"   Response length: {len(result['response'])} chars")
        else:
            print(f"❌ Customer service generation failed: {response.status_code}")
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"❌ Customer service generation error: {e}")

def test_generate_data_analysis():
    """Test data analysis prompt generation"""
    print("\n🔍 Testing data analysis prompt generation...")
    
    test_data = {
        "context": "data_analysis",
        "data_type": "csv_analysis",
        "input_data": {
            "data_description": "Sales data for Q1 2024",
            "analysis_goal": "Identify top performing products",
            "data_columns": "Product, Sales, Revenue, Region",
            "specific_questions": "Which products have the highest revenue?"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Data analysis generation passed")
            print(f"   Template used: {result['template_used']}")
            print(f"   Tokens used: {result['tokens_used']}")
            print(f"   Processing time: {result['processing_time']:.2f}s")
            print(f"   Prompt length: {len(result['prompt'])} chars")
            print(f"   Response length: {len(result['response'])} chars")
        else:
            print(f"❌ Data analysis generation failed: {response.status_code}")
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"❌ Data analysis generation error: {e}")

def test_feedback():
    """Test the feedback endpoint"""
    print("\n🔍 Testing feedback endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/feedback")
        if response.status_code == 200:
            feedback = response.json()
            print("✅ Feedback endpoint passed")
            print(f"   Interaction count: {feedback['interaction_count']}")
            print(f"   Suggestions count: {len(feedback['suggestions'])}")
            if feedback['suggestions']:
                print("   Sample suggestions:")
                for i, suggestion in enumerate(feedback['suggestions'][:2]):
                    print(f"     {i+1}. {suggestion}")
        else:
            print(f"❌ Feedback endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Feedback endpoint error: {e}")

def test_stats():
    """Test the statistics endpoint"""
    print("\n🔍 Testing statistics endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Statistics endpoint passed")
            print(f"   Available contexts: {len(stats['available_contexts'])}")
            print(f"   Available data types: {len(stats['available_data_types'])}")
            if 'usage_statistics' in stats:
                usage = stats['usage_statistics']
                print(f"   Total interactions: {usage['total_interactions']}")
                print(f"   Unique templates: {usage['unique_templates']}")
        else:
            print(f"❌ Statistics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Statistics endpoint error: {e}")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Prompting Engine Demo API Tests")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    test_health()
    test_templates()
    test_generate_customer_service()
    test_generate_data_analysis()
    test_feedback()
    test_stats()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")

if __name__ == "__main__":
    run_all_tests() 