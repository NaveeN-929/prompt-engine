"""
Agentic Prompt Generator - Intelligent, autonomous prompt generation
"""

import time
import json
import re
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
from app.templates.base import TemplateRegistry
from app.templates.banking import (
    transaction_categorization,
    cash_flow_analysis,
    credit_assessment,
    offer_generation,
    card_spend_analysis,
    credit_utilization
)
# Try to import vector service, fallback gracefully if not available
try:
    from app.vector.vector_service import VectorService
    VECTOR_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Vector service not available: {e}")
    print("Agentic generator will work without vector acceleration")
    VectorService = None
    VECTOR_SERVICE_AVAILABLE = False

class AgenticPromptGenerator:
    """
    Intelligent prompt generator that autonomously analyzes data,
    infers context, and creates optimized prompts with learning capabilities
    """
    
    def __init__(self, enable_vector_db: bool = True):
        self.template_registry = TemplateRegistry()
        self._register_templates()
        
        # Vector database for fast similarity search
        self.vector_service = None
        if enable_vector_db and VECTOR_SERVICE_AVAILABLE and VectorService:
            try:
                # Import config for Qdrant settings
                from config import QDRANT_HOST, QDRANT_PORT
                self.vector_service = VectorService(qdrant_host=QDRANT_HOST, qdrant_port=QDRANT_PORT)
                print(f"Vector database enabled for ultra-fast prompt generation (Qdrant: {QDRANT_HOST}:{QDRANT_PORT})")
            except Exception as e:
                print(f"Vector database unavailable: {e}")
                print("Falling back to memory-based optimization")
        else:
            print("Vector service disabled - using memory-based agentic mode")
        
        # Learning and adaptation systems (legacy - now enhanced by vector DB)
        self.interaction_history = []
        self.learning_weights = {}
        self.adaptive_patterns = {}
        self.optimization_cache = {}
        
        # Context inference patterns
        self.context_patterns = {
            'core_banking': [
                'transaction', 'account', 'balance', 'deposit', 'withdrawal',
                'transfer', 'payment', 'merchant', 'amount', 'date'
            ],
            'lending_decision': [
                'cash_flow', 'revenue', 'expenses', 'monthly', 'quarterly',
                'income', 'outflow', 'net_cash', 'liquidity'
            ],
            'loan_approval': [
                'credit', 'debt', 'liability', 'loan', 'assessment', 'risk',
                'dscr', 'ratio', 'financial', 'borrower'
            ],
            'loan_offers': [
                'offer', 'product', 'interest_rate', 'term', 'amount',
                'variant', 'conservative', 'balanced', 'growth'
            ],
            'card_data': [
                'card', 'merchant', 'category', 'spend', 'transaction_type',
                'business', 'personal', 'recurring'
            ],
            'risk_assessment': [
                'utilization', 'payment', 'credit_limit', 'balance',
                'minimum_payment', 'late', 'missed', 'history'
            ]
        }
        
        # Data type inference patterns
        self.data_type_patterns = {
            'transaction_history': ['transactions', 'transaction_data', 'history'],
            'time_series_data': ['monthly_data', 'time_series', 'periods'],
            'transaction_analysis': ['analysis', 'monthly_revenue', 'debt_service'],
            'credit_assessment': ['credit_score', 'dscr', 'default_probability'],
            'card_transactions': ['card_transactions', 'merchant', 'category'],
            'card_behavior': ['statements', 'payment_history', 'utilization']
        }
    
    def _register_templates(self):
        """Register all available templates"""
        self.template_registry.register(transaction_categorization)
        self.template_registry.register(cash_flow_analysis)
        self.template_registry.register(credit_assessment)
        self.template_registry.register(offer_generation)
        self.template_registry.register(card_spend_analysis)
        self.template_registry.register(credit_utilization)
    
    def _analyze_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intelligently analyze input data to understand its characteristics
        """
        analysis = {
            'data_complexity': 'simple',
            'data_volume': 'small',
            'contains_numbers': False,
            'contains_dates': False,
            'contains_financial_terms': False,
            'suggested_context': None,
            'suggested_data_type': None,
            'key_insights': [],
            'enhancement_suggestions': []
        }
        
        # Convert input data to string for analysis
        data_str = json.dumps(input_data, default=str).lower()
        
        # Analyze data complexity
        if len(data_str) > 1000:
            analysis['data_complexity'] = 'complex'
        elif len(data_str) > 500:
            analysis['data_complexity'] = 'moderate'
        
        # Analyze data volume
        if 'transactions' in input_data:
            tx_count = len(input_data.get('transactions', []))
            if tx_count > 50:
                analysis['data_volume'] = 'large'
            elif tx_count > 10:
                analysis['data_volume'] = 'medium'
        
        # Check for numbers and financial data
        analysis['contains_numbers'] = bool(re.search(r'\d+\.?\d*', data_str))
        analysis['contains_dates'] = bool(re.search(r'\d{4}-\d{2}-\d{2}', data_str))
        
        # Check for financial terms
        financial_terms = ['amount', 'revenue', 'expense', 'credit', 'debit', 'balance']
        analysis['contains_financial_terms'] = any(term in data_str for term in financial_terms)
        
        # Infer context and data type
        analysis['suggested_context'] = self._infer_context(data_str)
        analysis['suggested_data_type'] = self._infer_data_type(input_data)
        
        # Generate insights
        analysis['key_insights'] = self._extract_insights(input_data, analysis)
        
        # Generate enhancement suggestions
        analysis['enhancement_suggestions'] = self._suggest_enhancements(analysis)
        
        return analysis
    
    def _infer_context(self, data_str: str) -> Optional[str]:
        """Infer the most likely context from data content"""
        scores = {}
        
        for context, keywords in self.context_patterns.items():
            score = sum(1 for keyword in keywords if keyword in data_str)
            if score > 0:
                scores[context] = score
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    def _infer_data_type(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Infer the most likely data type from data structure"""
        scores = {}
        
        for data_type, patterns in self.data_type_patterns.items():
            score = sum(1 for pattern in patterns if pattern in input_data)
            if score > 0:
                scores[data_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    def _extract_insights(self, input_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Extract key insights from the data"""
        insights = []
        
        if analysis['contains_financial_terms']:
            insights.append("Data contains financial metrics requiring careful analysis")
        
        if analysis['data_complexity'] == 'complex':
            insights.append("Complex dataset requiring systematic breakdown")
        
        if 'transactions' in input_data:
            tx_count = len(input_data.get('transactions', []))
            insights.append(f"Dataset contains {tx_count} transactions for analysis")
        
        if analysis['contains_dates']:
            insights.append("Time-series data present - trend analysis recommended")
        
        return insights
    
    def _suggest_enhancements(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest prompt enhancements based on analysis"""
        suggestions = []
        
        if analysis['data_complexity'] == 'complex':
            suggestions.append("Include step-by-step analysis approach")
            suggestions.append("Add data validation checks")
        
        if analysis['data_volume'] == 'large':
            suggestions.append("Implement sampling strategy for large datasets")
            suggestions.append("Focus on statistical summaries")
        
        if analysis['contains_financial_terms']:
            suggestions.append("Include financial regulatory considerations")
            suggestions.append("Add risk assessment components")
        
        return suggestions
    
    def generate_agentic_prompt(self, 
                              context: Optional[str] = None, 
                              data_type: Optional[str] = None, 
                              input_data: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any], float]:
        """
        Generate an intelligent, context-aware prompt with vector-enhanced speed
        
        Returns:
            Tuple of (prompt_text, metadata, processing_time)
        """
        start_time = time.time()
        
        if not input_data:
            raise ValueError("Input data is required for agentic prompt generation")
        
        # VECTOR-POWERED OPTIMIZATION
        # Check vector database for similar patterns first
        if self.vector_service:
            similar_prompts = self.vector_service.find_similar_prompts(input_data, limit=3, min_similarity=0.8)
            if similar_prompts:
                # Found high-similarity match - use it as base
                best_match = similar_prompts[0]
                if best_match['score'] > 0.9:  # Very high similarity
                    print(f"⚡ Ultra-fast generation using vector similarity (score: {best_match['score']:.3f})")
                    
                    # Adapt the similar prompt to current data
                    adapted_prompt = self._adapt_similar_prompt(best_match['data'], input_data)
                    
                    processing_time = time.time() - start_time
                    metadata = {
                        "template_used": "vector_similarity",
                        "context": best_match['data']['metadata'].get('context', 'auto_inferred'),
                        "data_type": best_match['data']['metadata'].get('data_type', 'auto_inferred'),
                        "generation_mode": "vector_accelerated",
                        "similarity_score": best_match['score'],
                        "similar_prompts_used": len(similar_prompts),
                        "processing_time": processing_time,
                        "timestamp": datetime.now().isoformat(),
                        "vector_optimization": True
                    }
                    
                    return adapted_prompt, metadata, processing_time
        
        # Standard agentic analysis for new patterns
        analysis = self._analyze_input_data(input_data)
        
        # Use provided context/data_type or infer from analysis
        final_context = context or analysis['suggested_context']
        final_data_type = data_type or analysis['suggested_data_type']
        
        # Vector enhancement of metadata
        base_metadata = {
            "context": final_context,
            "data_type": final_data_type,
            "analysis": analysis,
            "generation_mode": "agentic_enhanced",
            "timestamp": datetime.now().isoformat()
        }
        
        if self.vector_service:
            base_metadata = self.vector_service.optimize_with_vectors(input_data, base_metadata)
        
        if not final_context or not final_data_type:
            # Fallback to autonomous prompt generation
            return self._generate_autonomous_prompt(input_data, analysis, time.time() - start_time)
        
        # Get the base template
        template = self.template_registry.get_template(final_context, final_data_type)
        if not template:
            return self._generate_autonomous_prompt(input_data, analysis, time.time() - start_time)
        
        # Enhance the base template with agentic intelligence
        enhanced_prompt = self._enhance_template_prompt(template, input_data, analysis)
        
        # Apply vector insights if available
        if self.vector_service and base_metadata.get('vector_enhancement_suggestions'):
            enhanced_prompt = self._apply_vector_enhancements(enhanced_prompt, base_metadata)
        
        processing_time = time.time() - start_time
        
        metadata = {
            **base_metadata,
            "template_used": template.name,
            "processing_time": processing_time
        }
        
        return enhanced_prompt, metadata, processing_time
    
    def _enhance_template_prompt(self, template, input_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Enhance a base template with agentic intelligence"""
        
        # Validate and render the base template
        try:
            # Create template parameters mapping
            template_params = {}
            
            # Map input data to expected template parameters
            if template.context == "core_banking" and "transactions" in input_data:
                # Map transactions data to transaction_data for compatibility
                template_params["transaction_data"] = input_data["transactions"]
                template_params.update({k: v for k, v in input_data.items() if k != "transactions"})
            else:
                template_params = input_data
            
            template.validate_parameters(template_params)
            base_prompt = template.render(template_params)
        except Exception as e:
            # Fallback to safe template rendering
            try:
                safe_params = {"data": str(input_data)}
                base_prompt = f"Analyze the following data:\n{input_data}\n\nProvide insights and recommendations."
            except:
                base_prompt = template.template
        
        # Create agentic enhancement
        enhancement = self._create_agentic_enhancement(analysis, input_data)
        
        # Combine base template with agentic enhancements
        enhanced_prompt = f"""
{enhancement}

=== CORE ANALYSIS TASK ===
{base_prompt}

=== AGENTIC PROCESSING INSTRUCTIONS ===

Based on the data analysis, follow this autonomous approach:

1. **Data Validation & Understanding**
   - Verify data integrity and completeness
   - Identify any anomalies or missing information
   - Note data quality considerations

2. **Contextual Analysis**
   {self._format_insights(analysis['key_insights'])}

3. **Adaptive Processing**
   {self._format_suggestions(analysis['enhancement_suggestions'])}

4. **Output Optimization**
   - Structure results for maximum clarity
   - Include confidence levels for key findings
   - Highlight actionable insights
   - Provide reasoning for conclusions

5. **Quality Assurance**
   - Cross-validate findings against industry standards
   - Identify potential edge cases or limitations
   - Suggest follow-up analysis if needed

Remember: This is an autonomous analysis system. Be thorough, accurate, and provide reasoning for all conclusions.
"""
        
        return enhanced_prompt.strip()
    
    def _generate_autonomous_prompt(self, input_data: Dict[str, Any], analysis: Dict[str, Any], elapsed_time: float) -> Tuple[str, Dict[str, Any], float]:
        """Generate a fully autonomous prompt when no template matches"""
        
        prompt = f"""
=== AUTONOMOUS DATA ANALYSIS SYSTEM ===

You are an intelligent data analysis agent. Analyze the following data autonomously and provide comprehensive insights.

**DATA CHARACTERISTICS:**
- Complexity: {analysis['data_complexity']}
- Volume: {analysis['data_volume']}
- Contains Financial Data: {analysis['contains_financial_terms']}
- Contains Time Series: {analysis['contains_dates']}

**INPUT DATA:**
{json.dumps(input_data, indent=2)}

**AUTONOMOUS ANALYSIS PROTOCOL:**

1. **Data Structure Analysis**
   - Identify data types and structures
   - Map relationships between data elements
   - Assess data quality and completeness

2. **Pattern Recognition**
   - Identify trends, anomalies, and patterns
   - Perform statistical analysis where applicable
   - Detect correlations and dependencies

3. **Contextual Interpretation**
   - Infer business context from data characteristics
   - Apply domain knowledge for interpretation
   - Consider regulatory and compliance factors

4. **Insight Generation**
   - Extract actionable insights
   - Quantify findings with confidence levels
   - Prioritize insights by business impact

5. **Recommendation Engine**
   - Provide specific, actionable recommendations
   - Suggest next steps for further analysis
   - Identify risk factors and mitigation strategies

**OUTPUT REQUIREMENTS:**
- Structured analysis with clear sections
- Quantified findings where possible
- Risk assessment and confidence levels
- Actionable recommendations
- Reasoning behind conclusions

Perform this analysis autonomously using best practices for the identified data type and context.
"""
        
        processing_time = time.time() - elapsed_time
        
        metadata = {
            "template_used": "autonomous_generation",
            "context": "auto_inferred",
            "data_type": "autonomous",
            "analysis": analysis,
            "generation_mode": "fully_autonomous",
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat()
        }
        
        return prompt.strip(), metadata, processing_time
    
    def _create_agentic_enhancement(self, analysis: Dict[str, Any], input_data: Dict[str, Any]) -> str:
        """Create the agentic intelligence enhancement header"""
        
        enhancement = f"""
=== AGENTIC INTELLIGENCE SYSTEM ACTIVATED ===

**Autonomous Data Analysis Report:**
- Analysis Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Data Complexity Assessment: {analysis['data_complexity'].upper()}
- Processing Mode: Intelligent Template Enhancement

**AI Agent Context Awareness:**
- Suggested Context: {analysis.get('suggested_context', 'Auto-detecting...')}
- Suggested Data Type: {analysis.get('suggested_data_type', 'Auto-detecting...')}
- Financial Data Detected: {"Yes" if analysis['contains_financial_terms'] else "No"}
- Time Series Data: {"Yes" if analysis['contains_dates'] else "No"}
"""
        
        if analysis['key_insights']:
            enhancement += f"\n**Key Data Insights Detected:**\n"
            for insight in analysis['key_insights']:
                enhancement += f"- {insight}\n"
        
        return enhancement
    
    def _format_insights(self, insights: List[str]) -> str:
        """Format insights for prompt inclusion"""
        if not insights:
            return "- Perform standard analysis based on data characteristics"
        return "\n   ".join(f"- {insight}" for insight in insights)
    
    def _format_suggestions(self, suggestions: List[str]) -> str:
        """Format suggestions for prompt inclusion"""
        if not suggestions:
            return "- Apply standard analytical approach"
        return "\n   ".join(f"- {suggestion}" for suggestion in suggestions)
    
    def learn_from_interaction(self, input_data: Dict[str, Any], 
                                prompt_result: str, 
                                llm_response: str, 
                                quality_score: float = None,
                                user_feedback: str = None,
                                metadata: Dict[str, Any] = None) -> None:
        """
        Learn from interaction results to improve future prompt generation
        Enhanced with vector database storage for ultra-fast retrieval
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "input_data": input_data,
            "prompt_result": prompt_result,
            "llm_response": llm_response,
            "quality_score": quality_score or 0.5,
            "user_feedback": user_feedback,
            "data_analysis": self._analyze_input_data(input_data),
            "metadata": metadata or {}
        }
        
        # VECTOR DATABASE LEARNING
        # Store successful patterns in vector database for fast retrieval
        if self.vector_service and quality_score and quality_score > 0.6:
            self.vector_service.store_successful_prompt(
                input_data=input_data,
                prompt=prompt_result,
                response=llm_response,
                metadata=metadata or {},
                quality_score=quality_score
            )
            print(f"Stored successful pattern in vector database (quality: {quality_score:.2f})")
        
        # Legacy learning systems (still useful for fallback)
        self.interaction_history.append(interaction)
        
        # Update learning weights based on outcomes
        if quality_score is not None:
            self._update_learning_weights(interaction, quality_score)
        
        # Update adaptive patterns
        self._update_adaptive_patterns(interaction)
        
        # Limit history size to prevent memory issues
        if len(self.interaction_history) > 1000:
            self.interaction_history = self.interaction_history[-800:]  # Keep recent 800
    
    def _update_learning_weights(self, interaction: Dict[str, Any], quality_score: float) -> None:
        """Update learning weights based on interaction quality"""
        analysis = interaction["data_analysis"]
        
        # Update weights for successful patterns
        if quality_score > 0.7:
            for insight in analysis.get("key_insights", []):
                self.learning_weights[insight] = self.learning_weights.get(insight, 0) + 0.1
            
            for suggestion in analysis.get("enhancement_suggestions", []):
                self.learning_weights[suggestion] = self.learning_weights.get(suggestion, 0) + 0.1
        
        # Decrease weights for poor patterns
        elif quality_score < 0.4:
            for insight in analysis.get("key_insights", []):
                self.learning_weights[insight] = max(0, self.learning_weights.get(insight, 0) - 0.1)
    
    def _update_adaptive_patterns(self, interaction: Dict[str, Any]) -> None:
        """Update adaptive patterns based on successful interactions"""
        analysis = interaction["data_analysis"]
        context = analysis.get("suggested_context")
        data_type = analysis.get("suggested_data_type")
        
        if context and data_type:
            pattern_key = f"{context}_{data_type}"
            if pattern_key not in self.adaptive_patterns:
                self.adaptive_patterns[pattern_key] = {
                    "success_count": 0,
                    "total_count": 0,
                    "best_enhancements": [],
                    "common_insights": []
                }
            
            pattern = self.adaptive_patterns[pattern_key]
            pattern["total_count"] += 1
            
            # Track successful enhancements
            quality_score = interaction.get("quality_score", 0.5)
            if quality_score > 0.6:
                pattern["success_count"] += 1
                enhancements = analysis.get("enhancement_suggestions", [])
                for enhancement in enhancements:
                    if enhancement not in pattern["best_enhancements"]:
                        pattern["best_enhancements"].append(enhancement)
    
    def generate_multi_step_reasoning_prompt(self, 
                                           input_data: Dict[str, Any],
                                           reasoning_steps: int = 5) -> Tuple[str, Dict[str, Any], float]:
        """
        Generate a prompt with explicit multi-step reasoning instructions
        """
        start_time = time.time()
        
        # First, analyze the data
        analysis = self._analyze_input_data(input_data)
        
        # Determine optimal reasoning steps based on data complexity
        if analysis['data_complexity'] == 'complex':
            reasoning_steps = max(reasoning_steps, 7)
        elif analysis['data_complexity'] == 'simple':
            reasoning_steps = min(reasoning_steps, 3)
        
        # Generate reasoning framework
        reasoning_framework = self._create_reasoning_framework(analysis, reasoning_steps)
        
        # Get base agentic prompt
        base_prompt, base_metadata, _ = self.generate_agentic_prompt(
            input_data=input_data
        )
        
        # Enhance with multi-step reasoning
        enhanced_prompt = f"""
{base_prompt}

=== MULTI-STEP REASONING FRAMEWORK ===

Follow this systematic reasoning approach:

{reasoning_framework}

**REASONING REQUIREMENTS:**
- Show your work for each step explicitly
- State assumptions and validate them
- Provide confidence levels for each conclusion
- Cross-reference findings between steps
- Identify any logical gaps or limitations

**OUTPUT STRUCTURE:**
For each reasoning step, provide:
1. Step description and objective
2. Analysis and findings
3. Confidence level (0-100%)
4. Dependencies on previous steps
5. Implications for next steps

Complete all reasoning steps before providing final conclusions.
"""
        
        processing_time = time.time() - start_time
        
        metadata = {
            **base_metadata,
            "reasoning_steps": reasoning_steps,
            "reasoning_framework": reasoning_framework,
            "generation_mode": "multi_step_reasoning",
            "processing_time": processing_time
        }
        
        return enhanced_prompt.strip(), metadata, processing_time
    
    def _create_reasoning_framework(self, analysis: Dict[str, Any], steps: int) -> str:
        """Create a customized reasoning framework based on data analysis"""
        framework_steps = []
        
        # Step 1: Always start with data validation
        framework_steps.append("**Step 1: Data Validation & Understanding**\n   - Verify data completeness and accuracy\n   - Identify data types and structures\n   - Note any anomalies or missing information")
        
        # Add domain-specific steps based on context
        suggested_context = analysis.get('suggested_context')
        if suggested_context == 'core_banking':
            framework_steps.append("**Step 2: Transaction Pattern Analysis**\n   - Categorize transaction types\n   - Identify spending patterns and trends\n   - Calculate key financial metrics")
        elif suggested_context == 'lending_decision':
            framework_steps.append("**Step 2: Cash Flow Assessment**\n   - Analyze revenue and expense patterns\n   - Calculate cash flow ratios\n   - Identify seasonal variations")
        elif suggested_context == 'risk_assessment':
            framework_steps.append("**Step 2: Risk Factor Identification**\n   - Identify potential risk indicators\n   - Assess risk severity and likelihood\n   - Map risk relationships")
        else:
            framework_steps.append("**Step 2: Pattern Recognition**\n   - Identify key patterns in the data\n   - Look for correlations and relationships\n   - Note significant trends or anomalies")
        
        # Add complexity-based steps
        if analysis.get('data_complexity') == 'complex':
            framework_steps.append("**Step 3: Dimensional Analysis**\n   - Break down complex data into components\n   - Analyze each dimension separately\n   - Identify interdependencies")
            framework_steps.append("**Step 4: Integration & Synthesis**\n   - Combine findings from different dimensions\n   - Resolve any contradictions\n   - Form integrated conclusions")
        else:
            framework_steps.append("**Step 3: Core Analysis**\n   - Perform primary analysis objectives\n   - Calculate key metrics and indicators\n   - Draw preliminary conclusions")
        
        # Final steps
        framework_steps.append("**Step " + str(steps-1) + ": Validation & Verification**\n   - Cross-check findings against industry standards\n   - Validate conclusions with alternative methods\n   - Assess confidence levels")
        
        framework_steps.append("**Step " + str(steps) + ": Insights & Recommendations**\n   - Synthesize key insights\n   - Provide actionable recommendations\n   - Highlight areas for further investigation")
        
        return "\n\n".join(framework_steps)
    
    def optimize_prompt_continuously(self, 
                                   input_data: Dict[str, Any],
                                   performance_feedback: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any], float]:
        """
        Continuously optimize prompts based on learned patterns and feedback
        """
        start_time = time.time()
        
        # Check optimization cache
        data_hash = hash(str(sorted(input_data.items())))
        if data_hash in self.optimization_cache:
            cached_result = self.optimization_cache[data_hash]
            cached_result["metadata"]["cache_hit"] = True
            return cached_result["prompt"], cached_result["metadata"], time.time() - start_time
        
        # Generate base agentic prompt
        base_prompt, metadata, _ = self.generate_agentic_prompt(input_data=input_data)
        
        # Apply learned optimizations
        optimized_prompt = self._apply_learned_optimizations(base_prompt, input_data, metadata)
        
        # Apply adaptive patterns
        final_prompt = self._apply_adaptive_patterns(optimized_prompt, metadata)
        
        processing_time = time.time() - start_time
        
        # Update metadata
        metadata.update({
            "optimization_applied": True,
            "learned_patterns_used": len([w for w, score in self.learning_weights.items() if score > 0.5]),
            "cache_hit": False,
            "generation_mode": "continuous_optimization",
            "processing_time": processing_time
        })
        
        # Cache the result
        self.optimization_cache[data_hash] = {
            "prompt": final_prompt,
            "metadata": metadata
        }
        
        # Limit cache size
        if len(self.optimization_cache) > 100:
            # Remove oldest entries
            sorted_cache = sorted(self.optimization_cache.items(), 
                                key=lambda x: x[1]["metadata"].get("timestamp", ""))
            self.optimization_cache = dict(sorted_cache[-80:])
        
        return final_prompt, metadata, processing_time
    
    def _apply_learned_optimizations(self, prompt: str, input_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Apply optimizations learned from previous interactions"""
        
        # Apply high-weight learning patterns
        high_value_patterns = [pattern for pattern, weight in self.learning_weights.items() if weight > 0.7]
        
        if high_value_patterns:
            optimization_section = "\n\n=== LEARNED OPTIMIZATIONS ===\n"
            optimization_section += "Based on successful past interactions, prioritize:\n"
            for pattern in high_value_patterns[:5]:  # Top 5 patterns
                optimization_section += f"- {pattern}\n"
            
            prompt = prompt + optimization_section
        
        return prompt
    
    def _apply_adaptive_patterns(self, prompt: str, metadata: Dict[str, Any]) -> str:
        """Apply adaptive patterns based on context and data type"""
        
        context = metadata.get("context")
        data_type = metadata.get("data_type")
        
        if context and data_type:
            pattern_key = f"{context}_{data_type}"
            if pattern_key in self.adaptive_patterns:
                pattern_info = self.adaptive_patterns[pattern_key]
                
                # Apply successful enhancements
                if pattern_info["best_enhancements"] and pattern_info["success_count"] > 2:
                    adaptive_section = "\n\n=== ADAPTIVE ENHANCEMENTS ===\n"
                    adaptive_section += f"Success rate for {pattern_key}: {pattern_info['success_count']}/{pattern_info['total_count']}\n"
                    adaptive_section += "Applying proven enhancements:\n"
                    
                    for enhancement in pattern_info["best_enhancements"][:3]:
                        adaptive_section += f"- {enhancement}\n"
                    
                    prompt = prompt + adaptive_section
        
        return prompt

    def _adapt_similar_prompt(self, similar_data: Dict[str, Any], current_input: Dict[str, Any]) -> str:
        """
        Adapt a similar prompt to current input data for ultra-fast generation
        """
        base_prompt = similar_data.get('prompt', '')
        
        # Extract key elements from current input
        current_text = json.dumps(current_input, default=str)
        
        # Simple adaptation - replace data references
        adapted_prompt = base_prompt
        
        # Add current data context
        adaptation_note = f"""
=== VECTOR-ACCELERATED ADAPTATION ===
This prompt has been rapidly adapted from a high-similarity successful pattern.

**Current Input Data:**
{json.dumps(current_input, indent=2)}

**Adaptation Instructions:**
- Apply the proven analysis framework below to the current data
- Maintain the successful analytical approach from the similar case
- Focus on the same quality standards that made the original prompt successful

=== PROVEN SUCCESSFUL FRAMEWORK ===
"""
        
        return adaptation_note + adapted_prompt
    
    def _apply_vector_enhancements(self, prompt: str, metadata: Dict[str, Any]) -> str:
        """
        Apply enhancements learned from vector similarity search
        """
        vector_suggestions = metadata.get('vector_enhancement_suggestions', [])
        
        if vector_suggestions:
            enhancement_section = "\n\n=== VECTOR-ENHANCED OPTIMIZATIONS ===\n"
            enhancement_section += "Based on similar successful cases in our vector database:\n\n"
            
            for suggestion in vector_suggestions[:5]:  # Top 5 suggestions
                enhancement_section += f"{suggestion}\n"
            
            enhancement_section += "\nApply these proven enhancements to maximize analysis quality.\n"
            
            return prompt + enhancement_section
        
        return prompt

    def get_agentic_capabilities(self) -> Dict[str, Any]:
        """Return information about agentic capabilities"""
        return {
            "capabilities": [
                "Autonomous context inference",
                "Intelligent data type detection", 
                "Adaptive prompt optimization",
                "Real-time data analysis",
                "Quality-aware processing",
                "Self-improving templates",
                "Multi-step reasoning",
                "Learning from interactions",
                "Dynamic pattern recognition",
                "Context-aware adaptation",
                "Continuous optimization"
            ],
            "supported_contexts": list(self.context_patterns.keys()),
            "supported_data_types": list(self.data_type_patterns.keys()),
            "analysis_features": [
                "Data complexity assessment",
                "Volume analysis",
                "Pattern recognition",
                "Financial data detection",
                "Time series identification",
                "Insight extraction",
                "Enhancement suggestions",
                "Learning pattern analysis",
                "Adaptive optimization",
                "Multi-dimensional reasoning"
            ],
            "learning_stats": {
                "total_interactions": len(self.interaction_history),
                "learned_patterns": len(self.learning_weights),
                "optimization_cache_size": len(self.optimization_cache),
                "adaptive_contexts": len(self.adaptive_patterns)
            },
            "vector_stats": self.vector_service.get_stats() if self.vector_service else {
                "status": "disabled",
                "cache_hits": 0,
                "similarity_searches": 0
            }
        }