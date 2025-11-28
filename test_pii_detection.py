#!/usr/bin/env python3
"""
Test PII Detection and Pseudonymization
Demonstrates the enhanced features with 20+ PII types
"""

import requests
import json
from datetime import datetime

# Service URLs
PSEUDO_URL = "http://localhost:5003"
REPERSONAL_URL = "http://localhost:5004"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_pii_detection():
    """Test comprehensive PII detection"""
    print_section("🔒 Testing PII Detection & Pseudonymization")
    
    # Sample data with various PII types
    test_data = {
        "customer_id": "CUST_12345",
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "555-123-4567",
        "transactions": [
            {
                "date": "2025-10-16",
                "amount": 5000.00,
                "type": "credit",
                "description": "Monthly salary deposit"
            },
            {
                "date": "2025-10-18",
                "amount": -150.00,
                "type": "debit",
                "description": "Grocery shopping at Whole Foods"
            },
            {
                "date": "2025-10-20",
                "amount": -2500.00,
                "type": "debit",
                "description": "Rent payment"
            }
        ],
        "account_info": {
            "account_number": "1234-5678-9012",
            "routing_number": "021000021",
            "bank_name": "Example Bank",
            "account_type": "checking"
        },
        "account_balance": 15350.00,
        "timestamp": "2025-10-16T10:30:00Z"
    }
    
    print("\n📊 Original Data:")
    print(f"   Customer ID: {test_data['customer_id']}")
    print(f"   Name: {test_data['name']}")
    print(f"   Email: {test_data['email']}")
    print(f"   Phone: {test_data.get('phone', 'N/A')}")
    print(f"   Account Balance: ${test_data['account_balance']:,.2f}")
    print(f"   Transactions: {len(test_data['transactions'])}")
    
    # Pseudonymize
    print("\n🔒 Pseudonymizing with PII detection...")
    response = requests.post(
        f"{PSEUDO_URL}/pseudonymize",
        json=test_data
    )
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.text}")
        return None
    
    result = response.json()
    
    print("\n✅ Pseudonymization Complete!")
    print(f"\n📋 PII Detection Summary:")
    print(f"   Total PII Fields Detected: {result['pii_summary']['total_pii_fields']}")
    print(f"   High Confidence Detections: {result['pii_summary']['high_confidence_count']}")
    print(f"   Fields Affected: {len(result['pii_summary']['fields_affected'])}")
    
    print(f"\n🔍 PII Types Found:")
    for pii_type, count in result['pii_summary']['pii_types_found'].items():
        print(f"   - {pii_type}: {count} occurrence(s)")
    
    print(f"\n🔐 Pseudonymization Results:")
    print(f"   Pseudonym ID: {result['pseudonym_id']}")
    print(f"   Processing Time: {result['processing_time_ms']:.2f}ms")
    print(f"   Total Fields Pseudonymized: {len(result['fields_pseudonymized'])}")
    
    print(f"\n📝 PII Detections:")
    for detection in result['pii_detected'][:5]:  # Show first 5
        print(f"   - Field: {detection['field']}")
        print(f"     Type: {detection['type']}")
        print(f"     Original: {detection['original_preview']}")
        print(f"     Pseudonymized: {detection['pseudonymized']}")
        print()
    
    print("\n🔐 Pseudonymized Data Sample:")
    pseudo_data = result['pseudonymized_data']
    print(f"   Customer ID: {pseudo_data.get('customer_id', 'N/A')}")
    print(f"   Name: {pseudo_data.get('name', 'N/A')}")
    print(f"   Email: {pseudo_data.get('email', 'N/A')}")
    if 'phone' in pseudo_data:
        print(f"   Phone: {pseudo_data.get('phone', 'N/A')}")
    
    return result['pseudonym_id'], test_data


