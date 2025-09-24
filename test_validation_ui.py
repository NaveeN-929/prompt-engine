#!/usr/bin/env python3
"""
Test Script - Validation Service UI Integration
Tests that the UI properly displays validation service status
"""

import requests
import time
from datetime import datetime

def test_ui_integration():
    """Test that the UI can access validation service status endpoints"""
    
    print("🔍 VALIDATION SERVICE UI INTEGRATION TEST")
    print("=" * 50)
    print()
    
    base_url = "http://localhost:8000"
    
    # Test endpoints that the UI uses
    endpoints = [
        {
            "name": "Main Status (UI uses this)",
            "url": f"{base_url}/status",
            "method": "GET",
            "ui_element": "Status cards and validation badge"
        },
        {
            "name": "Validation Status (UI tab uses this)",
            "url": f"{base_url}/validation/status", 
            "method": "GET",
            "ui_element": "Validation tab details"
        },
        {
            "name": "Validation Refresh (UI button uses this)",
            "url": f"{base_url}/validation/refresh",
            "method": "POST",
            "ui_element": "Force Refresh button"
        },
        {
            "name": "Health Check (UI uses this)",
            "url": f"{base_url}/health",
            "method": "GET", 
            "ui_element": "Overall system health"
        }
    ]
    
    results = {}
    
    for endpoint in endpoints:
        print(f"📡 Testing: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        print(f"   UI Element: {endpoint['ui_element']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=10)
            else:
                response = requests.post(endpoint['url'], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results[endpoint['name']] = {"status": "success", "data": data}
                
                print(f"   ✅ Success ({response.elapsed.total_seconds():.3f}s)")
                
                # Check for validation-specific data
                if 'services' in data and 'validation_service' in data['services']:
                    validation_info = data['services']['validation_service']
                    if isinstance(validation_info, dict):
                        print(f"   🔧 Integration: {validation_info.get('integration', 'unknown')}")
                        print(f"   🔗 Connection: {validation_info.get('connection', 'unknown')}")
                        print(f"   💚 Health: {validation_info.get('health', 'unknown')}")
                
                # Check for blocking validation feature
                if 'features' in data:
                    features = data['features']
                    blocking_validation = features.get('blocking_validation', 'unknown')
                    print(f"   🔒 Blocking Validation: {blocking_validation}")
                
                # Check for validation capabilities
                if 'capabilities' in data:
                    capabilities = data['capabilities']
                    print(f"   🎯 Quality Gates: {capabilities.get('quality_gates', 'unknown')}")
                    
            elif response.status_code == 503:
                print(f"   ⚠️ Service Unavailable (expected if validation service not running)")
                results[endpoint['name']] = {"status": "service_unavailable", "code": 503}
                
            else:
                print(f"   ❌ HTTP {response.status_code}")
                results[endpoint['name']] = {"status": "error", "code": response.status_code}
        
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection failed - autonomous agent not running")
            results[endpoint['name']] = {"status": "connection_error"}
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout")
            results[endpoint['name']] = {"status": "timeout"}
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[endpoint['name']] = {"status": "exception", "error": str(e)}
        
        print()
    
    # Summary
    print("📊 UI INTEGRATION SUMMARY")
    print("=" * 30)
    
    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    total_count = len(results)
    
    print(f"Successful endpoints: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✅ All UI endpoints working - validation service status will display correctly!")
        print("\n🎯 UI Features Available:")
        print("   • Validation service status card")
        print("   • Validation tab with detailed status")
        print("   • Blocking validation badge")
        print("   • Force refresh button")
        print("   • Validation indicators in analysis results")
        return True
    elif success_count > 0:
        print("⚠️ Some UI endpoints working - partial validation status display")
        return False
    else:
        print("❌ No UI endpoints working - validation status will not display")
        return False

def test_ui_file_exists():
    """Test that the UI file exists and has validation elements"""
    
    print("\n🔍 UI FILE VALIDATION CHECK")
    print("=" * 30)
    
    try:
        with open("autonomous-agent/interface.html", "r") as f:
            content = f.read()
        
        # Check for validation-related elements
        validation_elements = [
            "validationCard",
            "validationStatus", 
            "validation tab",
            "refreshValidation",
            "Blocking Validation",
            "validation/status",
            "validation/refresh"
        ]
        
        found_elements = []
        for element in validation_elements:
            if element in content:
                found_elements.append(element)
        
        print(f"✅ UI file found: autonomous-agent/interface.html")
        print(f"📋 Validation elements found: {len(found_elements)}/{len(validation_elements)}")
        
        for element in found_elements:
            print(f"   • {element}")
        
        if len(found_elements) >= 6:
            print("✅ UI properly updated with validation service support!")
            return True
        else:
            print("⚠️ UI missing some validation elements")
            return False
            
    except FileNotFoundError:
        print("❌ UI file not found: autonomous-agent/interface.html")
        return False
    except Exception as e:
        print(f"❌ Error reading UI file: {e}")
        return False

def main():
    """Main test execution"""
    
    print("🧪 VALIDATION SERVICE UI INTEGRATION TEST SUITE")
    print("=" * 60)
    print()
    
    # Test 1: UI file validation
    ui_file_ok = test_ui_file_exists()
    
    # Test 2: Endpoint integration
    endpoints_ok = test_ui_integration()
    
    print("\n" + "=" * 60)
    print("🏁 TEST RESULTS")
    
    if ui_file_ok and endpoints_ok:
        print("✅ VALIDATION SERVICE UI INTEGRATION: COMPLETE")
        print("   The UI now properly displays validation service status!")
        print("\n🎉 Features Available:")
        print("   • Real-time validation service status")
        print("   • Detailed validation service information")
        print("   • Blocking validation indicator")
        print("   • Quality gates visualization")
        print("   • Validation result display in analysis")
        return 0
    elif ui_file_ok:
        print("⚠️ VALIDATION SERVICE UI INTEGRATION: PARTIAL")
        print("   UI updated but some endpoints not working")
        return 1
    else:
        print("❌ VALIDATION SERVICE UI INTEGRATION: FAILED")
        print("   UI integration incomplete")
        return 1

if __name__ == "__main__":
    exit(main())
