"""
Web Scraper Module
Scrapes company information from the web
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus, urlparse
import re

logger = logging.getLogger(__name__)


class WebScraper:
    """Scrape company information from web sources"""
    
    def __init__(self, user_agent: str, timeout: int = 10, 
                 rate_limit_delay: float = 1.0, max_retries: int = 3):
        """
        Initialize web scraper
        
        Args:
            user_agent: User agent string for requests
            timeout: Request timeout in seconds
            rate_limit_delay: Delay between requests in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        self.last_request_time = 0
        
    def _respect_rate_limit(self):
        """Ensure rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def _safe_get(self, url: str) -> Optional[requests.Response]:
        """
        Safely perform HTTP GET request with retries
        
        Args:
            url: URL to fetch
            
        Returns:
            Response object or None if failed
        """
        self._respect_rate_limit()
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def scrape_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Scrape information about a company from multiple sources
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dictionary with company information
        """
        logger.info(f"Scraping information for: {company_name}")
        
        result = {
            'company_name': company_name,
            'overview': None,
            'news': [],
            'industry': None,
            'founded': None,
            'headquarters': None,
            'key_people': [],
            'recent_events': [],
            'linkedin_profile': None,
            'latest_trends': [],
            'sources': []
        }
        
        try:
            # 1. Try LinkedIn search
            linkedin_info = self._search_linkedin(company_name)
            if linkedin_info:
                result['linkedin_profile'] = linkedin_info.get('profile_url')
                result['overview'] = linkedin_info.get('about') or result['overview']
                result['industry'] = linkedin_info.get('industry') or result['industry']
                result['headquarters'] = linkedin_info.get('location') or result['headquarters']
                result['sources'].append('LinkedIn')
            
            # 2. Google search for company overview and trends
            search_results = self._google_search_info(company_name)
            if search_results:
                result['overview'] = search_results.get('overview') or result['overview']
                result['news'].extend(search_results.get('news', []))
                result['sources'].append('Google Search')
            
            # 3. Latest trends and news
            trends = self._scrape_latest_trends(company_name)
            if trends:
                result['latest_trends'] = trends
                result['sources'].append('News Search')
            
            # 4. Wikipedia for detailed info
            wiki_info = self._scrape_wikipedia(company_name)
            if wiki_info:
                result['overview'] = wiki_info.get('overview') or result['overview']
                result['industry'] = wiki_info.get('industry') or result['industry']
                result['founded'] = wiki_info.get('founded') or result['founded']
                result['headquarters'] = wiki_info.get('headquarters') or result['headquarters']
                result['sources'].append('Wikipedia')
            
            # Remove duplicates from news
            result['news'] = list({item for item in result['news'] if item})[:5]
            result['latest_trends'] = list({item for item in result['latest_trends'] if item})[:5]
            
        except Exception as e:
            logger.error(f"Error scraping company info for {company_name}: {e}")
        
        return result
    
    def _google_search_info(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Extract company information from Google search results
        
        Args:
            company_name: Company name to search
            
        Returns:
            Dictionary with extracted information
        """
        try:
            # Google search URL
            search_query = f"{company_name} company overview"
            search_url = f"https://www.google.com/search?q={quote_plus(search_query)}"
            
            response = self._safe_get(search_url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            result = {
                'overview': None,
                'news': [],
                'sources': ['Google Search']
            }
            
            # Try to extract knowledge graph info
            knowledge_panel = soup.find('div', {'class': 'kp-wholepage'})
            if knowledge_panel:
                # Extract overview/description
                description = knowledge_panel.find('span', {'class': 'kno-rdesc'})
                if description:
                    result['overview'] = description.get_text(strip=True)
            
            # Extract news snippets
            news_items = soup.find_all('div', {'class': 'BNeawe'}, limit=5)
            for item in news_items:
                text = item.get_text(strip=True)
                if len(text) > 20:  # Filter out short snippets
                    result['news'].append(text[:200])  # Limit length
            
            return result
            
        except Exception as e:
            logger.warning(f"Error in Google search for {company_name}: {e}")
            return None
    
    def _scrape_wikipedia(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Scrape company information from Wikipedia
        
        Args:
            company_name: Company name
            
        Returns:
            Dictionary with Wikipedia information
        """
        try:
            # Wikipedia search
            wiki_search_url = f"https://en.wikipedia.org/wiki/{quote_plus(company_name.replace(' ', '_'))}"
            
            response = self._safe_get(wiki_search_url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            result = {}
            
            # Extract first paragraph as overview
            content = soup.find('div', {'id': 'mw-content-text'})
            if content:
                first_para = content.find('p', recursive=False)
                if first_para:
                    result['overview'] = first_para.get_text(strip=True)[:500]  # Limit length
            
            # Extract infobox data
            infobox = soup.find('table', {'class': 'infobox'})
            if infobox:
                rows = infobox.find_all('tr')
                for row in rows:
                    header = row.find('th')
                    data = row.find('td')
                    
                    if header and data:
                        header_text = header.get_text(strip=True).lower()
                        data_text = data.get_text(strip=True)
                        
                        if 'industry' in header_text or 'type' in header_text:
                            result['industry'] = data_text
                        elif 'founded' in header_text:
                            result['founded'] = data_text
                        elif 'headquarters' in header_text:
                            result['headquarters'] = data_text
            
            return result if result else None
            
        except Exception as e:
            logger.warning(f"Error scraping Wikipedia for {company_name}: {e}")
            return None
    
    def scrape_news(self, company_name: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Scrape recent news about a company
        
        Args:
            company_name: Company name
            limit: Maximum number of news items
            
        Returns:
            List of news items
        """
        try:
            # Google News search
            news_query = f"{company_name} news latest"
            news_url = f"https://www.google.com/search?q={quote_plus(news_query)}&tbm=nws"
            
            response = self._safe_get(news_url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            news_items = []
            
            # Extract news articles
            articles = soup.find_all('div', {'class': 'SoaBEf'}, limit=limit)
            
            for article in articles:
                try:
                    # Extract title
                    title_elem = article.find('div', {'role': 'heading'})
                    title = title_elem.get_text(strip=True) if title_elem else None
                    
                    # Extract snippet
                    snippet_elem = article.find('div', {'class': 'GI74Re'})
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else None
                    
                    # Extract source
                    source_elem = article.find('div', {'class': 'CEMjEf'})
                    source = source_elem.get_text(strip=True) if source_elem else 'Unknown'
                    
                    if title:
                        news_items.append({
                            'title': title,
                            'snippet': snippet,
                            'source': source
                        })
                
                except Exception as e:
                    logger.debug(f"Error parsing news article: {e}")
                    continue
            
            return news_items
            
        except Exception as e:
            logger.warning(f"Error scraping news for {company_name}: {e}")
            return []
    
    def _search_linkedin(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for company LinkedIn profile
        
        Args:
            company_name: Company name to search
            
        Returns:
            Dictionary with LinkedIn information
        """
        try:
            # LinkedIn company search
            search_query = f"{company_name} LinkedIn company"
            search_url = f"https://www.google.com/search?q={quote_plus(search_query)}"
            
            response = self._safe_get(search_url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            result = {
                'profile_url': None,
                'about': None,
                'industry': None,
                'location': None
            }
            
            # Try to find LinkedIn link
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if 'linkedin.com/company/' in href:
                    # Extract clean LinkedIn URL
                    if 'url?q=' in href:
                        linkedin_url = href.split('url?q=')[1].split('&')[0]
                    else:
                        linkedin_url = href
                    result['profile_url'] = linkedin_url
                    break
            
            # Extract snippets that might contain company info
            snippets = soup.find_all('div', {'class': 'BNeawe'}, limit=5)
            for snippet in snippets:
                text = snippet.get_text(strip=True)
                if len(text) > 50:
                    if not result['about'] and company_name.lower() in text.lower():
                        result['about'] = text[:300]
            
            return result if result['profile_url'] or result['about'] else None
            
        except Exception as e:
            logger.warning(f"Error searching LinkedIn for {company_name}: {e}")
            return None
    
    def _scrape_latest_trends(self, company_name: str) -> List[str]:
        """
        Scrape latest trends and news about a company
        
        Args:
            company_name: Company name
            
        Returns:
            List of trend descriptions
        """
        try:
            trends = []
            
            # Search for recent news and trends
            query = f"{company_name} latest news trends 2025"
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&tbm=nws"
            
            response = self._safe_get(search_url)
            if not response:
                return trends
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract news headlines and snippets
            articles = soup.find_all('div', limit=10)
            
            for article in articles:
                text = article.get_text(strip=True)
                # Look for meaningful content
                if len(text) > 30 and len(text) < 250:
                    if any(keyword in text.lower() for keyword in ['trend', 'growth', 'launch', 'announce', 'expand', 'new', 'latest']):
                        trends.append(text)
                        if len(trends) >= 5:
                            break
            
            return trends
            
        except Exception as e:
            logger.warning(f"Error scraping latest trends for {company_name}: {e}")
            return []
    
    def scrape_market_trends(self, industry: str = None) -> Dict[str, Any]:
        """
        Scrape general market trends
        
        Args:
            industry: Optional industry to focus on
            
        Returns:
            Dictionary with market trends
        """
        logger.info(f"Scraping market trends for industry: {industry or 'general'}")
        
        result = {
            'trends': [],
            'insights': [],
            'sources': []
        }
        
        try:
            # Search for market trends
            query = f"{industry} industry trends 2025" if industry else "business market trends 2025"
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            
            response = self._safe_get(search_url)
            if not response:
                return result
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract relevant snippets
            snippets = soup.find_all('div', {'class': 'BNeawe'}, limit=10)
            
            for snippet in snippets:
                text = snippet.get_text(strip=True)
                if len(text) > 30 and 'trend' in text.lower():
                    result['trends'].append(text[:200])
            
            result['sources'].append('Google Search')
            
        except Exception as e:
            logger.warning(f"Error scraping market trends: {e}")
        
        return result

