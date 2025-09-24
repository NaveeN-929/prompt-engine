#!/usr/bin/env python3
"""
Simple Validation Server - Compatible with all Flask versions
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
validation_engine: Optional[object] = None
server_stats = {
    "start_time": time.time(),
    "total_requests": 0,
    "successful_validations": 0,
    "failed_validations": 0,
    "uptime": 0.0
}

def initialize_validation_engine():
    """Initialize the validation engine"""
    global validation_engine
    
    try:
        logger.info("🚀 Initializing Response Validation LLM System...")
        
        from core import ValidationEngine
        from config import get_config
        
        # Run async initialization in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        validation_engine = ValidationEngine()
        loop.run_until_complete(validation_engine.initialize())
        
        loop.close()
        logger.info("✅ Validation system ready!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize validation system: {e}")
        validation_engine = None
        return False

@app.route('/')
def home():
    """Home endpoint with system information"""
    try:
        from config import get_config
        config = get_config()
        
        return jsonify({
            "system": config["base"]["system"],
            "status": "operational" if validation_engine else "initializing",
            "endpoints": [
                "POST /validate/response - Validate a single response",
                "GET /health - Health check",
                "GET /status - System status"
            ],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    global server_stats
    
    server_stats["uptime"] = time.time() - server_stats["start_time"]
    
    health_status = {
        "status": "healthy" if validation_engine else "initializing",
        "uptime_seconds": server_stats["uptime"],
        "total_requests": server_stats["total_requests"],
        "validation_engine_initialized": validation_engine is not None,
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(health_status)

@app.route('/validate/response', methods=['POST'])
def validate_response():
    """Validate a single autonomous agent response"""
    global server_stats
    
    if not validation_engine:
        return jsonify({
            "error": "Validation engine not initialized",
            "suggestion": "Try again in a few seconds or check server logs"
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
        
        # Perform actual validation using the validation engine
        if not validation_engine or not validation_engine.is_initialized:
            return jsonify({
                "error": "Validation engine not properly initialized",
                "details": "Please ensure Ollama is running with required models",
                "status": "service_unavailable"
            }), 503
        
        # Create async event loop for validation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Perform actual validation
            validation_result = loop.run_until_complete(
                validation_engine.validate_response(
                    response_data=response_data,
                    input_data=input_data,
                    validation_config=validation_config
                )
            )
            
            loop.close()
            
            if validation_result.status == "completed":
                server_stats["successful_validations"] += 1
                return jsonify(validation_result.to_dict())
            else:
                server_stats["failed_validations"] += 1
                return jsonify({
                    "error": "Validation failed",
                    "details": validation_result.validation_details.get("error", "Unknown error"),
                    "validation_id": validation_result.validation_id,
                    "status": validation_result.status
                }), 500
                
        except Exception as e:
            loop.close()
            server_stats["failed_validations"] += 1
            logger.error(f"Validation processing error: {e}")
            return jsonify({
                "error": "Validation processing failed",
                "details": str(e),
                "status": "processing_error"
            }), 500
        
    except Exception as e:
        server_stats["failed_validations"] += 1
        logger.error(f"Validation request failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status')
def system_status():
    """System status endpoint"""
    try:
        from config import get_config
        config = get_config()
        
        return jsonify({
            "system": {
                "name": config["base"]["system"]["name"],
                "version": config["base"]["system"]["version"],
                "status": "operational" if validation_engine else "initializing",
                "uptime_seconds": time.time() - server_stats["start_time"]
            },
            "validation_engine": {
                "initialized": validation_engine is not None,
                "status": "ready" if validation_engine else "not_ready"
            },
            "server_statistics": server_stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({"error": str(e)}), 500

def start_simple_server():
    """Start the simple validation server"""
    try:
        from config import get_config
        config = get_config()
        server_config = config["base"]["server"]
        
        logger.info("🚀 Starting Simple Validation Server...")
        logger.info(f"Server will run on {server_config['host']}:{server_config['port']}")
        logger.info("=" * 60)
        
        # Initialize validation engine in background
        logger.info("Initializing validation engine...")
        init_success = initialize_validation_engine()
        
        if init_success:
            logger.info("✅ Validation engine initialized successfully")
        else:
            logger.error("❌ Validation engine initialization failed")
            logger.error("Please ensure:")
            logger.error("  1. Ollama is running: ollama serve")
            logger.error("  2. Required models are available: python setup_models.py")
            logger.error("  3. Qdrant is running: docker run -d -p 6333:6333 qdrant/qdrant")
            logger.error("Server will start but validation requests will fail until services are available")
            return False
        
        # Start Flask server
        logger.info("Starting Flask server...")
        app.run(
            host=server_config["host"],
            port=server_config["port"],
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    start_simple_server()
