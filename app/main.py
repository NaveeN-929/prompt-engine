"""
Main Flask Application for Prompting Engine Demo
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import time
import traceback
import json
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OLLAMA_HOST, OLLAMA_PORT, OLLAMA_MODEL, FLASK_HOST, FLASK_PORT, FLASK_DEBUG

# Import our components
from app.generators.agentic_prompt_generator import AgenticPromptGenerator
from app.llm.mock_llm import OllamaLLM
from app.feedback.feedback_system import FeedbackSystem

# Initialize components
app = Flask(__name__)
CORS(app)

# Initialize system components - PURE AGENTIC MODE
print("🚀 Initializing Pure Agentic Prompt Engine with Vector Database...")
agentic_generator = AgenticPromptGenerator(enable_vector_db=True)
ollama_llm = OllamaLLM(
    base_url=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}",
    model=OLLAMA_MODEL
)
feedback_system = FeedbackSystem()

@app.route('/')
def root():
    """Serve the main web interface"""
    try:
        with open("app/static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <head><title>Prompting Engine Demo</title></head>
            <body>
                <h1>Prompting Engine Demo</h1>
                <p>Web interface not found. Please check the static files.</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """

@app.route('/generate', methods=['POST'])
def generate_prompt():
    """
    Generate a prompt and get LLM response (Pure Agentic Mode)
    
    Expected JSON:
    {
        "input_data": {
            "transactions": [...],
            "account_data": {...}
        },
        "context": "core_banking" (optional - AI will auto-detect),
        "data_type": "transaction_history" (optional - AI will auto-detect),
        "generation_type": "standard" | "reasoning" | "autonomous" | "optimize" (optional)
    }
    """
    try:
        start_time = time.time()
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        input_data = data.get('input_data')
        if not input_data:
            return jsonify({"error": "Missing required field: input_data"}), 400
        
        # Optional hints (AI can auto-detect if not provided)
        context = data.get('context')
        data_type = data.get('data_type')
        generation_type = data.get('generation_type', 'standard')
        
        # Choose generation method
        if generation_type == 'reasoning':
            reasoning_steps = data.get('reasoning_steps', 5)
            prompt_text, metadata, prompt_time = agentic_generator.generate_multi_step_reasoning_prompt(
                input_data=input_data,
                reasoning_steps=reasoning_steps
            )
        elif generation_type == 'optimize':
            performance_feedback = data.get('performance_feedback')
            prompt_text, metadata, prompt_time = agentic_generator.optimize_prompt_continuously(
                input_data=input_data,
                performance_feedback=performance_feedback
            )
        elif generation_type == 'autonomous':
            # Force autonomous by not providing hints
            prompt_text, metadata, prompt_time = agentic_generator.generate_agentic_prompt(
                context=None,
                data_type=None,
                input_data=input_data
            )
        else:  # standard agentic
            prompt_text, metadata, prompt_time = agentic_generator.generate_agentic_prompt(
                context=context,
                data_type=data_type,
                input_data=input_data
            )
        
        template_name = metadata.get('template_used', 'agentic_intelligent')
        
        # Get LLM response using Ollama
        response_text, tokens_used, llm_time = ollama_llm.generate_response(
            prompt=prompt_text,
            template_name=template_name
        )
        
        total_time = time.time() - start_time
        
        # Enhanced learning: Store successful interaction in vector database
        if metadata.get('generation_mode') != 'vector_accelerated':  # Don't re-store vector results
            agentic_generator.learn_from_interaction(
                input_data=input_data,
                prompt_result=prompt_text,
                llm_response=response_text,
                quality_score=0.8,  # Default good quality, user can provide feedback
                metadata=metadata
            )
        
        # Log the interaction for analytics
        feedback_system.log_interaction(
            prompt=prompt_text,
            response=response_text,
            template_name=template_name,
            tokens_used=tokens_used,
            processing_time=llm_time,
            context=metadata.get('context', 'auto_inferred'),
            data_type=metadata.get('data_type', 'auto_inferred')
        )
        
        # Prepare comprehensive response
        response_data = {
            "prompt": prompt_text,
            "response": response_text,
            "tokens_used": tokens_used,
            "template_used": template_name,
            "processing_time": total_time,
            "generation_mode": metadata.get('generation_mode', 'agentic'),
            "agentic_metadata": metadata,
            "vector_accelerated": metadata.get('generation_mode') == 'vector_accelerated'
        }
        
        return jsonify(response_data)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error in generate endpoint: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/agentic/analyze', methods=['POST'])
