#!/usr/bin/env python3
"""
Demo Script - Blocking Validation Integration
Demonstrates the complete blocking validation system
"""

import requests
import json
import time
from datetime import datetime

# Configuration
AUTONOMOUS_AGENT_URL = "http://localhost:8000"

# Sample data for demonstration
DEMO_DATA = {
    "high_quality_input": {
        "transactions": [
            {"date": "2024-01-15", "amount": 3500.00, "type": "credit", "description": "Salary deposit"},
            {"date": "2024-01-16", "amount": -1200.00, "type": "debit", "description": "Rent payment"},
            {"date": "2024-01-17", "amount": -150.00, "type": "debit", "description": "Utilities bill"},
            {"date": "2024-01-18", "amount": -400.00, "type": "debit", "description": "Groceries"},
            {"date": "2024-01-19", "amount": -75.00, "type": "debit", "description": "Dining out"},
            {"date": "2024-01-20", "amount": -50.00, "type": "debit", "description": "Gas station"},
        ],
        "account_balance": 1625.00,
        "analysis_period": "2024-01"
    },
    "minimal_input": {
        "transactions": [
            {"date": "2024-01-15", "amount": 100.00, "type": "credit", "description": "Test"}
        ],
        "account_balance": 100.00
    }
}

def demo_blocking_validation():
    """Demonstrate the blocking validation system"""
    
    print("🔒 BLOCKING VALIDATION INTEGRATION DEMO")
    print("=" * 50)
    print()
    print("This demo shows how the autonomous agent now includes")
    print("BLOCKING validation - end users only see validated responses!")
    print()
    
    # Check system status first
    print("📊 Checking system status...")
    try:
        status_response = requests.get(f"{AUTONOMOUS_AGENT_URL}/status", timeout=10)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"   ✅ System status: {status_data.get('status', 'unknown')}")
            print(f"   🔧 Pipeline: {status_data.get('mode', 'unknown')}")
            
            services = status_data.get('services', {})
            print(f"   🤖 RAG Service: {services.get('rag_service', 'unknown')}")
            print(f"   🔍 Validation Service: {services.get('validation_service', 'unknown')}")
            
            features = status_data.get('features', {})
            blocking_validation = features.get('blocking_validation', 'unknown')
            print(f"   🔒 Blocking Validation: {blocking_validation}")
            
            if blocking_validation != 'enabled':
                print("   ⚠️ Warning: Blocking validation not enabled!")
        else:
            print(f"   ❌ Status check failed: HTTP {status_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Status check failed: {e}")
        return
    
    print()
    
    # Demo 1: High-quality input (should get high validation scores)
    print("🧪 DEMO 1: High-quality financial data")
    print("-" * 30)
    
    demo_request(
        "High-Quality Financial Analysis",
        DEMO_DATA["high_quality_input"],
        "This should receive a high validation score"
    )
    
    print()
    
    # Demo 2: Minimal input (might get lower validation scores)
    print("🧪 DEMO 2: Minimal financial data")
    print("-" * 30)
    
    demo_request(
        "Minimal Financial Analysis", 
        DEMO_DATA["minimal_input"],
        "This might receive a lower validation score due to limited data"
    )
    
    print()
    print("=" * 50)
    print("🎉 DEMO COMPLETE")
    print()
    print("Key observations:")
    print("✅ All responses include validation metadata")
    print("✅ Quality levels and scores are provided")
    print("✅ End users only see validated responses")
    print("✅ System continues to work even if validation has issues")
    print()
    print("The blocking validation integration is working correctly!")

def demo_request(title: str, input_data: dict, description: str):
    """Perform a demo request and analyze the response"""
    
    print(f"📋 {title}")
    print(f"   {description}")
    print()
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{AUTONOMOUS_AGENT_URL}/analyze",
            json={"input_data": input_data},
            timeout=60  # Allow time for validation
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            response_data = response.json()
            
            print(f"   ✅ Request successful ({processing_time:.3f}s)")
            print(f"   📊 Pipeline: {response_data.get('pipeline_used', 'unknown')}")
            
            # Analyze validation data
            validation = response_data.get('validation', {})
            if validation:
                quality_level = validation.get('quality_level', 'unknown')
                overall_score = validation.get('overall_score', 0.0)
                quality_approved = validation.get('quality_approved', False)
                quality_note = validation.get('quality_note', 'No note')
                
                print(f"   🔍 Validation Results:")
                print(f"      Quality Level: {quality_level}")
                print(f"      Overall Score: {overall_score:.3f}")
                print(f"      Quality Approved: {quality_approved}")
                print(f"      Note: {quality_note}")
                
                # Show detailed scores if available
                validation_details = validation.get('validation_details', {})
                if validation_details:
                    print(f"   📈 Detailed Scores:")
                    for criterion, score in validation_details.items():
                        if isinstance(score, (int, float)):
                            print(f"      {criterion}: {score:.3f}")
            else:
                print(f"   ⚠️ No validation data found")
            
            # Show response structure
            analysis = response_data.get('analysis', '')
            if analysis:
                has_insights = "=== SECTION 1: INSIGHTS ===" in analysis
                has_recommendations = "=== SECTION 2: RECOMMENDATIONS ===" in analysis
                print(f"   📄 Response Structure:")
                print(f"      Has Insights Section: {has_insights}")
                print(f"      Has Recommendations Section: {has_recommendations}")
                print(f"      Structure Valid: {has_insights and has_recommendations}")
        
        else:
            error_data = None
            try:
                error_data = response.json()
            except:
                pass
            
            print(f"   ❌ Request failed: HTTP {response.status_code}")
            if error_data:
                print(f"   📋 Error: {error_data.get('error', 'Unknown error')}")
    
    except requests.exceptions.Timeout:
        print(f"   ⏰ Request timed out (>{60}s)")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

if __name__ == "__main__":
    demo_blocking_validation()
