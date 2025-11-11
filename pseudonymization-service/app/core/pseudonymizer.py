"""
Core Pseudonymization Logic
Handles anonymization of sensitive financial data with advanced PII detection
"""

import hashlib
import hmac
import uuid
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
import logging

from .pii_detector import PIIDetector
from .tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class Pseudonymizer:
    """
    Handles pseudonymization of sensitive financial data with PII detection
    """
    
    def __init__(self, key_manager):
        self.key_manager = key_manager
        self.pii_detector = PIIDetector()
        self.tokenizer = Tokenizer(key_manager)
        self.pseudonym_map = {}  # In-memory map (in production, use Redis/database)
        self.stats = {
            "total_pseudonymized": 0,
            "total_fields_processed": 0,
            "total_pii_detected": 0,
            "pii_types_processed": {},
            "last_pseudonymization": None
        }
    
    def pseudonymize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pseudonymize data with automatic PII detection
        
        Args:
            data: Original data
            
        Returns:
            Dictionary with pseudonymized data and metadata
        """
        # Generate unique pseudonym ID
        pseudonym_id = str(uuid.uuid4())
        
        # Detect PII in the data
        detected_pii = self.pii_detector.detect_pii_in_dict(data)
        pii_summary = self.pii_detector.get_pii_summary(detected_pii)
        
        # Deep copy to avoid modifying original
        pseudonymized_data = json.loads(json.dumps(data))
        fields_pseudonymized = []
        pii_detections = []
        
        # Pseudonymize detected PII fields
        pseudonymized_data = self._pseudonymize_recursive(
            pseudonymized_data, 
            detected_pii,
            fields_pseudonymized,
            pii_detections
        )
        
        # Additional field-specific pseudonymization
        if 'transactions' in pseudonymized_data:
            for transaction in pseudonymized_data['transactions']:
                # Pseudonymize amounts (add noise while preserving general magnitude)
                if 'amount' in transaction:
                    transaction['amount'] = self._pseudonymize_amount(transaction['amount'])
                    if 'transaction.amount' not in fields_pseudonymized:
                        fields_pseudonymized.append('transaction.amount')
                
                # Pseudonymize dates (shift by random offset)
                if 'date' in transaction:
                    transaction['date'] = self._pseudonymize_date(transaction['date'])
                    if 'transaction.date' not in fields_pseudonymized:
                        fields_pseudonymized.append('transaction.date')
        
        # Store mapping for reversal
        self.pseudonym_map[pseudonym_id] = {
            'original_data': data,
            'created_at': datetime.utcnow().isoformat(),
            'fields_pseudonymized': list(set(fields_pseudonymized)),
            'pii_detected': pii_detections,
            'pii_summary': pii_summary
        }
        
        # Update statistics
        self.stats['total_pseudonymized'] += 1
        self.stats['total_fields_processed'] += len(set(fields_pseudonymized))
        self.stats['total_pii_detected'] += len(detected_pii)
        self.stats['last_pseudonymization'] = datetime.utcnow().isoformat()
        
        # Update PII type stats
        for pii_type, count in pii_summary['pii_types_found'].items():
            self.stats['pii_types_processed'][pii_type] = \
                self.stats['pii_types_processed'].get(pii_type, 0) + count
        
        logger.info(f"Pseudonymized data: {len(set(fields_pseudonymized))} fields, {len(detected_pii)} PII items detected")
        
        return {
            'data': pseudonymized_data,
            'pseudonym_id': pseudonym_id,
            'fields_pseudonymized': list(set(fields_pseudonymized)),
            'pii_detected': pii_detections,
            'pii_summary': pii_summary
        }
    
    def _pseudonymize_recursive(
        self,
        data: Any,
        detected_pii: List[Dict],
        fields_pseudonymized: List[str],
        pii_detections: List[Dict],
        parent_key: str = ''
    ) -> Any:
        """
        Recursively pseudonymize data based on detected PII
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                
                # Check if this field contains PII
                field_pii = [p for p in detected_pii if p['field'] == full_key]
                
                if field_pii and isinstance(value, str):
                    # Pseudonymize this field
                    pii_type = field_pii[0]['type']
                    pseudonymized_value = self.tokenizer.tokenize_by_type(value, pii_type)
                    result[key] = pseudonymized_value
                    fields_pseudonymized.append(full_key)
                    pii_detections.append({
                        'field': full_key,
                        'type': pii_type,
                        'original_preview': value[:20] + '...' if len(value) > 20 else value,
                        'pseudonymized': pseudonymized_value
                    })
                else:
                    result[key] = self._pseudonymize_recursive(
                        value, detected_pii, fields_pseudonymized, pii_detections, full_key
                    )
            return result
        elif isinstance(data, list):
            return [
                self._pseudonymize_recursive(
                    item, detected_pii, fields_pseudonymized, pii_detections, 
                    f"{parent_key}[{idx}]"
                )
                for idx, item in enumerate(data)
            ]
        else:
            return data
    
    def _pseudonymize_id(self, identifier: str) -> str:
        """
        Pseudonymize an identifier using HMAC
        """
        key = self.key_manager.get_current_key()
        hmac_obj = hmac.new(
            key.encode('utf-8'),
            identifier.encode('utf-8'),
            hashlib.sha256
        )
        return f"PSEUDO_{hmac_obj.hexdigest()[:16].upper()}"
    
    def _pseudonymize_amount(self, amount: float) -> float:
        """
        Pseudonymize amount by adding deterministic noise
        Preserves general magnitude and sign
        """
        # Use amount as seed for deterministic pseudonymization
        noise_seed = int(abs(amount * 1000)) % 100
        noise_factor = 1 + (noise_seed - 50) / 500  # ±10% noise
        
        pseudonymized = round(amount * noise_factor, 2)
        return pseudonymized
    
    def _pseudonymize_date(self, date_str: str) -> str:
        """
        Pseudonymize date by shifting by deterministic offset
        Preserves temporal relationships
        """
        try:
            # Parse date
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Deterministic offset based on date hash
            date_hash = hashlib.md5(date_str.encode()).hexdigest()
            offset_days = int(date_hash[:4], 16) % 60 - 30  # ±30 days
            
            # Shift date
            pseudonymized_date = date_obj + timedelta(days=offset_days)
            return pseudonymized_date.date().isoformat()
        except Exception as e:
            logger.warning(f"Date pseudonymization failed: {str(e)}")
            return date_str
    
    def _pseudonymize_text(self, text: str) -> str:
        """
        Pseudonymize text by creating a hash-based representation
        """
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]
        
        # Categorize based on common patterns
        categories = {
            'salary': 'INCOME_CAT_A',
            'rent': 'EXPENSE_CAT_B',
            'grocery': 'EXPENSE_CAT_C',
            'dining': 'EXPENSE_CAT_D',
            'loan': 'DEBT_CAT_E',
            'bonus': 'INCOME_CAT_F'
        }
        
        text_lower = text.lower()
        for keyword, category in categories.items():
            if keyword in text_lower:
                return f"{category}_{text_hash}"
        
        return f"TRANSACTION_{text_hash}"
    
    def get_original_data(self, pseudonym_id: str) -> Dict[str, Any]:
        """
        Retrieve original data (for repersonalization service)
        """
        if pseudonym_id not in self.pseudonym_map:
            raise ValueError(f"Pseudonym ID not found: {pseudonym_id}")
        
        return self.pseudonym_map[pseudonym_id]['original_data']
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pseudonymization statistics"""
        return {
            **self.stats,
            "active_pseudonyms": len(self.pseudonym_map)
        }
    
    def clear_pseudonym(self, pseudonym_id: str):
        """Clear a pseudonym mapping (after successful repersonalization)"""
        if pseudonym_id in self.pseudonym_map:
            del self.pseudonym_map[pseudonym_id]
            logger.info(f"Cleared pseudonym: {pseudonym_id}")

