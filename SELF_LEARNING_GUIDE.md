# 🧠 Advanced Self-Learning System Guide

## Overview

The **Advanced Self-Learning System** is a sophisticated multi-dimensional learning framework that enables your LLMs to continuously improve through interaction patterns, quality feedback, and cross-component knowledge sharing.

---

## 🌟 Key Features

### 1. **Multi-Dimensional Knowledge Graph**
- Stores knowledge across multiple dimensions: prompts, analyses, validations, reasoning patterns
- Links related knowledge together for contextual learning
- Uses Qdrant vector database for ultra-fast similarity matching

### 2. **Reinforcement Learning**
- Patterns get weighted by success rates over time
- Higher quality outcomes increase pattern weights
- Temporal decay ensures knowledge stays fresh

### 3. **Cross-Component Learning Bridge**
- **Prompt Engine** → **Autonomous Agent**: Shares successful prompt patterns
- **Autonomous Agent** → **Validator**: Shares analysis patterns and quality indicators  
- **Validator** → **Prompt Engine**: Completes the feedback loop with validation insights

### 4. **Adaptive Intelligence**
- Dynamic threshold adjustment based on performance trends
- Automatic quality gate calibration
- Context-aware pattern matching

### 5. **Predictive Quality Scoring**
- Predicts interaction quality **before** execution
- Provides confidence levels and recommendations
- Helps optimize resource allocation

### 6. **Learning Analytics**
- Comprehensive performance tracking
- Trend analysis and milestone detection
- Improvement recommendations

---

## 🚀 Getting Started

### Installation

The self-learning system is already integrated into the prompt engine. Simply ensure Qdrant is running:

```bash
# Start Qdrant (if not already running)
docker-compose up -d qdrant

# Verify Qdrant is accessible
curl http://localhost:6333/collections
```

### Initialization

The system auto-initializes when the server starts. To manually initialize:

```python
from app.learning.integration_helper import setup_self_learning

# Setup with default Qdrant connection
setup_self_learning(
    qdrant_host="localhost",
    qdrant_port=6333
)
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│           SELF-LEARNING MANAGER (Core)                  │
│  • Pattern Storage & Reinforcement Learning             │
│  • Adaptive Thresholds & Temporal Decay                 │
│  • Quality Prediction & Pattern Matching                │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────────┐  ┌──────────────────────┐
│  KNOWLEDGE  │  │  CROSS-COMPONENT     │
│    GRAPH    │  │      BRIDGE          │
│             │  │                      │
│ • Prompts   │  │ • Prompt→Agent       │
│ • Analyses  │  │ • Agent→Validator    │
│ • Validation│  │ • Validator→Prompt   │
│ • Reasoning │  │ • Complete Cycles    │
└─────────────┘  └──────────────────────┘
       │                    │
       └──────────┬─────────┘
                  ▼
         ┌─────────────────┐
         │    LEARNING     │
         │    ANALYTICS    │
         │                 │
         │ • Metrics       │
         │ • Trends        │
         │ • Reports       │
         └─────────────────┘
```

---

## 💡 Usage Examples

### 1. Learn from Complete Interaction

```python
from app.learning.integration_helper import get_self_learning

sl = get_self_learning()

# After processing a complete interaction
result = await sl.learn_from_interaction(
    input_data={"transactions": [...]},
    prompt_result={"prompt": "...", "metadata": {...}},
    analysis_result={"analysis": "...", "confidence_score": {...}},
    validation_result={"overall_score": 0.85, "quality_level": "high_quality"},
    metadata={"context": "banking", "data_type": "transactions"}
)

print(f"Learning result: {result['status']}")
print(f"Patterns created: {result['patterns_created']}")
```

### 2. Predict Quality Before Execution

```python
# Before generating analysis
prediction = await sl.predict_interaction_quality(
    input_data={"transactions": [...]},
    context="banking"
)

print(f"Predicted quality: {prediction['predicted_quality']:.2f}")
print(f"Confidence: {prediction['confidence']}")
print(f"Recommendations: {prediction['recommendations']}")
```

### 3. Find Similar Successful Patterns

```python
# Find patterns similar to current input
patterns = await sl.get_similar_successful_patterns(
    input_data={"transactions": [...]},
    pattern_type="prompt",  # or "analysis", "validation"
    limit=5
)

for pattern in patterns:
    print(f"Pattern: {pattern['pattern']['pattern_id']}")
    print(f"Score: {pattern['similarity_score']:.3f}")
    print(f"Recommendation: {pattern['recommendation']}")
```

### 4. Get Learning Metrics

