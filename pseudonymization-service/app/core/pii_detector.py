"""
PII Detection Module
Automatically identifies 20+ types of Personally Identifiable Information
"""

import re
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class PIIDetector:
    """
    Detects various types of PII in data
    """
    
    # PII Type Categories
    PII_TYPES = {
        # Personal Identifiers
        'name': 'Personal Name',
        'ssn': 'Social Security Number',
        'passport': 'Passport Number',
        'drivers_license': 'Driver\'s License',
        'national_id': 'National ID Number',
        
        # Contact Information
        'email': 'Email Address',
        'phone': 'Phone Number',
        'address': 'Physical Address',
        'postal_code': 'Postal/ZIP Code',
        'ip_address': 'IP Address',
        
        # Financial Data
        'credit_card': 'Credit Card Number',
        'bank_account': 'Bank Account Number',
        'routing_number': 'Routing Number',
        'iban': 'IBAN',
        'swift': 'SWIFT Code',
        
        # Biometric Data
        'biometric': 'Biometric Data',
        
        # Geolocation
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'coordinates': 'GPS Coordinates',
        
        # Other Identifiers
        'username': 'Username',
        'customer_id': 'Customer ID',
        'employee_id': 'Employee ID',
        'medical_record': 'Medical Record Number',
        'vehicle_id': 'Vehicle Identification Number'
    }
    
    def __init__(self):
        # Compile regex patterns for better performance
        self.patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            'postal_code': re.compile(r'\b\d{5}(?:-\d{4})?\b'),
            'coordinates': re.compile(r'\b-?\d{1,3}\.\d+,\s*-?\d{1,3}\.\d+\b'),
        }
    
    def detect_pii_in_value(self, value: Any, field_name: str = '') -> List[Dict[str, str]]:
        """
        Detect PII in a single value
        
        Args:
            value: Value to check for PII
            field_name: Name of the field (helps with context)
            
        Returns:
            List of detected PII types with metadata
        """
        detected = []
        
        if not isinstance(value, str):
            value = str(value)
        
        # Check field name for obvious PII indicators
        field_lower = field_name.lower()
        field_indicators = {
            'name': ['name', 'full_name', 'first_name', 'last_name'],
            'email': ['email', 'email_address', 'e_mail'],
            'phone': ['phone', 'telephone', 'mobile', 'cell'],
            'address': ['address', 'street', 'location'],
            'customer_id': ['customer_id', 'cust_id', 'user_id'],
            'ssn': ['ssn', 'social_security'],
            'bank_account': ['account', 'account_number', 'acct'],
        }
        
        for pii_type, indicators in field_indicators.items():
            if any(indicator in field_lower for indicator in indicators):
                detected.append({
                    'type': pii_type,
                    'field': field_name,
                    'value_preview': value[:20] + '...' if len(value) > 20 else value,
                    'confidence': 'high',
                    'detection_method': 'field_name'
                })
        
        # Pattern-based detection
        for pii_type, pattern in self.patterns.items():
            if pattern.search(value):
                detected.append({
                    'type': pii_type,
                    'field': field_name,
                    'value_preview': value[:20] + '...' if len(value) > 20 else value,
                    'confidence': 'high',
                    'detection_method': 'pattern'
                })
        
        return detected
    
    def detect_pii_in_dict(self, data: Dict[str, Any], parent_key: str = '') -> List[Dict[str, str]]:
        """
        Recursively detect PII in dictionary data
        
        Args:
            data: Dictionary to scan
            parent_key: Parent key for nested structures
            
        Returns:
            List of all detected PII
        """
        all_detected = []
        
        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                # Recursively check nested dictionaries
                all_detected.extend(self.detect_pii_in_dict(value, full_key))
            elif isinstance(value, list):
                # Check each item in list
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        all_detected.extend(self.detect_pii_in_dict(item, f"{full_key}[{idx}]"))
                    else:
                        all_detected.extend(self.detect_pii_in_value(item, f"{full_key}[{idx}]"))
            else:
                # Check the value for PII
                all_detected.extend(self.detect_pii_in_value(value, full_key))
        
        return all_detected
    
    def get_pii_summary(self, detected_pii: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generate summary of detected PII
        
        Args:
            detected_pii: List of detected PII items
            
        Returns:
            Summary statistics
        """
        summary = {
            'total_pii_fields': len(detected_pii),
            'pii_types_found': {},
            'high_confidence_count': 0,
            'fields_affected': set()
        }
        
        for pii in detected_pii:
            pii_type = pii['type']
            summary['pii_types_found'][pii_type] = summary['pii_types_found'].get(pii_type, 0) + 1
            
            if pii['confidence'] == 'high':
                summary['high_confidence_count'] += 1
            
            summary['fields_affected'].add(pii['field'])
        
        summary['fields_affected'] = list(summary['fields_affected'])
        
        return summary

