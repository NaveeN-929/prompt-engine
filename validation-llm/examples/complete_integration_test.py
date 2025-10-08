#!/usr/bin/env python3
"""
Complete Integration Test
Tests the full blocking validation pipeline integration
"""

import asyncio
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any

# Test configuration
AUTONOMOUS_AGENT_URL = "http://localhost:5001"
VALIDATION_SYSTEM_URL = "http://localhost:5002"
PROMPT_ENGINE_URL = "http://localhost:5000"

# Sample test data
SAMPLE_INPUT_DATA = {
    "transactions": [
        {"date": "2024-01-15", "amount": 3500.00, "type": "credit", "description": "Salary deposit"},
        {"date": "2024-01-16", "amount": -1200.00, "type": "debit", "description": "Rent payment"},
        {"date": "2024-01-17", "amount": -150.00, "type": "debit", "description": "Utilities"},
        {"date": "2024-01-18", "amount": -400.00, "type": "debit", "description": "Groceries"},
        {"date": "2024-01-19", "amount": -75.00, "type": "debit", "description": "Dining out"},
        {"date": "2024-01-20", "amount": -50.00, "type": "debit", "description": "Gas"},
        {"date": "2024-01-21", "amount": -100.00, "type": "debit", "description": "Entertainment"},
        {"date": "2024-01-22", "amount": -25.00, "type": "debit", "description": "Coffee"}
    ],
    "account_balance": 1500.00,
    "analysis_period": "2024-01"
}

