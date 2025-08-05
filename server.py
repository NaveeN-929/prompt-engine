#!/usr/bin/env python3
"""
Fixed UI Server - Guaranteed to show prompts
"""

import sys
import os
import time
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def start_fixed_server():
    """Start server with guaranteed prompt display"""
    try:
        print("Starting Fixed UI Server...")
        
        # Import Flask components
        from flask import Flask, jsonify, request, render_template_string
        from flask_cors import CORS
        
        # Create Flask app
        app = Flask(__name__)
        CORS(app)
        
        # Simple, bulletproof HTML template
        HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agentic Prompt Engine - Fixed UI</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            color: #333; 
        }
        .header h1 { 
            color: #667eea; 
            margin-bottom: 10px; 
        }
        .section { 
            margin: 20px 0; 
            padding: 20px; 
            border: 1px solid #e0e0e0; 
            border-radius: 10px; 
            background: #fafafa; 
        }
        .button { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            margin: 5px; 
            font-size: 16px; 
            font-weight: bold; 
        }
        .button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); 
        }
        textarea { 
            width: 100%; 
            height: 120px; 
            margin: 10px 0; 
            padding: 15px; 
            border: 2px solid #e0e0e0; 
            border-radius: 8px; 
            font-family: 'Courier New', monospace; 
            font-size: 14px; 
        }
        .status { 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 8px; 
            background: #e3f2fd; 
            border-left: 4px solid #2196f3; 
        }
        .prompt-container { 
            background: #f8f9fa; 
            border: 2px solid #28a745; 
            border-radius: 10px; 
            margin: 20px 0; 
            overflow: hidden;
        }
        .prompt-header { 
            background: #28a745; 
            color: white; 
            padding: 15px; 
            font-weight: bold; 
            font-size: 18px; 
        }
        .prompt-content { 
            padding: 20px; 
            font-family: 'Courier New', monospace; 
            line-height: 1.6; 
            white-space: pre-wrap; 
            word-wrap: break-word; 
            max-height: 600px; 
            overflow-y: auto; 
            background: white; 
        }
        .metadata { 
            background: #fff3e0; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 15px 0; 
            border-left: 4px solid #ff9800; 
        }
        .hidden { 
            display: none; 
        }
        .loading { 
            text-align: center; 
            padding: 20px; 
            font-size: 18px; 
            color: #666; 
        }
        .error { 
            background: #f8d7da; 
            color: #721c24; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 15px 0; 
            border-left: 4px solid #dc3545; 
        }
        .success { 
            background: #d4edda; 
            color: #155724; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 15px 0; 
            border-left: 4px solid #28a745; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Agentic Prompt Engine</h1>
            <p>AI-powered prompt generation with vector acceleration</p>
        </div>
        
        <div class="section">
            <h3>System Status</h3>
            <div class="status">
                Server running on port 5000<br>
                Agentic mode active<br>
                Vector database enabled<br>
                Ready for generation
            </div>
        </div>
        
        <div class="section">
            <h3>Test Agentic Generation</h3>
            <p>Enter financial data to test the AI prompt generation:</p>
            <textarea id="testData" placeholder='{"transactions": [{"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"}]}'></textarea>
            <br>
            <button class="button" onclick="generatePrompt()">Generate Agentic Prompt</button>
            <button class="button" onclick="loadExample()">Load Example</button>
            <button class="button" onclick="clearAll()">Clear</button>
        </div>
        
        <!-- Status Message Area -->
        <div id="statusMessage" class="hidden"></div>
        
        <!-- Prompt Display Area -->
        <div id="promptContainer" class="prompt-container hidden">
            <div class="prompt-header">
                Generated Agentic Prompt
                <span id="promptMeta" style="float: right; font-size: 14px;"></span>
            </div>
            <div id="promptContent" class="prompt-content">
                No prompt generated yet.
            </div>
        </div>
        
        <!-- Metadata Display -->
        <div id="metadataContainer" class="metadata hidden">
            <h4>Generation Details</h4>
            <div id="metadataContent"></div>
        </div>
    </div>
    
    <script>
        console.log('Fixed UI JavaScript loaded successfully');
        
        function loadExample() {
            console.log('Loading example data');
            document.getElementById('testData').value = JSON.stringify({
                "transactions": [
                    {"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"},
                    {"date": "2024-01-16", "amount": -50.00, "type": "debit", "description": "Grocery shopping"},
                    {"date": "2024-01-17", "amount": -1200.00, "type": "debit", "description": "Rent payment"}
                ],
                "account_balance": 2250.00,
                "customer_id": "CUST_001"
            }, null, 2);
        }
        
        function clearAll() {
            console.log('Clearing all results');
            document.getElementById('statusMessage').className = 'hidden';
            document.getElementById('promptContainer').className = 'prompt-container hidden';
            document.getElementById('metadataContainer').className = 'metadata hidden';
            document.getElementById('promptContent').textContent = 'No prompt generated yet.';
        }
        
        function showStatus(message, isError = false) {
            const statusEl = document.getElementById('statusMessage');
            statusEl.className = isError ? 'error' : 'success';
            statusEl.innerHTML = message;
        }
        
        function showLoading() {
            const statusEl = document.getElementById('statusMessage');
            statusEl.className = 'loading';
            statusEl.innerHTML = '⏳ Generating agentic prompt... Please wait...';
        }
        
        async function generatePrompt() {
            const data = document.getElementById('testData').value;
            const promptContainer = document.getElementById('promptContainer');
            const promptContent = document.getElementById('promptContent');
            const promptMeta = document.getElementById('promptMeta');
            const metadataContainer = document.getElementById('metadataContainer');
            const metadataContent = document.getElementById('metadataContent');
            
            try {
                console.log('Starting prompt generation...');
                
                // Show loading
                showLoading();
                promptContainer.className = 'prompt-container hidden';
                metadataContainer.className = 'metadata hidden';
                
                // Parse input data
                let inputData;
                try {
                    inputData = JSON.parse(data);
                    console.log('Input data parsed successfully:', inputData);
                } catch (parseError) {
                    throw new Error('Invalid JSON format in input data: ' + parseError.message);
                }
                
                // Make API request
                console.log('📡 Sending request to /generate endpoint...');
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        input_data: inputData,
                        generation_type: 'standard'
                    })
                });
                
                console.log('📡 Response received, status:', response.status);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                console.log('Response parsed successfully');
                console.log('Response data:', {
                    hasPrompt: !!result.prompt,
                    promptLength: result.prompt ? result.prompt.length : 0,
                    vectorAccelerated: result.vector_accelerated,
                    processingTime: result.processing_time
                });
                
                if (result.prompt) {
                    // Show success status
                    showStatus(`Prompt generated successfully! Length: ${result.prompt.length} chars, Vector: ${result.vector_accelerated ? 'Yes' : 'No'}, Time: ${(result.processing_time || 0).toFixed(3)}s`);
                    
                    // Display the prompt
                    promptContent.textContent = result.prompt;
                    promptMeta.textContent = `${result.prompt.length} chars | ${(result.processing_time || 0).toFixed(3)}s | Vector: ${result.vector_accelerated ? '⚡' : '❌'}`;
                    promptContainer.className = 'prompt-container';
                    
                    console.log('Prompt displayed in UI');
                    
                    // Display metadata
                    metadataContent.innerHTML = `
                        <strong>Generation Details:</strong><br>
                        • Mode: ${result.agentic_metadata?.generation_mode || 'standard'}<br>
                        • Context: ${result.agentic_metadata?.context || 'auto-detected'}<br>
                        • Data Type: ${result.agentic_metadata?.data_type || 'auto-inferred'}<br>
                        • Template: ${result.agentic_metadata?.template_used || 'autonomous'}<br>
                        • Processing Time: ${(result.processing_time || 0).toFixed(4)} seconds<br>
                        • Vector Acceleration: ${result.vector_accelerated ? 'Enabled' : 'Disabled'}<br>
                        • Prompt Length: ${result.prompt.length} characters<br>
                        • Generated At: ${new Date().toLocaleString()}<br>
                        • Status: ${result.status || 'success'}
                    `;
                    metadataContainer.className = 'metadata';
                    
                    console.log('Metadata displayed in UI');
                    
                } else {
                    throw new Error('No prompt in API response: ' + JSON.stringify(result));
                }
                
            } catch (error) {
                console.error('❌ Generation error:', error);
                showStatus(`❌ Generation failed: ${error.message}`, true);
                promptContainer.className = 'prompt-container hidden';
                metadataContainer.className = 'metadata hidden';
            }
        }
        
        // Load example on page load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded, initializing...');
            loadExample();
            console.log('Initialization complete');
        });
        
        console.log('All JavaScript functions defined successfully');
    </script>
