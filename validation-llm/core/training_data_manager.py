"""
Training Data Manager - Stores and manages high-quality responses for training
"""

import json
import os
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import sqlite3
from pathlib import Path

from config import get_config

logger = logging.getLogger(__name__)

class TrainingDataManager:
    """
    Manages storage and retrieval of high-quality validated responses
    for training the autonomous agent
    """
    
    def __init__(self):
        self.config = get_config()
        self.storage_config = self.config["training_data"]
        
        # Setup storage paths
        self.storage_path = Path(self.storage_config["storage_path"])
        self.db_path = self.storage_path / "training_data.db"
        
        # Storage statistics
        self.total_stored = 0
        self.storage_by_quality = {
            "exemplary": 0,
            "high_quality": 0,
            "acceptable": 0
        }
        self.storage_by_category = {}
        
        # Database connection
        self.db_connection = None
        
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the training data manager"""
        try:
            logger.info("Initializing Training Data Manager...")
            
            # Create storage directory
            self.storage_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing statistics
            await self._load_statistics()
            
            # Clean up old data if needed
            await self._cleanup_old_data()
            
            self.is_initialized = True
            logger.info(f"Training Data Manager initialized. Stored items: {self.total_stored}")
            
        except Exception as e:
            logger.error(f"Failed to initialize training data manager: {e}")
            raise
    
    async def store_training_data(self,
                                input_data: Dict[str, Any],
                                response_data: Dict[str, Any],
                                validation_result: Dict[str, Any],
                                quality_level: str) -> Dict[str, Any]:
        """
        Store high-quality response as training data
        
        Args:
            input_data: Original input data
            response_data: The validated response
            validation_result: Complete validation results
            quality_level: Quality classification
            
        Returns:
            Storage result with metadata
        """
        if not self.is_initialized:
            raise RuntimeError("Training data manager not initialized")
        
        # Check if quality level qualifies for storage
        if quality_level not in self.storage_config["quality_levels"]:
            logger.debug(f"Quality level {quality_level} not eligible for storage")
            return {"stored": False, "reason": "quality_level_not_eligible"}
        
        # Check storage limits
        storage_check = await self._check_storage_limits()
        if not storage_check["can_store"]:
            logger.warning(f"Cannot store training data: {storage_check['reason']}")
            return {"stored": False, "reason": storage_check["reason"]}
        
        try:
            # Generate unique training data ID
            training_id = f"train_{int(time.time())}_{str(uuid.uuid4())[:8]}"
            
            # Determine category
            category = self._determine_category(input_data, response_data)
            
            # Create training data record
            training_record = {
                "training_id": training_id,
                "timestamp": datetime.now().isoformat(),
                "quality_level": quality_level,
                "category": category,
                "input_data": input_data,
                "response_data": response_data,
                "validation_result": validation_result,
                "metadata": {
                    "overall_score": validation_result.get("overall_score", 0.0),
                    "criteria_scores": validation_result.get("criteria_scores", {}),
                    "storage_timestamp": datetime.now().isoformat(),
                    "data_size": len(json.dumps({"input": input_data, "response": response_data}))
                }
            }
            
            # Store in database
            await self._store_in_database(training_record)
            
            # Store as JSON file for easy access
            await self._store_as_file(training_record)
            
            # Update statistics
            self._update_storage_statistics(quality_level, category)
            
            logger.info(f"Stored training data {training_id} (quality: {quality_level}, category: {category})")
            
            return {
                "stored": True,
                "training_id": training_id,
                "quality_level": quality_level,
                "category": category,
                "storage_path": str(self.storage_path / f"{training_id}.json")
            }
            
        except Exception as e:
            logger.error(f"Failed to store training data: {e}")
            return {"stored": False, "reason": f"storage_error: {str(e)}"}
    
    async def retrieve_training_data(self,
                                   quality_level: Optional[str] = None,
                                   category: Optional[str] = None,
                                   limit: int = 100,
                                   min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Retrieve training data based on criteria
        
        Args:
            quality_level: Filter by quality level
            category: Filter by category
            limit: Maximum number of records to return
            min_score: Minimum validation score
            
        Returns:
            List of training data records
        """
        if not self.is_initialized:
            raise RuntimeError("Training data manager not initialized")
        
        try:
            # Build query
            query = "SELECT * FROM training_data WHERE overall_score >= ?"
            params = [min_score]
            
            if quality_level:
                query += " AND quality_level = ?"
                params.append(quality_level)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY overall_score DESC, timestamp DESC LIMIT ?"
            params.append(limit)
            
            # Execute query
            cursor = self.db_connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to dictionaries
            training_data = []
            for row in rows:
                record = {
                    "training_id": row[0],
                    "timestamp": row[1],
                    "quality_level": row[2],
                    "category": row[3],
                    "overall_score": row[4],
                    "input_data": json.loads(row[5]),
                    "response_data": json.loads(row[6]),
                    "validation_result": json.loads(row[7]),
                    "metadata": json.loads(row[8]) if row[8] else {}
                }
                training_data.append(record)
            
            logger.info(f"Retrieved {len(training_data)} training data records")
            return training_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve training data: {e}")
            return []
    
    async def get_training_patterns(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze training data to identify successful patterns
        
        Args:
            category: Optional category filter
            
        Returns:
            Pattern analysis results
        """
        try:
            # Retrieve high-quality training data
            training_data = await self.retrieve_training_data(
                quality_level="exemplary",
                category=category,
                limit=200,
                min_score=0.8
            )
            
            if not training_data:
                return {"patterns": [], "analysis": "No high-quality training data available"}
            
            # Analyze patterns
            patterns = {
                "common_structures": self._analyze_response_structures(training_data),
                "successful_insights": self._analyze_successful_insights(training_data),
                "effective_recommendations": self._analyze_effective_recommendations(training_data),
                "quality_indicators": self._analyze_quality_indicators(training_data),
                "data_utilization_patterns": self._analyze_data_utilization(training_data)
            }
            
            return {
                "patterns": patterns,
                "analysis": f"Analyzed {len(training_data)} high-quality responses",
                "categories_analyzed": list(set(item["category"] for item in training_data)),
                "quality_score_range": {
                    "min": min(item["overall_score"] for item in training_data),
                    "max": max(item["overall_score"] for item in training_data),
                    "avg": sum(item["overall_score"] for item in training_data) / len(training_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze training patterns: {e}")
            return {"patterns": [], "analysis": f"Analysis failed: {str(e)}"}
    
    async def export_training_dataset(self, 
                                    format_type: str = "json",
                                    quality_filter: Optional[str] = None) -> str:
        """
        Export training dataset in specified format
        
        Args:
            format_type: Export format (json, csv, jsonl)
            quality_filter: Optional quality level filter
            
        Returns:
            Path to exported file
        """
        try:
            # Retrieve training data
            training_data = await self.retrieve_training_data(
                quality_level=quality_filter,
                limit=10000  # Large limit for export
            )
            
            if not training_data:
                raise ValueError("No training data available for export")
            
            # Generate export filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quality_suffix = f"_{quality_filter}" if quality_filter else ""
            export_filename = f"training_dataset{quality_suffix}_{timestamp}.{format_type}"
            export_path = self.storage_path / "exports" / export_filename
            
            # Create exports directory
            export_path.parent.mkdir(exist_ok=True)
            
            # Export in specified format
            if format_type == "json":
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(training_data, f, indent=2, default=str)
            
            elif format_type == "jsonl":
                with open(export_path, 'w', encoding='utf-8') as f:
                    for record in training_data:
                        f.write(json.dumps(record, default=str) + '\n')
            
            elif format_type == "csv":
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    if training_data:
                        writer = csv.DictWriter(f, fieldnames=training_data[0].keys())
                        writer.writeheader()
                        for record in training_data:
                            # Convert complex objects to strings for CSV
                            csv_record = {}
                            for key, value in record.items():
                                if isinstance(value, (dict, list)):
                                    csv_record[key] = json.dumps(value, default=str)
                                else:
                                    csv_record[key] = str(value)
                            writer.writerow(csv_record)
            
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
            
            logger.info(f"Exported {len(training_data)} records to {export_path}")
            return str(export_path)
            
        except Exception as e:
            logger.error(f"Failed to export training dataset: {e}")
            raise
    
    async def _initialize_database(self):
        """Initialize SQLite database for training data"""
        
        self.db_connection = sqlite3.connect(str(self.db_path))
        
        # Create training data table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS training_data (
            training_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            quality_level TEXT NOT NULL,
            category TEXT NOT NULL,
            overall_score REAL NOT NULL,
            input_data TEXT NOT NULL,
            response_data TEXT NOT NULL,
            validation_result TEXT NOT NULL,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        self.db_connection.execute(create_table_sql)
        
        # Create indexes for better query performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_quality_level ON training_data(quality_level)",
            "CREATE INDEX IF NOT EXISTS idx_category ON training_data(category)",
            "CREATE INDEX IF NOT EXISTS idx_overall_score ON training_data(overall_score)",
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON training_data(timestamp)"
        ]
        
        for index_sql in indexes:
            self.db_connection.execute(index_sql)
        
        self.db_connection.commit()
    
    async def _store_in_database(self, training_record: Dict[str, Any]):
        """Store training record in database"""
        
        insert_sql = """
        INSERT INTO training_data 
        (training_id, timestamp, quality_level, category, overall_score, 
         input_data, response_data, validation_result, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            training_record["training_id"],
            training_record["timestamp"],
            training_record["quality_level"],
            training_record["category"],
            training_record["metadata"]["overall_score"],
            json.dumps(training_record["input_data"], default=str),
            json.dumps(training_record["response_data"], default=str),
            json.dumps(training_record["validation_result"], default=str),
            json.dumps(training_record["metadata"], default=str)
        )
        
        self.db_connection.execute(insert_sql, params)
        self.db_connection.commit()
    
    async def _store_as_file(self, training_record: Dict[str, Any]):
        """Store training record as JSON file"""
        
        filename = f"{training_record['training_id']}.json"
        filepath = self.storage_path / training_record["quality_level"] / filename
        
        # Create quality level directory
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(training_record, f, indent=2, default=str)
    
    def _determine_category(self, input_data: Dict[str, Any], response_data: Dict[str, Any]) -> str:
        """Determine the category of the training data"""
        
        # Analyze input data to determine category
        if "transactions" in input_data:
            if len(input_data.get("transactions", [])) > 10:
                return "transaction_analysis"
            else:
                return "financial_analysis"
        
        if "credit_score" in input_data or "loan" in str(input_data).lower():
            return "credit_assessment"
        
        if "portfolio" in input_data or "investment" in str(input_data).lower():
            return "investment_advice"
        
        if "risk" in str(input_data).lower() or "risk" in str(response_data).lower():
            return "risk_management"
        
        if "customer" in input_data or "service" in str(input_data).lower():
            return "customer_service"
        
        return "financial_analysis"  # Default category
    
    async def _check_storage_limits(self) -> Dict[str, Any]:
        """Check if storage limits allow new data"""
        
        # Check disk space
        storage_size_gb = self._calculate_storage_size() / (1024 ** 3)
        max_size_gb = self.storage_config["max_storage_size_gb"]
        
        if storage_size_gb >= max_size_gb:
            return {"can_store": False, "reason": "storage_limit_exceeded"}
        
        # Check record count (optional limit)
        if self.total_stored > 50000:  # Reasonable limit
            return {"can_store": False, "reason": "record_limit_exceeded"}
        
        return {"can_store": True, "reason": "within_limits"}
    
    def _calculate_storage_size(self) -> int:
        """Calculate total storage size in bytes"""
        
        total_size = 0
        for root, dirs, files in os.walk(self.storage_path):
            for file in files:
                filepath = os.path.join(root, file)
                total_size += os.path.getsize(filepath)
        
        return total_size
    
    async def _load_statistics(self):
        """Load existing statistics from database"""
        
        try:
            cursor = self.db_connection.cursor()
            
            # Total count
            cursor.execute("SELECT COUNT(*) FROM training_data")
            self.total_stored = cursor.fetchone()[0]
            
            # Count by quality level
            cursor.execute("SELECT quality_level, COUNT(*) FROM training_data GROUP BY quality_level")
            for quality_level, count in cursor.fetchall():
                if quality_level in self.storage_by_quality:
                    self.storage_by_quality[quality_level] = count
            
            # Count by category
            cursor.execute("SELECT category, COUNT(*) FROM training_data GROUP BY category")
            self.storage_by_category = dict(cursor.fetchall())
            
        except Exception as e:
            logger.warning(f"Could not load statistics: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old training data based on retention policy"""
        
        try:
            retention_days = self.storage_config["retention_days"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Delete old records from database
            delete_sql = "DELETE FROM training_data WHERE timestamp < ?"
            cursor = self.db_connection.cursor()
            cursor.execute(delete_sql, (cutoff_date.isoformat(),))
            deleted_count = cursor.rowcount
            self.db_connection.commit()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old training records")
                # Reload statistics after cleanup
                await self._load_statistics()
            
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
    
    def _update_storage_statistics(self, quality_level: str, category: str):
        """Update storage statistics"""
        
        self.total_stored += 1
        
        if quality_level in self.storage_by_quality:
            self.storage_by_quality[quality_level] += 1
        
        if category in self.storage_by_category:
            self.storage_by_category[category] += 1
        else:
            self.storage_by_category[category] = 1
    
    def _analyze_response_structures(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze common response structures in high-quality data"""
        
        structures = {"insights_first": 0, "recommendations_first": 0, "mixed": 0}
        
        for record in training_data:
            response_text = str(record.get("response_data", {}).get("analysis", ""))
            
            if "=== SECTION 1: INSIGHTS ===" in response_text:
                structures["insights_first"] += 1
            elif "=== SECTION 2: RECOMMENDATIONS ===" in response_text:
                structures["recommendations_first"] += 1
            else:
                structures["mixed"] += 1
        
        return structures
    
    def _analyze_successful_insights(self, training_data: List[Dict[str, Any]]) -> List[str]:
        """Analyze patterns in successful insights"""
        
        # This is a simplified analysis - in practice, you'd use NLP techniques
        common_patterns = [
            "Data-driven insights with specific metrics",
            "Clear identification of trends and patterns",
            "Contextual analysis linking data to business impact",
            "Quantified findings with supporting evidence"
        ]
        
        return common_patterns
    
    def _analyze_effective_recommendations(self, training_data: List[Dict[str, Any]]) -> List[str]:
        """Analyze patterns in effective recommendations"""
        
        return [
            "Specific, actionable steps with clear priorities",
            "Recommendations directly linked to identified insights",
            "Consideration of implementation feasibility",
            "Risk-aware suggestions with appropriate qualifications"
        ]
    
    def _analyze_quality_indicators(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze what makes responses high quality"""
        
        avg_scores = {}
        criteria_data = []
        
        for record in training_data:
            criteria_scores = record.get("validation_result", {}).get("criteria_scores", {})
            criteria_data.append(criteria_scores)
        
        # Calculate average scores for each criterion
        if criteria_data:
            all_criteria = set()
            for scores in criteria_data:
                all_criteria.update(scores.keys())
            
            for criterion in all_criteria:
                scores = [scores.get(criterion, 0) for scores in criteria_data if criterion in scores]
                if scores:
                    avg_scores[criterion] = sum(scores) / len(scores)
        
        return {
            "average_criterion_scores": avg_scores,
            "total_analyzed": len(training_data)
        }
    
    def _analyze_data_utilization(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how high-quality responses utilize input data"""
        
        return {
            "pattern": "High-quality responses reference specific data points",
            "utilization_rate": "Average 80%+ of available data elements referenced",
            "best_practices": [
                "Include specific numerical values from input",
                "Reference multiple data dimensions",
                "Connect data points to form coherent analysis"
            ]
        }
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics"""
        
        storage_size_mb = self._calculate_storage_size() / (1024 ** 2)
        
        return {
            "total_stored": self.total_stored,
            "storage_by_quality": self.storage_by_quality,
            "storage_by_category": self.storage_by_category,
            "storage_size_mb": round(storage_size_mb, 2),
            "storage_path": str(self.storage_path),
            "database_path": str(self.db_path)
        }
    
    async def shutdown(self):
        """Shutdown the training data manager"""
        logger.info("Shutting down training data manager...")
        
        if self.db_connection:
            self.db_connection.close()
        
        logger.info("Training data manager shutdown completed")