class IntegrationTester:
    """Complete integration testing suite"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 60  # Longer timeout for validation
        self.results = []
    
    def test_service_availability(self) -> Dict[str, Any]:
        """Test that all required services are available"""
        print("🔍 Testing service availability...")
        
        services = {
            "autonomous_agent": AUTONOMOUS_AGENT_URL,
            "validation_system": VALIDATION_SYSTEM_URL,
            "prompt_engine": PROMPT_ENGINE_URL
        }
        
        availability = {}
        
        for service_name, url in services.items():
            try:
                if service_name == "autonomous_agent":
                    response = self.session.get(f"{url}/status")
                elif service_name == "validation_system":
                    response = self.session.get(f"{url}/health")
                else:
                    response = self.session.get(f"{url}/system/status")
                
                if response.status_code == 200:
                    availability[service_name] = {
                        "status": "available",
                        "response_time": response.elapsed.total_seconds(),
                        "data": response.json()
                    }
                    print(f"   ✅ {service_name}: Available ({response.elapsed.total_seconds():.3f}s)")
                else:
                    availability[service_name] = {
                        "status": "error",
                        "http_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    }
                    print(f"   ❌ {service_name}: HTTP {response.status_code}")
                    
            except Exception as e:
                availability[service_name] = {
                    "status": "unavailable",
                    "error": str(e)
                }
                print(f"   ❌ {service_name}: {e}")
        
        return availability
    
    def test_blocking_validation_pipeline(self) -> Dict[str, Any]:
        """Test the complete blocking validation pipeline"""
        print("\n🚀 Testing blocking validation pipeline...")
        
        start_time = time.time()
        
        try:
            # Send request to autonomous agent (which should now include blocking validation)
            response = self.session.post(
                f"{AUTONOMOUS_AGENT_URL}/analyze",
                json={"input_data": SAMPLE_INPUT_DATA}
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Analyze the response structure
                analysis = self.analyze_response_structure(response_data)
                
                result = {
                    "status": "success",
                    "processing_time": processing_time,
                    "response_data": response_data,
                    "analysis": analysis,
                    "validation_included": "validation" in response_data,
                    "pipeline_used": response_data.get("pipeline_used", "unknown")
                }
                
                print(f"   ✅ Pipeline completed successfully ({processing_time:.3f}s)")
                print(f"   📊 Pipeline: {result['pipeline_used']}")
                print(f"   🔍 Validation included: {result['validation_included']}")
                
                if result['validation_included']:
                    validation_info = response_data["validation"]
                    print(f"   📈 Quality level: {validation_info.get('quality_level', 'unknown')}")
                    print(f"   🎯 Quality score: {validation_info.get('overall_score', 0.0):.3f}")
                    print(f"   ✅ Quality approved: {validation_info.get('quality_approved', False)}")
                
                return result
                
            else:
                error_data = None
                try:
                    error_data = response.json()
                except:
                    pass
                
                result = {
                    "status": "error",
                    "processing_time": processing_time,
                    "http_code": response.status_code,
                    "error_data": error_data,
                    "raw_response": response.text[:500]
                }
                
                print(f"   ❌ Pipeline failed: HTTP {response.status_code}")
                if error_data:
                    print(f"   📋 Error: {error_data.get('error', 'Unknown error')}")
                
                return result
                
        except Exception as e:
            result = {
                "status": "exception",
                "processing_time": time.time() - start_time,
                "error": str(e)
            }
            
            print(f"   ❌ Pipeline exception: {e}")
            return result
    
    def analyze_response_structure(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the structure and content of the response"""
        analysis = {
            "has_analysis": "analysis" in response_data,
            "has_validation": "validation" in response_data,
            "has_rag_metadata": "rag_metadata" in response_data,
            "structure_valid": False,
            "sections_found": []
        }
        
        # Check for two-section structure
        if analysis["has_analysis"]:
            analysis_text = response_data["analysis"]
            
            if "=== SECTION 1: INSIGHTS ===" in analysis_text:
                analysis["sections_found"].append("insights")
            
            if "=== SECTION 2: RECOMMENDATIONS ===" in analysis_text:
                analysis["sections_found"].append("recommendations")
            
            analysis["structure_valid"] = len(analysis["sections_found"]) == 2
        
        # Analyze validation information
        if analysis["has_validation"]:
            validation_data = response_data["validation"]
            analysis["validation_analysis"] = {
                "quality_level": validation_data.get("quality_level", "unknown"),
                "overall_score": validation_data.get("overall_score", 0.0),
                "quality_approved": validation_data.get("quality_approved", False),
                "validation_status": validation_data.get("validation_status", "unknown"),
                "has_quality_note": "quality_note" in validation_data
            }
        
        return analysis
    
    def test_validation_service_directly(self) -> Dict[str, Any]:
        """Test the validation service directly"""
        print("\n🔍 Testing validation service directly...")
        
        # Create a mock response for validation
        mock_response = {
            "request_id": "test_req_123",
            "status": "success",
            "analysis": """=== SECTION 1: INSIGHTS ===

Based on the transaction analysis, several key patterns emerge:

• The account shows consistent monthly income of $3,500 from salary deposits
• Regular expenses include rent ($1,200), utilities ($150), and groceries ($400)
• Discretionary spending on dining and entertainment averages $175/month
• The account maintains a healthy balance with positive cash flow

=== SECTION 2: RECOMMENDATIONS ===

To optimize financial management, consider the following actions:

• Establish an emergency fund with 3-6 months of expenses
• Set up automatic transfers to savings account
• Review discretionary spending categories for potential optimization
• Consider investment opportunities for excess cash flow""",
            "processing_time": 2.45,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            validation_request = {
                "response_data": mock_response,
                "input_data": SAMPLE_INPUT_DATA
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{VALIDATION_SYSTEM_URL}/validate/response",
                json=validation_request
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                validation_result = response.json()
                
                result = {
                    "status": "success",
                    "processing_time": processing_time,
                    "validation_result": validation_result,
                    "quality_level": validation_result.get("quality_level", "unknown"),
                    "overall_score": validation_result.get("overall_score", 0.0)
                }
                
                print(f"   ✅ Validation service working ({processing_time:.3f}s)")
                print(f"   📈 Quality level: {result['quality_level']}")
                print(f"   🎯 Overall score: {result['overall_score']:.3f}")
                
                return result
                
            else:
                result = {
                    "status": "error",
                    "processing_time": processing_time,
                    "http_code": response.status_code,
                    "error": response.text[:500]
                }
                
                print(f"   ❌ Validation service error: HTTP {response.status_code}")
                return result
                
        except Exception as e:
            result = {
                "status": "exception",
                "error": str(e)
            }
            
            print(f"   ❌ Validation service exception: {e}")
            return result
    
    def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run the complete integration test suite"""
        print("🧪 Starting Complete Integration Test Suite")
        print("=" * 60)
        
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_duration": 0.0,
            "tests": {}
        }
        
        suite_start_time = time.time()
        
        # Test 1: Service availability
        test_results["tests"]["service_availability"] = self.test_service_availability()
        
        # Test 2: Validation service directly
        test_results["tests"]["validation_service_direct"] = self.test_validation_service_directly()
        
        # Test 3: Complete blocking validation pipeline
        test_results["tests"]["blocking_validation_pipeline"] = self.test_blocking_validation_pipeline()
        
        test_results["test_duration"] = time.time() - suite_start_time
        
        # Generate summary
        summary = self.generate_test_summary(test_results)
        test_results["summary"] = summary
        
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Total duration: {test_results['test_duration']:.3f}s")
        
        if summary['blocking_validation_working']:
            print("\n✅ BLOCKING VALIDATION INTEGRATION: WORKING")
            print("   End users will only see validated responses!")
        else:
            print("\n❌ BLOCKING VALIDATION INTEGRATION: NOT WORKING")
            print("   Integration needs attention!")
        
        return test_results
    
    def generate_test_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of test results"""
        tests = test_results["tests"]
        
        total_tests = len(tests)
        passed_tests = 0
        failed_tests = 0
        
        service_availability_ok = True
        validation_service_ok = True
        blocking_validation_ok = True
        
        for test_name, result in tests.items():
            if isinstance(result, dict):
                if result.get("status") == "success":
                    passed_tests += 1
                else:
                    failed_tests += 1
                    
                if test_name == "service_availability":
                    service_availability_ok = all(
                        service.get("status") == "available" 
                        for service in result.values()
                        if isinstance(service, dict)
                    )
                elif test_name == "validation_service_direct":
                    validation_service_ok = result.get("status") == "success"
                elif test_name == "blocking_validation_pipeline":
                    blocking_validation_ok = (
                        result.get("status") == "success" and
                        result.get("validation_included", False)
                    )
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "service_availability_ok": service_availability_ok,
            "validation_service_ok": validation_service_ok,
            "blocking_validation_working": blocking_validation_ok
        }

def main():
    """Main test execution"""
    tester = IntegrationTester()
    results = tester.run_complete_test_suite()
    
    # Save results to file
    with open("integration_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: integration_test_results.json")
    
    # Return appropriate exit code
    if results["summary"]["blocking_validation_working"]:
        print("\n🎉 Integration test PASSED - Blocking validation is working!")
        return 0
    else:
        print("\n⚠️ Integration test FAILED - Issues detected!")
        return 1

if __name__ == "__main__":
    exit(main())