def analyze_data():
    """
    Analyze input data using agentic intelligence without generating full prompts
    """
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({"error": "Missing input_data field"}), 400
        
        input_data = data['input_data']
        
        # Use the agentic generator's analysis capabilities
        analysis = agentic_generator._analyze_input_data(input_data)
        
        return jsonify({
            "analysis": analysis,
            "timestamp": time.time()
        })
        
    except Exception as e:
        print(f"Error in analyze endpoint: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/agentic/autonomous', methods=['POST'])
def generate_autonomous():
    """
    Generate completely autonomous prompts without any template constraints
    """
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({"error": "Missing input_data field"}), 400
        
        input_data = data['input_data']
        
        # Force autonomous generation by not providing context/data_type
        prompt_text, metadata, prompt_time = agentic_generator.generate_agentic_prompt(
            context=None,
            data_type=None,
            input_data=input_data
        )
        
        # Get LLM response
        response_text, tokens_used, llm_time = ollama_llm.generate_response(
            prompt=prompt_text,
            template_name="autonomous_generation"
        )
        
        return jsonify({
            "prompt": prompt_text,
            "response": response_text,
            "tokens_used": tokens_used,
            "metadata": metadata,
            "processing_time": prompt_time + llm_time,
            "generation_mode": "fully_autonomous"
        })
        
    except Exception as e:
        print(f"Error in autonomous endpoint: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Removed duplicate endpoint - functionality moved to /capabilities

@app.route('/agentic/reasoning', methods=['POST'])
def generate_multi_step_reasoning_deprecated():
    """
    Generate prompts with explicit multi-step reasoning framework
    """
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({"error": "Missing input_data field"}), 400
        
        input_data = data['input_data']
        reasoning_steps = data.get('reasoning_steps', 5)
        
        # Generate multi-step reasoning prompt
        prompt_text, metadata, prompt_time = agentic_generator.generate_multi_step_reasoning_prompt(
            input_data=input_data,
            reasoning_steps=reasoning_steps
        )
        
        # Get LLM response
        response_text, tokens_used, llm_time = ollama_llm.generate_response(
            prompt=prompt_text,
            template_name="multi_step_reasoning"
        )
        
        return jsonify({
            "prompt": prompt_text,
            "response": response_text,
            "tokens_used": tokens_used,
            "metadata": metadata,
            "processing_time": prompt_time + llm_time,
            "generation_mode": "multi_step_reasoning"
        })
        
    except Exception as e:
        print(f"Error in reasoning endpoint: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/agentic/optimize', methods=['POST'])
def optimize_continuously():
    """
    Generate continuously optimized prompts based on learned patterns
    """
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({"error": "Missing input_data field"}), 400
        
        input_data = data['input_data']
        performance_feedback = data.get('performance_feedback')
        
        # Generate optimized prompt
        prompt_text, metadata, prompt_time = agentic_generator.optimize_prompt_continuously(
            input_data=input_data,
            performance_feedback=performance_feedback
        )
        
        # Get LLM response
        response_text, tokens_used, llm_time = ollama_llm.generate_response(
            prompt=prompt_text,
            template_name="continuous_optimization"
        )
        
        return jsonify({
            "prompt": prompt_text,
            "response": response_text,
            "tokens_used": tokens_used,
            "metadata": metadata,
            "processing_time": prompt_time + llm_time,
            "generation_mode": "continuous_optimization"
        })
        
    except Exception as e:
        print(f"Error in optimize endpoint: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/learn', methods=['POST'])
def learn_from_interaction():
    """
    Submit feedback for the agentic system to learn from (with vector storage)
    """
    try:
        data = request.get_json()
        required_fields = ['input_data', 'prompt_result', 'llm_response']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400
        
        # Submit learning data with enhanced vector storage
        agentic_generator.learn_from_interaction(
            input_data=data['input_data'],
            prompt_result=data['prompt_result'],
            llm_response=data['llm_response'],
            quality_score=data.get('quality_score'),
            user_feedback=data.get('user_feedback'),
            metadata=data.get('metadata', {})
        )
        
        # Get updated capabilities including vector stats
        capabilities = agentic_generator.get_agentic_capabilities()
        
        return jsonify({
            "message": "Learning data submitted successfully and stored in vector database",
            "learning_stats": capabilities["learning_stats"],
            "vector_stats": capabilities["vector_stats"],
            "total_interactions": len(agentic_generator.interaction_history)
        })
        
    except Exception as e:
        print(f"Error in learn endpoint: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/vector/stats', methods=['GET'])
def get_vector_stats():
    """
    Get vector database performance statistics
    """
    try:
        if agentic_generator.vector_service:
            stats = agentic_generator.vector_service.get_stats()
            return jsonify({
                "vector_database": "enabled",
                "stats": stats
            })
        else:
            return jsonify({
                "vector_database": "disabled",
                "message": "Vector database not available"
            })
            
    except Exception as e:
        print(f"Error in vector stats endpoint: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/feedback', methods=['GET'])
def get_feedback():
    """
    Get optimization suggestions based on interaction history
    """
    try:
        feedback_data = feedback_system.get_optimization_suggestions()
        
        return jsonify({
            "suggestions": feedback_data["suggestions"],
            "interaction_count": feedback_data["interaction_count"],
            "performance_metrics": feedback_data.get("performance_metrics", {})
        })
        
    except Exception as e:
        print(f"Error in feedback endpoint: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/capabilities', methods=['GET'])
def get_system_capabilities():
    """
    Get comprehensive agentic system capabilities and statistics
    """
    try:
        capabilities = agentic_generator.get_agentic_capabilities()
        
        # Add system status
        system_status = {
            "agentic_mode": "enabled",
            "vector_database": "enabled" if agentic_generator.vector_service else "disabled",
            "ollama_status": "connected" if ollama_llm.test_connection() else "disconnected",
            "total_capabilities": len(capabilities["capabilities"]),
            "supported_contexts": capabilities["supported_contexts"],
            "supported_data_types": capabilities["supported_data_types"]
        }
        
        return jsonify({
            "system_status": system_status,
            "capabilities": capabilities["capabilities"],
            "analysis_features": capabilities["analysis_features"],
            "learning_stats": capabilities["learning_stats"],
            "vector_stats": capabilities["vector_stats"]
        })
        
    except Exception as e:
        print(f"Error in capabilities endpoint: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    # Test Ollama connection
    ollama_status = "connected" if ollama_llm.test_connection() else "disconnected"
    
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "agentic_generator": "initialized",
            "vector_database": "enabled" if agentic_generator.vector_service else "disabled",
            "ollama_llm": ollama_status,
            "feedback_system": "initialized"
        },
        "ollama_config": {
            "host": OLLAMA_HOST,
            "port": OLLAMA_PORT,
            "model": OLLAMA_MODEL
        }
    })

@app.route('/ollama/models', methods=['GET'])
def get_ollama_models():
    """Get available Ollama models"""
    try:
        models = ollama_llm.list_models()
        return jsonify({
            "models": models,
            "current_model": OLLAMA_MODEL
        })
    except Exception as e:
        return jsonify({"error": f"Could not retrieve models: {str(e)}"}), 500

@app.route('/ollama/info', methods=['GET'])
def get_ollama_info():
    """Get Ollama model information"""
    try:
        model_info = ollama_llm.get_model_info()
        return jsonify(model_info)
    except Exception as e:
        return jsonify({"error": f"Could not retrieve model info: {str(e)}"}), 500

@app.route('/stats', methods=['GET'])
def get_statistics():
    """Get system usage statistics"""
    try:
        stats = feedback_system.get_usage_statistics()
        return jsonify({
            "usage_statistics": stats,
            "available_contexts": [
                "core_banking", "lending_decision", "loan_approval", 
                "loan_offers", "card_data", "risk_assessment"
            ],
            "available_data_types": [
                "transaction_history", "time_series_data", "transaction_analysis",
                "credit_assessment", "card_transactions", "card_behavior"
            ],
            "ollama_status": "connected" if ollama_llm.test_connection() else "disconnected"
        })
    except Exception as e:
        print(f"Error in stats endpoint: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/feedback/clear', methods=['DELETE'])
def clear_feedback():
    """Clear all interaction history (for testing/demo purposes)"""
    try:
        feedback_system.clear_interactions()
        return jsonify({"message": "Interaction history cleared successfully"})
    except Exception as e:
        print(f"Error clearing feedback: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    """Custom 404 handler"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/",
            "/generate",
            "/learn",
            "/feedback", 
            "/capabilities",
            "/vector/stats",
            "/agentic/analyze",
            "/agentic/capabilities",
            "/health",
            "/stats",
            "/ollama/models",
            "/ollama/info"
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
    print("🚀 Starting Prompting Engine Demo...")
    print(f"🤖 Ollama Configuration:")
    print(f"   Host: {OLLAMA_HOST}")
    print(f"   Port: {OLLAMA_PORT}")
    print(f"   Model: {OLLAMA_MODEL}")
    print("🌐 Web Interface available at /")
    print("=" * 60)
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG) 