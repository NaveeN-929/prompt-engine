"""
Repersonalization Service API (Flask)
Restores original data from pseudonymized versions
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import logging
import traceback
import requests
from datetime import datetime

from .core.repersonalizer import Repersonalizer
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
repersonalizer = Repersonalizer(key_manager, settings.PSEUDONYMIZATION_SERVICE_URL)

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service information"""
    return jsonify({
        "service": "Repersonalization Service",
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
        
        # Check pseudonymization service connectivity
        try:
            pseudo_response = requests.get(
                f"{settings.PSEUDONYMIZATION_SERVICE_URL}/health",
                timeout=2
            )
            pseudo_status = "connected" if pseudo_response.status_code == 200 else "error"
        except Exception:
            pseudo_status = "unreachable"
        
        return jsonify({
            "status": "healthy",
            "service": "repersonalization-service",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "key_manager_status": key_status,
            "pseudonymization_service_status": pseudo_status
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"error": "Service unhealthy"}), 500

# Repersonalize endpoint
@app.route('/repersonalize', methods=['POST'])
def repersonalize_data():
    """
    Restore original data from pseudonymized version
    
    - Retrieves original data using pseudonym ID
    - Optionally verifies data integrity
    - Returns complete original dataset
    """
    try:
        start_time = time.time()
        
        # Get request data
        data = request.get_json()
        if not data or 'pseudonym_id' not in data:
            return jsonify({"error": "Missing required field: pseudonym_id"}), 400
        
        pseudonym_id = data['pseudonym_id']
        verify = data.get('verify', True)
        
        # Repersonalize the data
        result = repersonalizer.repersonalize(pseudonym_id, verify=verify)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        logger.info(f"Repersonalized data for pseudonym: {pseudonym_id}")
        
        return jsonify({
            "original_data": result['original_data'],
            "pseudonym_id": pseudonym_id,
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": processing_time,
            "verified": result.get('verified', False)
        })
        
    except ValueError as e:
        logger.error(f"Repersonalization failed: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Repersonalization failed: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Repersonalization failed: {str(e)}"
        }), 500

# Bulk repersonalization
@app.route('/repersonalize/bulk', methods=['POST'])
def repersonalize_bulk():
    """
    Bulk repersonalization for multiple pseudonym IDs
    
    - Processes multiple pseudonym IDs in one request
    - Returns array of repersonalization results
    - Can continue on individual failures if specified
    """
    try:
        start_time = time.time()
        
        # Get request data
        data = request.get_json()
        if not data or 'pseudonym_ids' not in data:
            return jsonify({"error": "Missing required field: pseudonym_ids"}), 400
        
        pseudonym_ids = data['pseudonym_ids']
        batch_id = data.get('batch_id')
        continue_on_error = data.get('continue_on_error', True)
        
        results = []
        for idx, pseudonym_id in enumerate(pseudonym_ids):
            try:
                result = repersonalizer.repersonalize(pseudonym_id, verify=True)
                
                results.append({
                    "index": idx,
                    "success": True,
                    "pseudonym_id": pseudonym_id,
                    "original_data": result['original_data'],
                    "verified": result.get('verified', False)
                })
            except Exception as e:
                logger.error(f"Failed to repersonalize {pseudonym_id}: {str(e)}")
                results.append({
                    "index": idx,
                    "success": False,
                    "pseudonym_id": pseudonym_id,
                    "error": str(e)
                })
                
                if not continue_on_error:
                    break
        
        processing_time = (time.time() - start_time) * 1000
        
        successful = sum(1 for r in results if r.get("success", False))
        failed = len(results) - successful
        
        logger.info(f"Bulk repersonalization completed: {successful} success, {failed} failed")
        
        return jsonify({
            "batch_id": batch_id or f"batch_{int(time.time())}",
            "total_requests": len(pseudonym_ids),
            "successful": successful,
            "failed": failed,
            "results": results,
            "processing_time_ms": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Bulk repersonalization failed: {str(e)}")
        return jsonify({
            "error": f"Bulk repersonalization failed: {str(e)}"
        }), 500

# Statistics endpoint
@app.route('/stats', methods=['GET'])
def get_statistics():
    """Get repersonalization service statistics"""
    try:
        stats = repersonalizer.get_stats()
        return jsonify({
            "service": "repersonalization",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Cleanup endpoint
@app.route('/cleanup/<pseudonym_id>', methods=['DELETE'])
def cleanup_pseudonym(pseudonym_id):
    """
    Clean up pseudonym mapping after successful repersonalization
    
    - Removes pseudonym mapping from storage
    - Should be called after data is no longer needed
    - Helps with GDPR compliance
    """
    try:
        # Request cleanup from pseudonymization service
        response = requests.delete(
            f"{settings.PSEUDONYMIZATION_SERVICE_URL}/cleanup/{pseudonym_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"Cleaned up pseudonym: {pseudonym_id}")
            return jsonify({
                "message": "Pseudonym cleaned up successfully",
                "pseudonym_id": pseudonym_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            return jsonify({"error": "Cleanup failed"}), response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Cleanup request failed: {str(e)}")
        return jsonify({
            "error": "Pseudonymization service unavailable"
        }), 503
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Verify endpoint
@app.route('/verify', methods=['POST'])
def verify_pseudonymization():
    """
    Verify pseudonymization integrity
    
    - Checks if pseudonymized data matches original
    - Useful for auditing and compliance
    """
    try:
        data = request.get_json()
        if not data or 'pseudonym_id' not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        pseudonym_id = data['pseudonym_id']
        pseudonymized_data = data.get('pseudonymized_data', {})
        
        result = repersonalizer.repersonalize(pseudonym_id, verify=True)
        original_data = result['original_data']
        
        # Basic verification
        customer_id_match = (
            original_data.get('customer_id') != 
            pseudonymized_data.get('customer_id')
        )
        
        return jsonify({
            "verified": result.get('verified', False),
            "pseudonym_id": pseudonym_id,
            "customer_id_pseudonymized": customer_id_match,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
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
            "/repersonalize",
            "/repersonalize/bulk",
            "/stats",
            "/cleanup/<pseudonym_id>",
            "/verify"
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
    print("🚀 Starting Repersonalization Service (Flask)...")
    print(f"🔓 Port: {settings.PORT}")
    print(f"🌐 Host: {settings.HOST}")
    print("=" * 60)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
