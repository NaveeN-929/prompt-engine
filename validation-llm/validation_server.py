"""
Validation Server - Main server for the Response Validation LLM System
"""

import asyncio
import json
import logging
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

from core import ValidationEngine
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global validation engine instance
validation_engine: Optional[ValidationEngine] = None
server_stats = {
    "start_time": time.time(),
    "total_requests": 0,
    "successful_validations": 0,
    "failed_validations": 0,
    "uptime": 0.0
}

def initialize_validation_engine_sync():
    """Initialize the validation engine synchronously"""
    global validation_engine
    
    try:
        logger.info("🚀 Initializing Response Validation LLM System...")
        
        # Run async initialization in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        validation_engine = ValidationEngine()
        loop.run_until_complete(validation_engine.initialize())
        
        loop.close()
        logger.info("✅ Validation system ready!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize validation system: {e}")
        raise

# Global initialization flag
_validation_engine_initialized = False

def ensure_validation_engine():
    """Ensure validation engine is initialized"""
    global _validation_engine_initialized
    if not _validation_engine_initialized:
        initialize_validation_engine_sync()
        _validation_engine_initialized = True

@app.route('/')
def home():
    """Home endpoint with system information"""
    config = get_config()
    
    return jsonify({
        "system": config["base"]["system"],
        "status": "operational" if validation_engine and validation_engine.is_initialized else "initializing",
        "endpoints": [
            "POST /validate/response - Validate a single response",
            "POST /validate/batch - Validate multiple responses",
            "GET /validation/metrics - Get validation statistics",
            "GET /training-data/quality - Retrieve high-quality training data",
            "POST /feedback/autonomous-agent - Send feedback to main system",
            "GET /health - Health check",
            "GET /status - System status"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    global server_stats
    
    server_stats["uptime"] = time.time() - server_stats["start_time"]
    
    health_status = {
        "status": "healthy" if validation_engine and validation_engine.is_initialized else "unhealthy",
        "uptime_seconds": server_stats["uptime"],
        "total_requests": server_stats["total_requests"],
        "validation_engine_initialized": validation_engine is not None and validation_engine.is_initialized,
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(health_status)

@app.route('/status')
def system_status():
    """Comprehensive system status"""
    # Ensure validation engine is initialized
    ensure_validation_engine()
    
    if not validation_engine or not validation_engine.is_initialized:
        return jsonify({
            "error": "Validation engine not properly initialized",
            "details": "Please ensure all required services (Ollama, Qdrant) are running",
            "status": "service_unavailable"
        }), 503
    
    try:
        # Get validation statistics
        validation_stats = validation_engine.get_validation_statistics()
        
        # Get component statistics
        llm_stats = validation_engine.llm_validator.get_validator_statistics()
        quality_stats = validation_engine.quality_assessor.get_assessor_statistics()
        training_stats = validation_engine.training_data_manager.get_storage_stats()
        feedback_stats = validation_engine.feedback_manager.get_feedback_statistics()
        
        config = get_config()
        
        return jsonify({
            "system": {
                "name": config["base"]["system"]["name"],
                "version": config["base"]["system"]["version"],
                "status": "operational",
                "uptime_seconds": time.time() - server_stats["start_time"]
            },
            "validation_engine": validation_stats,
            "llm_validator": llm_stats,
            "quality_assessor": quality_stats,
            "training_data_manager": training_stats,
            "feedback_manager": feedback_stats,
            "server_statistics": server_stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/validate/response', methods=['POST'])
async def validate_response():
    """Validate a single autonomous agent response"""
    global server_stats
    
    # Ensure validation engine is initialized
    ensure_validation_engine()
    
    if not validation_engine or not validation_engine.is_initialized:
        return jsonify({
            "error": "Validation engine not properly initialized",
            "details": "Please ensure all required services (Ollama, Qdrant) are running",
            "status": "service_unavailable"
        }), 503
    
    server_stats["total_requests"] += 1
    
    try:
        data = request.get_json()
        
        # Validate request data
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        if "response_data" not in data:
            return jsonify({"error": "Missing response_data field"}), 400
        
        if "input_data" not in data:
            return jsonify({"error": "Missing input_data field"}), 400
        
        response_data = data["response_data"]
        input_data = data["input_data"]
        validation_config = data.get("validation_config")
        
        # Perform validation
        validation_result = await validation_engine.validate_response(
            response_data=response_data,
            input_data=input_data,
            validation_config=validation_config
        )
        
        if validation_result.status == "completed":
            server_stats["successful_validations"] += 1
        else:
            server_stats["failed_validations"] += 1
        
        return jsonify(validation_result.to_dict())
        
    except Exception as e:
        server_stats["failed_validations"] += 1
        logger.error(f"Validation request failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/validate/batch', methods=['POST'])
async def validate_batch():
    """Validate multiple responses in batch"""
    global server_stats
    
    # Ensure validation engine is initialized
    ensure_validation_engine()
    
    if not validation_engine or not validation_engine.is_initialized:
        return jsonify({
            "error": "Validation engine not properly initialized",
            "details": "Please ensure all required services (Ollama, Qdrant) are running",
            "status": "service_unavailable"
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or "batch_data" not in data:
            return jsonify({"error": "Missing batch_data field"}), 400
        
        batch_data = data["batch_data"]
        validation_config = data.get("validation_config")
        
        if not isinstance(batch_data, list):
            return jsonify({"error": "batch_data must be a list"}), 400
        
        server_stats["total_requests"] += len(batch_data)
        
        # Perform batch validation
        validation_results = await validation_engine.validate_batch(
            batch_data=batch_data,
            validation_config=validation_config
        )
        
        # Update statistics
        successful_count = sum(1 for result in validation_results if result.status == "completed")
        failed_count = len(validation_results) - successful_count
        
        server_stats["successful_validations"] += successful_count
        server_stats["failed_validations"] += failed_count
        
        return jsonify({
            "batch_results": [result.to_dict() for result in validation_results],
            "summary": {
                "total_processed": len(validation_results),
                "successful": successful_count,
                "failed": failed_count,
                "success_rate": successful_count / len(validation_results) if validation_results else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Batch validation failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/validation/metrics')
def validation_metrics():
    """Get validation system metrics and statistics"""
    if not validation_engine:
        return jsonify({"error": "Validation engine not initialized"}), 503
    
    try:
        metrics = validation_engine.get_validation_statistics()
        
        return jsonify({
            "metrics": metrics,
            "server_stats": server_stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting validation metrics: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/training-data/quality', methods=['GET'])
async def get_quality_training_data():
    """Retrieve high-quality training data"""
    if not validation_engine:
        return jsonify({"error": "Validation engine not initialized"}), 503
    
    try:
        # Get query parameters
        quality_level = request.args.get('quality_level')
        category = request.args.get('category')
        limit = int(request.args.get('limit', 50))
        min_score = float(request.args.get('min_score', 0.75))
        
        # Retrieve training data
        training_data = await validation_engine.training_data_manager.retrieve_training_data(
            quality_level=quality_level,
            category=category,
            limit=limit,
            min_score=min_score
        )
        
        return jsonify({
            "training_data": training_data,
            "count": len(training_data),
            "filters_applied": {
                "quality_level": quality_level,
                "category": category,
                "limit": limit,
                "min_score": min_score
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving training data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/training-data/patterns', methods=['GET'])
async def get_training_patterns():
    """Get analysis of successful response patterns"""
    if not validation_engine:
        return jsonify({"error": "Validation engine not initialized"}), 503
    
    try:
        category = request.args.get('category')
        
        patterns = await validation_engine.training_data_manager.get_training_patterns(category)
        
        return jsonify({
            "patterns": patterns,
            "category_filter": category,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting training patterns: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/training-data/export', methods=['POST'])
async def export_training_dataset():
    """Export training dataset in specified format"""
    if not validation_engine:
        return jsonify({"error": "Validation engine not initialized"}), 503
    
    try:
        data = request.get_json() or {}
        format_type = data.get('format', 'json')
        quality_filter = data.get('quality_filter')
        
        export_path = await validation_engine.training_data_manager.export_training_dataset(
            format_type=format_type,
            quality_filter=quality_filter
        )
        
        return jsonify({
            "exported": True,
            "export_path": export_path,
            "format": format_type,
            "quality_filter": quality_filter,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error exporting training dataset: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/feedback/autonomous-agent', methods=['POST'])
async def send_agent_feedback():
    """Send validation feedback to the autonomous agent"""
    if not validation_engine:
        return jsonify({"error": "Validation engine not initialized"}), 503
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        required_fields = ["response_data", "validation_result", "input_data"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing {field} field"}), 400
        
        # Send feedback
        feedback_result = await validation_engine.feedback_manager.send_feedback_to_agent(
            response_data=data["response_data"],
            validation_result=data["validation_result"],
            input_data=data["input_data"]
        )
        
        return jsonify(feedback_result)
        
    except Exception as e:
        logger.error(f"Error sending feedback: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/recent/validations', methods=['GET'])
async def get_recent_validations():
    """Get recent validation results"""
    if not validation_engine:
        return jsonify({"error": "Validation engine not initialized"}), 503
    
    try:
        limit = int(request.args.get('limit', 20))
        
        recent_validations = await validation_engine.get_recent_validations(limit)
        
        return jsonify({
            "recent_validations": recent_validations,
            "count": len(recent_validations),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting recent validations: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "POST /validate/response",
            "POST /validate/batch", 
            "GET /validation/metrics",
            "GET /training-data/quality",
            "GET /training-data/patterns",
            "POST /training-data/export",
            "POST /feedback/autonomous-agent",
            "GET /recent/validations",
            "GET /health",
            "GET /status"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

def start_validation_server():
    """Start the validation server"""
    try:
        config = get_config()
        server_config = config["base"]["server"]
        
        logger.info("🚀 Starting Response Validation LLM Server...")
        logger.info(f"Server will run on {server_config['host']}:{server_config['port']}")
        logger.info("=" * 60)
        
        # Initialize validation engine before starting server
        logger.info("Initializing validation engine...")
        ensure_validation_engine()
        
        # Start Flask server
        app.run(
            host=server_config["host"],
            port=server_config["port"],
            debug=server_config["debug"],
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start validation server: {e}")
        raise

if __name__ == "__main__":
    start_validation_server()
