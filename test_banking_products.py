#!/usr/bin/env python3
"""
Test script to verify the refactored banking product recommendations
"""

import requests
import json

def test_banking_product_recommendations():
    """Test that the system uses the correct banking products for upsell/cross-sell"""
    
    print("🧪 Testing Refactored Banking Product Recommendations")
    print("=" * 70)
    
    # Test Case 1: High Cash Flow Business (Should get savings products)
    high_cashflow_case = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": 50000, "type": "credit", "description": "Large Contract Payment"},
                {"date": "2024-01-02", "amount": 30000, "type": "credit", "description": "Consulting Revenue"},
                {"date": "2024-01-03", "amount": 25000, "type": "credit", "description": "Software License Sales"},
                {"date": "2024-01-04", "amount": -5000, "type": "debit", "description": "Office Rent"},
                {"date": "2024-01-05", "amount": -2000, "type": "debit", "description": "Staff Payroll"},
                {"date": "2024-01-06", "amount": -1000, "type": "debit", "description": "Marketing Spend"}
            ],
            "account_balance": 97000
        }
    }
    
    # Test Case 2: Cash Flow Deficit Business (Should get overdraft/financing)
    deficit_case = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": 5000, "type": "credit", "description": "Small Invoice Payment"},
                {"date": "2024-01-02", "amount": 3000, "type": "credit", "description": "Consulting Fee"},
                {"date": "2024-01-03", "amount": -15000, "type": "debit", "description": "Large Equipment Purchase"},
                {"date": "2024-01-04", "amount": -8000, "type": "debit", "description": "Staff Payroll"},
                {"date": "2024-01-05", "amount": -5000, "type": "debit", "description": "Office Rent"},
                {"date": "2024-01-06", "amount": -3000, "type": "debit", "description": "Marketing Campaign"}
            ],
            "account_balance": 2000
        }
    }
    
    # Test Case 3: International Business (Should get multi-currency)
    international_case = {
        "input_data": {
            "transactions": [
                {"date": "2024-01-01", "amount": 12000, "type": "credit", "description": "USD Invoice Payment - International Client"},
                {"date": "2024-01-02", "amount": 8000, "type": "credit", "description": "EUR Consulting Revenue"},
                {"date": "2024-01-03", "amount": 6000, "type": "credit", "description": "GBP Software License"},
                {"date": "2024-01-04", "amount": -2000, "type": "debit", "description": "Office Rent"},
                {"date": "2024-01-05", "amount": -1500, "type": "debit", "description": "Currency Exchange Fees"},
                {"date": "2024-01-06", "amount": -1000, "type": "debit", "description": "International Wire Transfer"}
            ],
            "account_balance": 21500
        }
    }
    
    test_cases = [
        ("High Cash Flow Business", high_cashflow_case, ["high-yield savings", "term deposits"]),
        ("Cash Deficit Business", deficit_case, ["overdraft facilities", "invoice financing"]),
        ("International Business", international_case, ["multi-currency business accounts"])
    ]
    
    expected_products = {
        "Upsell": ["High-yield savings accounts", "Flexible overdraft facilities", "invoice financing", "Revolving credit lines"],
        "Cross-sell": ["Multi-currency business accounts", "Payroll and cash management services"]
    }
    
    print("🏦 Expected Banking Products:")
    print("   Upsell: High-yield savings, Overdraft facilities, Invoice financing, Revolving credit lines")
    print("   Cross-sell: Multi-currency accounts, Payroll & cash management services")
    print()
    
    results = []
    
    for case_name, test_data, expected_keywords in test_cases:
        print(f"🔍 Testing: {case_name}")
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
                
                # Extract recommendations section
                if "SECTION 2: RECOMMENDATIONS" in analysis:
                    recommendations = analysis.split("SECTION 2: RECOMMENDATIONS")[1].split("=== ANALYSIS METADATA ===")[0]
                    
                    # Check for banking product recommendations
                    upsell_count = recommendations.count("(Upsell)")
                    crosssell_count = recommendations.count("(Cross-sell)")
                    
                    print(f"📊 Banking Products Found:")
                    print(f"   Upsell recommendations: {upsell_count}")
                    print(f"   Cross-sell recommendations: {crosssell_count}")
                    
                    # Check for expected keywords
                    found_expected = False
                    for keyword in expected_keywords:
                        if keyword.lower() in recommendations.lower():
                            found_expected = True
                            print(f"   ✅ Found expected product: {keyword}")
                            break
                    
                    if not found_expected:
                        print(f"   ❌ Expected products not found: {expected_keywords}")
                    
                    print(f"\n📋 Recommendations:")
                    rec_lines = [line.strip() for line in recommendations.split('\n') if line.strip() and line.strip().startswith('Recommendation')]
                    for rec in rec_lines:
                        if "(Upsell)" in rec or "(Cross-sell)" in rec:
                            print(f"   🏦 {rec}")
                        else:
                            print(f"   💡 {rec}")
                    
                    results.append((case_name, upsell_count + crosssell_count, found_expected))
                else:
                    print("❌ Could not find recommendations section")
                    results.append((case_name, 0, False))
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                results.append((case_name, 0, False))
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append((case_name, 0, False))
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 Banking Product Recommendation Summary")
    print("=" * 70)
    
    total_banking_products = sum(result[1] for result in results)
    successful_matches = sum(1 for result in results if result[2])
    
    print(f"Total Banking Product Recommendations: {total_banking_products}")
    print(f"Cases with Expected Products: {successful_matches}/{len(results)}")
    
    for case_name, product_count, matched in results:
        status = "✅ PASS" if matched and product_count >= 2 else "❌ FAIL"
        print(f"   {case_name}: {product_count} products, {status}")
    
    if successful_matches == len(results) and total_banking_products >= 6:
        print("\n🎉 SUCCESS: Banking product recommendations are working correctly!")
        print("The system now uses the approved banking products for upsell/cross-sell.")
        return True
    else:
        print("\n🔧 Banking product recommendations may need adjustment.")
        return False

if __name__ == "__main__":
    print("🚀 Testing Banking Product Recommendations")
    print("Make sure the autonomous agent server is running on port 5001")
    print()
    
    success = test_banking_product_recommendations()
    
    if success:
        print("\n🎯 Visit http://localhost:5001/simple to see the updated banking products in action!")
    else:
        print("\n🔧 Check the server logs for any issues with the banking product logic.")
