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
from app.generators.prompt_generator import PromptGenerator
from app.llm.mock_llm import OllamaLLM
from app.feedback.feedback_system import FeedbackSystem

# Initialize components
app = Flask(__name__)
CORS(app)

# Initialize system components
prompt_generator = PromptGenerator()
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
    Generate a prompt and get LLM response
    
    Expected JSON:
    {
        "context": "core_banking",
        "data_type": "transaction_history", 
        "input_data": {
            "transaction_data": "{\"transactions\": [...]}"
        }
    }
    """
    try:
        start_time = time.time()
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        context = data.get('context')
        data_type = data.get('data_type')
        input_data = data.get('input_data')
        
        if not all([context, data_type, input_data]):
            return jsonify({"error": "Missing required fields: context, data_type, input_data"}), 400
        
        # Generate the prompt
        prompt_text, template_name, prompt_time = prompt_generator.generate_prompt(
            context=context,
            data_type=data_type,
            input_data=input_data
        )
        
        # Get LLM response using Ollama
        response_text, tokens_used, llm_time = ollama_llm.generate_response(
            prompt=prompt_text,
            template_name=template_name
        )
        
        total_time = time.time() - start_time
        
        # Log the interaction
        feedback_system.log_interaction(
            prompt=prompt_text,
            response=response_text,
            template_name=template_name,
            tokens_used=tokens_used,
            processing_time=llm_time,
            context=context,
            data_type=data_type
        )
        
        return jsonify({
            "prompt": prompt_text,
            "response": response_text,
            "tokens_used": tokens_used,
            "template_used": template_name,
            "processing_time": total_time
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error in generate endpoint: {traceback.format_exc()}")
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

@app.route('/templates', methods=['GET'])
def get_templates():
    """
    Get information about all available templates
    """
    try:
        template_info = prompt_generator.get_available_templates()
        
        # Convert to the expected response format
        templates = []
        for template in template_info["templates"]:
            templates.append({
                "name": template["name"],
                "category": template["category"],
                "description": template["description"],
                "parameters": [p["name"] for p in template["parameters"]],
                "examples": template["examples"]
            })
        
        return jsonify({"templates": templates})
        
    except Exception as e:
        print(f"Error in templates endpoint: {traceback.format_exc()}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/templates/<context>/<data_type>', methods=['GET'])
def get_template_details(context, data_type):
    """
    Get detailed information about a specific template
    """
    try:
        template_info = prompt_generator.get_template_parameters(context, data_type)
        
        if not template_info:
            return jsonify({
                "error": f"No template found for context '{context}' and data_type '{data_type}'"
            }), 404
        
        return jsonify(template_info)
        
    except Exception as e:
        print(f"Error in template details endpoint: {traceback.format_exc()}")
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
            "prompt_generator": "initialized",
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
            "/feedback", 
            "/templates",
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