def test_repersonalization(pseudonym_id, original_data):
    """Test data repersonalization"""
    print_section("🔓 Testing Repersonalization")
    
    print(f"\n🔍 Restoring data for pseudonym: {pseudonym_id}")
    
    response = requests.post(
        f"{REPERSONAL_URL}/repersonalize",
        json={
            "pseudonym_id": pseudonym_id,
            "verify": True
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.text}")
        return
    
    result = response.json()
    restored_data = result['original_data']
    
    print("\n✅ Repersonalization Complete!")
    print(f"   Processing Time: {result['processing_time_ms']:.2f}ms")
    print(f"   Verified: {result['verified']}")
    
    print("\n📊 Restored Data:")
    print(f"   Customer ID: {restored_data['customer_id']}")
    print(f"   Name: {restored_data['name']}")
    print(f"   Email: {restored_data['email']}")
    
    # Verify integrity
    print("\n🔍 Data Integrity Check:")
    if restored_data == original_data:
        print("   ✅ Perfect match - Data integrity verified!")
    else:
        print("   ⚠️  Data mismatch detected")
        # Show differences
        for key in original_data:
            if original_data[key] != restored_data.get(key):
                print(f"      Mismatch in '{key}':")
                print(f"        Original: {original_data[key]}")
                print(f"        Restored: {restored_data.get(key)}")


def test_pii_types_table():
    """Display PII types detection table"""
    print_section("📋 PII Types Supported")
    
    pii_examples = [
        ("Name", "John Doe", "USER_A7B3C9", "Personal Identifier"),
        ("Email", "john@email.com", "EMAIL_X4Y2Z8@anon.email.com", "Contact Information"),
        ("Phone", "555-123-4567", "PHONE_N3P7Q1", "Contact Information"),
        ("SSN", "123-45-6789", "SSN_K5M8P2Q9R", "Personal Identifier"),
        ("Account", "1234-5678-9012", "ACCT_K9L2M5N8P3", "Financial Data"),
        ("Credit Card", "4532-1234-5678-9010", "CARD_T7U9V2W5X8Y1", "Financial Data"),
        ("Address", "123 Main St", "ADDR_F3G6H9J2K5", "Contact Information"),
        ("IP Address", "192.168.1.1", "IP_M4N7P1Q8", "Technical Data"),
    ]
    
    print("\n| Type | Original | Pseudonymised | Category |")
    print("|------|----------|---------------|----------|")
    
    for pii_type, original, pseudo, category in pii_examples:
        print(f"| {pii_type:<12} | {original:<20} | {pseudo:<25} | {category} |")


def check_services():
    """Check if services are running"""
    print_section("🏥 Checking Service Health")
    
    try:
        pseudo_health = requests.get(f"{PSEUDO_URL}/health", timeout=5)
        if pseudo_health.status_code == 200:
            print("✅ Pseudonymization Service: Healthy (Port 5003)")
        else:
            print("❌ Pseudonymization Service: Unhealthy")
            return False
        
        repersonal_health = requests.get(f"{REPERSONAL_URL}/health", timeout=5)
        if repersonal_health.status_code == 200:
            print("✅ Repersonalization Service: Healthy (Port 5004)")
        else:
            print("❌ Repersonalization Service: Unhealthy")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Cannot connect to services: {str(e)}")
        print("\n💡 Start services with:")
        print("   ./start_data_services.sh")
        return False


def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("  🔐 PII Detection & Pseudonymization Test Suite")
    print("  Enhanced with 20+ PII Types")
    print("=" * 70)
    
    # Check services
    if not check_services():
        return
    
    # Show PII types table
    test_pii_types_table()
    
    # Test PII detection and pseudonymization
    result = test_pii_detection()
    if result:
        pseudonym_id, original_data = result
        
        # Test repersonalization
        test_repersonalization(pseudonym_id, original_data)
    
    print_section("✅ Tests Complete!")
    print("\n📚 Next Steps:")
    print("   - View API docs: http://localhost:5003/docs")
    print("   - View API docs: http://localhost:5004/docs")
    print("   - Check comprehensive guide: DATA_SERVICES_GUIDE.md")
    print("")


if __name__ == "__main__":
    main()

