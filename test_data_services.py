#!/usr/bin/env python3
"""
Test Data Services - Pseudonymization and Repersonalization
Complete workflow demonstration
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, Any

# Service URLs
PSEUDO_URL = "http://localhost:5003"
REPERSONAL_URL = "http://localhost:5004"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_services():
    """Check if both services are running"""
    print_section("🏥 Checking Service Health")
    
    try:
        # Check Pseudonymization Service
        pseudo_health = requests.get(f"{PSEUDO_URL}/health", timeout=5)
        if pseudo_health.status_code == 200:
            print("✅ Pseudonymization Service: Healthy")
        else:
            print("❌ Pseudonymization Service: Unhealthy")
            return False
        
        # Check Repersonalization Service
        repersonal_health = requests.get(f"{REPERSONAL_URL}/health", timeout=5)
        if repersonal_health.status_code == 200:
            print("✅ Repersonalization Service: Healthy")
            
            # Check connectivity
            health_data = repersonal_health.json()
            pseudo_status = health_data.get('pseudonymization_service_status')
            if pseudo_status == 'connected':
                print("✅ Service Connectivity: Connected")
            else:
                print(f"⚠️  Service Connectivity: {pseudo_status}")
        else:
            print("❌ Repersonalization Service: Unhealthy")
            return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to services: {str(e)}")
        print("\n💡 Make sure services are running:")
        print("   ./start_data_services.sh")
        return False


def test_single_pseudonymization():
    """Test single data pseudonymization and repersonalization"""
    print_section("🧪 Test 1: Single Pseudonymization")
    
    # Sample data
    original_data = {
        "transactions": [
            {
                "date": "2025-11-10",
                "amount": 5000.00,
                "type": "credit",
                "description": "Monthly salary"
            },
            {
                "date": "2025-11-12",
                "amount": -150.00,
                "type": "debit",
                "description": "Grocery shopping"
            },
            {
                "date": "2025-11-15",
                "amount": -75.50,
                "type": "debit",
                "description": "Dining out"
            }
        ],
        "account_balance": 15000.00,
        "customer_id": "CUST_12345"
    }
    
    print("\n📊 Original Data:")
    print(f"   Customer ID: {original_data['customer_id']}")
    print(f"   Account Balance: ${original_data['account_balance']:,.2f}")
    print(f"   Transactions: {len(original_data['transactions'])}")
    
    # Step 1: Pseudonymize
    print("\n🔒 Step 1: Pseudonymizing...")
    start_time = time.time()
    
    pseudo_response = requests.post(
        f"{PSEUDO_URL}/pseudonymize",
        json=original_data
    )
    
    if pseudo_response.status_code != 200:
        print(f"❌ Pseudonymization failed: {pseudo_response.text}")
        return None
    
    pseudo_result = pseudo_response.json()
    pseudonym_id = pseudo_result['pseudonym_id']
    pseudonymized_data = pseudo_result['pseudonymized_data']
    
    pseudo_time = time.time() - start_time
    
    print(f"✅ Pseudonymized successfully in {pseudo_time*1000:.2f}ms")
    print(f"   Pseudonym ID: {pseudonym_id}")
    print(f"   Pseudonymized Customer ID: {pseudonymized_data['customer_id']}")
    print(f"   Pseudonymized Balance: ${pseudonymized_data['account_balance']:,.2f}")
    print(f"   Fields pseudonymized: {len(pseudo_result['fields_pseudonymized'])}")
    
    # Step 2: Process pseudonymized data
    print("\n🔬 Step 2: Processing pseudonymized data...")
    print("   (This is where you'd safely analyze the data)")
    time.sleep(0.5)  # Simulate processing
    print("✅ Processing complete")
    
    # Step 3: Repersonalize
    print("\n🔓 Step 3: Repersonalizing...")
    start_time = time.time()
    
    repersonal_response = requests.post(
        f"{REPERSONAL_URL}/repersonalize",
        json={
            'pseudonym_id': pseudonym_id,
            'verify': True
        }
    )
    
    if repersonal_response.status_code != 200:
        print(f"❌ Repersonalization failed: {repersonal_response.text}")
        return None
    
    repersonal_result = repersonal_response.json()
    restored_data = repersonal_result['original_data']
    
    repersonal_time = time.time() - start_time
    
    print(f"✅ Repersonalized successfully in {repersonal_time*1000:.2f}ms")
    print(f"   Restored Customer ID: {restored_data['customer_id']}")
    print(f"   Restored Balance: ${restored_data['account_balance']:,.2f}")
    print(f"   Verified: {repersonal_result['verified']}")
    
    # Verify data integrity
    print("\n🔍 Verifying data integrity...")
    if restored_data == original_data:
        print("✅ Data integrity verified - exact match!")
    else:
        print("⚠️  Data mismatch detected")
    
    # Step 4: Cleanup
    print("\n🧹 Step 4: Cleaning up...")
    cleanup_response = requests.delete(
        f"{REPERSONAL_URL}/cleanup/{pseudonym_id}"
    )
    
    if cleanup_response.status_code == 200:
        print("✅ Pseudonym cleaned up")
    else:
        print(f"⚠️  Cleanup warning: {cleanup_response.text}")
    
    return pseudonym_id


def test_bulk_pseudonymization():
    """Test bulk pseudonymization with sample datasets"""
    print_section("🧪 Test 2: Bulk Pseudonymization")
    
    # Check if sample data exists
    data_dir = Path('data/generated_data')
    if not data_dir.exists():
        print("⚠️  Sample data directory not found. Creating sample datasets...")
        datasets = create_sample_datasets(5)
    else:
        data_files = list(data_dir.glob('dataset_*.json'))[:5]
        if not data_files:
            print("⚠️  No sample datasets found. Creating sample datasets...")
            datasets = create_sample_datasets(5)
        else:
            print(f"📁 Loading {len(data_files)} sample datasets...")
            datasets = []
            for file in data_files:
                with open(file) as f:
                    datasets.append(json.load(f))
    
    print(f"📊 Processing {len(datasets)} datasets...")
    
    # Bulk pseudonymize
    print("\n🔒 Bulk pseudonymizing...")
    start_time = time.time()
    
    pseudo_response = requests.post(
        f"{PSEUDO_URL}/pseudonymize/bulk",
        json={
            'datasets': datasets,
            'batch_id': 'test_batch_001'
        }
    )
    
    if pseudo_response.status_code != 200:
        print(f"❌ Bulk pseudonymization failed: {pseudo_response.text}")
        return
    
    bulk_result = pseudo_response.json()
    pseudo_time = time.time() - start_time
    
    print(f"✅ Bulk pseudonymization complete in {pseudo_time*1000:.2f}ms")
    print(f"   Successful: {bulk_result['successful']}")
    print(f"   Failed: {bulk_result['failed']}")
    print(f"   Average: {pseudo_time/len(datasets)*1000:.2f}ms per dataset")
    
    # Extract pseudonym IDs
    pseudonym_ids = [
        r['pseudonym_id'] for r in bulk_result['results']
        if r.get('success', False)
    ]
    
    # Bulk repersonalize
    print("\n🔓 Bulk repersonalizing...")
    start_time = time.time()
    
    repersonal_response = requests.post(
        f"{REPERSONAL_URL}/repersonalize/bulk",
        json={
            'pseudonym_ids': pseudonym_ids,
            'batch_id': 'test_batch_001',
            'continue_on_error': True
        }
    )
    
    if repersonal_response.status_code != 200:
        print(f"❌ Bulk repersonalization failed: {repersonal_response.text}")
        return
    
    repersonal_result = repersonal_response.json()
    repersonal_time = time.time() - start_time
    
    print(f"✅ Bulk repersonalization complete in {repersonal_time*1000:.2f}ms")
    print(f"   Successful: {repersonal_result['successful']}")
    print(f"   Failed: {repersonal_result['failed']}")
    print(f"   Average: {repersonal_time/len(pseudonym_ids)*1000:.2f}ms per dataset")


def create_sample_datasets(count: int) -> list:
    """Create sample datasets for testing"""
    datasets = []
    for i in range(count):
        datasets.append({
            "transactions": [
                {
                    "date": f"2025-11-{10+i}",
                    "amount": 5000.00 + (i * 100),
                    "type": "credit",
                    "description": f"Transaction {i+1}"
                }
            ],
            "account_balance": 15000.00 + (i * 1000),
            "customer_id": f"TEST_{i+1:03d}"
        })
    return datasets


def check_statistics():
    """Check service statistics"""
    print_section("📊 Service Statistics")
    
    # Pseudonymization stats
    pseudo_stats = requests.get(f"{PSEUDO_URL}/stats").json()
    print("\n🔒 Pseudonymization Service:")
    print(f"   Total pseudonymized: {pseudo_stats['statistics']['total_pseudonymized']}")
    print(f"   Fields processed: {pseudo_stats['statistics']['total_fields_processed']}")
    print(f"   Active pseudonyms: {pseudo_stats['statistics']['active_pseudonyms']}")
    
    # Repersonalization stats
    repersonal_stats = requests.get(f"{REPERSONAL_URL}/stats").json()
    print("\n🔓 Repersonalization Service:")
    print(f"   Total repersonalized: {repersonal_stats['statistics']['total_repersonalized']}")
    print(f"   Total failed: {repersonal_stats['statistics']['total_failed']}")
    print(f"   Success rate: {repersonal_stats['statistics']['success_rate']:.2f}%")


def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("  🔐 Data Services Test Suite")
    print("  Pseudonymization & Repersonalization")
    print("=" * 70)
    
    # Check if services are running
    if not check_services():
        return
    
    # Run tests
    test_single_pseudonymization()
    test_bulk_pseudonymization()
    check_statistics()
    
    print_section("✅ All Tests Complete!")
    print("\n📚 Next Steps:")
    print("   - View API docs: http://localhost:8001/docs")
    print("   - View API docs: http://localhost:8002/docs")
    print("   - Check logs: docker-compose -f docker-compose.data-services.yml logs -f")
    print("   - Read guide: cat DATA_SERVICES_GUIDE.md")
    print("")


if __name__ == "__main__":
    main()

