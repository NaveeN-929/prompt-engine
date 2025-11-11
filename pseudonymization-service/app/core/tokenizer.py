"""
Advanced Tokenization Module
Generates reversible pseudonyms for different PII types
"""

import hashlib
import hmac
import uuid
import re
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Tokenizer:
    """
    Advanced tokenization with type-specific pseudonym generation
    """
    
    def __init__(self, key_manager):
        self.key_manager = key_manager
    
    def tokenize_name(self, name: str) -> str:
        """Generate pseudonym for names"""
        key = self.key_manager.get_current_key()
        hmac_obj = hmac.new(key.encode('utf-8'), name.encode('utf-8'), hashlib.sha256)
        token = hmac_obj.hexdigest()[:8].upper()
        return f"USER_{token}"
    
    def tokenize_email(self, email: str) -> str:
        """Generate pseudonym for email addresses"""
        key = self.key_manager.get_current_key()
        hmac_obj = hmac.new(key.encode('utf-8'), email.encode('utf-8'), hashlib.sha256)
        token = hmac_obj.hexdigest()[:8].upper()
        
        # Keep domain structure for utility
        if '@' in email:
            domain = email.split('@')[1]
            return f"EMAIL_{token}@anon.{domain}"
        return f"EMAIL_{token}@anon.local"
    
    def tokenize_phone(self, phone: str) -> str:
        """Generate pseudonym for phone numbers"""
        # Remove formatting
        clean_phone = re.sub(r'\D', '', phone)
        key = self.key_manager.get_current_key()
        hmac_obj = hmac.new(key.encode('utf-8'), clean_phone.encode('utf-8'), hashlib.sha256)
        token = hmac_obj.hexdigest()[:6].upper()
        return f"PHONE_{token}"
    
    def tokenize_ssn(self, ssn: str) -> str:
        """Generate pseudonym for SSN"""
        key = self.key_manager.get_current_key()
        hmac_obj = hmac.new(key.encode('utf-8'), ssn.encode('utf-8'), hashlib.sha256)
        token = hmac_obj.hexdigest()[:9].upper()
        return f"SSN_{token}"
    
    def tokenize_credit_card(self, card: str) -> str:
        """Generate pseudonym for credit card numbers"""
        # Remove formatting
        clean_card = re.sub(r'\D', '', card)
        key = self.key_manager.get_current_key()
        hmac_obj = hmac.new(key.encode('utf-8'), clean_card.encode('utf-8'), hashlib.sha256)
        token = hmac_obj.hexdigest()[:12].upper()
        return f"CARD_{token}"
    
    def tokenize_account(self, account: str) -> str:
        """Generate pseudonym for account numbers"""
        key = self.key_manager.get_current_key()
        hmac_obj = hmac.new(key.encode('utf-8'), account.encode('utf-8'), hashlib.sha256)
        token = hmac_obj.hexdigest()[:10].upper()
        return f"ACCT_{token}"
    
    def tokenize_address(self, address: str) -> str:
        """Generate pseudonym for addresses"""
        key = self.key_manager.get_current_key()
        hmac_obj = hmac.new(key.encode('utf-8'), address.encode('utf-8'), hashlib.sha256)
        token = hmac_obj.hexdigest()[:10].upper()
        return f"ADDR_{token}"
    
    def tokenize_ip_address(self, ip: str) -> str:
        """Generate pseudonym for IP addresses"""
        key = self.key_manager.get_current_key()
        hmac_obj = hmac.new(key.encode('utf-8'), ip.encode('utf-8'), hashlib.sha256)
        token = hmac_obj.hexdigest()[:8].upper()
        return f"IP_{token}"
    
    def tokenize_customer_id(self, customer_id: str) -> str:
        """Generate pseudonym for customer IDs"""
        key = self.key_manager.get_current_key()
        hmac_obj = hmac.new(key.encode('utf-8'), customer_id.encode('utf-8'), hashlib.sha256)
        token = hmac_obj.hexdigest()[:12].upper()
        return f"CUST_{token}"
    
    def tokenize_generic(self, value: str, pii_type: str = 'UNKNOWN') -> str:
        """Generic tokenization for unknown PII types"""
        key = self.key_manager.get_current_key()
        hmac_obj = hmac.new(key.encode('utf-8'), value.encode('utf-8'), hashlib.sha256)
        token = hmac_obj.hexdigest()[:10].upper()
        return f"{pii_type.upper()}_{token}"
    
    def tokenize_by_type(self, value: str, pii_type: str) -> str:
        """
        Route tokenization based on PII type
        
        Args:
            value: Original value to tokenize
            pii_type: Type of PII
            
        Returns:
            Tokenized value
        """
        tokenizers = {
            'name': self.tokenize_name,
            'email': self.tokenize_email,
            'phone': self.tokenize_phone,
            'ssn': self.tokenize_ssn,
            'credit_card': self.tokenize_credit_card,
            'bank_account': self.tokenize_account,
            'address': self.tokenize_address,
            'ip_address': self.tokenize_ip_address,
            'customer_id': self.tokenize_customer_id,
        }
        
        tokenizer = tokenizers.get(pii_type, self.tokenize_generic)
        
        if pii_type not in tokenizers:
            return tokenizer(value, pii_type)
        else:
            return tokenizer(value)

