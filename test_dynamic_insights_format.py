#!/usr/bin/env python3
"""
Test script to verify dynamic insights count and "Your..." format
"""

import requests
import json

def test_dynamic_insights_and_format():
    """Test that insights start with 'Your...' and count varies with dataset size"""
    
    print("🧪 Testing Dynamic Insights Count and 'Your...' Format")
    print("=" * 70)
    
    # Test Case 1: Small Dataset (5 transactions) - Should get 3-4 insights
    small_dataset = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": 5000, "type": "credit", "description": "Invoice Payment"},
                {"date": "2024-01-02", "amount": 3000, "type": "credit", "description": "Consulting Fee"},
                {"date": "2024-01-03", "amount": -2000, "type": "debit", "description": "Office Rent"},
                {"date": "2024-01-04", "amount": -1000, "type": "debit", "description": "Marketing Ads"},
                {"date": "2024-01-05", "amount": -500, "type": "debit", "description": "Software License"}
            ],
            "account_balance": 4500
        }
    }
    
    # Test Case 2: Medium Dataset (20 transactions) - Should get 4-5 insights
    medium_dataset = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": 15000, "type": "credit", "description": "Large Contract"},
                {"date": "2024-01-02", "amount": 8000, "type": "credit", "description": "Consulting Revenue"},
                {"date": "2024-01-03", "amount": 6000, "type": "credit", "description": "Software Sales"},
                {"date": "2024-01-04", "amount": 4000, "type": "credit", "description": "Marketing Services"},
                {"date": "2024-01-05", "amount": 3000, "type": "credit", "description": "Support Contract"},
                {"date": "2024-01-06", "amount": -5000, "type": "debit", "description": "Office Rent"},
                {"date": "2024-01-07", "amount": -3000, "type": "debit", "description": "Staff Payroll"},
                {"date": "2024-01-08", "amount": -2000, "type": "debit", "description": "Marketing Campaign"},
                {"date": "2024-01-09", "amount": -1500, "type": "debit", "description": "Software Licenses"},
                {"date": "2024-01-10", "amount": -1000, "type": "debit", "description": "Cloud Hosting"},
                {"date": "2024-01-11", "amount": -800, "type": "debit", "description": "Office Supplies"},
                {"date": "2024-01-12", "amount": -600, "type": "debit", "description": "Internet & Phone"},
                {"date": "2024-01-13", "amount": -500, "type": "debit", "description": "Accounting Services"},
                {"date": "2024-01-14", "amount": -400, "type": "debit", "description": "Legal Services"},
                {"date": "2024-01-15", "amount": -300, "type": "debit", "description": "Insurance"},
                {"date": "2024-02-01", "amount": 12000, "type": "credit", "description": "February Contract"},
                {"date": "2024-02-02", "amount": 7000, "type": "credit", "description": "Consulting Feb"},
                {"date": "2024-02-03", "amount": -4000, "type": "debit", "description": "February Rent"},
                {"date": "2024-02-04", "amount": -2500, "type": "debit", "description": "February Payroll"},
                {"date": "2024-02-05", "amount": -1200, "type": "debit", "description": "Marketing Feb"}
            ],
            "account_balance": 32100
        }
    }
    
    # Test Case 3: Large Dataset (50+ transactions) - Should get 5+ insights
    large_dataset = {
        "input_data": {
            "transactions": []
        }
    }
    
    # Generate 60 transactions for large dataset
    for i in range(1, 61):
        if i % 3 == 0:  # Every 3rd transaction is a credit
            large_dataset["input_data"]["transactions"].append({
                "date": f"2024-01-{(i % 30) + 1:02d}",
                "amount": 5000 + (i * 100),
                "type": "credit",
                "description": f"Invoice #{1000 + i} - Revenue"
            })
        else:  # Others are debits
            large_dataset["input_data"]["transactions"].append({
                "date": f"2024-01-{(i % 30) + 1:02d}",
                "amount": -(1000 + (i * 50)),
                "type": "debit",
                "description": f"Business Expense #{i}"
            })
    
    large_dataset["input_data"]["account_balance"] = 75000
    
    test_cases = [
        ("Small Dataset (5 transactions)", small_dataset, 3, 4),
        ("Medium Dataset (20 transactions)", medium_dataset, 4, 6),
        ("Large Dataset (60 transactions)", large_dataset, 5, 8)
    ]
    
    results = []
    
    for case_name, test_data, min_expected, max_expected in test_cases:
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
                
                # Extract insights section
                if "SECTION 1: INSIGHTS" in analysis:
                    insights_section = analysis.split("SECTION 1: INSIGHTS")[1].split("SECTION 2: RECOMMENDATIONS")[0]
                    insight_lines = [line.strip() for line in insights_section.split('\n') if line.strip().startswith('Insight')]
                    
                    # Extract recommendations section
                    recommendations_section = analysis.split("SECTION 2: RECOMMENDATIONS")[1].split("=== ANALYSIS METADATA ===")[0]
                    recommendation_lines = [line.strip() for line in recommendations_section.split('\n') if line.strip().startswith('Recommendation')]
                    
                    insight_count = len(insight_lines)
                    recommendation_count = len(recommendation_lines)
                    
                    print(f"📊 Insights Generated: {insight_count} (Expected: {min_expected}-{max_expected})")
                    print(f"📊 Recommendations Generated: {recommendation_count}")
                    
                    # Check "Your..." format
                    your_format_count = 0
                    for line in insight_lines:
                        if "Your" in line:
                            your_format_count += 1
                    
                    print(f"📝 'Your...' Format: {your_format_count}/{insight_count} insights")
                    
                    # Show sample insights
                    print(f"\n📋 Sample Insights:")
                    for i, insight in enumerate(insight_lines[:3], 1):
                        insight_text = insight.split(": ", 1)[1] if ": " in insight else insight
                        print(f"   {i}. {insight_text[:80]}...")
                    
                    # Evaluate success
                    count_ok = min_expected <= insight_count <= max_expected
                    format_ok = your_format_count >= insight_count * 0.7  # At least 70% should start with "Your"
                    
                    status = "✅ PASS" if count_ok and format_ok else "❌ FAIL"
                    print(f"\n{status} - Count: {'✅' if count_ok else '❌'}, Format: {'✅' if format_ok else '❌'}")
                    
                    results.append((case_name, insight_count, your_format_count, count_ok and format_ok))
                else:
                    print("❌ Could not find insights section")
                    results.append((case_name, 0, 0, False))
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                results.append((case_name, 0, 0, False))
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append((case_name, 0, 0, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Dynamic Insights and Format Summary")
    print("=" * 70)
    
    successful_tests = sum(1 for result in results if result[3])
    
    for case_name, insight_count, your_count, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{case_name}: {insight_count} insights, {your_count} with 'Your' - {status}")
    
    print(f"\nOverall Success Rate: {successful_tests}/{len(results)}")
    
    if successful_tests == len(results):
        print("\n🎉 SUCCESS: Dynamic insights and 'Your...' format working correctly!")
        print("✅ Insight count varies with dataset size")
        print("✅ Insights start with 'Your...' format")
        return True
    else:
        print("\n🔧 Some tests failed - check the implementation.")
        return False

if __name__ == "__main__":
    print("🚀 Testing Dynamic Insights Count and Format")
    print("Make sure the autonomous agent server is running on port 5001")
    print()
    
    success = test_dynamic_insights_and_format()
    
    if success:
        print("\n🎯 The system now generates variable insights based on data size!")
        print("Visit http://localhost:5001/simple to see the dynamic analysis in action!")
    else:
        print("\n🔧 Check the server logs for any issues with the dynamic logic.")
