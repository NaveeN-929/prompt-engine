"""
Core Repersonalization Logic
Handles restoration of original data from pseudonymized versions
"""

import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class Repersonalizer:
    """
    Handles repersonalization of pseudonymized data
    """
    
    def __init__(self, key_manager, pseudonymization_service_url: str):
        self.key_manager = key_manager
        self.pseudonymization_service_url = pseudonymization_service_url
        self.stats = {
            "total_repersonalized": 0,
            "total_failed": 0,
            "last_repersonalization": None
        }
    
    def repersonalize(
        self,
        pseudonym_id: str,
        verify: bool = True
    ) -> Dict[str, Any]:
        """
        Restore original data from pseudonymized version
        
        Args:
            pseudonym_id: Unique identifier for the pseudonymized data
            verify: Whether to verify data integrity
            
        Returns:
            Dictionary with original data and metadata
        """
        try:
            # Request original data from pseudonymization service
            response = requests.post(
                f"{self.pseudonymization_service_url}/repersonalize/retrieve",
                json={"pseudonym_id": pseudonym_id},
                timeout=10
            )
            
            if response.status_code == 404:
                self.stats['total_failed'] += 1
                raise ValueError(f"Pseudonym ID not found: {pseudonym_id}")
            
            if response.status_code != 200:
                self.stats['total_failed'] += 1
                raise Exception(f"Failed to retrieve data: {response.text}")
            
            result = response.json()
            original_data = result.get('original_data')
            
            if not original_data:
                self.stats['total_failed'] += 1
                raise ValueError("No original data returned")
            
            # Verify data integrity if requested
            verified = False
            if verify:
                verified = self._verify_data_integrity(
                    original_data,
                    result.get('fields_pseudonymized', [])
                )
            
            # Update statistics
            self.stats['total_repersonalized'] += 1
            self.stats['last_repersonalization'] = datetime.utcnow().isoformat()
            
            logger.info(f"Repersonalized data for pseudonym: {pseudonym_id}")
            
            return {
                'original_data': original_data,
                'verified': verified,
                'pseudonym_id': pseudonym_id
            }
            
        except requests.exceptions.RequestException as e:
            self.stats['total_failed'] += 1
            logger.error(f"Request to pseudonymization service failed: {str(e)}")
            raise Exception(f"Cannot connect to pseudonymization service: {str(e)}")
        except Exception as e:
            self.stats['total_failed'] += 1
            logger.error(f"Repersonalization failed: {str(e)}")
            raise
    
    def _verify_data_integrity(
        self,
        data: Dict[str, Any],
        fields_pseudonymized: list
    ) -> bool:
        """
        Verify that restored data has proper structure
        
        Args:
            data: Original data to verify
            fields_pseudonymized: List of fields that were pseudonymized
            
        Returns:
            True if data appears valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = ['customer_id', 'account_balance', 'transactions']
            for field in required_fields:
                if field not in data:
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Verify transactions structure
            if not isinstance(data['transactions'], list):
                logger.warning("Transactions is not a list")
                return False
            
            for transaction in data['transactions']:
                required_tx_fields = ['date', 'amount', 'type', 'description']
                for field in required_tx_fields:
                    if field not in transaction:
                        logger.warning(f"Transaction missing field: {field}")
                        return False
            
            # Verify numeric fields
            if not isinstance(data['account_balance'], (int, float)):
                logger.warning("Account balance is not numeric")
                return False
            
            logger.info("Data integrity verification passed")
            return True
            
        except Exception as e:
            logger.error(f"Data verification failed: {str(e)}")
            return False
    
    def batch_repersonalize(
        self,
        pseudonym_ids: list,
        verify: bool = True
    ) -> list:
        """
        Repersonalize multiple datasets
        
        Args:
            pseudonym_ids: List of pseudonym IDs
            verify: Whether to verify each dataset
            
        Returns:
            List of repersonalization results
        """
        results = []
        for pseudonym_id in pseudonym_ids:
            try:
                result = self.repersonalize(pseudonym_id, verify=verify)
                results.append({
                    'success': True,
                    'pseudonym_id': pseudonym_id,
                    'original_data': result['original_data'],
                    'verified': result['verified']
                })
            except Exception as e:
                logger.error(f"Failed to repersonalize {pseudonym_id}: {str(e)}")
                results.append({
                    'success': False,
                    'pseudonym_id': pseudonym_id,
                    'error': str(e)
                })
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get repersonalization statistics"""
        return {
            **self.stats,
            "success_rate": (
                self.stats['total_repersonalized'] / 
                max(self.stats['total_repersonalized'] + self.stats['total_failed'], 1)
            ) * 100
        }

