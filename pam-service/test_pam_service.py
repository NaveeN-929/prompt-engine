#!/usr/bin/env python3
"""
Test PAM Service
Unit tests for PAM service components
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.company_extractor import CompanyExtractor
from app.core.web_scraper import WebScraper
from app.config import settings


def test_company_extractor():
    """Test company extraction from transaction data"""
    print("\n" + "=" * 60)
    print("TEST: Company Extractor")
    print("=" * 60)
    
    extractor = CompanyExtractor()
    
    # Sample transaction data
    sample_data = {
        "customer_id": "BIZ_0001",
        "transactions": [
            {
                "date": "2025-11-01",
                "amount": 5000.00,
                "description": "Payment to TechCorp Inc for software licenses"
            },
            {
                "date": "2025-11-02",
                "amount": -2500.00,
                "description": "Consulting fees from Global Logistics Ltd"
            },
            {
                "date": "2025-11-03",
                "amount": 1500.00,
                "description": "Monthly subscription - Microsoft"
            }
        ]
    }
    
    # Extract companies
    result = extractor.extract_with_context(sample_data)
    
    print(f"\n✅ Extracted {result['total_companies']} companies:")
    for company in result['companies']:
        context = result['company_context'].get(company, {})
        print(f"   • {company}")
        print(f"     - Transactions: {context.get('transaction_count', 0)}")
        print(f"     - Total amount: ${context.get('total_amount', 0):,.2f}")
    
    return len(result['companies']) > 0


def test_web_scraper():
    """Test web scraping functionality"""
    print("\n" + "=" * 60)
    print("TEST: Web Scraper (Basic)")
    print("=" * 60)
    
    scraper = WebScraper(
        user_agent=settings.USER_AGENT,
        timeout=settings.SCRAPING_TIMEOUT,
        rate_limit_delay=settings.RATE_LIMIT_DELAY
    )
    
    # Test with a well-known company
    test_company = "Microsoft"
    
    print(f"\n🔍 Scraping info for: {test_company}")
    print("   (This may take a few seconds...)")
    
    try:
        info = scraper.scrape_company_info(test_company)
        
        print(f"\n✅ Scraping completed:")
        print(f"   • Overview: {info.get('overview', 'Not found')[:100]}...")
        print(f"   • Industry: {info.get('industry', 'Not found')}")
        print(f"   • News items: {len(info.get('news', []))}")
        print(f"   • Sources: {', '.join(info.get('sources', []))}")
        
        return True
    except Exception as e:
        print(f"⚠️  Scraping test failed: {e}")
        print("   (This is expected if no internet connection)")
        return False


def test_pam_service_api():
    """Test PAM service API endpoint"""
    print("\n" + "=" * 60)
    print("TEST: PAM Service API")
    print("=" * 60)
    
    import requests
    
    # Check if service is running
    try:
        response = requests.get("http://localhost:5005/health", timeout=2)
        
        if response.status_code == 200:
            health = response.json()
            print(f"\n✅ PAM Service is running:")
            print(f"   • Status: {health.get('status')}")
            print(f"   • Components:")
            for component, status in health.get('components', {}).items():
                status_icon = "✅" if status else "❌"
                print(f"     {status_icon} {component}: {status}")
            
            return True
        else:
            print(f"⚠️  PAM Service returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  PAM Service is not running")
        print("   Start it with: cd pam-service && python3 run_service.py")
        return False
    except Exception as e:
        print(f"❌ Error testing PAM API: {e}")
        return False


def test_augmentation_request():
    """Test full augmentation request"""
    print("\n" + "=" * 60)
    print("TEST: Full Augmentation Request")
    print("=" * 60)
    
    import requests
    
    # Sample request
    sample_request = {
        "input_data": {
            "customer_id": "BIZ_0001",
            "transactions": [
                {
                    "date": "2025-11-01",
                    "amount": 5000.00,
                    "description": "Payment from TechCorp Inc"
                },
                {
                    "date": "2025-11-02",
                    "amount": -2500.00,
                    "description": "Vendor payment to Global Solutions Ltd"
                }
            ]
        },
        "prompt_text": "Analyze the transaction patterns and provide insights.",
        "context": "core_banking"
    }
    
    try:
        print("\n📤 Sending augmentation request...")
        response = requests.post(
            "http://localhost:5005/augment",
            json=sample_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Augmentation completed:")
            print(f"   • Companies analyzed: {len(result.get('companies_analyzed', []))}")
            for company in result.get('companies_analyzed', [])[:3]:
                print(f"     - {company}")
            print(f"   • Cache hit: {result.get('cache_hit', False)}")
            print(f"   • Processing time: {result.get('processing_time_ms', 0):.2f}ms")
            
            # Show augmented prompt snippet
            augmented = result.get('augmented_prompt', '')
            if augmented:
                print(f"\n   📝 Augmented prompt (first 200 chars):")
                print(f"      {augmented[:200]}...")
            
            return True
        else:
            print(f"❌ Augmentation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  PAM Service is not running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 PAM SERVICE TESTS")
    print("=" * 60)
    
    tests = [
        ("Company Extractor", test_company_extractor),
        ("Web Scraper", test_web_scraper),
        ("PAM Service API", test_pam_service_api),
        ("Full Augmentation", test_augmentation_request)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

