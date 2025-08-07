"""
RAG-Enhanced Autonomous Financial Analysis Agent Server
"""

import asyncio
import json
import time
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

# Import core components
from core.rag_service import RAGService
from core.prompt_consumer import PromptConsumerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global services
rag_service = None
prompt_consumer = None

# Simple storage for demo purposes
interaction_history = []
agent_statistics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "average_processing_time": 0.0,
    "rag_augmented_requests": 0
}

@app.before_first_request
async def initialize_services():
    """Initialize RAG and other services"""
    global rag_service, prompt_consumer
    
    try:
        logger.info("Initializing RAG-enhanced services...")
        
        # Initialize RAG service
        rag_service = RAGService()
        await rag_service.initialize()
        
        # Initialize prompt consumer
        prompt_consumer = PromptConsumerService()
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Continue with limited functionality

@app.route('/')
def index():
    """Serve the main RAG-enhanced interface"""
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG-Enhanced Autonomous Financial Agent</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
            min-height: 100vh; 
            color: white;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1); 
            padding: 30px; 
            border-radius: 15px; 
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3); 
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .header h1 { 
            color: #00d4ff; 
            margin-bottom: 10px; 
            font-size: 2.8em;
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
        }
        .rag-badge {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            display: inline-block;
            margin: 10px;
        }
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .feature-card {
            background: rgba(0, 212, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(0, 212, 255, 0.3);
            transition: transform 0.3s ease;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 212, 255, 0.2);
        }
        .feature-card h3 {
            color: #00d4ff;
            margin-bottom: 15px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .status-card {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid;
        }
        .status-active { border-left-color: #00d4ff; }
        .status-warning { border-left-color: #ffc107; }
        .status-error { border-left-color: #dc3545; }
        .button { 
            background: linear-gradient(45deg, #00d4ff, #0099cc); 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            margin: 5px; 
            font-size: 16px; 
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4); 
        }
        .button.secondary {
            background: linear-gradient(45deg, #6c757d, #495057);
        }
        textarea { 
            width: 100%; 
            height: 150px; 
            margin: 10px 0; 
            padding: 15px; 
            border: 1px solid rgba(0, 212, 255, 0.3); 
            border-radius: 8px; 
            font-family: 'Courier New', monospace; 
            font-size: 14px;
            background: rgba(255,255,255,0.1);
            color: white;
            resize: vertical;
        }
        .result-container { 
            background: rgba(0, 212, 255, 0.1); 
            border: 2px solid #00d4ff; 
            border-radius: 10px; 
            margin: 20px 0; 
            overflow: hidden;
            display: none;
        }
        .result-header { 
            background: #00d4ff; 
            color: #1a1a2e; 
            padding: 15px; 
            font-weight: bold; 
            font-size: 18px; 
        }
        .result-content { 
            padding: 20px; 
            max-height: 600px; 
            overflow-y: auto; 
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            line-height: 1.6;
        }
        .rag-indicator {
            float: right;
            background: rgba(255, 107, 107, 0.2);
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            font-size: 18px;
        }
        .tab-container {
            margin: 20px 0;
        }
        .tabs {
            display: flex;
            border-bottom: 2px solid rgba(0, 212, 255, 0.3);
        }
        .tab {
            padding: 12px 24px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        .tab.active {
            border-bottom-color: #00d4ff;
            color: #00d4ff;
        }
        .tab-content {
            display: none;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 0 0 10px 10px;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 RAG-Enhanced Autonomous Agent</h1>
            <span class="rag-badge">🚀 Vector Accelerated</span>
            <span class="rag-badge">🧠 Knowledge Augmented</span>
            <p>Advanced AI-powered financial analysis with Retrieval Augmented Generation</p>
        </div>
        
        <div class="features-grid">
            <div class="feature-card">
                <h3>🔍 RAG-Enhanced Analysis</h3>
                <p>Retrieval Augmented Generation with financial knowledge base and vector acceleration</p>
            </div>
            <div class="feature-card">
                <h3>⚡ Vector Database</h3>
                <p>Ultra-fast similarity search and context retrieval using Qdrant vector database</p>
            </div>
            <div class="feature-card">
                <h3>🧠 Knowledge Base</h3>
                <p>Curated financial knowledge and best practices for enhanced analysis accuracy</p>
            </div>
            <div class="feature-card">
                <h3>🔄 Continuous Learning</h3>
                <p>Stores successful patterns and improves recommendations over time</p>
            </div>
        </div>
        
        <div class="status-grid" id="statusGrid">
            <div class="status-card status-active">
                <strong>🌐 Server Status</strong><br>
                <span id="serverStatus">Loading...</span>
            </div>
            <div class="status-card status-active">
                <strong>🔍 RAG Service</strong><br>
                <span id="ragStatus">Loading...</span>
            </div>
            <div class="status-card status-active">
                <strong>📊 Vector Database</strong><br>
                <span id="vectorStatus">Loading...</span>
            </div>
            <div class="status-card status-active">
                <strong>🔗 Prompt Engine</strong><br>
                <span id="promptEngineStatus">Loading...</span>
            </div>
        </div>
        
        <div class="tab-container">
            <div class="tabs">
                <div class="tab active" onclick="switchTab('analysis')">🔍 Analysis</div>
                <div class="tab" onclick="switchTab('rag')">🧠 RAG Status</div>
                <div class="tab" onclick="switchTab('vector')">⚡ Vector DB</div>
                <div class="tab" onclick="switchTab('history')">📊 History</div>
            </div>
            
            <div id="analysis" class="tab-content active">
                <h3>🔍 RAG-Enhanced Financial Analysis</h3>
                <p>Provide financial data for comprehensive analysis with knowledge augmentation:</p>
                <textarea id="analysisData" placeholder='{"transactions": [{"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"}], "account_balance": 2250.00}'></textarea>
                <br>
                <button class="button" onclick="processAnalysis()">🚀 RAG-Enhanced Analysis</button>
                <button class="button secondary" onclick="loadExampleData()">📝 Load Example</button>
                <button class="button secondary" onclick="clearResults()">🗑️ Clear</button>
            </div>
            
            <div id="rag" class="tab-content">
                <h3>🧠 RAG Service Status</h3>
                <div id="ragDetails">Loading RAG status...</div>
                <button class="button" onclick="refreshRAGStatus()">🔄 Refresh</button>
            </div>
            
            <div id="vector" class="tab-content">
                <h3>⚡ Vector Database Status</h3>
                <div id="vectorDetails">Loading vector database status...</div>
                <button class="button" onclick="refreshVectorStatus()">🔄 Refresh</button>
            </div>
            
            <div id="history" class="tab-content">
                <h3>📊 Interaction History</h3>
                <div id="historyDetails">Loading history...</div>
                <button class="button" onclick="refreshHistory()">🔄 Refresh</button>
                <button class="button secondary" onclick="clearHistory()">🗑️ Clear History</button>
            </div>
        </div>
        
        <!-- Results Display -->
        <div id="resultsContainer" class="result-container">
            <div class="result-header">
                <span>RAG-Enhanced Analysis Results</span>
                <span class="rag-indicator" id="ragIndicator">🧠 RAG: Enabled</span>
                <span style="float: right; font-size: 14px;" id="processingTime"></span>
            </div>
            <div id="resultsContent" class="result-content"></div>
        </div>
        
        <!-- Loading Indicator -->
        <div id="loadingIndicator" class="loading" style="display: none;">
            🔄 Processing RAG-enhanced analysis... Retrieving relevant knowledge...
        </div>
    </div>
    
    <script>
        // Tab switching
        function switchTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
            
            // Load content for specific tabs
            if (tabName === 'rag') refreshRAGStatus();
            if (tabName === 'vector') refreshVectorStatus();
            if (tabName === 'history') refreshHistory();
        }
        
        // Load example data
        function loadExampleData() {
            document.getElementById('analysisData').value = JSON.stringify({
                "transactions": [
                    {"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"},
                    {"date": "2024-01-16", "amount": -50.00, "type": "debit", "description": "Grocery shopping"},
                    {"date": "2024-01-17", "amount": -1200.00, "type": "debit", "description": "Rent payment"},
                    {"date": "2024-01-18", "amount": -75.50, "type": "debit", "description": "Utilities bill"},
                    {"date": "2024-01-20", "amount": 2000.00, "type": "credit", "description": "Freelance income"}
                ],
                "account_balance": 2175.50,
                "customer_id": "CUST_001",
                "account_type": "checking"
            }, null, 2);
        }
        
        // Process analysis
        async function processAnalysis() {
            const data = document.getElementById('analysisData').value;
            const loadingEl = document.getElementById('loadingIndicator');
            const resultsEl = document.getElementById('resultsContainer');
            const contentEl = document.getElementById('resultsContent');
            const timeEl = document.getElementById('processingTime');
            const ragEl = document.getElementById('ragIndicator');
            
            try {
                loadingEl.style.display = 'block';
                resultsEl.style.display = 'none';
                
                let inputData;
                try {
                    inputData = JSON.parse(data);
                } catch (parseError) {
                    throw new Error('Invalid JSON format: ' + parseError.message);
                }
                
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        input_data: inputData,
                        enable_rag: true
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                
                loadingEl.style.display = 'none';
                resultsEl.style.display = 'block';
                
                contentEl.textContent = result.analysis || result.response || 'No analysis available';
                timeEl.textContent = `${result.processing_time?.toFixed(3)}s`;
                
                // Update RAG indicator
                if (result.rag_metadata?.rag_enabled) {
                    ragEl.textContent = `🧠 RAG: ${result.rag_metadata.context_items_used} items`;
                    ragEl.style.background = 'rgba(40, 167, 69, 0.3)';
                } else {
                    ragEl.textContent = '🧠 RAG: Disabled';
                    ragEl.style.background = 'rgba(255, 107, 107, 0.3)';
                }
                
            } catch (error) {
                loadingEl.style.display = 'none';
                resultsEl.style.display = 'block';
                contentEl.textContent = `Error: ${error.message}`;
                ragEl.textContent = '🧠 RAG: Error';
                ragEl.style.background = 'rgba(220, 53, 69, 0.3)';
            }
        }
        
        // Refresh statuses
        async function refreshStatus() {
            try {
                const response = await fetch('/status');
                const status = await response.json();
                
                document.getElementById('serverStatus').innerHTML = `✅ ${status.status || 'Running'}`;
                
            } catch (error) {
                document.getElementById('serverStatus').innerHTML = '❌ Error';
            }
        }
        
        async function refreshRAGStatus() {
            try {
                const response = await fetch('/rag/status');
                const status = await response.json();
                
                document.getElementById('ragStatus').innerHTML = `✅ ${status.status || 'Active'}`;
                
                let details = `
                    <h4>RAG Service Statistics:</h4>
                    <p><strong>Status:</strong> ${status.status || 'Unknown'}</p>
                    <p><strong>Total Retrievals:</strong> ${status.total_retrievals || 0}</p>
                    <p><strong>Cache Hit Rate:</strong> ${((status.cache_hit_rate || 0) * 100).toFixed(1)}%</p>
                    <p><strong>Successful Augmentations:</strong> ${status.successful_augmentations || 0}</p>
                    <p><strong>Vector Searches:</strong> ${status.vector_searches || 0}</p>
                    <p><strong>Collections:</strong> ${(status.collections || []).join(', ')}</p>
                    <p><strong>Embedding Dimension:</strong> ${status.embedding_dimension || 'Unknown'}</p>
                `;
                
                document.getElementById('ragDetails').innerHTML = details;
                
            } catch (error) {
                document.getElementById('ragStatus').innerHTML = '❌ Error';
                document.getElementById('ragDetails').innerHTML = `Error loading RAG status: ${error.message}`;
            }
        }
        
        async function refreshVectorStatus() {
            try {
                const response = await fetch('/vector/status');
                const status = await response.json();
                
                document.getElementById('vectorStatus').innerHTML = `✅ ${status.status || 'Connected'}`;
                
                let details = `
                    <h4>Vector Database Details:</h4>
                    <p><strong>Status:</strong> ${status.status || 'Unknown'}</p>
                    <p><strong>Host:</strong> ${status.host || 'Unknown'}:${status.port || 'Unknown'}</p>
                    <p><strong>Total Collections:</strong> ${status.total_collections || 0}</p>
                    <p><strong>Embedding Model:</strong> ${status.embedding_model || 'Unknown'}</p>
                    <p><strong>Embedding Dimension:</strong> ${status.embedding_dimension || 'Unknown'}</p>
                `;
                
                if (status.collections_detail) {
                    details += '<h5>Collections:</h5><ul>';
                    status.collections_detail.forEach(col => {
                        details += `<li><strong>${col.name}:</strong> ${col.points_count || 0} points</li>`;
                    });
                    details += '</ul>';
                }
                
                document.getElementById('vectorDetails').innerHTML = details;
                
            } catch (error) {
                document.getElementById('vectorStatus').innerHTML = '❌ Error';
                document.getElementById('vectorDetails').innerHTML = `Error loading vector status: ${error.message}`;
            }
        }
        
        async function refreshHistory() {
            try {
                const response = await fetch('/history');
                const history = await response.json();
                
                let details = `<h4>Recent Interactions:</h4>`;
                
                if (history.history && history.history.length > 0) {
                    details += '<ul>';
                    history.history.forEach((item, index) => {
                        details += `
                            <li>
                                <strong>Request ${item.request_id || index + 1}:</strong> 
                                ${item.status || 'Unknown'} 
                                (${item.processing_time?.toFixed(3) || 'Unknown'}s)
                                ${item.rag_metadata?.rag_enabled ? '🧠' : ''}
                            </li>
                        `;
                    });
                    details += '</ul>';
                } else {
                    details += '<p>No interactions recorded yet.</p>';
                }
                
                document.getElementById('historyDetails').innerHTML = details;
                
            } catch (error) {
                document.getElementById('historyDetails').innerHTML = `Error loading history: ${error.message}`;
            }
        }
        
        async function clearHistory() {
            try {
                await fetch('/clear_history', { method: 'DELETE' });
                refreshHistory();
            } catch (error) {
                console.error('Error clearing history:', error);
            }
        }
        
        function clearResults() {
            document.getElementById('resultsContainer').style.display = 'none';
            document.getElementById('loadingIndicator').style.display = 'none';
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadExampleData();
            refreshStatus();
            refreshRAGStatus();
            
            // Check prompt engine status
            fetch('/prompt_engine/status')
                .then(response => response.json())
                .then(status => {
                    document.getElementById('promptEngineStatus').innerHTML = 
                        status.available ? '✅ Connected' : '⚠️ Unavailable';
                })
                .catch(() => {
                    document.getElementById('promptEngineStatus').innerHTML = '❌ Error';
                });
        });
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/analyze', methods=['POST'])
async def analyze():
    """RAG-enhanced analysis endpoint"""
    global agent_statistics
    
    start_time = time.time()
    agent_statistics["total_requests"] += 1
    
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({"error": "Missing input_data field"}), 400
        
        input_data = data['input_data']
        enable_rag = data.get('enable_rag', True)
        
        # Generate basic analysis
        analysis = perform_enhanced_analysis(input_data)
        
        # Augment with RAG if enabled and available
        rag_metadata = {"rag_enabled": False}
        
        if enable_rag and rag_service:
            try:
                # Augment the analysis with RAG
                augmented_analysis, rag_metadata = await rag_service.augment_prompt(
                    analysis, input_data
                )
                analysis = augmented_analysis
                agent_statistics["rag_augmented_requests"] += 1
                
                # Store interaction pattern for future retrieval
                await rag_service.store_interaction_pattern(
                    input_data, analysis, analysis, 0.8  # Assume good quality
                )
                
            except Exception as e:
                logger.warning(f"RAG augmentation failed: {e}")
                rag_metadata = {"rag_enabled": False, "error": str(e)}
        
        processing_time = time.time() - start_time
        
        # Create response
        response_data = {
            "request_id": f"req_{int(time.time())}_{id(analysis)}",
            "status": "success",
            "analysis": analysis,
            "processing_time": processing_time,
            "rag_metadata": rag_metadata,
            "input_data_summary": {
                "transaction_count": len(input_data.get("transactions", [])),
                "has_balance": "account_balance" in input_data,
                "keys": list(input_data.keys())
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in history
        interaction_history.append(response_data)
        if len(interaction_history) > 50:  # Keep last 50
            interaction_history[:] = interaction_history[-40:]
        
        # Update statistics
        agent_statistics["successful_requests"] += 1
        total_time = agent_statistics.get("total_processing_time", 0) + processing_time
        agent_statistics["total_processing_time"] = total_time
        agent_statistics["average_processing_time"] = total_time / agent_statistics["successful_requests"]
        
        return jsonify(response_data)
        
    except Exception as e:
        agent_statistics["failed_requests"] += 1
        logger.error(f"Analysis error: {e}")
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get agent status"""
    try:
        return jsonify({
            "status": "operational",
            "mode": "rag_enhanced",
            "version": "2.0.0-rag",
            "timestamp": datetime.now().isoformat(),
            "statistics": agent_statistics,
            "services": {
                "rag_service": "active" if rag_service else "inactive",
                "prompt_consumer": "active" if prompt_consumer else "inactive",
                "vector_database": "connected" if rag_service and rag_service.client else "disconnected"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/rag/status', methods=['GET'])
def get_rag_status():
    """Get RAG service status"""
    try:
        if not rag_service:
            return jsonify({"status": "inactive", "error": "RAG service not initialized"}), 503
        
        stats = rag_service.get_rag_statistics()
        return jsonify({
            "status": "active",
            **stats
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/vector/status', methods=['GET'])
async def get_vector_status():
    """Get vector database status"""
    try:
        if not rag_service:
            return jsonify({"status": "inactive", "error": "RAG service not initialized"}), 503
        
        vector_status = await rag_service.get_vector_status()
        return jsonify(vector_status)
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/prompt_engine/status', methods=['GET'])
async def get_prompt_engine_status():
    """Check prompt engine connectivity"""
    try:
        if not prompt_consumer:
            return jsonify({"available": False, "error": "Prompt consumer not initialized"})
        
        async with prompt_consumer as consumer:
            capabilities = await consumer.get_prompt_engine_capabilities()
            
        return jsonify({
            "available": "error" not in capabilities,
            "capabilities": capabilities if "error" not in capabilities else None,
            "error": capabilities.get("error")
        })
    except Exception as e:
        return jsonify({"available": False, "error": str(e)})

@app.route('/history', methods=['GET'])
def get_history():
    """Get interaction history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        return jsonify({
            "history": interaction_history[-limit:] if interaction_history else [],
            "total_count": len(interaction_history)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear_history', methods=['DELETE'])
def clear_history():
    """Clear interaction history"""
    try:
        global interaction_history
        interaction_history.clear()
        return jsonify({"success": True, "message": "History cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "mode": "rag_enhanced",
        "version": "2.0.0-rag",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "rag_service": rag_service is not None,
            "vector_database": rag_service.client is not None if rag_service else False,
            "prompt_consumer": prompt_consumer is not None
        }
    })

def perform_enhanced_analysis(input_data: Dict[str, Any]) -> str:
    """Perform enhanced financial analysis"""
    
    analysis = "=== RAG-ENHANCED FINANCIAL ANALYSIS ===\\n\\n"
    
    try:
        # Transaction analysis
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            analysis += f"TRANSACTION OVERVIEW:\\n"
            analysis += f"Total Transactions: {len(transactions)}\\n\\n"
            
            # Calculate metrics
            total_credits = sum(abs(tx.get("amount", 0)) for tx in transactions 
                              if tx.get("type") == "credit" or tx.get("amount", 0) > 0)
            total_debits = sum(abs(tx.get("amount", 0)) for tx in transactions 
                             if tx.get("type") == "debit" or tx.get("amount", 0) < 0)
            net_flow = total_credits - total_debits
            
            analysis += f"FINANCIAL METRICS:\\n"
            analysis += f"Total Inflows: ${total_credits:,.2f}\\n"
            analysis += f"Total Outflows: ${total_debits:,.2f}\\n"
            analysis += f"Net Cash Flow: ${net_flow:,.2f}\\n\\n"
            
            # Cash flow analysis
            if net_flow > 0:
                analysis += f"CASH FLOW ASSESSMENT:\\n"
                analysis += f"✅ Positive cash flow indicates healthy financial position\\n"
                analysis += f"💡 Consider investment opportunities for excess funds\\n"
            elif net_flow < 0:
                analysis += f"CASH FLOW ASSESSMENT:\\n"
                analysis += f"⚠️ Negative cash flow requires attention\\n"
                analysis += f"💡 Review expenses and identify optimization opportunities\\n"
            else:
                analysis += f"CASH FLOW ASSESSMENT:\\n"
                analysis += f"📊 Balanced cash flow - monitor closely\\n"
            
            analysis += "\\n"
            
            # Transaction patterns
            categories = {}
            for tx in transactions:
                desc = tx.get("description", "").lower()
                amount = abs(tx.get("amount", 0))
                
                if any(word in desc for word in ["salary", "payroll", "income"]):
                    categories["Income"] = categories.get("Income", 0) + amount
                elif any(word in desc for word in ["rent", "mortgage"]):
                    categories["Housing"] = categories.get("Housing", 0) + amount
                elif any(word in desc for word in ["grocery", "food", "restaurant"]):
                    categories["Food & Dining"] = categories.get("Food & Dining", 0) + amount
                elif any(word in desc for word in ["utility", "electric", "gas", "water"]):
                    categories["Utilities"] = categories.get("Utilities", 0) + amount
                elif any(word in desc for word in ["transport", "gas", "uber", "taxi"]):
                    categories["Transportation"] = categories.get("Transportation", 0) + amount
                else:
                    categories["Other"] = categories.get("Other", 0) + amount
            
            if categories:
                analysis += f"SPENDING ANALYSIS:\\n"
                total_spending = sum(v for k, v in categories.items() if k != "Income")
                
                for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    if category == "Income":
                        analysis += f"💰 {category}: ${amount:,.2f}\\n"
                    else:
                        percentage = (amount / total_spending * 100) if total_spending > 0 else 0
                        analysis += f"📊 {category}: ${amount:,.2f} ({percentage:.1f}%)\\n"
                
                analysis += "\\n"
        
        # Account balance analysis
        if "account_balance" in input_data:
            balance = input_data["account_balance"]
            analysis += f"ACCOUNT POSITION:\\n"
            analysis += f"Current Balance: ${balance:,.2f}\\n"
            
            # Balance assessment with financial best practices
            if balance > 10000:
                analysis += f"✅ Strong liquidity position\\n"
                analysis += f"💡 Consider high-yield savings or investment options\\n"
            elif balance > 5000:
                analysis += f"📊 Adequate emergency fund coverage\\n"
                analysis += f"💡 Maintain current savings discipline\\n"
            elif balance > 1000:
                analysis += f"⚠️ Limited emergency fund - consider building reserves\\n"
                analysis += f"💡 Target 3-6 months of expenses for financial security\\n"
            else:
                analysis += f"🚨 Low balance requires immediate attention\\n"
                analysis += f"💡 Focus on expense reduction and income optimization\\n"
            
            analysis += "\\n"
        
        # Risk assessment
        analysis += f"RISK ASSESSMENT:\\n"
        
        risk_factors = []
        if "account_balance" in input_data and input_data["account_balance"] < 1000:
            risk_factors.append("Low account balance increases financial vulnerability")
        
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            large_debits = [tx for tx in transactions if tx.get("amount", 0) < -500]
            if len(large_debits) > len(transactions) * 0.3:
                risk_factors.append("High frequency of large expenditures")
        
        if risk_factors:
            for risk in risk_factors:
                analysis += f"⚠️ {risk}\\n"
        else:
            analysis += f"✅ No significant risk factors identified\\n"
        
        analysis += "\\n"
        
        # Recommendations
        analysis += f"ACTIONABLE RECOMMENDATIONS:\\n"
        
        if "transactions" in input_data and "account_balance" in input_data:
            balance = input_data["account_balance"]
            transactions = input_data["transactions"]
            
            # Calculate monthly spending
            monthly_spending = sum(abs(tx.get("amount", 0)) for tx in transactions 
                                 if tx.get("amount", 0) < 0)
            
            if balance < monthly_spending * 3:
                analysis += f"🎯 Priority: Build emergency fund to ${monthly_spending * 3:,.2f}\\n"
            
            analysis += f"📊 Track spending patterns using transaction categorization\\n"
            analysis += f"💼 Consider automatic savings transfers to build wealth\\n"
            analysis += f"📈 Review and optimize recurring expenses quarterly\\n"
        
        analysis += "\\n=== END ENHANCED ANALYSIS ===\\n"
        analysis += "\\n✨ This analysis incorporates financial best practices and domain expertise."
        
    except Exception as e:
        analysis += f"\\nError during analysis: {str(e)}\\n"
        analysis += "Please verify your input data format."
    
    return analysis

if __name__ == "__main__":
    print("🚀 Starting RAG-Enhanced Autonomous Financial Analysis Agent...")
    print("🧠 Features: Knowledge Augmentation, Vector Acceleration, Continuous Learning")
    print("🌐 Server: http://localhost:5001")
    print("=" * 80)
    
    # Initialize services
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_services())
    
    app.run(host='0.0.0.0', port=5001, debug=True)