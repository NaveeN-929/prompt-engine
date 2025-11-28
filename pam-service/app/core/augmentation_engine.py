"""
Augmentation Engine
Main orchestrator that combines all components to augment prompts
"""

import logging
from typing import Dict, Any, List, Optional
import time
from datetime import datetime

from .company_extractor import CompanyExtractor
from .web_scraper import WebScraper
from .llm_researcher import LLMResearcher
from .qdrant_cache import QdrantCache

logger = logging.getLogger(__name__)


class AugmentationEngine:
    """Main engine that orchestrates prompt augmentation"""
    
    def __init__(self, config):
        """
        Initialize augmentation engine
        
        Args:
            config: Configuration object with all settings
        """
        self.config = config
        
        # Initialize components
        logger.info("Initializing augmentation engine components...")
        
        # Company extractor
        self.company_extractor = CompanyExtractor()
        
        # Web scraper
        if config.ENABLE_WEB_SCRAPING:
            self.web_scraper = WebScraper(
                user_agent=config.USER_AGENT,
                timeout=config.SCRAPING_TIMEOUT,
                rate_limit_delay=config.RATE_LIMIT_DELAY,
                max_retries=config.MAX_RETRIES
            )
            logger.info("Web scraper initialized")
        else:
            self.web_scraper = None
            logger.info("Web scraping disabled")
        
        # LLM researcher
        if config.ENABLE_LLM_RESEARCH:
            self.llm_researcher = LLMResearcher(
                ollama_host=config.OLLAMA_HOST,
                ollama_port=config.OLLAMA_PORT,
                model=config.OLLAMA_MODEL,
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS,
                timeout=config.LLM_TIMEOUT
            )
            logger.info("LLM researcher initialized")
        else:
            self.llm_researcher = None
            logger.info("LLM research disabled")
        
        # Qdrant cache
        if config.ENABLE_CACHING:
            try:
                self.qdrant_cache = QdrantCache(
                    qdrant_host=config.QDRANT_HOST,
                    qdrant_port=config.QDRANT_PORT,
                    collection_name=config.QDRANT_COLLECTION,
                    cache_ttl_hours=config.CACHE_TTL_HOURS,
                    similarity_threshold=config.SIMILARITY_THRESHOLD
                )
                logger.info("Qdrant cache initialized")
            except Exception as e:
                logger.warning(f"Qdrant cache initialization failed: {e}")
                self.qdrant_cache = None
        else:
            self.qdrant_cache = None
            logger.info("Caching disabled")
        
        # Statistics
        self.stats = {
            'total_augmentations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'companies_analyzed': 0,
            'web_scrapes': 0,
            'llm_calls': 0,
            'errors': 0
        }
    
    def augment(self, input_data: Dict[str, Any], 
                prompt_text: str = None,
                companies: List[str] = None,
                context: str = None) -> Dict[str, Any]:
        """
        Main augmentation function
        
        Args:
            input_data: Transaction data or other input
            prompt_text: Original prompt to augment (optional)
            companies: Explicit list of companies (optional)
            context: Context for the augmentation (optional)
            
        Returns:
            Dictionary with augmented data
        """
        start_time = time.time()
        self.stats['total_augmentations'] += 1
        
        logger.info("Starting prompt augmentation...")
        
        try:
            # Step 1: Extract companies
            logger.info("Step 1: Extracting companies...")
            logger.info(f"Input data keys: {list(input_data.keys())}")
            logger.info(f"Transaction count: {len(input_data.get('transactions', []))}")
            
            # Log sample transactions for debugging
            if input_data.get('transactions'):
                sample_tx = input_data['transactions'][:2]
                logger.info(f"Sample transaction descriptions: {[tx.get('description') for tx in sample_tx]}")
            
            extraction_result = self.company_extractor.extract_with_context(
                input_data, 
                explicit_companies=companies
            )
            extracted_companies = extraction_result['companies']
            
            logger.info(f"Extracted companies: {extracted_companies}")
            
            if not extracted_companies:
                logger.warning("No companies extracted, returning minimal augmentation")
                logger.warning("This usually means no company names were found in transaction descriptions")
                return self._create_empty_response(prompt_text, start_time)
            
            self.stats['companies_analyzed'] += len(extracted_companies)
            logger.info(f"Extracted {len(extracted_companies)} companies")
            
            # Step 2: Check cache
            cached_data = None
            if self.qdrant_cache:
                logger.info("Step 2: Checking cache...")
                cached_data = self.qdrant_cache.get_cached_augmentation(
                    extracted_companies, 
                    context
                )
                
                if cached_data:
                    self.stats['cache_hits'] += 1
                    logger.info("Cache hit! Using cached augmentation")
                    
                    # Enhance prompt with cached data
                    augmented_prompt = self._enhance_prompt(
                        prompt_text,
                        cached_data['augmented_data']
                    )
                    
                    processing_time = (time.time() - start_time) * 1000
                    
                    return {
                        'augmented_prompt': augmented_prompt,
                        'companies_analyzed': cached_data['companies_analyzed'],
                        'augmentation_summary': cached_data['augmented_data'],
                        'cache_hit': True,
                        'processing_time_ms': round(processing_time, 2),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    self.stats['cache_misses'] += 1
                    logger.info("Cache miss, proceeding with fresh augmentation")
            
            # Step 3: Scrape web data (if enabled)
            company_data = {}
            if self.web_scraper:
                logger.info("Step 3: Scraping web data...")
                company_data = self._scrape_companies(extracted_companies[:5])  # Limit to 5
                self.stats['web_scrapes'] += len(company_data)
            
            # Step 4: LLM-based research and synthesis (if enabled)
            company_insights = []
            market_trends = {}
            
            if self.llm_researcher:
                logger.info("Step 4: Performing LLM research...")
                
                # Synthesize insights for each company
                for company_name in extracted_companies[:3]:  # Limit to top 3
                    scraped_data = company_data.get(company_name, {})
                    insights = self.llm_researcher.synthesize_company_insights(
                        company_name,
                        scraped_data
                    )
                    company_insights.append(insights)
                    self.stats['llm_calls'] += 1
                
                # Analyze market trends
                primary_industry = None
                if company_data:
                    for data in company_data.values():
                        if data.get('industry'):
                            primary_industry = data['industry']
                            break
                
                market_trends = self.llm_researcher.analyze_market_trends(
                    industry=primary_industry,
                    scraped_trends={}
                )
                self.stats['llm_calls'] += 1
            
            # Step 5: Create augmentation summary
            logger.info("Step 5: Creating augmentation summary...")
            augmentation_data = self._create_augmentation_summary(
                extracted_companies,
                company_data,
                company_insights,
                market_trends
            )
            
            # Step 6: Store in cache (if enabled)
            if self.qdrant_cache:
                logger.info("Step 6: Storing in cache...")
                self.qdrant_cache.store_augmentation(
                    extracted_companies,
                    augmentation_data,
                    context
                )
            
            # Step 7: Enhance prompt
            augmented_prompt = self._enhance_prompt(prompt_text, augmentation_data)
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.info(f"Augmentation complete in {processing_time:.2f}ms")
            
            return {
                'augmented_prompt': augmented_prompt,
                'companies_analyzed': extracted_companies,
                'augmentation_summary': augmentation_data,
                'cache_hit': False,
                'processing_time_ms': round(processing_time, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Augmentation failed: {e}", exc_info=True)
            
            # Return graceful fallback
            processing_time = (time.time() - start_time) * 1000
            return {
                'augmented_prompt': prompt_text or "",
                'companies_analyzed': [],
                'augmentation_summary': {'error': str(e)},
                'cache_hit': False,
                'processing_time_ms': round(processing_time, 2),
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _scrape_companies(self, companies: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Scrape data for multiple companies
        
        Args:
            companies: List of company names
            
        Returns:
            Dictionary mapping company names to scraped data
        """
        company_data = {}
        
        for company in companies:
            try:
                data = self.web_scraper.scrape_company_info(company)
                news = self.web_scraper.scrape_news(company, limit=3)
                data['news_items'] = news
                company_data[company] = data
            except Exception as e:
                logger.warning(f"Failed to scrape {company}: {e}")
                company_data[company] = {'error': str(e)}
        
        return company_data
    
    def _create_augmentation_summary(self, companies: List[str],
                                    company_data: Dict[str, Any],
                                    company_insights: List[Dict[str, Any]],
                                    market_trends: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create augmentation summary from all collected data
        
        Args:
            companies: List of companies
            company_data: Scraped company data
            company_insights: LLM-generated insights
            market_trends: Market trend analysis
            
        Returns:
            Augmentation summary dictionary
        """
        summary = {
            'company_count': len(companies),
            'companies': []
        }
        
        # Add company information
        for company in companies[:3]:  # Top 3
            company_info = {
                'name': company,
                'overview': None,
                'insights': [],
                'news': []
            }
            
            # Add scraped data
            if company in company_data:
                data = company_data[company]
                company_info['overview'] = data.get('overview')
                company_info['industry'] = data.get('industry')
                
                # Add news
                news_items = data.get('news_items', [])
                for news in news_items[:2]:
                    company_info['news'].append(news.get('title', ''))
            
            # Add LLM insights
            for insight_data in company_insights:
                if insight_data.get('company_name') == company:
                    company_info['insights'] = insight_data.get('insights', [])
                    break
            
            summary['companies'].append(company_info)
        
        # Add market trends
        if market_trends:
            summary['market_trends'] = market_trends.get('trends', [])
            summary['industry'] = market_trends.get('industry')
        
        return summary
    
    def _enhance_prompt(self, original_prompt: str, 
                       augmentation_data: Dict[str, Any]) -> str:
        """
        Enhance prompt with augmentation data
        
        Args:
            original_prompt: Original prompt text
            augmentation_data: Augmentation data to add
            
        Returns:
            Enhanced prompt
        """
        if not original_prompt:
            original_prompt = "Analyze the provided financial data."
        
        # Build augmentation text
        augmentation_parts = []
        
        # Add company context
        companies = augmentation_data.get('companies', [])
        if companies:
            augmentation_parts.append("\n## Company Intelligence Context\n")
            
            for company_info in companies[:3]:
                name = company_info.get('name', 'Unknown')
                augmentation_parts.append(f"\n**{name}:**")
                
                # Add overview
                overview = company_info.get('overview')
                if overview:
                    augmentation_parts.append(f"- Overview: {overview[:200]}...")
                
                # Add insights
                insights = company_info.get('insights', [])
                for insight in insights[:2]:
                    augmentation_parts.append(f"- {insight[:150]}")
                
                # Add news
                news = company_info.get('news', [])
                if news:
                    augmentation_parts.append(f"- Recent: {news[0][:150]}")
        
        # Add market trends
        trends = augmentation_data.get('market_trends', [])
        if trends:
            augmentation_parts.append("\n## Market Context\n")
            for trend in trends[:3]:
                augmentation_parts.append(f"- {trend[:150]}")
        
        # Combine
        if augmentation_parts:
            augmentation_text = "\n".join(augmentation_parts)
            enhanced = f"""{original_prompt}

---
{augmentation_text}

*Consider the above business intelligence context in your analysis for more informed insights.*
"""
            return enhanced
        
        return original_prompt
    
    def _create_empty_response(self, prompt_text: str, start_time: float) -> Dict[str, Any]:
        """Create empty response when no augmentation possible"""
        processing_time = (time.time() - start_time) * 1000
        
        return {
            'augmented_prompt': prompt_text or "",
            'companies_analyzed': [],
            'augmentation_summary': {
                'company_count': 0,
                'companies': [],
                'message': 'No companies identified for augmentation'
            },
            'cache_hit': False,
            'processing_time_ms': round(processing_time, 2),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        stats = self.stats.copy()
        
        # Add cache stats if available
        if self.qdrant_cache:
            cache_stats = self.qdrant_cache.get_stats()
            stats['cache_stats'] = cache_stats
        
        return stats
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        if self.qdrant_cache:
            self.qdrant_cache.cleanup_expired()

