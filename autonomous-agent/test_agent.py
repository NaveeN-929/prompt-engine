#!/usr/bin/env python3
"""
Test script for the Autonomous Financial Analysis Agent
"""

import asyncio
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.autonomous_agent import AutonomousAgent

async def test_autonomous_agent():
    """Test the autonomous agent with sample data"""
    
    print("🧪 Testing Autonomous Financial Analysis Agent")
    print("=" * 50)
    
    # Sample financial data
    test_data = {
        "transactions": [
            {
                "date": "2024-01-15",
                "amount": 1500.00,
                "type": "credit",
                "description": "Salary deposit",
                "merchant": "EMPLOYER_CORP"
            },
            {
                "date": "2024-01-16", 
                "amount": -50.00,
                "type": "debit",
                "description": "Grocery shopping",
                "merchant": "GROCERY_STORE"
            },
            {
                "date": "2024-01-17",
                "amount": -1200.00,
                "type": "debit", 
                "description": "Rent payment",
                "merchant": "PROPERTY_MGMT"
            },
            {
                "date": "2024-01-18",
                "amount": -75.50,
                "type": "debit",
                "description": "Utilities bill",
                "merchant": "UTILITY_COMPANY"
            },
            {
                "date": "2024-01-20",
                "amount": 2000.00,
                "type": "credit",
                "description": "Freelance payment",
                "merchant": "CLIENT_ABC"
            }
        ],
        "account_balance": 2175.50,
        "customer_id": "CUST_001",
        "account_type": "checking",
        "account_opened": "2023-06-15"
    }
    
    try:
        # Initialize agent
        print("🤖 Initializing autonomous agent...")
        agent = AutonomousAgent()
        await agent.initialize()
        print("✅ Agent initialized successfully")
        
        # Test autonomous processing
        print("🔄 Processing autonomous analysis...")
        
        request_config = {
            "generation_type": "autonomous"
        }
        
        result = await agent.process_autonomous_request(test_data, request_config)
        
        # Display results
        print("📊 Analysis Results:")
        print("-" * 30)
        print(f"Status: {result['status']}")
        print(f"Processing Time: {result['processing_time']:.3f}s")
        print(f"Confidence Level: {result['confidence_score']['confidence_level']}")
        print(f"Overall Score: {result['confidence_score']['overall_score']:.3f}")
        print(f"Quality Passed: {result['reliability_indicators']['overall_quality_score']:.3f}")
        
        # Show analysis excerpt
        analysis = result['analysis']
        print(f"\\nAnalysis (first 500 chars):")
        print("-" * 30)
        print(analysis[:500] + "..." if len(analysis) > 500 else analysis)
        
        # Show confidence components
        print(f"\\nConfidence Components:")
        print("-" * 30)
        for component, score in result['confidence_score']['component_scores'].items():
            print(f"  {component}: {score:.3f}")
        
        # Show validation results
        print(f"\\nValidation Results:")
        print("-" * 30)
        validation = result['validation_result']
        print(f"  Validation Passed: {validation['passed']}")
        print(f"  Hallucination Detected: {validation['hallucination_result']['is_hallucinated']}")
        print(f"  Validation Score: {validation['validation_score']:.3f}")
        
        # Show agent status
        print(f"\\nAgent Status:")
        print("-" * 30)
        status = agent.get_agent_status()
        print(f"  Success Rate: {status['statistics']['success_rate']:.1%}")
        print(f"  Average Quality: {status['statistics']['average_quality_score']:.3f}")
        
        print("\\n✅ Test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_component_integration():
    """Test individual component integration"""
    
    print("\\n🔧 Testing Component Integration")
    print("=" * 50)
    
    from core.prompt_consumer import PromptConsumerService
    from core.confidence_engine import ConfidenceEngine
    from core.hallucination_detector import HallucinationDetector
    
    try:
        # Test prompt consumer
        print("🔌 Testing prompt consumer...")
        test_data = {"transactions": [{"amount": 100, "date": "2024-01-01"}]}
        
        async with PromptConsumerService() as consumer:
            # Test connectivity
            capabilities = await consumer.get_prompt_engine_capabilities()
            if "error" not in capabilities:
                print("✅ Prompt engine connectivity confirmed")
            else:
                print(f"⚠️ Prompt engine issue: {capabilities}")
        
        # Test confidence engine
        print("📊 Testing confidence engine...")
        confidence_engine = ConfidenceEngine()
        
        # Mock data for testing
        mock_response = "This is a test financial analysis based on the provided transaction data."
        mock_reasoning = {"steps": [], "overall_confidence": 0.8}
        mock_prompt = {"agentic_metadata": {"generation_mode": "test"}}
        
        confidence_result = await confidence_engine.calculate_confidence(
            mock_response, mock_reasoning, test_data, mock_prompt
        )
        print(f"✅ Confidence calculation: {confidence_result.overall_score:.3f}")
        
        # Test hallucination detector
        print("🛡️ Testing hallucination detector...")
        hallucination_detector = HallucinationDetector()
        
        hallucination_result = await hallucination_detector.detect_hallucinations(
            mock_response, test_data, mock_reasoning, mock_prompt
        )
        print(f"✅ Hallucination detection: {hallucination_result.hallucination_type}")
        
        print("\\n✅ All component tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Autonomous Agent Test Suite")
    print("=" * 60)
    
    # Run tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Test autonomous agent
        agent_test_passed = loop.run_until_complete(test_autonomous_agent())
        
        # Test component integration
        component_test_passed = loop.run_until_complete(test_component_integration())
        
        # Summary
        print("\\n" + "=" * 60)
        print("📋 Test Summary:")
        print(f"  Autonomous Agent: {'✅ PASSED' if agent_test_passed else '❌ FAILED'}")
        print(f"  Component Integration: {'✅ PASSED' if component_test_passed else '❌ FAILED'}")
        
        overall_success = agent_test_passed and component_test_passed
        print(f"  Overall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        
        return 0 if overall_success else 1
        
    except Exception as e:
        print(f"❌ Test suite error: {e}")
        return 1
    finally:
        loop.close()

if __name__ == "__main__":
    sys.exit(main())