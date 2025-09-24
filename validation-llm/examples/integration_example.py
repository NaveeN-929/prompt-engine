"""
Integration Example - Demonstrates how to integrate the validation system
with the existing autonomous agent
"""

import asyncio
import json
import time
from typing import Dict, Any
import requests
from datetime import datetime

# Mock autonomous agent response for demonstration
SAMPLE_AUTONOMOUS_RESPONSE = {
    "request_id": "req_1703123456",
    "status": "success",
    "analysis": """=== SECTION 1: INSIGHTS ===

Based on the transaction analysis, several key patterns emerge:

• The account shows consistent monthly income of $3,500 from salary deposits
• Regular expenses include rent ($1,200), utilities ($150), and groceries ($400)
• Discretionary spending on dining and entertainment averages $300/month
• The account maintains a healthy balance with positive cash flow of $1,450/month
• No overdrafts or concerning spending patterns detected

=== SECTION 2: RECOMMENDATIONS ===

To optimize financial management, consider the following actions:

• Establish an emergency fund with 3-6 months of expenses ($4,500-$9,000)
• Set up automatic transfers to savings account (recommend $500/month)
• Review discretionary spending categories for potential optimization
• Consider investment opportunities for excess cash flow
• Implement budget tracking to monitor spending patterns more closely
• Evaluate insurance coverage to protect against financial risks""",
    "processing_time": 2.45,
    "rag_metadata": {
        "rag_enabled": True,
        "context_retrieved": 5,
        "similarity_scores": [0.89, 0.85, 0.82, 0.78, 0.75]
    },
    "input_summary": {
        "transaction_count": 15,
        "has_balance": True
    },
    "pipeline_used": "complete_rag_enhanced",
    "timestamp": "2024-01-15T10:30:45Z"
}

SAMPLE_INPUT_DATA = {
    "transactions": [
        {"date": "2024-01-01", "amount": 3500.00, "type": "credit", "description": "Salary deposit"},
        {"date": "2024-01-02", "amount": -1200.00, "type": "debit", "description": "Rent payment"},
        {"date": "2024-01-03", "amount": -150.00, "type": "debit", "description": "Utilities"},
        {"date": "2024-01-05", "amount": -85.50, "type": "debit", "description": "Grocery shopping"},
        {"date": "2024-01-07", "amount": -45.00, "type": "debit", "description": "Dining out"},
        {"date": "2024-01-10", "amount": -120.00, "type": "debit", "description": "Gas and transportation"},
        {"date": "2024-01-12", "amount": -75.25, "type": "debit", "description": "Online shopping"},
        {"date": "2024-01-15", "amount": 3500.00, "type": "credit", "description": "Salary deposit"},
        {"date": "2024-01-18", "amount": -200.00, "type": "debit", "description": "Entertainment"},
        {"date": "2024-01-20", "amount": -90.00, "type": "debit", "description": "Grocery shopping"},
        {"date": "2024-01-22", "amount": -60.00, "type": "debit", "description": "Dining out"},
        {"date": "2024-01-25", "amount": -35.00, "type": "debit", "description": "Coffee and snacks"},
        {"date": "2024-01-28", "amount": -150.00, "type": "debit", "description": "Utilities"},
        {"date": "2024-01-30", "amount": -100.00, "type": "debit", "description": "Miscellaneous"}
    ],
    "account_balance": 5280.25,
    "customer_id": "CUST_001",
    "analysis_period": "2024-01"
}

