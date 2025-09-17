#!/usr/bin/env python3
"""
Test script to verify dynamic analysis is working with different datasets
"""

import requests
import json

def test_dynamic_analysis():
    """Test multiple different datasets to verify dynamic analysis"""
    
    print("🧪 Testing Dynamic CRM Analysis")
    print("=" * 70)
    
    # Test Case 1: High Revenue, Low Expenses (Profitable Business)
    test_case_1 = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": 15000, "type": "credit", "description": "Invoice #001 - Consulting Services"},
                {"date": "2024-01-02", "amount": 12000, "type": "credit", "description": "Invoice #002 - Web Development"},
                {"date": "2024-01-03", "amount": 8000, "type": "credit", "description": "Invoice #003 - Marketing Campaign"},
                {"date": "2024-01-04", "amount": -2000, "type": "debit", "description": "Office Rent"},
                {"date": "2024-01-05", "amount": -500, "type": "debit", "description": "Software Subscriptions"},
                {"date": "2024-01-06", "amount": -300, "type": "debit", "description": "Marketing Ads"}
            ],
            "account_balance": 32200
        }
    }
    
    # Test Case 2: Low Revenue, High Expenses (Struggling Business)
    test_case_2 = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": 2000, "type": "credit", "description": "Small Invoice Payment"},
                {"date": "2024-01-02", "amount": 1500, "type": "credit", "description": "Freelance Payment"},
                {"date": "2024-01-03", "amount": -5000, "type": "debit", "description": "Office Rent"},
                {"date": "2024-01-04", "amount": -3000, "type": "debit", "description": "Staff Payroll"},
                {"date": "2024-01-05", "amount": -2000, "type": "debit", "description": "Equipment Purchase"},
                {"date": "2024-01-06", "amount": -1000, "type": "debit", "description": "Marketing Spend"},
                {"date": "2024-01-07", "amount": -800, "type": "debit", "description": "Software Licenses"}
            ],
            "account_balance": 5000
        }
    }
    
    # Test Case 3: Tech-Heavy Business
    test_case_3 = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": 10000, "type": "credit", "description": "SaaS Revenue"},
                {"date": "2024-01-02", "amount": 8000, "type": "credit", "description": "Software License Sales"},
                {"date": "2024-01-03", "amount": -3000, "type": "debit", "description": "AWS Cloud Hosting"},
                {"date": "2024-01-04", "amount": -2000, "type": "debit", "description": "Software Development Tools"},
                {"date": "2024-01-05", "amount": -1500, "type": "debit", "description": "GitHub Enterprise"},
                {"date": "2024-01-06", "amount": -1000, "type": "debit", "description": "Microsoft 365"},
                {"date": "2024-01-07", "amount": -800, "type": "debit", "description": "Zoom Pro"},
                {"date": "2024-01-08", "amount": -500, "type": "debit", "description": "Slack Premium"}
            ],
            "account_balance": 15000
        }
    }
    
    test_cases = [
        ("Profitable Business", test_case_1),
        ("Struggling Business", test_case_2), 
        ("Tech-Heavy Business", test_case_3)
    ]
    
    results = []
    
    for case_name, test_data in test_cases:
        print(f"\n🔍 Testing: {case_name}")
        print("-" * 50)
        
        try:
            response = requests.post(
                "http://localhost:5001/test/generic-insights", 
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get('analysis', '')
                
                print("✅ Analysis generated successfully!")
                print("\n📋 Generated Analysis:")
                print(analysis)
                
                # Check if analysis is dynamic (different for each case)
                results.append((case_name, analysis))
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                results.append((case_name, None))
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append((case_name, None))
    
    # Analyze results for uniqueness
    print("\n" + "=" * 70)
    print("📊 Dynamic Analysis Verification")
    print("=" * 70)
    
    if len(results) >= 2:
        analysis_texts = [result[1] for result in results if result[1]]
        
        if len(set(analysis_texts)) == len(analysis_texts):
            print("✅ SUCCESS: All analyses are unique - Dynamic analysis is working!")
            print("🎯 Each dataset produced different insights and recommendations")
        else:
            print("❌ FAILED: Some analyses are identical - Analysis may still be hardcoded")
            
        # Show comparison
        for i, (case_name, analysis) in enumerate(results):
            if analysis:
                insights = analysis.split("SECTION 1: INSIGHTS")[1].split("SECTION 2: RECOMMENDATIONS")[0] if "SECTION 1: INSIGHTS" in analysis else "No insights found"
                print(f"\n{i+1}. {case_name} Key Insight:")
                print(f"   {insights.strip()[:100]}...")
    else:
        print("❌ FAILED: Not enough test results to verify dynamic analysis")
    
    return len(set([result[1] for result in results if result[1]])) == len([result[1] for result in results if result[1]])

if __name__ == "__main__":
    success = test_dynamic_analysis()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 DYNAMIC ANALYSIS IS WORKING!")
        print("The system now generates different insights based on actual transaction patterns.")
        print("Visit http://localhost:5001/simple to see the dynamic analysis in action!")
    else:
        print("🔧 Dynamic analysis needs more work - insights may still be hardcoded.")
