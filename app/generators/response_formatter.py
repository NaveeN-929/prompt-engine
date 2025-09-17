"""
Response Formatter - Ensures all responses follow the required format (two-section or paired JSON)
"""

import re
import json
from typing import Dict, Any, List, Tuple

class ResponseFormatter:
    """Formats responses to ensure they follow the required two-section structure"""
    
    def __init__(self):
        self.insights_section_pattern = r"=== SECTION 1: INSIGHTS ===(.*?)(?=== SECTION 2: RECOMMENDATIONS ===|$)"
        self.recommendations_section_pattern = r"=== SECTION 2: RECOMMENDATIONS ===(.*?)(?===|$)"
        self.section_header_pattern = r"=== SECTION \d+: (INSIGHTS|RECOMMENDATIONS) ==="
    
    def format_response(self, response_text: str) -> str:
        """
        Format a response to ensure it follows the required two-section structure
        
        Args:
            response_text: The raw response text from the LLM
            
        Returns:
            Formatted response with proper section structure
        """
        # Check if response already has the required structure
        if self._has_proper_structure(response_text):
            return self._clean_and_format(response_text)
        
        # If not, try to extract insights and recommendations from the response
        insights, recommendations = self._extract_sections(response_text)
        
        # Format into the required structure
        formatted_response = self._create_formatted_response(insights, recommendations)
        
        return formatted_response
    
    def _has_proper_structure(self, response_text: str) -> bool:
        """Check if response already has the required section structure"""
        has_insights = "=== SECTION 1: INSIGHTS ===" in response_text
        has_recommendations = "=== SECTION 2: RECOMMENDATIONS ===" in response_text
        return has_insights and has_recommendations
    
    def _extract_sections(self, response_text: str) -> Tuple[str, str]:
        """Extract insights and recommendations from unstructured response"""
        
        # Try to find existing sections
        insights_match = re.search(self.insights_section_pattern, response_text, re.DOTALL | re.IGNORECASE)
        recommendations_match = re.search(self.recommendations_section_pattern, response_text, re.DOTALL | re.IGNORECASE)
        
        insights = ""
        recommendations = ""
        
        if insights_match:
            insights = insights_match.group(1).strip()
        
        if recommendations_match:
            recommendations = recommendations_match.group(1).strip()
        
        # If sections not found, try to intelligently split the response
        if not insights and not recommendations:
            insights, recommendations = self._intelligently_split_response(response_text)
        
        return insights, recommendations
    
    def _intelligently_split_response(self, response_text: str) -> Tuple[str, str]:
        """Intelligently split response into insights and recommendations"""
        
        # Common patterns that indicate insights vs recommendations
        insight_indicators = [
            "insight", "finding", "observation", "pattern", "trend", "analysis",
            "data shows", "we can see", "it appears", "the data indicates",
            "key finding", "notable", "significant", "important"
        ]
        
        recommendation_indicators = [
            "recommend", "suggest", "should", "need to", "action", "next step",
            "improve", "enhance", "implement", "consider", "focus on",
            "strategy", "plan", "approach", "solution"
        ]
        
        # Split response into sentences
        sentences = re.split(r'[.!?]+', response_text)
        
        insights_sentences = []
        recommendations_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_lower = sentence.lower()
            
            # Count indicators for each sentence
            insight_score = sum(1 for indicator in insight_indicators if indicator in sentence_lower)
            recommendation_score = sum(1 for indicator in recommendation_indicators if indicator in sentence_lower)
            
            if insight_score > recommendation_score:
                insights_sentences.append(sentence)
            elif recommendation_score > insight_score:
                recommendations_sentences.append(sentence)
            else:
                # Default to insights if unclear
                insights_sentences.append(sentence)
        
        insights = ". ".join(insights_sentences) + "."
        recommendations = ". ".join(recommendations_sentences) + "."
        
        return insights, recommendations
    
    def _create_formatted_response(self, insights: str, recommendations: str) -> str:
        """Create a properly formatted response with the required sections"""
        
        # Ensure we have content for both sections
        if not insights.strip():
            insights = "• No specific insights could be extracted from the provided data.\n• Additional data analysis may be required to generate meaningful insights."
        
        if not recommendations.strip():
            recommendations = "• No specific recommendations could be generated from the current analysis.\n• Consider providing additional context or data for more actionable recommendations."
        
        formatted_response = f"""=== SECTION 1: INSIGHTS ===

{insights}

=== SECTION 2: RECOMMENDATIONS ===

{recommendations}"""
        
        return formatted_response
    
    def _clean_and_format(self, response_text: str) -> str:
        """Clean and format an already properly structured response"""
        
        # Ensure consistent formatting
        response_text = re.sub(r'=== SECTION 1: INSIGHTS ===', '=== SECTION 1: INSIGHTS ===', response_text, flags=re.IGNORECASE)
        response_text = re.sub(r'=== SECTION 2: RECOMMENDATIONS ===', '=== SECTION 2: RECOMMENDATIONS ===', response_text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        response_text = re.sub(r'\n\s*\n\s*\n', '\n\n', response_text)
        
        return response_text.strip()
    
    def validate_response_structure(self, response_text: str) -> Dict[str, Any]:
        """Validate that a response follows the required structure"""
        
        validation_result = {
            "is_valid": False,
            "has_insights_section": False,
            "has_recommendations_section": False,
            "insights_content_length": 0,
            "recommendations_content_length": 0,
            "issues": []
        }
        
        # Check for section headers
        if "=== SECTION 1: INSIGHTS ===" in response_text:
            validation_result["has_insights_section"] = True
        
        if "=== SECTION 2: RECOMMENDATIONS ===" in response_text:
            validation_result["has_recommendations_section"] = True
        
        # Extract content lengths
        insights_match = re.search(self.insights_section_pattern, response_text, re.DOTALL | re.IGNORECASE)
        if insights_match:
            validation_result["insights_content_length"] = len(insights_match.group(1).strip())
        
        recommendations_match = re.search(self.recommendations_section_pattern, response_text, re.DOTALL | re.IGNORECASE)
        if recommendations_match:
            validation_result["recommendations_content_length"] = len(recommendations_match.group(1).strip())
        
        # Check for issues
        if not validation_result["has_insights_section"]:
            validation_result["issues"].append("Missing insights section header")
        
        if not validation_result["has_recommendations_section"]:
            validation_result["issues"].append("Missing recommendations section header")
        
        if validation_result["insights_content_length"] < 10:
            validation_result["issues"].append("Insights section has insufficient content")
        
        if validation_result["recommendations_content_length"] < 10:
            validation_result["issues"].append("Recommendations section has insufficient content")
        
        # Determine if response is valid
        validation_result["is_valid"] = (
            validation_result["has_insights_section"] and
            validation_result["has_recommendations_section"] and
            validation_result["insights_content_length"] >= 10 and
            validation_result["recommendations_content_length"] >= 10
        )
        
        return validation_result

    def format_paired_response(self, response_text: str) -> Dict[str, Any]:
        """
        Format response for the refined CRM insights template with paired insights/recommendations

        Args:
            response_text: Raw response from LLM (expected to be JSON array)

        Returns:
            Dictionary with 'json_output' for RAG pipeline and 'display_output' for CRM
        """
        # Clean the response text first
        response_text = response_text.strip()

        # Remove any markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        try:
            # Try to parse as JSON first
            if response_text.startswith('['):
                pairs = json.loads(response_text)

                # Validate the structure
                if not isinstance(pairs, list):
                    raise ValueError("Response is not a list")

                # Ensure each item has the required keys
                validated_pairs = []
                for i, item in enumerate(pairs):
                    if isinstance(item, dict) and 'insight' in item and 'recommendation' in item:
                        validated_pairs.append({
                            'insight': str(item['insight']).strip(),
                            'recommendation': str(item['recommendation']).strip()
                        })
                    else:
                        print(f"Warning: Invalid pair at index {i}, skipping")

                pairs = validated_pairs

            else:
                # If not JSON, try to extract pairs from text
                pairs = self._extract_json_pairs_from_text(response_text)

            # Ensure we have exactly 5 pairs
            while len(pairs) < 5:
                pairs.append({
                    "insight": "Additional analysis may be needed to identify more patterns",
                    "recommendation": "Consider providing more transaction data for comprehensive analysis"
                })

            pairs = pairs[:5]  # Limit to 5 pairs max

            # Create JSON output for RAG pipeline
            json_output = pairs

            # Create display output with emojis for CRM
            display_output = self._create_crm_display_format(pairs)

            return {
                "json_output": json_output,
                "display_output": display_output,
                "pairs_count": len(pairs)
            }

        except (json.JSONDecodeError, ValueError) as e:
            # If JSON parsing fails, try to extract insights and recommendations from text
            insights, recommendations = self._extract_sections(response_text)

            # Convert to paired format
            pairs = self._convert_sections_to_pairs(insights, recommendations)

            json_output = pairs
            display_output = self._create_crm_display_format(pairs)

            return {
                "json_output": json_output,
                "display_output": display_output,
                "pairs_count": len(pairs)
            }

    def _extract_json_pairs_from_text(self, response_text: str) -> List[Dict[str, str]]:
        """Extract insight/recommendation pairs from unstructured text"""
        pairs = []

        # Split by numbered items or bullet points
        lines = response_text.split('\n')
        current_insight = ""
        current_recommendation = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for insight patterns
            if re.search(r'insight\s*\d*:|🔍|insight:', line, re.IGNORECASE):
                if current_insight and current_recommendation:
                    pairs.append({
                        "insight": current_insight.strip(),
                        "recommendation": current_recommendation.strip()
                    })
                current_insight = re.sub(r'insight\s*\d*:|🔍|insight:', '', line, flags=re.IGNORECASE).strip()
                current_recommendation = ""
            elif re.search(r'recommendation\s*\d*:|💡|recommendation:', line, re.IGNORECASE):
                current_recommendation = re.sub(r'recommendation\s*\d*:|💡|recommendation:', '', line, flags=re.IGNORECASE).strip()
            elif current_insight and not current_recommendation:
                # Continuation of insight
                current_insight += " " + line

        # Add the last pair
        if current_insight and current_recommendation:
            pairs.append({
                "insight": current_insight.strip(),
                "recommendation": current_recommendation.strip()
            })

        return pairs

    def _convert_sections_to_pairs(self, insights: str, recommendations: str) -> List[Dict[str, str]]:
        """Convert traditional insights/recommendations sections to paired format"""
        pairs = []

        # Split insights and recommendations into individual items
        insight_items = self._split_into_items(insights)
        recommendation_items = self._split_into_items(recommendations)

        # Create pairs by matching insights with recommendations
        max_pairs = min(len(insight_items), len(recommendation_items), 5)

        for i in range(max_pairs):
            pairs.append({
                "insight": insight_items[i].strip(),
                "recommendation": recommendation_items[i].strip()
            })

        return pairs

    def _split_into_items(self, text: str) -> List[str]:
        """Split text into individual items based on bullets, numbers, or line breaks"""
        # Split by bullet points, numbers, or line breaks
        items = re.split(r'[•\-\*\d]+\.?\s*', text)
        items = [item.strip() for item in items if item.strip()]

        # If no clear separators, try splitting by sentences
        if len(items) <= 1:
            items = re.split(r'[.!?]+\s*', text)
            items = [item.strip() + '.' for item in items if item.strip()]

        return items

    def _create_crm_display_format(self, pairs: List[Dict[str, str]]) -> str:
        """Create the CRM display format with emojis and banking product labels"""
        display_lines = []

        for i, pair in enumerate(pairs, 1):
            display_lines.append(f"🔍 Insight {i}")
            display_lines.append(f"{pair['insight']}")
            display_lines.append(f"💡 Recommendation {i}")
            display_lines.append(f"{pair['recommendation']}")
            display_lines.append("")  # Empty line between pairs

        return "\n".join(display_lines).strip()
