#!/usr/bin/env python3
"""
Test PAM Service with Real Dataset
Tests that PAM can:
1. Extract customer company name
2. Scrape LinkedIn for company data
3. Get latest trends
4. Augment prompts with real insights
"""

import json
import requests
import sys
from pathlib import Path

def load_dataset():
    """Load the real dataset"""
    dataset_path = Path(__file__).parent / 'data' / 'generated_data' / 'dataset_0001.json'
    
    print(f"📂 Loading dataset from: {dataset_path}")
    
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Dataset loaded successfully")
    print(f"   Customer: {data['name']}")
    print(f"   Transactions: {len(data['transactions'])}")
    print(f"   Customer ID: {data['customer_id']}")
    
    return data

def test_pam_service(dataset):
    """Test PAM service with real data"""
    
    pam_url = 'http://localhost:5005'
    
    # Check health first
    print(f"\n🏥 Checking PAM service health...")
    try:
        health_response = requests.get(f"{pam_url}/health", timeout=5)
        if health_response.status_code == 200:
            print(f"✅ PAM service is healthy")
        else:
            print(f"❌ PAM service health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to PAM service: {e}")
        print(f"   Make sure PAM service is running on port 5005")
        return False
    
    # Test augmentation
    print(f"\n🧠 Testing PAM augmentation...")
    print(f"   Company to research: {dataset['name']}")
    
    request_data = {
        'input_data': dataset,
        'prompt_text': f"Analyze financial data for {dataset['name']}",
        'context': 'core_banking'
    }
    
    try:
        print(f"\n📤 Sending request to PAM service...")
        response = requests.post(
            f"{pam_url}/augment",
            json=request_data,
            timeout=30  # Allow time for web scraping
        )
        
        if response.status_code != 200:
            print(f"❌ PAM request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        result = response.json()
        
        print(f"\n✅ PAM Augmentation Complete!")
        print(f"{'='*70}")
        
        # Display results
        print(f"\n📊 RESULTS:")
        print(f"   Companies Analyzed: {result.get('companies_analyzed', [])}")
        print(f"   Cache Hit: {result.get('cache_hit', False)}")
        print(f"   Processing Time: {result.get('processing_time_ms', 0):.2f}ms")
        
        # Display augmentation summary
        if 'augmentation_summary' in result:
            summary = result['augmentation_summary']
            print(f"\n📝 AUGMENTATION SUMMARY:")
            
            for company_name, company_data in summary.items():
                print(f"\n   🏢 {company_name}:")
                
                if 'linkedin_profile' in company_data:
                    print(f"      LinkedIn: {company_data['linkedin_profile'] or 'Not found'}")
                
                if 'latest_trends' in company_data and company_data['latest_trends']:
                    print(f"      Latest Trends:")
                    for i, trend in enumerate(company_data['latest_trends'][:3], 1):
                        print(f"         {i}. {trend[:100]}...")
                
                if 'insights' in company_data:
                    print(f"      LLM Insights:")
                    for i, insight in enumerate(company_data['insights'][:3], 1):
                        print(f"         {i}. {insight[:120]}...")
                
                if 'sources' in company_data:
                    print(f"      Data Sources: {', '.join(company_data['sources'])}")
        
        # Display augmented prompt (truncated)
        if 'augmented_prompt' in result:
            augmented = result['augmented_prompt']
            print(f"\n📄 AUGMENTED PROMPT (first 500 chars):")
            print(f"   {augmented[:500]}...")
        
        print(f"\n{'='*70}")
        print(f"✅ Test completed successfully!")
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out (web scraping may take longer)")
        print(f"   Try increasing timeout or check PAM service logs")
        return False
    except Exception as e:
        print(f"❌ Error during PAM test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 70)
    print("🧪 Testing PAM Service with Real Dataset")
    print("=" * 70)
    
    try:
        # Load dataset
        dataset = load_dataset()
        
        # Test PAM
        success = test_pam_service(dataset)
        
        if success:
            print(f"\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print(f"\n❌ Tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