</body>
</html>
        """
        
        @app.route('/')
        def home():
            return render_template_string(HTML_TEMPLATE)
        
        # Initialize agentic generator at startup
        print("🚀 Initializing agentic generator with vector DB...")
        try:
            from app.generators.agentic_prompt_generator import AgenticPromptGenerator
            app.agentic_gen = AgenticPromptGenerator(enable_vector_db=True)
            print("✅ Agentic generator ready!")
        except Exception as e:
            print(f"⚠️ Error initializing agentic generator: {e}")
            app.agentic_gen = None

        @app.route('/generate', methods=['POST'])
        def generate():
            try:
                # Use the pre-initialized agentic generator
                if not app.agentic_gen:
                    return jsonify({"error": "Agentic generator not available", "status": "error"}), 503
                
                data = request.get_json()
                input_data = data.get('input_data', {})
                generation_type = data.get('generation_type', 'standard')
                
                print(f"Processing generation request: {generation_type}")
                start_time = time.time()
                
                # Generate prompt
                prompt, metadata, gen_time = app.agentic_gen.generate_agentic_prompt(
                    input_data=input_data
                )
                
                total_time = time.time() - start_time
                print(f"Generated in {total_time:.3f}s")
                
                # Check if vector was used
                vector_used = hasattr(app.agentic_gen, 'vector_service') and app.agentic_gen.vector_service is not None
                
                response_data = {
                    "prompt": prompt,
                    "agentic_metadata": metadata,
                    "processing_time": total_time,
                    "status": "success",
                    "vector_accelerated": vector_used,
                    "generation_type": generation_type
                }
                
                print(f"Sending response: prompt_length={len(prompt)}, vector_used={vector_used}")
                return jsonify(response_data)
                
            except Exception as e:
                print(f"Generation error: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({"error": str(e), "status": "error"}), 500
        

        @app.route('/system/status')
        def system_status():
            """Get overall system status"""
            try:
                # Check Ollama connection
                from app.llm.mock_llm import OllamaLLM
                from config import OLLAMA_HOST, OLLAMA_PORT, OLLAMA_MODEL
                
                ollama = OllamaLLM(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}", OLLAMA_MODEL)
                ollama_connected = ollama.test_connection()
                
                # Check vector database
                vector_status = "disabled"
                vector_collections = 0
                if app.agentic_gen and hasattr(app.agentic_gen, 'vector_service'):
                    if app.agentic_gen.vector_service and app.agentic_gen.vector_service.client:
                        vector_status = "memory_mode" if app.agentic_gen.vector_service.memory_mode else "connected"
                        try:
                            collections = app.agentic_gen.vector_service.client.get_collections()
                            vector_collections = len(collections.collections)
                        except:
                            pass
                
                return jsonify({
                    "status": "operational",
                    "components": {
                        "server": "running",
                        "ollama": "connected" if ollama_connected else "disconnected",
                        "vector_db": vector_status,
                        "agentic_generator": "ready" if app.agentic_gen else "not_initialized"
                    },
                    "configuration": {
                        "ollama_host": OLLAMA_HOST,
                        "ollama_port": OLLAMA_PORT,
                        "ollama_model": OLLAMA_MODEL,
                        "vector_collections": vector_collections
                    },
                    "timestamp": time.time()
                })
            except Exception as e:
                return jsonify({"error": str(e), "status": "error"}), 500
        
        @app.route('/system/llm')
        def system_llm():
            """Get LLM system information"""
            try:
                from app.llm.mock_llm import OllamaLLM
                from config import OLLAMA_HOST, OLLAMA_PORT, OLLAMA_MODEL
                
                ollama = OllamaLLM(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}", OLLAMA_MODEL)
                
                # Test connection
                connected = ollama.test_connection()
                
                llm_info = {
                    "status": "connected" if connected else "disconnected",
                    "host": OLLAMA_HOST,
                    "port": OLLAMA_PORT,
                    "current_model": OLLAMA_MODEL,
                    "connection_url": f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
                }
                
                if connected:
                    try:
                        model_info = ollama.get_model_info()
                        llm_info["model_details"] = model_info
                    except:
                        llm_info["model_details"] = "unavailable"
                
                return jsonify(llm_info)
            except Exception as e:
                return jsonify({"error": str(e), "status": "error"}), 500
        
        @app.route('/ollama/models')
        def ollama_models():
            """Get available Ollama models"""
            try:
                from app.llm.mock_llm import OllamaLLM
                from config import OLLAMA_HOST, OLLAMA_PORT, OLLAMA_MODEL
                
                ollama = OllamaLLM(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}", OLLAMA_MODEL)
                
                if not ollama.test_connection():
                    return jsonify({"error": "Ollama not connected", "models": []}), 503
                
                models = ollama.list_models()
                
                return jsonify({
                    "status": "success",
                    "current_model": OLLAMA_MODEL,
                    "available_models": models,
                    "total_models": len(models)
                })
            except Exception as e:
                return jsonify({"error": str(e), "models": []}), 500
        
        @app.route('/system/vector')
        def system_vector():
            """Get vector database system information"""
            try:
                # Check if agentic generator is initialized
                if not app.agentic_gen:
                    return jsonify({
                        "status": "not_initialized",
                        "message": "Agentic generator not initialized"
                    })
                
                vector_service = app.agentic_gen.vector_service
                if not vector_service:
                    return jsonify({
                        "status": "disabled",
                        "message": "Vector service not available"
                    })
                
                # Get vector service stats
                stats = vector_service.get_stats()
                
                return jsonify({
                    "status": "active",
                    "mode": "memory" if vector_service.memory_mode else "persistent",
                    "embedding_model": "all-MiniLM-L6-v2",
                    "embedding_dimension": vector_service.embedding_dim,
                    "statistics": stats,
                    "collections": vector_service.collections
                })
            except Exception as e:
                return jsonify({"error": str(e), "status": "error"}), 500
        
        @app.route('/qdrant/info')
        def qdrant_info():
            """Get Qdrant database information"""
            try:
                # Check if agentic generator is initialized
                if not app.agentic_gen:
                    return jsonify({
                        "error": "Agentic generator not initialized"
                    }), 503
                
                vector_service = app.agentic_gen.vector_service
                if not vector_service or not vector_service.client:
                    return jsonify({
                        "error": "Qdrant client not available"
                    }), 503
                
                # Get Qdrant cluster info
                try:
                    cluster_info = vector_service.client.get_cluster_info()
                    return jsonify({
                        "status": "connected",
                        "mode": "memory" if vector_service.memory_mode else "persistent",
                        "cluster_info": cluster_info,
                        "collections_count": len(vector_service.collections)
                    })
                except:
                    # Fallback for memory mode or simplified info
                    collections = vector_service.client.get_collections()
                    return jsonify({
                        "status": "connected",
                        "mode": "memory" if vector_service.memory_mode else "persistent",
                        "collections_count": len(collections.collections),
                        "available_collections": [col.name for col in collections.collections]
                    })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/qdrant/collections')
        def qdrant_collections():
            """Get Qdrant collections information"""
            try:
                # Check if agentic generator is initialized
                if not app.agentic_gen:
                    return jsonify({
                        "error": "Agentic generator not initialized",
                        "collections": []
                    }), 503
                
                vector_service = app.agentic_gen.vector_service
                if not vector_service or not vector_service.client:
                    return jsonify({
                        "error": "Qdrant client not available",
                        "collections": []
                    }), 503
                
                # Get collections info
                collections = vector_service.client.get_collections()
                
                detailed_collections = []
                for collection in collections.collections:
                    try:
                        collection_info = vector_service.client.get_collection(collection.name)
                        detailed_collections.append({
                            "name": collection.name,
                            "points_count": collection_info.points_count,
                            "vectors_count": collection_info.vectors_count,
                            "indexed_vectors_count": getattr(collection_info, 'indexed_vectors_count', 0),
                            "status": getattr(collection_info, 'status', 'active')
                        })
                    except Exception as e:
                        detailed_collections.append({
                            "name": collection.name,
                            "error": str(e),
                            "status": "error"
                        })
                
                return jsonify({
                    "status": "success",
                    "total_collections": len(collections.collections),
                    "collections": detailed_collections,
                    "configured_collections": vector_service.collections
                })
            except Exception as e:
                return jsonify({"error": str(e), "collections": []}), 500
        
        print("Starting Fixed UI Server on http://localhost:5000")
        print("Guaranteed prompt display!")
        print("Vector acceleration enabled")
        print("=" * 60)
        
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_fixed_server()