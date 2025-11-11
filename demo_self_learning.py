#!/usr/bin/env python3
"""
Self-Learning System Demonstration
Shows how the advanced self-learning system works in practice
"""

import asyncio
import json
from datetime import datetime

# Setup path
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.learning.integration_helper import setup_self_learning, get_self_learning


async def demo_complete_learning_cycle():
    """Demonstrate a complete learning cycle"""
    
    print("=" * 80)
    print("🧠 SELF-LEARNING SYSTEM DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Setup self-learning
    print("1️⃣ Setting up self-learning system...")
    setup_self_learning(qdrant_host="localhost", qdrant_port=6333)
    sl = get_self_learning()
    
    if not sl.is_ready():
        print("❌ Self-learning system not ready. Ensure Qdrant is running.")
        return
    
    print("✅ Self-learning system ready!\n")
    
    # Example interaction data
    input_data = {
        "transactions": [
            {"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary"},
            {"date": "2024-01-16", "amount": -50.00, "type": "debit", "description": "Groceries"},
            {"date": "2024-01-17", "amount": -1200.00, "type": "debit", "description": "Rent"}
        ],
        "account_balance": 2250.00,
        "customer_id": "CUST_001"
    }
    
    # Simulate prompt generation
    prompt_result = {
        "prompt": "Analyze the following financial transactions...",
        "metadata": {
            "template_used": "transaction_analysis",
            "context": "banking",
            "data_type": "transactions",
            "generation_mode": "agentic_enhanced",
            "vector_accelerated": True
        }
    }
    
    # Simulate analysis
    analysis_result = {
        "analysis": "The customer shows stable income with regular expenses...",
        "confidence_score": {
            "overall_score": 0.85,
            "confidence_level": "high"
        },
        "reasoning_chain": {
            "steps": [
                {"description": "Validated transaction data", "confidence": 0.9},
                {"description": "Analyzed spending patterns", "confidence": 0.85},
                {"description": "Generated insights", "confidence": 0.8}
            ],
            "overall_confidence": 0.85
        }
    }
    
    # Simulate validation
    validation_result = {
        "overall_score": 0.85,
        "quality_level": "high_quality",
        "criteria_scores": {
            "accuracy": 0.9,
            "completeness": 0.85,
            "clarity": 0.88,
            "relevance": 0.78
        },
        "recommendations": []
    }
    
    # Step 2: Predict quality before processing (simulation)
    print("2️⃣ Predicting interaction quality...")
    prediction = await sl.predict_interaction_quality(
        input_data=input_data,
        context="banking"
    )
    
    print(f"   Predicted quality: {prediction['predicted_quality']:.3f}")
    print(f"   Confidence: {prediction['confidence']}")
    print(f"   Explanation: {prediction['explanation']}")
    
    if prediction['recommendations']:
        print("   Recommendations:")
        for rec in prediction['recommendations'][:3]:
            print(f"   • {rec}")
    print()
    
    # Step 3: Find similar patterns
    print("3️⃣ Finding similar successful patterns...")
    similar_patterns = await sl.get_similar_successful_patterns(
        input_data=input_data,
        pattern_type="prompt",
        limit=3
    )
    
    print(f"   Found {len(similar_patterns)} similar patterns")
    for i, pattern in enumerate(similar_patterns[:3], 1):
        print(f"   Pattern {i}: Score {pattern['similarity_score']:.3f} - {pattern['recommendation']}")
    print()
    
    # Step 4: Process complete learning cycle
    print("4️⃣ Processing complete learning cycle...")
    learning_result = await sl.learn_from_interaction(
        input_data=input_data,
        prompt_result=prompt_result,
        analysis_result=analysis_result,
        validation_result=validation_result,
        metadata={"source": "demo", "timestamp": datetime.now().isoformat()}
    )
    
    print(f"   Status: {learning_result['status']}")
    print(f"   Quality score: {learning_result.get('quality_score', 0):.3f}")
    print(f"   Successful: {learning_result.get('is_successful', False)}")
    print()
    
    # Step 5: Get learning metrics
    print("5️⃣ Current learning metrics...")
    metrics = sl.get_learning_metrics()
    
    print(f"   Total interactions: {metrics['total_interactions']}")
    print(f"   Success rate: {metrics['success_rate']:.1%}")
    print(f"   Patterns stored: {metrics['patterns_stored']}")
    print(f"   Pattern types:")
    for ptype, count in metrics['pattern_types'].items():
        print(f"      {ptype}: {count}")
    print()
    
    # Step 6: Learning insights
    print("6️⃣ Learning insights...")
    insights = sl.get_learning_insights()
    
    print(f"   Total insights: {len(insights['insights'])}")
    for insight in insights['insights'][:5]:
        level_emoji = "✅" if insight['level'] == 'positive' else "⚠️"
        print(f"   {level_emoji} [{insight['type']}] {insight['message']}")
    print()
    
    # Step 7: Performance trends
    print("7️⃣ Performance trends...")
    trend = metrics['performance_trend']
    
    trend_emoji = "📈" if trend['quality_improvement'] > 0 else "📉" if trend['quality_improvement'] < 0 else "➡️"
    print(f"   Quality trend: {trend_emoji} {trend['quality_improvement']:+.1%}")
    print(f"   Recent quality: {trend['recent_quality']:.3f}")
    print(f"   Overall quality: {trend['overall_quality']:.3f}")
    print()
    
    # Step 8: Knowledge graph stats
    print("8️⃣ Knowledge graph statistics...")
    if sl.knowledge_graph:
        kg_stats = sl.knowledge_graph.get_knowledge_stats()
        if kg_stats.get('status') == 'active':
            print(f"   Status: {kg_stats['status']}")
            print(f"   Total knowledge points: {kg_stats['total_knowledge_points']}")
            print(f"   Collections:")
            for name, stats in kg_stats['collections'].items():
                print(f"      {name}: {stats['points_count']} points")
            print(f"   Retrieval success rate: {kg_stats['retrieval_success_rate']:.1%}")
        else:
            print(f"   Status: {kg_stats.get('status', 'unknown')}")
    print()
    
    # Step 9: Top patterns
    print("9️⃣ Top performing patterns...")
    top_patterns = metrics.get('top_patterns', [])
    
    if top_patterns:
        for i, pattern in enumerate(top_patterns[:5], 1):
            print(f"   {i}. {pattern['pattern_type']}: Score {pattern['overall_score']:.3f} "
                  f"(used {pattern['use_count']} times, {pattern['success_rate']:.1%} success)")
    else:
        print("   No patterns yet - system is learning!")
    print()
    
    # Step 10: Adaptive thresholds
    print("🔟 Adaptive thresholds...")
    thresholds = metrics.get('adaptive_thresholds', {})
    
    for threshold_name, value in thresholds.items():
        print(f"   {threshold_name}: {value:.3f}")
    print()
    
    print("=" * 80)
    print("✨ DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("The self-learning system is now continuously improving!")
    print("Each interaction makes it smarter, faster, and more accurate.")
    print()


async def demo_predictive_features():
    """Demonstrate predictive features"""
    
    print("\n" + "=" * 80)
    print("🔮 PREDICTIVE FEATURES DEMONSTRATION")
    print("=" * 80)
    print()
    
    sl = get_self_learning()
    
    if not sl.is_ready():
        print("❌ Self-learning not ready")
        return
    
    # Test data variations
    test_cases = [
        {
            "name": "Simple transaction",
            "data": {
                "transactions": [
                    {"date": "2024-01-15", "amount": 100.00, "type": "credit"}
                ]
            }
        },
        {
            "name": "Complex financial analysis",
            "data": {
                "transactions": [
                    {"date": "2024-01-15", "amount": 1500.00, "type": "credit"},
                    {"date": "2024-01-16", "amount": -50.00, "type": "debit"},
                    {"date": "2024-01-17", "amount": -1200.00, "type": "debit"}
                ],
                "monthly_data": [
                    {"month": "2024-01", "revenue": 5000, "expenses": 3000}
                ],
                "credit_score": 750,
                "debt_ratio": 0.35
            }
        }
    ]
    
    for case in test_cases:
        print(f"📊 Test case: {case['name']}")
        
        prediction = await sl.predict_interaction_quality(
            input_data=case['data'],
            context="banking"
        )
        
        print(f"   Predicted quality: {prediction['predicted_quality']:.3f}")
        print(f"   Confidence: {prediction['confidence']} (score: {prediction.get('confidence_score', 0):.3f})")
        print(f"   Similar patterns: {prediction.get('similar_patterns_found', 0)}")
        print(f"   Explanation: {prediction['explanation']}")
        
        if prediction.get('quality_range'):
            qr = prediction['quality_range']
            print(f"   Quality range: {qr['min']:.3f} - {qr['max']:.3f} (avg: {qr['mean']:.3f})")
        
        print()


async def demo_analytics_report():
    """Demonstrate analytics report generation"""
    
    print("\n" + "=" * 80)
    print("📊 LEARNING ANALYTICS REPORT")
    print("=" * 80)
    print()
    
    sl = get_self_learning()
    
    if not sl.is_ready():
        print("❌ Self-learning not ready")
        return
    
    report = sl.generate_learning_report()
    
    print(f"Report ID: {report['report_id']}")
    print(f"Generated: {report['generated_at']}")
    print()
    
    # Summary
    summary = report['summary']
    print(f"Overall Status: {summary['overall_status'].upper()}")
    print(f"Status Message: {summary['status_message']}")
    print()
    
    # Key metrics
    print("Key Metrics:")
    print(f"  Total interactions: {summary['total_interactions']}")
    print(f"  Success rate: {summary['success_rate']:.1%}")
    print(f"  Patterns learned: {summary['patterns_learned']}")
    print(f"  Current quality: {summary['current_quality']:.3f}")
    print(f"  Quality trend: {summary['quality_trend']}")
    print(f"  Milestones: {summary['milestones_achieved']}")
    print()
    
    # Recommendations
    if report.get('improvement_recommendations'):
        print("Improvement Recommendations:")
        for rec in report['improvement_recommendations'][:5]:
            priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
            print(f"  {priority_emoji} [{rec['category']}] {rec['recommendation']}")
        print()
    
    print("=" * 80)


async def main():
    """Run all demonstrations"""
    
    try:
        # Main learning cycle demo
        await demo_complete_learning_cycle()
        
        # Predictive features demo
        await demo_predictive_features()
        
        # Analytics report demo
        await demo_analytics_report()
        
        print("\n🎉 All demonstrations completed successfully!")
        print()
        print("Next steps:")
        print("  1. Start using the system with real interactions")
        print("  2. Monitor learning metrics via API: GET /self-learning/metrics")
        print("  3. Review analytics dashboard: GET /self-learning/analytics/dashboard")
        print("  4. Generate periodic reports: GET /self-learning/report")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

