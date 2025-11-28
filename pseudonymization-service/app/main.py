"""
Pseudonymization Service API (Flask)
Anonymizes sensitive financial data for secure processing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import logging
import traceback
from datetime import datetime

from .core.pseudonymizer import Pseudonymizer
from .core.key_manager import KeyManager
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize services
key_manager = KeyManager(settings.KEY_STORE_PATH)
pseudonymizer = Pseudonymizer(
    key_manager,
    redis_url=settings.REDIS_URL,
    redis_ttl=settings.REDIS_TTL
)

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service information"""
    return jsonify({
        "service": "Pseudonymization Service",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs (see README.md)",
        "health": "/health"
    })

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        key_status = "operational" if key_manager.is_initialized() else "not_initialized"
        return jsonify({
            "status": "healthy",
            "service": "pseudonymization-service",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "key_manager_status": key_status
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"error": "Service unhealthy"}), 500

# Pseudonymize endpoint
@app.route('/pseudonymize', methods=['POST'])
def pseudonymize_data():
    """
    Pseudonymize data with automatic PII detection
    
    Features:
    - Automatic PII Detection: Identifies 20+ PII types
    - Field-Level Security: Granular pseudonymization control
    - Reversible Tokenization: Secure pseudonym generation
    - Maintains data utility for analysis
    
    PII Types Detected:
    - Personal: Names, SSN, ID numbers
    - Contact: Email, phone, address
    - Financial: Account numbers, card numbers
    - Biometric & Geolocation data
    """
    try:
        start_time = time.time()
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        if 'customer_id' not in data:
            return jsonify({"error": "Missing required field: customer_id"}), 400
        
        # Pseudonymize the data with PII detection
        pseudonymized_result = pseudonymizer.pseudonymize(data)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        logger.info(f"Pseudonymized data for customer {data['customer_id']} -> {pseudonymized_result['pseudonym_id']}")
        logger.info(f"PII detected: {pseudonymized_result['pii_summary']['total_pii_fields']} fields")
        
        return jsonify({
            "pseudonymized_data": pseudonymized_result['data'],
            "pseudonym_id": pseudonymized_result['pseudonym_id'],
            "timestamp": datetime.utcnow().isoformat(),
            "fields_pseudonymized": pseudonymized_result['fields_pseudonymized'],
            "pii_detected": pseudonymized_result['pii_detected'],
            "pii_summary": pseudonymized_result['pii_summary'],
            "processing_time_ms": processing_time
        })
        
    except Exception as e:
        logger.error(f"Pseudonymization failed: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Pseudonymization failed: {str(e)}"
        }), 500

# Bulk pseudonymization
@app.route('/pseudonymize/bulk', methods=['POST'])
def pseudonymize_bulk():
    """
    Bulk pseudonymization for multiple datasets
    
    - Processes multiple financial datasets in one request
    - Returns array of pseudonymized results
    - Useful for batch processing
    """
    try:
        start_time = time.time()
        
        # Get request data
        data = request.get_json()
        if not data or 'datasets' not in data:
            return jsonify({"error": "Missing required field: datasets"}), 400
        
        datasets = data['datasets']
        batch_id = data.get('batch_id')
        
        results = []
        for idx, dataset in enumerate(datasets):
            try:
                pseudonymized_result = pseudonymizer.pseudonymize(dataset)
                
                results.append({
                    "index": idx,
                    "success": True,
                    "pseudonymized_data": pseudonymized_result['data'],
                    "pseudonym_id": pseudonymized_result['pseudonym_id'],
                    "fields_pseudonymized": pseudonymized_result['fields_pseudonymized']
                })
            except Exception as e:
                logger.error(f"Failed to pseudonymize dataset {idx}: {str(e)}")
                results.append({
                    "index": idx,
                    "success": False,
                    "error": str(e)
                })
        
        processing_time = (time.time() - start_time) * 1000
        
        successful = sum(1 for r in results if r.get("success", False))
        failed = len(results) - successful
        
        logger.info(f"Bulk pseudonymization completed: {successful} success, {failed} failed")
        
        return jsonify({
            "batch_id": batch_id or f"batch_{int(time.time())}",
            "total_datasets": len(datasets),
            "successful": successful,
            "failed": failed,
            "results": results,
            "processing_time_ms": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Bulk pseudonymization failed: {str(e)}")
        return jsonify({
            "error": f"Bulk pseudonymization failed: {str(e)}"
        }), 500

# Statistics endpoint
@app.route('/stats', methods=['GET'])
def get_statistics():
    """Get pseudonymization service statistics"""
    try:
        stats = pseudonymizer.get_stats()
        return jsonify({
            "service": "pseudonymization",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Retrieve original data (internal endpoint for repersonalization service)
@app.route('/repersonalize/retrieve', methods=['POST'])
def retrieve_original_data():
    """
    Retrieve original data for repersonalization service
    
    Internal endpoint used by Repersonalization Service
    """
    try:
        data = request.get_json()
        pseudonym_id = data.get('pseudonym_id') if data else None
        
        if not pseudonym_id:
            return jsonify({"error": "Missing pseudonym_id"}), 400
        
        # Retrieve original data
        original_data = pseudonymizer.get_original_data(pseudonym_id)
        
        logger.info(f"Retrieved original data for pseudonym: {pseudonym_id}")
        
        return jsonify({
            "original_data": original_data,
            "pseudonym_id": pseudonym_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except ValueError as e:
        logger.error(f"Data retrieval failed: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Data retrieval failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Cleanup endpoint
@app.route('/cleanup/<pseudonym_id>', methods=['DELETE'])
def cleanup_pseudonym(pseudonym_id):
    """
    Clean up pseudonym mapping (GDPR compliance)
    
    Removes pseudonym mapping after successful repersonalization
    """
    try:
        pseudonymizer.clear_pseudonym(pseudonym_id)
        logger.info(f"Cleaned up pseudonym: {pseudonym_id}")
        return jsonify({
            "message": "Pseudonym cleaned up successfully",
            "pseudonym_id": pseudonym_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Key rotation endpoint
@app.route('/key/rotate', methods=['POST'])
def rotate_keys():
    """
    Rotate encryption keys (admin operation)
    
    WARNING: This should be coordinated with the repersonalization service
    """
    try:
        key_manager.rotate_keys()
        logger.warning("Encryption keys rotated")
        return jsonify({
            "message": "Keys rotated successfully",
            "timestamp": datetime.utcnow().isoformat(),
            "warning": "Ensure repersonalization service is updated"
        })
    except Exception as e:
        logger.error(f"Key rotation failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Custom 404 handler"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/",
            "/health",
            "/pseudonymize",
            "/pseudonymize/bulk",
            "/stats",
            "/repersonalize/retrieve",
            "/cleanup/<pseudonym_id>",
            "/key/rotate"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Custom 500 handler"""
    return jsonify({
        "error": "Internal server error",
        "detail": str(error)
    }), 500

if __name__ == "__main__":
    print("🚀 Starting Pseudonymization Service (Flask)...")
    print(f"🔒 Port: {settings.PORT}")
    print(f"🌐 Host: {settings.HOST}")
    print("=" * 60)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