```python
metrics = sl.get_learning_metrics()

print(f"Total interactions: {metrics['total_interactions']}")
print(f"Success rate: {metrics['success_rate']:.1%}")
print(f"Patterns stored: {metrics['patterns_stored']}")
print(f"Quality trend: {metrics['performance_trend']['quality_improvement']:.1%}")
```

### 5. Generate Learning Report

```python
report = sl.generate_learning_report()

print(f"Report ID: {report['report_id']}")
print(f"Overall status: {report['summary']['overall_status']}")
print(f"Quality trend: {report['trend_analysis']['trend']}")
print(f"Milestones: {report['milestones_achieved']}")

for rec in report['improvement_recommendations']:
    print(f"• {rec['recommendation']}")
```

---

## 🔌 API Endpoints

### System Status
```bash
GET /self-learning/status
```

### Learning Metrics
```bash
GET /self-learning/metrics
```

### Learning Insights
```bash
GET /self-learning/insights
```

### Generate Report
```bash
GET /self-learning/report
```

### Analytics Dashboard
```bash
GET /self-learning/analytics/dashboard
```

### Predict Quality
```bash
POST /self-learning/predict-quality
Content-Type: application/json

{
  "input_data": {"transactions": [...]},
  "context": "banking"
}
```

### Find Similar Patterns
```bash
POST /self-learning/similar-patterns
Content-Type: application/json

{
  "input_data": {"transactions": [...]},
  "pattern_type": "prompt",
  "limit": 5
}
```

### Knowledge Graph Stats
```bash
GET /self-learning/knowledge-graph/stats
```

### Cross-Component Stats
```bash
GET /self-learning/cross-component/stats
```

---

## 📈 Learning Metrics Explained

### **Total Interactions**
Number of complete learning cycles processed

### **Success Rate**
Percentage of interactions that met quality thresholds

### **Patterns Stored**
Total number of learned patterns in the knowledge graph

### **Pattern Types Distribution**
- **Prompt patterns**: Successful prompt generation patterns
- **Analysis patterns**: Effective analysis approaches
- **Validation patterns**: Quality validation insights

### **Knowledge Graph Edges**
Number of links between related patterns (indicates knowledge interconnectedness)

### **Domain Expertise**
Performance metrics by domain (banking, lending, risk assessment, etc.)

### **Adaptive Thresholds**
Current dynamic thresholds:
- `quality_gate`: Minimum quality for successful interaction
- `similarity_match`: Threshold for pattern matching
- `reinforcement_cutoff`: Minimum score for pattern use

### **Performance Trend**
- **Recent quality**: Average quality of last 10 interactions
- **Overall quality**: Historical average quality
- **Quality improvement**: Change in quality over time

---

## 🎯 How It Works

### Learning Pattern Lifecycle

1. **Interaction Occurs**
   - User submits data → Prompt generated → Analysis performed → Validation executed

2. **Pattern Creation**
   - Each component creates learning patterns
   - Patterns include: input data, results, quality scores, context tags

3. **Pattern Linking**
   - Patterns are linked together in knowledge graph
   - Creates multi-dimensional knowledge representation

4. **Vector Storage**
   - Patterns stored as embeddings in Qdrant
   - Enables ultra-fast similarity matching

5. **Reinforcement Learning**
   - Patterns updated with success/failure outcomes
   - Reinforcement scores calculated based on:
     - Success rate (40%)
     - Average quality (30%)
     - Recency (20%)
     - Confidence (10%)

6. **Temporal Decay**
   - Old patterns gradually lose weight
   - Ensures knowledge stays fresh and relevant

7. **Adaptive Adjustment**
   - Thresholds dynamically adjusted based on performance
   - System becomes more stringent as it improves

### Cross-Component Learning Flow

```
Input Data
    │
    ▼
┌───────────────┐
│ Prompt Engine │ → Generates prompt using patterns
└───────┬───────┘
        │ Shares prompt insights
        ▼
┌──────────────────┐
│ Autonomous Agent │ → Analyzes using reasoning patterns
└────────┬─────────┘
         │ Shares analysis insights
         ▼
┌─────────────────┐
│    Validator    │ → Validates quality
└────────┬────────┘
         │ Shares validation feedback
         ▼
┌───────────────┐
│ Prompt Engine │ ← Completes feedback loop
└───────────────┘
```

---

## 🛠️ Configuration

### Adaptive Thresholds

Configure starting thresholds in `self_learning_manager.py`:

```python
self.adaptive_thresholds = {
    'quality_gate': 0.7,        # Minimum quality for success
    'similarity_match': 0.8,    # Similarity threshold for matching
    'reinforcement_cutoff': 0.6 # Minimum score for pattern use
}
```

### Temporal Decay