class ValidationIntegrationExample:
    """
    Example class demonstrating integration between autonomous agent and validation system
    """
    
    def __init__(self, 
                 autonomous_agent_url: str = "http://localhost:8000",
                 validation_system_url: str = "http://localhost:5002"):
        self.autonomous_agent_url = autonomous_agent_url
        self.validation_system_url = validation_system_url
        
        self.session = requests.Session()
        self.session.timeout = 30
    
    async def run_complete_pipeline_example(self):
        """Run a complete pipeline example with validation"""
        
        print("🚀 Running Complete Pipeline Example")
        print("=" * 50)
        
        # Step 1: Get response from autonomous agent
        print("📡 Step 1: Getting response from autonomous agent...")
        agent_response = await self.get_autonomous_agent_response(SAMPLE_INPUT_DATA)
        
        if agent_response["success"]:
            print(f"   ✅ Received response (processing time: {agent_response['data']['processing_time']:.2f}s)")
        else:
            print(f"   ❌ Failed to get response: {agent_response['error']}")
            return
        
        # Step 2: Validate the response
        print("\n🔍 Step 2: Validating response quality...")
        validation_result = await self.validate_response(
            response_data=agent_response["data"],
            input_data=SAMPLE_INPUT_DATA
        )
        
        if validation_result["success"]:
            result = validation_result["data"]
            print(f"   ✅ Validation completed:")
            print(f"   📊 Overall Score: {result['overall_score']:.3f}")
            print(f"   🏆 Quality Level: {result['quality_level']}")
            print(f"   ⏱️ Processing Time: {result['processing_time']:.3f}s")
            
            # Show criteria breakdown
            print(f"   📋 Criteria Scores:")
            for criterion, score in result['criteria_scores'].items():
                print(f"      • {criterion.replace('_', ' ').title()}: {score:.3f}")
        else:
            print(f"   ❌ Validation failed: {validation_result['error']}")
            return
        
        # Step 3: Check if response qualifies for training data
        print(f"\n💾 Step 3: Training data assessment...")
        if result['training_data_eligible']:
            print(f"   ✅ Response qualifies for training data storage")
            print(f"   🎯 Quality level: {result['quality_level']}")
        else:
            print(f"   ❌ Response does not qualify for training data")
            print(f"   📈 Needs improvement in: {', '.join(result.get('recommendations', [])[:3])}")
        
        # Step 4: Show feedback that would be sent
        print(f"\n📝 Step 4: Feedback summary...")
        if result['quality_level'] in ['exemplary', 'high_quality']:
            print(f"   🌟 Positive feedback: High-quality response")
            print(f"   💡 Strengths: Excellent structure, accurate analysis, actionable recommendations")
        else:
            print(f"   🔧 Improvement feedback:")
            for rec in result.get('recommendations', [])[:3]:
                print(f"      • {rec}")
        
        # Step 5: Retrieve similar high-quality examples
        print(f"\n📚 Step 5: Retrieving training patterns...")
        patterns = await self.get_training_patterns()
        
        if patterns["success"]:
            print(f"   ✅ Retrieved successful patterns:")
            pattern_data = patterns["data"]["patterns"]
            if "successful_insights" in pattern_data:
                for pattern in pattern_data["successful_insights"][:2]:
                    print(f"      • {pattern}")
        else:
            print(f"   ⚠️ Could not retrieve patterns: {patterns['error']}")
        
        print(f"\n🎉 Pipeline example completed successfully!")
        return result
    
    async def get_autonomous_agent_response(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get response from autonomous agent (or use sample for demo)"""
        
        try:
            # For demonstration, we'll use the sample response
            # In real integration, this would call the actual autonomous agent
            
            # Simulate API call delay
            await asyncio.sleep(0.1)
            
            return {
                "success": True,
                "data": SAMPLE_AUTONOMOUS_RESPONSE
            }
            
            # Real implementation would be:
            # response = self.session.post(
            #     f"{self.autonomous_agent_url}/analyze",
            #     json={"input_data": input_data}
            # )
            # 
            # if response.status_code == 200:
            #     return {"success": True, "data": response.json()}
            # else:
            #     return {"success": False, "error": f"HTTP {response.status_code}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def validate_response(self, 
                              response_data: Dict[str, Any], 
                              input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response using validation system"""
        
        try:
            validation_request = {
                "response_data": response_data,
                "input_data": input_data,
                "validation_config": {
                    "criteria": {
                        "content_accuracy": {"weight": 0.25, "threshold": 0.7},
                        "structural_compliance": {"weight": 0.20, "threshold": 0.8},
                        "logical_consistency": {"weight": 0.20, "threshold": 0.7},
                        "completeness": {"weight": 0.15, "threshold": 0.6},
                        "business_relevance": {"weight": 0.15, "threshold": 0.6},
                        "actionability": {"weight": 0.05, "threshold": 0.5}
                    }
                }
            }
            
            response = self.session.post(
                f"{self.validation_system_url}/validate/response",
                json=validation_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_training_patterns(self) -> Dict[str, Any]:
        """Get training patterns from validation system"""
        
        try:
            response = self.session.get(
                f"{self.validation_system_url}/training-data/patterns"
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def demonstrate_batch_validation(self):
        """Demonstrate batch validation capabilities"""
        
        print("\n🔄 Demonstrating Batch Validation")
        print("=" * 40)
        
        # Create multiple sample responses with varying quality
        batch_data = []
        
        # High-quality response
        high_quality_response = {
            "response_data": SAMPLE_AUTONOMOUS_RESPONSE,
            "input_data": SAMPLE_INPUT_DATA
        }
        batch_data.append(high_quality_response)
        
        # Medium-quality response (missing recommendations section)
        medium_quality_response = {
            "response_data": {
                **SAMPLE_AUTONOMOUS_RESPONSE,
                "analysis": """=== SECTION 1: INSIGHTS ===
                
                The account shows some transaction activity. There are various expenses and income.
                
                === SECTION 2: RECOMMENDATIONS ===
                
                Consider reviewing your finances."""
            },
            "input_data": SAMPLE_INPUT_DATA
        }
        batch_data.append(medium_quality_response)
        
        # Poor-quality response (no structure)
        poor_quality_response = {
            "response_data": {
                **SAMPLE_AUTONOMOUS_RESPONSE,
                "analysis": "The transactions look okay. You have money coming in and going out."
            },
            "input_data": SAMPLE_INPUT_DATA
        }
        batch_data.append(poor_quality_response)
        
        try:
            batch_request = {"batch_data": batch_data}
            
            response = self.session.post(
                f"{self.validation_system_url}/validate/batch",
                json=batch_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Batch validation completed:")
                print(f"📊 Total processed: {result['summary']['total_processed']}")
                print(f"🎯 Successful: {result['summary']['successful']}")
                print(f"❌ Failed: {result['summary']['failed']}")
                print(f"📈 Success rate: {result['summary']['success_rate']:.2%}")
                
                print(f"\n📋 Individual Results:")
                for i, validation_result in enumerate(result['batch_results'], 1):
                    print(f"   {i}. Score: {validation_result['overall_score']:.3f}, "
                          f"Quality: {validation_result['quality_level']}")
                
                return result
            else:
                print(f"❌ Batch validation failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Batch validation error: {e}")
            return None
    
    async def demonstrate_training_data_export(self):
        """Demonstrate training data export functionality"""
        
        print("\n💾 Demonstrating Training Data Export")
        print("=" * 40)
        
        try:
            export_request = {
                "format": "json",
                "quality_filter": "high_quality"
            }
            
            response = self.session.post(
                f"{self.validation_system_url}/training-data/export",
                json=export_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Export completed:")
                print(f"📁 Export path: {result['export_path']}")
                print(f"📄 Format: {result['format']}")
                print(f"🎯 Quality filter: {result['quality_filter']}")
                
                return result
            else:
                print(f"❌ Export failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Export error: {e}")
            return None

async def main():
    """Main demonstration function"""
    
    print("🎯 Response Validation LLM System - Integration Example")
    print("=" * 60)
    print()
    
    # Create integration example instance
    integration_example = ValidationIntegrationExample()
    
    try:
        # Run complete pipeline example
        await integration_example.run_complete_pipeline_example()
        
        # Demonstrate batch validation
        await integration_example.demonstrate_batch_validation()
        
        # Demonstrate training data export
        await integration_example.demonstrate_training_data_export()
        
        print("\n🎉 All integration examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Integration example failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
