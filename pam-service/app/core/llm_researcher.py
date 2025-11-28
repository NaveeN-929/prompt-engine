"""
LLM Researcher Module
Uses LLM to analyze and synthesize company information
"""

import requests
import logging
from typing import Dict, Any, List, Optional
import json
import time

logger = logging.getLogger(__name__)


class LLMResearcher:
    """Use LLM to research and synthesize company information"""
    
    def __init__(self, ollama_host: str, ollama_port: int, 
                 model: str = "llama3", temperature: float = 0.7,
                 max_tokens: int = 500, timeout: int = 30):
        """
        Initialize LLM researcher
        
        Args:
            ollama_host: Ollama server host
            ollama_port: Ollama server port
            model: Model name to use
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.ollama_url = f"http://{ollama_host}:{ollama_port}"
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Connected to Ollama at {self.ollama_url}")
            else:
                logger.warning(f"Ollama server responded with status {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to Ollama at {self.ollama_url}: {e}")
    
    def _generate(self, prompt: str) -> Optional[str]:
        """
        Generate response from LLM
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text or None if failed
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"LLM generation failed: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("LLM request timed out")
            return None
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return None
    
    def synthesize_company_insights(self, company_name: str, 
                                    scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize company insights using LLM including LinkedIn and trends
        
        Args:
            company_name: Name of the company
            scraped_data: Data scraped from web sources (including LinkedIn)
            
        Returns:
            Dictionary with synthesized insights
        """
        logger.info(f"Synthesizing insights for: {company_name}")
        
        # Build comprehensive context from all sources
        context_parts = []
        
        # Company overview
        if scraped_data.get('overview'):
            context_parts.append(f"Company Overview: {scraped_data['overview'][:400]}")
        
        # Industry and location
        if scraped_data.get('industry'):
            context_parts.append(f"Industry: {scraped_data['industry']}")
        if scraped_data.get('headquarters'):
            context_parts.append(f"Location: {scraped_data['headquarters']}")
        
        # LinkedIn profile info
        if scraped_data.get('linkedin_profile'):
            context_parts.append(f"LinkedIn: Available")
        
        # Latest trends (NEW)
        if scraped_data.get('latest_trends'):
            trends_text = " | ".join(scraped_data['latest_trends'][:3])
            context_parts.append(f"Latest Trends: {trends_text[:400]}")
        
        # Recent news
        if scraped_data.get('news'):
            news_text = " | ".join(scraped_data['news'][:3])
            context_parts.append(f"Recent News: {news_text[:400]}")
        
        # Data sources
        if scraped_data.get('sources'):
            context_parts.append(f"Data Sources: {', '.join(scraped_data['sources'])}")
        
        context = "\n\n".join(context_parts) if context_parts else "Limited information available"
        
        # Create enhanced prompt for LLM
        prompt = f"""Analyze the following comprehensive information about {company_name} and provide actionable business intelligence in 4-5 bullet points. 

Focus on:
1. Key business operations and strengths
2. Recent developments and trends
3. Industry position and market dynamics
4. Financial implications and opportunities
5. Risk factors or concerns

Information Available:
{context}

Provide concise, actionable insights as bullet points (4-5 points, each under 80 words):"""
        
        # Generate insights
        response = self._generate(prompt)
        
        if not response:
            return {
                'company_name': company_name,
                'insights': [
                    f'{company_name} - Business analysis pending',
                    'LinkedIn and web data sources being processed',
                    'Limited real-time information available'
                ],
                'confidence': 'low',
                'sources': scraped_data.get('sources', [])
            }
        
        # Parse bullet points from response
        insights = self._parse_bullet_points(response)
        
        # If we have good data sources, boost confidence
        has_quality_data = (
            bool(scraped_data.get('linkedin_profile')) or
            bool(scraped_data.get('latest_trends')) or
            bool(scraped_data.get('news'))
        )
        
        return {
            'company_name': company_name,
            'insights': insights if insights else [f'Analysis of {company_name} in progress'],
            'confidence': 'high' if (len(insights) >= 3 and has_quality_data) else 'medium',
            'sources': scraped_data.get('sources', []),
            'linkedin_available': bool(scraped_data.get('linkedin_profile')),
            'trends_available': bool(scraped_data.get('latest_trends')),
            'raw_synthesis': response
        }
    
    def _parse_bullet_points(self, text: str) -> List[str]:
        """
        Parse bullet points from LLM response
        
        Args:
            text: LLM response text
            
        Returns:
            List of bullet points
        """
        # Split by common bullet markers
        lines = text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            # Remove common bullet markers
            for marker in ['•', '-', '*', '►', '▪']:
                if line.startswith(marker):
                    line = line[1:].strip()
                    break
            
            # Remove numbered bullets (1., 2., etc.)
            if line and line[0].isdigit() and '.' in line[:3]:
                line = line.split('.', 1)[1].strip()
            
            if line and len(line) > 10:  # Minimum length filter
                bullet_points.append(line)
        
        return bullet_points[:4]  # Max 4 points
    
    def analyze_market_trends(self, industry: str = None, 
                             scraped_trends: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze market trends using LLM
        
        Args:
            industry: Industry to analyze
            scraped_trends: Scraped trend data
            
        Returns:
            Dictionary with market trend analysis
        """
        logger.info(f"Analyzing market trends for: {industry or 'general market'}")
        
        # Build context
        context = ""
        if scraped_trends and scraped_trends.get('trends'):
            trends_text = " | ".join(scraped_trends['trends'][:5])
            context = f"Market Information: {trends_text[:400]}"
        
        industry_text = industry if industry else "general business"
        
        # Create prompt
        prompt = f"""Analyze current market trends for {industry_text} and provide 2-3 key insights relevant for financial decision-making and business analysis. Focus on:
1. Current market conditions
2. Growth opportunities or risks
3. Industry outlook

{context if context else 'Provide general market insights for this industry.'}

Provide insights as concise bullet points (max 3 points):"""
        
        # Generate analysis
        response = self._generate(prompt)
        
        if not response:
            return {
                'industry': industry,
                'trends': ['Market data unavailable'],
                'confidence': 'low'
            }
        
        # Parse insights
        trends = self._parse_bullet_points(response)
        
        return {
            'industry': industry or 'general',
            'trends': trends,
            'confidence': 'high' if len(trends) >= 2 else 'medium',
            'raw_analysis': response
        }
    
    def generate_augmentation_summary(self, companies: List[str],
                                     company_insights: List[Dict[str, Any]],
                                     market_trends: Dict[str, Any]) -> str:
        """
        Generate a concise summary for prompt augmentation
        
        Args:
            companies: List of company names
            company_insights: List of company insight dictionaries
            market_trends: Market trend analysis
            
        Returns:
            Formatted summary text
        """
        summary_parts = []
        
        # Add company context
        if company_insights:
            summary_parts.append("## Company Context\n")
            for insight_data in company_insights[:3]:  # Max 3 companies
                company = insight_data.get('company_name', 'Unknown')
                insights = insight_data.get('insights', [])
                
                if insights:
                    summary_parts.append(f"**{company}:**")
                    for insight in insights[:2]:  # Max 2 insights per company
                        summary_parts.append(f"- {insight[:150]}")  # Limit length
                    summary_parts.append("")
        
        # Add market trends
        if market_trends and market_trends.get('trends'):
            summary_parts.append("## Market Context\n")
            for trend in market_trends['trends'][:3]:
                summary_parts.append(f"- {trend[:150]}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def enhance_prompt_with_context(self, original_prompt: str,
                                   augmentation_summary: str) -> str:
        """
        Enhance original prompt with augmentation context
        
        Args:
            original_prompt: Original prompt text
            augmentation_summary: Augmentation summary to add
            
        Returns:
            Enhanced prompt
        """
        if not augmentation_summary.strip():
            return original_prompt
        
        # Add augmentation as additional context
        enhanced = f"""{original_prompt}

---
## Additional Business Intelligence Context

{augmentation_summary}

Consider the above context in your analysis to provide more informed insights.
"""
        
        return enhanced

