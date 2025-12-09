"""
PAM (Prompt Augmentation Model) Service API
Main Flask application
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time
import traceback
from datetime import datetime

from .config import settings
from .core.augmentation_engine import AugmentationEngine

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize augmentation engine
logger.info("Initializing PAM Service...")
try:
    augmentation_engine = AugmentationEngine(settings)
    logger.info("PAM Service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize PAM Service: {e}")
    augmentation_engine = None


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service information"""
    return jsonify({
        "service": "PAM (Prompt Augmentation Model) Service",
        "version": "1.0.0",
        "status": "operational" if augmentation_engine else "degraded",
        "description": "Enriches prompts with real-time company and market intelligence",
        "endpoints": {
            "augment": "POST /augment - Augment prompt with company data",
            "bulk": "POST /augment/bulk - Batch augmentation",
            "health": "GET /health - Health check",
            "stats": "GET /stats - Service statistics",
            "cleanup": "POST /cleanup - Clean expired cache"
        },
        "features": {
            "web_scraping": settings.ENABLE_WEB_SCRAPING,
            "llm_research": settings.ENABLE_LLM_RESEARCH,
            "caching": settings.ENABLE_CACHING
        }
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "service": "pam-service",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "augmentation_engine": augmentation_engine is not None,
                "web_scraping": settings.ENABLE_WEB_SCRAPING,
                "llm_research": settings.ENABLE_LLM_RESEARCH,
                "caching": settings.ENABLE_CACHING
            }
        }
        
        # Check Qdrant connectivity
        if augmentation_engine and augmentation_engine.qdrant_cache:
            try:
                cache_stats = augmentation_engine.qdrant_cache.get_stats()
                health_status["components"]["qdrant"] = cache_stats.get('connected', False)
            except:
                health_status["components"]["qdrant"] = False
        
        # Overall status
        if not augmentation_engine:
            health_status["status"] = "unhealthy"
            return jsonify(health_status), 503
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.route('/augment', methods=['POST'])
def augment_prompt():
    """
    Augment prompt with company and market intelligence
    
    Request body:
    {
        "input_data": {...},  // Transaction data or other input
        "prompt_text": "...", // Optional: prompt to augment
        "companies": [...],   // Optional: explicit company list
        "context": "...",     // Optional: context string
        "bank_contexts": [...]// Optional: bank-defined context cards
    }
    """
    if not augmentation_engine:
        return jsonify({
            "error": "Augmentation engine not initialized"
        }), 503
    
    try:
        start_time = time.time()
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        input_data = data.get('input_data')
        if not input_data:
            return jsonify({"error": "Missing required field: input_data"}), 400
        
        prompt_text = data.get('prompt_text')
        companies = data.get('companies')
        context = data.get('context')
        bank_contexts = data.get('bank_contexts')
        
        # Perform augmentation
        result = augmentation_engine.augment(
            input_data=input_data,
            prompt_text=prompt_text,
            companies=companies,
            context=context,
            bank_contexts=bank_contexts
        )
        
        logger.info(f"Augmentation completed: {len(result.get('companies_analyzed', []))} companies")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Augmentation failed: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Augmentation failed: {str(e)}",
            "augmented_prompt": data.get('prompt_text', ''),
            "companies_analyzed": [],
            "cache_hit": False
        }), 500


@app.route('/augment/bulk', methods=['POST'])
def augment_bulk():
    """
    Bulk augmentation for multiple requests
    
    Request body:
    {
        "requests": [
        {
            "input_data": {...},
            "prompt_text": "...",
            "companies": [...],
            "context": "...",
            "bank_contexts": [...]
        },
            ...
        ]
    }
    """
    if not augmentation_engine:
        return jsonify({
            "error": "Augmentation engine not initialized"
        }), 503
    
    try:
        start_time = time.time()
        
        # Get request data
        data = request.get_json()
        if not data or 'requests' not in data:
            return jsonify({"error": "Missing required field: requests"}), 400
        
        requests_list = data['requests']
        
        results = []
        for idx, req in enumerate(requests_list):
            try:
                input_data = req.get('input_data')
                if not input_data:
                    results.append({
                        "index": idx,
                        "success": False,
                        "error": "Missing input_data"
                    })
                    continue
                
                result = augmentation_engine.augment(
                    input_data=input_data,
                    prompt_text=req.get('prompt_text'),
                    companies=req.get('companies'),
                    context=req.get('context'),
                    bank_contexts=req.get('bank_contexts')
                )
                
                results.append({
                    "index": idx,
                    "success": True,
                    **result
                })
                
            except Exception as e:
                logger.error(f"Failed to augment request {idx}: {str(e)}")
                results.append({
                    "index": idx,
                    "success": False,
                    "error": str(e)
                })
        
        processing_time = (time.time() - start_time) * 1000
        
        successful = sum(1 for r in results if r.get("success", False))
        failed = len(results) - successful
        
        logger.info(f"Bulk augmentation completed: {successful} success, {failed} failed")
        
        return jsonify({
            "total_requests": len(requests_list),
            "successful": successful,
            "failed": failed,
            "results": results,
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Bulk augmentation failed: {str(e)}")
        return jsonify({
            "error": f"Bulk augmentation failed: {str(e)}"
        }), 500


@app.route('/stats', methods=['GET'])
def get_statistics():
    """Get service statistics"""
    if not augmentation_engine:
        return jsonify({
            "error": "Augmentation engine not initialized"
        }), 503
    
    try:
        stats = augmentation_engine.get_stats()
        return jsonify({
            "service": "pam-service",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/cleanup', methods=['POST'])
def cleanup_cache():
    """Clean up expired cache entries"""
    if not augmentation_engine:
        return jsonify({
            "error": "Augmentation engine not initialized"
        }), 503
    
    try:
        augmentation_engine.cleanup_cache()
        return jsonify({
            "message": "Cache cleanup completed",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Cache cleanup failed: {str(e)}")
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
            "/augment",
            "/augment/bulk",
            "/stats",
            "/cleanup"
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
    logger.info(f"Starting PAM Service on {settings.HOST}:{settings.PORT}")
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)

