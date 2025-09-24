#!/usr/bin/env python3
"""
Test Script - Validation Service Status Checking
Tests all the new validation service status endpoints and functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
AUTONOMOUS_AGENT_URL = "http://localhost:8000"

def test_validation_status_endpoints():
    """Test all validation service status endpoints"""
    
    print("🔍 VALIDATION SERVICE STATUS TESTING")
    print("=" * 50)
    print()
    
    endpoints_to_test = [
        {
            "name": "Main Status",
            "url": f"{AUTONOMOUS_AGENT_URL}/status",
            "method": "GET",
            "description": "Main system status with validation service info"
        },
        {
            "name": "Health Check",
            "url": f"{AUTONOMOUS_AGENT_URL}/health",
            "method": "GET", 
            "description": "Health check including validation capabilities"
        },
        {
            "name": "Validation Status",
            "url": f"{AUTONOMOUS_AGENT_URL}/validation/status",
            "method": "GET",
            "description": "Detailed validation service status"
        },
        {
            "name": "Validation Refresh",
            "url": f"{AUTONOMOUS_AGENT_URL}/validation/refresh",
            "method": "POST",
            "description": "Refresh validation service status"
        }
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        print(f"📡 Testing: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        print(f"   Description: {endpoint['description']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=10)
            else:
                response = requests.post(endpoint['url'], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results[endpoint['name']] = {
                    "status": "success",
                    "data": data,
                    "response_time": response.elapsed.total_seconds()
                }
                
                print(f"   ✅ Success ({response.elapsed.total_seconds():.3f}s)")
                
                # Extract key validation information
                if 'services' in data and 'validation_service' in data['services']:
                    validation_info = data['services']['validation_service']
                    if isinstance(validation_info, dict):
                        print(f"   🔧 Integration: {validation_info.get('integration', 'unknown')}")
                        print(f"   🔗 Connection: {validation_info.get('connection', 'unknown')}")
                        print(f"   💚 Health: {validation_info.get('health', 'unknown')}")
                        print(f"   🌐 URL: {validation_info.get('url', 'unknown')}")
                    else:
                        print(f"   🔧 Status: {validation_info}")
                
                # Extract capabilities if available
                if 'capabilities' in data:
                    capabilities = data['capabilities']
                    print(f"   🎯 Blocking Validation: {capabilities.get('blocking_validation', 'unknown')}")
                    print(f"   🚪 Quality Gates: {capabilities.get('quality_gates', 'unknown')}")
                
                # Extract validation-specific status
                if 'integration_initialized' in data:
                    print(f"   🔧 Integration: {data['integration_initialized']}")
                    print(f"   🔗 Connected: {data['service_connected']}")
                
            else:
                results[endpoint['name']] = {
                    "status": "error",
                    "http_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
                
                print(f"   ❌ Error: HTTP {response.status_code}")
                
                # Try to get error details
                try:
                    error_data = response.json()
                    print(f"   📋 Details: {error_data.get('error', 'No error details')}")
                except:
                    pass
        
        except requests.exceptions.Timeout:
            results[endpoint['name']] = {
                "status": "timeout",
                "error": "Request timed out"
            }
            print(f"   ⏰ Timeout")
        
        except Exception as e:
            results[endpoint['name']] = {
                "status": "exception",
                "error": str(e)
            }
            print(f"   ❌ Exception: {e}")
        
        print()
    
    return results

def analyze_validation_integration_status(results):
    """Analyze the results and provide integration status summary"""
    
    print("📊 VALIDATION INTEGRATION ANALYSIS")
    print("=" * 50)
    
    # Check main status
    main_status = results.get("Main Status", {})
    health_status = results.get("Health Check", {})
    validation_status = results.get("Validation Status", {})
    
    integration_working = True
    issues = []
    
    # Analyze main status
    if main_status.get("status") == "success":
        data = main_status["data"]
        services = data.get("services", {})
        validation_service = services.get("validation_service", {})
        
        if isinstance(validation_service, dict):
            integration = validation_service.get("integration")
            connection = validation_service.get("connection")
            health = validation_service.get("health")
            
            print(f"🔧 Integration Status: {integration}")
            print(f"🔗 Connection Status: {connection}")
            print(f"💚 Health Status: {health}")
            
            if integration != "active":
                integration_working = False
                issues.append("Validation integration not active")
            
            if connection != "connected":
                integration_working = False
                issues.append("Validation service not connected")
            
            if health not in ["healthy", "unknown"]:
                issues.append(f"Validation service health: {health}")
        else:
            print(f"🔧 Legacy Status: {validation_service}")
    else:
        integration_working = False
        issues.append("Main status endpoint failed")
    
    # Analyze health check
    if health_status.get("status") == "success":
        data = health_status["data"]
        mode = data.get("mode", "unknown")
        capabilities = data.get("capabilities", {})
        
        print(f"🏥 System Mode: {mode}")
        print(f"🎯 Blocking Validation: {capabilities.get('blocking_validation', 'unknown')}")
        print(f"🚪 Quality Gates: {capabilities.get('quality_gates', 'unknown')}")
        
        if not capabilities.get('blocking_validation', False):
            issues.append("Blocking validation not enabled")
    
    # Analyze detailed validation status
    if validation_status.get("status") == "success":
        data = validation_status["data"]
        status = data.get("status", "unknown")
        print(f"🔍 Detailed Status: {status}")
        
        if "integration_stats" in data:
            stats = data["integration_stats"]
            print(f"📈 Total Validations: {stats.get('validation_stats', {}).get('total_validations', 0)}")
    elif validation_status.get("http_code") == 503:
        issues.append("Validation service unavailable (expected if not running)")
    
    print()
    
    # Summary
    if integration_working and not issues:
        print("✅ VALIDATION INTEGRATION: FULLY OPERATIONAL")
        print("   All status endpoints working correctly")
        print("   Validation service properly integrated")
        print("   Blocking validation enabled")
    elif integration_working:
        print("⚠️ VALIDATION INTEGRATION: WORKING WITH ISSUES")
        print("   Integration is functional but has some issues:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("❌ VALIDATION INTEGRATION: NOT WORKING")
        print("   Critical issues detected:")
        for issue in issues:
            print(f"   - {issue}")
    
    return integration_working, issues

def test_validation_service_connectivity():
    """Test direct connectivity to validation service"""
    
    print("🌐 DIRECT VALIDATION SERVICE TEST")
    print("=" * 50)
    
    validation_url = "http://localhost:5002"
    
    endpoints = [
        {"path": "/health", "description": "Health check"},
        {"path": "/system/status", "description": "System status"},
        {"path": "/validation/stats", "description": "Validation statistics"}
    ]
    
    for endpoint in endpoints:
        url = f"{validation_url}{endpoint['path']}"
        print(f"📡 Testing: {endpoint['description']}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ Success ({response.elapsed.total_seconds():.3f}s)")
                
                try:
                    data = response.json()
                    if 'status' in data:
                        print(f"   📊 Status: {data['status']}")
                except:
                    print(f"   📄 Response length: {len(response.text)} chars")
            else:
                print(f"   ❌ HTTP {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection failed - service not running")
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

def main():
    """Main test execution"""
    
    print("🧪 VALIDATION SERVICE STATUS TEST SUITE")
    print("=" * 60)
    print()
    
    # Test 1: Status endpoints
    results = test_validation_status_endpoints()
    
    print()
    
    # Test 2: Analyze integration
    integration_working, issues = analyze_validation_integration_status(results)
    
    print()
    
    # Test 3: Direct service connectivity
    test_validation_service_connectivity()
    
    print()
    print("=" * 60)
    print("🏁 TEST COMPLETE")
    
    if integration_working:
        print("✅ Validation service status checking is working correctly!")
        return 0
    else:
        print("⚠️ Issues detected with validation service status checking")
        return 1

if __name__ == "__main__":
    exit(main())