Configure decay rate in `LearningPattern._calculate_recency_factor()`:

```python
# Half-life of 7 days (168 hours)
decay_rate = 0.693 / 168
```

### Trend Window

Configure analysis window in `learning_analytics.py`:

```python
self.trend_window = 50  # Number of interactions to analyze
```

---

## 📊 Learning Analytics Dashboard

### Performance Metrics
- Current learning statistics
- Quality trend direction and slope
- Learning velocity (patterns per hour)

### Quality Analytics
- Quality score distribution
- Percentile analysis (p25, p50, p75, p90)
- Quality timeline visualization

### Learning Progress
- Milestones achieved
- Pattern growth rate
- Success rate trends

### Recommendations
- Automated improvement suggestions
- Priority-based action items
- Performance bottleneck identification

---

## 🎓 Best Practices

### 1. **Consistent Quality Feedback**
Always provide quality scores when learning from interactions:

```python
await sl.learn_from_interaction(
    ...,
    validation_result={"overall_score": 0.85}  # Always include!
)
```

### 2. **Rich Metadata**
Include comprehensive metadata for better pattern matching:

```python
metadata = {
    "context": "banking",
    "data_type": "transactions",
    "complexity": "moderate",
    "domain": "lending"
}
```

### 3. **Regular Monitoring**
Check learning metrics regularly:

```python
metrics = sl.get_learning_metrics()
if metrics['success_rate'] < 0.7:
    # Review and refine patterns
    report = sl.generate_learning_report()
```

### 4. **Leverage Predictions**
Use quality predictions to optimize resource allocation:

```python
prediction = await sl.predict_interaction_quality(input_data)
if prediction['predicted_quality'] < 0.6:
    # Use more thorough analysis approach
    # Or provide additional context
```

### 5. **Pattern Diversity**
Ensure diverse interaction types for robust learning:
- Different data complexities
- Various domains and contexts
- Multiple data types

---

## 🔍 Troubleshooting

### Self-Learning Not Initialized
**Symptom**: API returns "Self-learning not initialized"

**Solution**:
```python
from app.learning.integration_helper import setup_self_learning
setup_self_learning()
```

### Low Similarity Match Rate
**Symptom**: Few patterns found in searches

**Solutions**:
- Lower `similarity_match` threshold
- Ensure consistent metadata structure
- Add more diverse training interactions

### Quality Declining
**Symptom**: Quality trend shows "declining"

**Solutions**:
- Review recent patterns: `sl.get_learning_metrics()['top_patterns']`
- Generate report: `sl.generate_learning_report()`
- Check adaptive thresholds: may be too aggressive

### Knowledge Graph Empty
**Symptom**: `patterns_stored: 0`

**Solutions**:
- Verify Qdrant is running: `curl http://localhost:6333/collections`
- Check Qdrant connection in logs
- Ensure `learn_from_interaction()` is called with quality scores

---

## 📚 Advanced Topics

### Custom Pattern Weighting

Override reinforcement scoring by modifying `LearningPattern._update_reinforcement()`:

```python
# Example: Emphasize recent patterns more
self.reinforcement_score = (
    success_rate * 0.3 +      # Reduced from 0.4
    avg_quality * 0.3 + 
    recency_factor * 0.3 +    # Increased from 0.2
    confidence_factor * 0.1
)
```

### Domain-Specific Learning

Track domain expertise:

```python
metrics = sl.get_learning_metrics()
banking_expertise = metrics['domain_expertise'].get('banking', {})

if banking_expertise['avg_quality'] > 0.85:
    print("Expert level in banking domain!")
```

### Learning Milestones

Custom milestones can be added in `learning_analytics.py`:

```python
# Example: Custom milestone
if metrics['patterns_stored'] >= 500 and metrics['success_rate'] > 0.9:
    self._record_milestone('expert_status', 'Achieved expert status!')
```

---

## 🎯 Performance Optimization

### Vector Database Tuning
- Adjust `score_threshold` in similarity searches
- Optimize embedding model choice
- Scale Qdrant cluster for high throughput

### Memory Management
- Patterns are automatically pruned with temporal decay
- History limited to recent 1000 interactions
- Cache limited to 100 optimizations

### Async Operations
All learning operations are async for non-blocking performance:

```python
# Non-blocking learning
asyncio.create_task(sl.learn_from_interaction(...))
```

---

## 📞 Support

For issues or questions:
1. Check logs for error messages
2. Verify Qdrant connectivity
3. Review learning metrics and reports
4. Generate comprehensive learning report for diagnostics

---

**🎉 The self-learning system will continuously improve your LLM's performance over time!**

*Last Updated: January 2025*  
*Version: 1.0.0*

