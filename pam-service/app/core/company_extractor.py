"""
Company Extractor Module
Extracts company names from transaction data
"""

import re
from typing import List, Dict, Any, Set
import logging

logger = logging.getLogger(__name__)


class CompanyExtractor:
    """Extract company names from transaction descriptions and merchant fields"""
    
    def __init__(self):
        # Common company suffixes
        self.company_suffixes = [
            'Inc', 'LLC', 'Ltd', 'Corp', 'Corporation', 'Company', 'Co',
            'Group', 'International', 'Enterprises', 'Solutions', 'Services',
            'Holdings', 'Partners', 'Associates', 'Industries'
        ]
        
        # Words to exclude (generic terms that aren't company names)
        self.exclude_words = {
            'payment', 'transfer', 'deposit', 'withdrawal', 'fee', 'charge',
            'debit', 'credit', 'transaction', 'monthly', 'annual', 'purchase',
            'online', 'store', 'shop', 'market', 'general', 'various',
            'miscellaneous', 'other', 'pending', 'processing'
        }
        
        # Minimum word length to consider as company name
        self.min_word_length = 3
        
    def extract_from_transactions(self, input_data: Dict[str, Any], 
                                  explicit_companies: List[str] = None) -> List[str]:
        """
        Extract company names from transaction data
        
        Args:
            input_data: Transaction data dictionary
            explicit_companies: Optional list of companies to prioritize
            
        Returns:
            List of unique company names
        """
        companies = set()
        
        # PRIORITY 1: Extract the customer's own company name
        # This is the most important - research the customer's company!
        if 'name' in input_data and input_data['name']:
            customer_company = input_data['name'].strip()
            companies.add(customer_company)
            logger.info(f"Added customer company: {customer_company}")
        
        # PRIORITY 2: Add explicit companies if provided
        if explicit_companies:
            companies.update(explicit_companies)
            logger.info(f"Added {len(explicit_companies)} explicit companies")
        
        # PRIORITY 3: Extract from transactions (merchant/vendor names)
        transactions = input_data.get('transactions', [])
        
        for transaction in transactions:
            # Extract from description
            if 'description' in transaction:
                extracted = self._extract_from_text(transaction['description'])
                companies.update(extracted)
            
            # Extract from merchant field if present
            if 'merchant' in transaction:
                extracted = self._extract_from_text(transaction['merchant'])
                companies.update(extracted)
            
            # Extract from counterparty field if present
            if 'counterparty' in transaction:
                extracted = self._extract_from_text(transaction['counterparty'])
                companies.update(extracted)
        
        # Filter and clean
        companies = self._clean_and_filter(companies)
        
        logger.info(f"Extracted {len(companies)} unique companies total")
        logger.info(f"Companies: {list(companies)}")
        return list(companies)
    
    def _extract_from_text(self, text: str) -> Set[str]:
        """
        Extract potential company names from a text string
        
        Args:
            text: Text to analyze
            
        Returns:
            Set of potential company names
        """
        if not text:
            return set()
        
        companies = set()
        
        # Pattern 1: Text followed by common suffixes (e.g., "TechCorp Inc")
        suffix_pattern = r'\b([A-Z][a-zA-Z&\s]+(?:' + '|'.join(self.company_suffixes) + r'))\b'
        matches = re.findall(suffix_pattern, text)
        companies.update(matches)
        
        # Pattern 2: Capitalized words (potential company names)
        # Look for sequences of capitalized words
        cap_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        cap_matches = re.findall(cap_pattern, text)
        
        # Only add if 2+ words or ends with common suffix
        for match in cap_matches:
            words = match.split()
            if len(words) >= 2 or any(suffix in match for suffix in self.company_suffixes):
                companies.add(match)
        
        # Pattern 3: All caps words (acronyms, e.g., "IBM", "NASA")
        acronym_pattern = r'\b([A-Z]{2,6})\b'
        acronyms = re.findall(acronym_pattern, text)
        companies.update(acronyms)
        
        return companies
    
    def _clean_and_filter(self, companies: Set[str]) -> Set[str]:
        """
        Clean and filter extracted company names
        
        Args:
            companies: Set of potential company names
            
        Returns:
            Filtered set of company names
        """
        cleaned = set()
        
        for company in companies:
            # Remove extra whitespace
            company = ' '.join(company.split())
            
            # Skip if too short
            if len(company) < self.min_word_length:
                continue
            
            # Skip if in exclude list
            if company.lower() in self.exclude_words:
                continue
            
            # Skip if all lowercase (likely not a company name)
            if company.islower():
                continue
            
            # Skip common financial terms and generic words
            financial_terms = ['invoice', 'payment', 'wire', 'ach', 'check', 'consulting', 
                             'service', 'contract', 'agreement', 'order', 'purchase']
            if any(term == company.lower() for term in financial_terms):
                continue
            
            # Skip standalone suffixes (like just "LLC", "Inc")
            if company in self.company_suffixes:
                continue
            
            # Skip if it's a phrase that starts with common action words
            action_words = ['payment from', 'payment to', 'service contract', 'consulting fees',
                          'vendor payment', 'customer payment']
            if any(company.lower().startswith(word) for word in action_words):
                # Try to extract the actual company name from the phrase
                for word in action_words:
                    if company.lower().startswith(word):
                        remaining = company[len(word):].strip()
                        if remaining and len(remaining) > 3:
                            company = remaining
                        break
            
            # Must have at least one letter
            if not any(c.isalpha() for c in company):
                continue
            
            cleaned.add(company)
        
        return cleaned
    
    def extract_with_context(self, input_data: Dict[str, Any], 
                           explicit_companies: List[str] = None) -> Dict[str, Any]:
        """
        Extract companies with additional context information
        
        Args:
            input_data: Transaction data
            explicit_companies: Optional explicit company list
            
        Returns:
            Dictionary with companies and metadata
        """
        companies = self.extract_from_transactions(input_data, explicit_companies)
        
        # Build context for each company
        company_context = {}
        transactions = input_data.get('transactions', [])
        
        for company in companies:
            # Find transactions mentioning this company
            related_transactions = []
            total_amount = 0
            
            for tx in transactions:
                tx_text = ' '.join([
                    str(tx.get('description', '')),
                    str(tx.get('merchant', '')),
                    str(tx.get('counterparty', ''))
                ])
                
                if company.lower() in tx_text.lower():
                    related_transactions.append(tx)
                    if 'amount' in tx:
                        total_amount += abs(float(tx['amount']))
            
            company_context[company] = {
                'transaction_count': len(related_transactions),
                'total_amount': round(total_amount, 2),
                'transactions': related_transactions[:5]  # Keep first 5
            }
        
        return {
            'companies': companies,
            'company_context': company_context,
            'total_companies': len(companies)
        }

