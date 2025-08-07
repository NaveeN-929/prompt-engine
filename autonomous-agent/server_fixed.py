"""
Fixed RAG-Enhanced Autonomous Financial Analysis Agent Server
"""

import json
import time
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import threading
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global services (will be initialized)
rag_service = None
services_initialized = False

# Simple storage
interaction_history = []
agent_statistics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "average_processing_time": 0.0,
    "rag_augmented_requests": 0
}

def initialize_services():
    """Initialize services in a separate thread"""
    global rag_service, services_initialized
    
    try:
        logger.info("Initializing RAG service...")
        
        # Try to initialize RAG service
        from core.rag_service import RAGService
        rag_service = RAGService()
        
        # Run async initialization in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(rag_service.initialize())
        loop.close()
        
        services_initialized = True
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.warning(f"Could not initialize full RAG service: {e}")
        logger.info("Running in basic mode")
        services_initialized = False

# Initialize services in background
threading.Thread(target=initialize_services, daemon=True).start()

@app.route('/')
def index():
    """Serve the main interface"""
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
        .section {
            margin: 20px 0;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
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
        
        <div class="status-grid" id="statusGrid">
            <div class="status-card status-active">
                <strong>🌐 Server Status</strong><br>
                <span id="serverStatus">✅ Running</span>
            </div>
            <div class="status-card" id="ragStatusCard">
                <strong>🔍 RAG Service</strong><br>
                <span id="ragStatus">Loading...</span>
            </div>
            <div class="status-card" id="vectorStatusCard">
                <strong>📊 Vector Database</strong><br>
                <span id="vectorStatus">Loading...</span>
            </div>
            <div class="status-card" id="promptEngineCard">
                <strong>🔗 Prompt Engine</strong><br>
                <span id="promptEngineStatus">Loading...</span>
            </div>
        </div>
        
        <div class="section">
            <h3>🔍 Enhanced Financial Analysis</h3>
            <p>Provide financial data for RAG-enhanced analysis with knowledge augmentation:</p>
            <textarea id="analysisData" placeholder='{"transactions": [{"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"}], "account_balance": 2250.00}'></textarea>
            <br>
            <button class="button" onclick="processAnalysis()">🚀 RAG-Enhanced Analysis</button>
            <button class="button secondary" onclick="loadExampleData()">📝 Load Example</button>
            <button class="button secondary" onclick="clearResults()">🗑️ Clear</button>
        </div>
        
        <div class="section">
            <h3>📊 Service Status</h3>
            <button class="button" onclick="refreshAllStatus()">🔄 Refresh All Status</button>
            <button class="button secondary" onclick="showRAGDetails()">🧠 RAG Details</button>
            <button class="button secondary" onclick="showVectorDetails()">⚡ Vector Details</button>
        </div>
        
        <!-- Results Display -->
        <div id="resultsContainer" class="result-container">
            <div class="result-header">
                <span>Enhanced Analysis Results</span>
                <span class="rag-indicator" id="ragIndicator">🧠 RAG: Enabled</span>
                <span style="float: right; font-size: 14px;" id="processingTime"></span>
            </div>
            <div id="resultsContent" class="result-content"></div>
        </div>
        
        <!-- Details Modal -->
        <div id="detailsContainer" class="result-container">
            <div class="result-header">
                <span id="detailsTitle">Service Details</span>
            </div>
            <div id="detailsContent" class="result-content"></div>
        </div>
    </div>
    
    <script>
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
            const resultsEl = document.getElementById('resultsContainer');
            const contentEl = document.getElementById('resultsContent');
            const timeEl = document.getElementById('processingTime');
            const ragEl = document.getElementById('ragIndicator');
            
            try {
                resultsEl.style.display = 'block';
                contentEl.textContent = '🔄 Processing enhanced analysis...';
                
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
                
                contentEl.textContent = result.analysis || result.response || 'No analysis available';
                timeEl.textContent = `${result.processing_time?.toFixed(3)}s`;
                
                // Update RAG indicator
                if (result.rag_metadata?.rag_enabled) {
                    ragEl.textContent = `🧠 RAG: ${result.rag_metadata.context_items_used || 0} items`;
                    ragEl.style.background = 'rgba(40, 167, 69, 0.3)';
                } else {
                    ragEl.textContent = '🧠 RAG: Basic Mode';
                    ragEl.style.background = 'rgba(255, 193, 7, 0.3)';
                }
                
            } catch (error) {
                contentEl.textContent = `Error: ${error.message}`;
                ragEl.textContent = '🧠 RAG: Error';
                ragEl.style.background = 'rgba(220, 53, 69, 0.3)';
            }
        }
        
        // Status functions
        async function refreshAllStatus() {
            await Promise.all([
                checkRAGStatus(),
                checkVectorStatus(),
                checkPromptEngineStatus()
            ]);
        }
        
        async function checkRAGStatus() {
            try {
                const response = await fetch('/rag/status');
                const status = await response.json();
                
                const statusEl = document.getElementById('ragStatus');
                const cardEl = document.getElementById('ragStatusCard');
                
                if (status.status === 'active') {
                    statusEl.innerHTML = '✅ Active';
                    cardEl.className = 'status-card status-active';
                } else {
                    statusEl.innerHTML = '⚠️ Basic Mode';
                    cardEl.className = 'status-card status-warning';
                }
                
            } catch (error) {
                document.getElementById('ragStatus').innerHTML = '❌ Error';
                document.getElementById('ragStatusCard').className = 'status-card status-error';
            }
        }
        
        async function checkVectorStatus() {
            try {
                const response = await fetch('/vector/status');
                const status = await response.json();
                
                const statusEl = document.getElementById('vectorStatus');
                const cardEl = document.getElementById('vectorStatusCard');
                
                if (status.status === 'connected') {
                    statusEl.innerHTML = '✅ Connected';
                    cardEl.className = 'status-card status-active';
                } else {
                    statusEl.innerHTML = '⚠️ Memory Mode';
                    cardEl.className = 'status-card status-warning';
                }
                
            } catch (error) {
                document.getElementById('vectorStatus').innerHTML = '❌ Error';
                document.getElementById('vectorStatusCard').className = 'status-card status-error';
            }
        }
        
        async function checkPromptEngineStatus() {
            try {
                const response = await fetch('/prompt_engine/status');
                const status = await response.json();
                
                const statusEl = document.getElementById('promptEngineStatus');
                const cardEl = document.getElementById('promptEngineCard');
                
                if (status.available) {
                    statusEl.innerHTML = '✅ Connected';
                    cardEl.className = 'status-card status-active';
                } else {
                    statusEl.innerHTML = '⚠️ Unavailable';
                    cardEl.className = 'status-card status-warning';
                }
                
            } catch (error) {
                document.getElementById('promptEngineStatus').innerHTML = '❌ Error';
                document.getElementById('promptEngineCard').className = 'status-card status-error';
            }
        }
        
        async function showRAGDetails() {
            try {
                const response = await fetch('/rag/status');
                const status = await response.json();
                
                let details = `
<h4>RAG Service Details:</h4>
<p><strong>Status:</strong> ${status.status || 'Unknown'}</p>
<p><strong>Total Retrievals:</strong> ${status.total_retrievals || 0}</p>
<p><strong>Cache Hit Rate:</strong> ${((status.cache_hit_rate || 0) * 100).toFixed(1)}%</p>
<p><strong>Successful Augmentations:</strong> ${status.successful_augmentations || 0}</p>
<p><strong>Vector Searches:</strong> ${status.vector_searches || 0}</p>
<p><strong>Collections:</strong> ${(status.collections || []).join(', ') || 'None'}</p>
<p><strong>Embedding Dimension:</strong> ${status.embedding_dimension || 'Unknown'}</p>
                `;
                
                document.getElementById('detailsTitle').textContent = 'RAG Service Details';
                document.getElementById('detailsContent').innerHTML = details;
                document.getElementById('detailsContainer').style.display = 'block';
                
            } catch (error) {
                document.getElementById('detailsContent').textContent = `Error loading RAG details: ${error.message}`;
                document.getElementById('detailsContainer').style.display = 'block';
            }
        }
        
        async function showVectorDetails() {
            try {
                const response = await fetch('/vector/status');
                const status = await response.json();
                
                let details = `
<h4>Vector Database Details:</h4>
<p><strong>Status:</strong> ${status.status || 'Unknown'}</p>
<p><strong>Host:</strong> ${status.host || 'Unknown'}:${status.port || 'Unknown'}</p>
<p><strong>Total Collections:</strong> ${status.total_collections || 0}</p>
<p><strong>Embedding Model:</strong> ${status.embedding_model || 'Unknown'}</p>
<p><strong>Embedding Dimension:</strong> ${status.embedding_dimension || 'Unknown'}</p>
                `;
                
                if (status.collections_detail && status.collections_detail.length > 0) {
                    details += '<h5>Collections:</h5><ul>';
                    status.collections_detail.forEach(col => {
                        details += `<li><strong>${col.name}:</strong> ${col.points_count || 0} points</li>`;
                    });
                    details += '</ul>';
                }
                
                document.getElementById('detailsTitle').textContent = 'Vector Database Details';
                document.getElementById('detailsContent').innerHTML = details;
                document.getElementById('detailsContainer').style.display = 'block';
                
            } catch (error) {
                document.getElementById('detailsContent').textContent = `Error loading vector details: ${error.message}`;
                document.getElementById('detailsContainer').style.display = 'block';
            }
        }
        
        function clearResults() {
            document.getElementById('resultsContainer').style.display = 'none';
            document.getElementById('detailsContainer').style.display = 'none';
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadExampleData();
            
            // Initial status check
            setTimeout(refreshAllStatus, 1000);
            
            // Periodic status refresh
            setInterval(refreshAllStatus, 30000); // Every 30 seconds
        });
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Enhanced analysis endpoint"""
    global agent_statistics
    
    start_time = time.time()
    agent_statistics["total_requests"] += 1
    
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({"error": "Missing input_data field"}), 400
        
        input_data = data['input_data']
        enable_rag = data.get('enable_rag', True)
        
        # Perform enhanced analysis
        analysis = perform_enhanced_analysis(input_data)
        
        # RAG augmentation if available
        rag_metadata = {"rag_enabled": False}
        
        if enable_rag and services_initialized and rag_service:
            try:
                # Run RAG augmentation in new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                augmented_analysis, rag_metadata = loop.run_until_complete(
                    rag_service.augment_prompt(analysis, input_data)
                )
                analysis = augmented_analysis
                agent_statistics["rag_augmented_requests"] += 1
                
                # Store interaction pattern
                loop.run_until_complete(
                    rag_service.store_interaction_pattern(input_data, analysis, analysis, 0.8)
                )
                
                loop.close()
                
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
        if len(interaction_history) > 50:
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
    return jsonify({
        "status": "operational",
        "mode": "rag_enhanced",
        "version": "2.0.0-rag-fixed",
        "timestamp": datetime.now().isoformat(),
        "statistics": agent_statistics,
        "services": {
            "rag_service": "active" if services_initialized and rag_service else "basic_mode",
            "vector_database": "connected" if services_initialized and rag_service else "memory_mode"
        }
    })

@app.route('/rag/status', methods=['GET'])
def get_rag_status():
    """Get RAG service status"""
    try:
        if not services_initialized or not rag_service:
            return jsonify({
                "status": "basic_mode",
                "total_retrievals": 0,
                "cache_hit_rate": 0.0,
                "successful_augmentations": 0,
                "vector_searches": 0,
                "collections": [],
                "embedding_dimension": 384
            })
        
        # Get stats in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        stats = rag_service.get_rag_statistics()
        
        loop.close()
        
        return jsonify({
            "status": "active",
            **stats
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "total_retrievals": 0,
            "cache_hit_rate": 0.0,
            "successful_augmentations": 0,
            "vector_searches": 0,
            "collections": [],
            "embedding_dimension": 384
        })

@app.route('/vector/status', methods=['GET'])
def get_vector_status():
    """Get vector database status"""
    try:
        if not services_initialized or not rag_service:
            return jsonify({
                "status": "memory_mode",
                "host": "localhost",
                "port": 6333,
                "total_collections": 0,
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimension": 384,
                "collections_detail": []
            })
        
        # Get vector status in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        vector_status = loop.run_until_complete(rag_service.get_vector_status())
        
        loop.close()
        
        return jsonify(vector_status)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "host": "localhost",
            "port": 6333
        })

@app.route('/prompt_engine/status', methods=['GET'])
def get_prompt_engine_status():
    """Check prompt engine connectivity"""
    try:
        # Simple connectivity check
        import requests
        response = requests.get("http://localhost:5000/health", timeout=5)
        
        return jsonify({
            "available": response.status_code == 200,
            "status_code": response.status_code
        })
        
    except Exception as e:
        return jsonify({
            "available": False,
            "error": str(e)
        })

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
        "mode": "rag_enhanced_fixed",
        "version": "2.0.0-rag-fixed",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "rag_service": services_initialized and rag_service is not None,
            "vector_database": services_initialized and rag_service is not None,
            "initialization_complete": services_initialized
        }
    })

def perform_enhanced_analysis(input_data):
    """Perform enhanced financial analysis with domain expertise"""
    
    analysis = "=== ENHANCED FINANCIAL ANALYSIS ===\\n\\n"
    
    try:
        # Transaction analysis
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            analysis += f"TRANSACTION SUMMARY:\\n"
            analysis += f"• Total Transactions Analyzed: {len(transactions)}\\n\\n"
            
            # Calculate financial metrics
            total_credits = sum(abs(tx.get("amount", 0)) for tx in transactions 
                              if tx.get("type") == "credit" or tx.get("amount", 0) > 0)
            total_debits = sum(abs(tx.get("amount", 0)) for tx in transactions 
                             if tx.get("type") == "debit" or tx.get("amount", 0) < 0)
            net_cash_flow = total_credits - total_debits
            
            analysis += f"CASH FLOW ANALYSIS:\\n"
            analysis += f"💰 Total Inflows: ${total_credits:,.2f}\\n"
            analysis += f"💸 Total Outflows: ${total_debits:,.2f}\\n"
            analysis += f"📊 Net Cash Flow: ${net_cash_flow:,.2f}\\n\\n"
            
            # Financial health assessment
            if net_cash_flow > 0:
                analysis += f"FINANCIAL HEALTH ASSESSMENT:\\n"
                analysis += f"✅ Positive cash flow indicates strong financial position\\n"
                analysis += f"💡 Recommendation: Consider investment opportunities for surplus funds\\n"
                analysis += f"🎯 Focus: Wealth building and long-term financial planning\\n"
            elif net_cash_flow < 0:
                analysis += f"FINANCIAL HEALTH ASSESSMENT:\\n"
                analysis += f"⚠️ Negative cash flow requires immediate attention\\n"
                analysis += f"💡 Recommendation: Review and optimize expenses, increase income sources\\n"
                analysis += f"🎯 Focus: Expense management and revenue enhancement\\n"
            else:
                analysis += f"FINANCIAL HEALTH ASSESSMENT:\\n"
                analysis += f"📊 Balanced cash flow - maintain current discipline\\n"
                analysis += f"💡 Recommendation: Monitor closely and build emergency reserves\\n"
            
            analysis += "\\n"
            
            # Transaction categorization and insights
            categories = self._categorize_transactions(transactions)
            
            if categories:
                analysis += f"SPENDING BREAKDOWN:\\n"
                total_spending = sum(v for k, v in categories.items() if k != "Income")
                
                for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    if category == "Income":
                        analysis += f"💰 {category}: ${amount:,.2f}\\n"
                    else:
                        percentage = (amount / total_spending * 100) if total_spending > 0 else 0
                        analysis += f"📊 {category}: ${amount:,.2f} ({percentage:.1f}% of spending)\\n"
                
                analysis += "\\n"
                
                # Spending insights
                analysis += f"SPENDING INSIGHTS:\\n"
                largest_category = max((k, v) for k, v in categories.items() if k != "Income")
                analysis += f"🔍 Largest expense category: {largest_category[0]} (${largest_category[1]:,.2f})\\n"
                
                # Check for concerning patterns
                if categories.get("Housing", 0) / total_spending > 0.4 if total_spending > 0 else False:
                    analysis += f"⚠️ Housing costs exceed 40% of spending - consider optimization\\n"
                
                if len([tx for tx in transactions if abs(tx.get("amount", 0)) > 500]) > 3:
                    analysis += f"📈 Multiple large transactions detected - review for accuracy\\n"
                
                analysis += "\\n"
        
        # Account balance analysis
        if "account_balance" in input_data:
            balance = input_data["account_balance"]
            analysis += f"LIQUIDITY ANALYSIS:\\n"
            analysis += f"💼 Current Account Balance: ${balance:,.2f}\\n"
            
            # Liquidity assessment using financial best practices
            if balance > 15000:
                analysis += f"✅ Excellent liquidity position\\n"
                analysis += f"💡 Strategy: Consider diversified investment portfolio\\n"
                analysis += f"🎯 Goal: Wealth accumulation and compound growth\\n"
            elif balance > 5000:
                analysis += f"📊 Good emergency fund coverage\\n"
                analysis += f"💡 Strategy: Maintain reserves while exploring growth opportunities\\n"
                analysis += f"🎯 Goal: Balance safety and growth potential\\n"
            elif balance > 1000:
                analysis += f"⚠️ Moderate liquidity - build emergency reserves\\n"
                analysis += f"💡 Strategy: Focus on increasing savings rate to 3-6 months expenses\\n"
                analysis += f"🎯 Goal: Financial security through adequate reserves\\n"
            else:
                analysis += f"🚨 Critical liquidity shortage\\n"
                analysis += f"💡 Strategy: Immediate expense reduction and income optimization\\n"
                analysis += f"🎯 Goal: Achieve minimum $1,000 emergency buffer\\n"
            
            analysis += "\\n"
        
        # Risk assessment with financial expertise
        analysis += f"RISK ASSESSMENT:\\n"
        
        risk_score = 0
        risk_factors = []
        
        if "account_balance" in input_data and input_data["account_balance"] < 1000:
            risk_score += 3
            risk_factors.append("Insufficient emergency reserves")
        
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            
            # Check for irregular large expenses
            large_expenses = [tx for tx in transactions if tx.get("amount", 0) < -1000]
            if len(large_expenses) > 2:
                risk_score += 2
                risk_factors.append("High frequency of large expenses")
            
            # Check debt payment patterns
            debt_payments = [tx for tx in transactions if any(word in tx.get("description", "").lower() 
                           for word in ["loan", "credit", "payment", "debt"])]
            if len(debt_payments) > len(transactions) * 0.3:
                risk_score += 1
                risk_factors.append("High debt service ratio")
        
        # Risk level determination
        if risk_score >= 4:
            risk_level = "HIGH"
            risk_color = "🔴"
        elif risk_score >= 2:
            risk_level = "MEDIUM"
            risk_color = "🟡"
        else:
            risk_level = "LOW"
            risk_color = "🟢"
        
        analysis += f"{risk_color} Overall Risk Level: {risk_level}\\n"
        
        if risk_factors:
            analysis += f"Risk Factors Identified:\\n"
            for risk in risk_factors:
                analysis += f"  • {risk}\\n"
        else:
            analysis += f"✅ No significant risk factors identified\\n"
        
        analysis += "\\n"
        
        # Strategic recommendations
        analysis += f"STRATEGIC RECOMMENDATIONS:\\n"
        
        if "transactions" in input_data and "account_balance" in input_data:
            balance = input_data["account_balance"]
            transactions = input_data["transactions"]
            
            monthly_expenses = sum(abs(tx.get("amount", 0)) for tx in transactions if tx.get("amount", 0) < 0)
            
            # Emergency fund recommendation
            target_emergency = monthly_expenses * 6
            if balance < target_emergency:
                analysis += f"🎯 Priority 1: Build emergency fund to ${target_emergency:,.2f} (6 months expenses)\\n"
            
            # Savings rate optimization
            monthly_income = sum(tx.get("amount", 0) for tx in transactions if tx.get("amount", 0) > 0)
            if monthly_income > 0:
                savings_rate = ((monthly_income - monthly_expenses) / monthly_income) * 100
                analysis += f"📊 Current Savings Rate: {savings_rate:.1f}%\\n"
                
                if savings_rate < 10:
                    analysis += f"🎯 Priority 2: Increase savings rate to 15-20% minimum\\n"
                elif savings_rate < 20:
                    analysis += f"💡 Good progress: Target 20%+ savings rate for optimal growth\\n"
                else:
                    analysis += f"✅ Excellent savings discipline: Consider investment diversification\\n"
        
        analysis += f"💼 Implement automated savings transfers for consistent wealth building\\n"
        analysis += f"📈 Review and optimize recurring subscriptions and services\\n"
        analysis += f"🎓 Consider financial education to enhance money management skills\\n"
        
        analysis += "\\n=== ANALYSIS COMPLETE ===\\n"
        analysis += "\\n💡 This analysis incorporates established financial principles and best practices."
        
    except Exception as e:
        analysis += f"\\nError during analysis: {str(e)}\\n"
        analysis += "Please verify your input data format and try again."
    
    return analysis

def _categorize_transactions(transactions):
    """Enhanced transaction categorization"""
    categories = {}
    
    for tx in transactions:
        desc = tx.get("description", "").lower()
        amount = abs(tx.get("amount", 0))
        
        # Income categorization
        if any(word in desc for word in ["salary", "payroll", "income", "freelance", "wage"]):
            categories["Income"] = categories.get("Income", 0) + amount
        
        # Housing and utilities
        elif any(word in desc for word in ["rent", "mortgage", "property", "hoa"]):
            categories["Housing"] = categories.get("Housing", 0) + amount
        elif any(word in desc for word in ["utility", "electric", "gas", "water", "internet", "cable"]):
            categories["Utilities"] = categories.get("Utilities", 0) + amount
        
        # Food and dining
        elif any(word in desc for word in ["grocery", "food", "restaurant", "dining", "cafe", "takeout"]):
            categories["Food & Dining"] = categories.get("Food & Dining", 0) + amount
        
        # Transportation
        elif any(word in desc for word in ["gas", "fuel", "uber", "taxi", "transport", "parking", "car"]):
            categories["Transportation"] = categories.get("Transportation", 0) + amount
        
        # Healthcare
        elif any(word in desc for word in ["medical", "doctor", "pharmacy", "health", "dental"]):
            categories["Healthcare"] = categories.get("Healthcare", 0) + amount
        
        # Entertainment and recreation
        elif any(word in desc for word in ["entertainment", "movie", "music", "streaming", "gym", "fitness"]):
            categories["Entertainment"] = categories.get("Entertainment", 0) + amount
        
        # Shopping and retail
        elif any(word in desc for word in ["amazon", "target", "walmart", "shopping", "retail", "store"]):
            categories["Shopping"] = categories.get("Shopping", 0) + amount
        
        # Financial services
        elif any(word in desc for word in ["bank", "fee", "interest", "loan", "credit", "payment"]):
            categories["Financial Services"] = categories.get("Financial Services", 0) + amount
        
        # Default category
        else:
            categories["Other"] = categories.get("Other", 0) + amount
    
    return categories

if __name__ == "__main__":
    print("🚀 Starting RAG-Enhanced Autonomous Financial Analysis Agent...")
    print("🧠 Features: Knowledge Augmentation, Vector Acceleration, Continuous Learning")
    print("🌐 Server: http://localhost:5001")
    print("⚡ Initializing services in background...")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
Fixed RAG-Enhanced Autonomous Financial Analysis Agent Server
"""

import json
import time
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import threading
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global services (will be initialized)
rag_service = None
services_initialized = False

# Simple storage
interaction_history = []
agent_statistics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "average_processing_time": 0.0,
    "rag_augmented_requests": 0
}

def initialize_services():
    """Initialize services in a separate thread"""
    global rag_service, services_initialized
    
    try:
        logger.info("Initializing RAG service...")
        
        # Try to initialize RAG service
        from core.rag_service import RAGService
        rag_service = RAGService()
        
        # Run async initialization in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(rag_service.initialize())
        loop.close()
        
        services_initialized = True
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.warning(f"Could not initialize full RAG service: {e}")
        logger.info("Running in basic mode")
        services_initialized = False

# Initialize services in background
threading.Thread(target=initialize_services, daemon=True).start()

@app.route('/')
def index():
    """Serve the main interface"""
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
        .section {
            margin: 20px 0;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
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
        
        <div class="status-grid" id="statusGrid">
            <div class="status-card status-active">
                <strong>🌐 Server Status</strong><br>
                <span id="serverStatus">✅ Running</span>
            </div>
            <div class="status-card" id="ragStatusCard">
                <strong>🔍 RAG Service</strong><br>
                <span id="ragStatus">Loading...</span>
            </div>
            <div class="status-card" id="vectorStatusCard">
                <strong>📊 Vector Database</strong><br>
                <span id="vectorStatus">Loading...</span>
            </div>
            <div class="status-card" id="promptEngineCard">
                <strong>🔗 Prompt Engine</strong><br>
                <span id="promptEngineStatus">Loading...</span>
            </div>
        </div>
        
        <div class="section">
            <h3>🔍 Enhanced Financial Analysis</h3>
            <p>Provide financial data for RAG-enhanced analysis with knowledge augmentation:</p>
            <textarea id="analysisData" placeholder='{"transactions": [{"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"}], "account_balance": 2250.00}'></textarea>
            <br>
            <button class="button" onclick="processAnalysis()">🚀 RAG-Enhanced Analysis</button>
            <button class="button secondary" onclick="loadExampleData()">📝 Load Example</button>
            <button class="button secondary" onclick="clearResults()">🗑️ Clear</button>
        </div>
        
        <div class="section">
            <h3>📊 Service Status</h3>
            <button class="button" onclick="refreshAllStatus()">🔄 Refresh All Status</button>
            <button class="button secondary" onclick="showRAGDetails()">🧠 RAG Details</button>
            <button class="button secondary" onclick="showVectorDetails()">⚡ Vector Details</button>
        </div>
        
        <!-- Results Display -->
        <div id="resultsContainer" class="result-container">
            <div class="result-header">
                <span>Enhanced Analysis Results</span>
                <span class="rag-indicator" id="ragIndicator">🧠 RAG: Enabled</span>
                <span style="float: right; font-size: 14px;" id="processingTime"></span>
            </div>
            <div id="resultsContent" class="result-content"></div>
        </div>
        
        <!-- Details Modal -->
        <div id="detailsContainer" class="result-container">
            <div class="result-header">
                <span id="detailsTitle">Service Details</span>
            </div>
            <div id="detailsContent" class="result-content"></div>
        </div>
    </div>
    
    <script>
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
            const resultsEl = document.getElementById('resultsContainer');
            const contentEl = document.getElementById('resultsContent');
            const timeEl = document.getElementById('processingTime');
            const ragEl = document.getElementById('ragIndicator');
            
            try {
                resultsEl.style.display = 'block';
                contentEl.textContent = '🔄 Processing enhanced analysis...';
                
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
                
                contentEl.textContent = result.analysis || result.response || 'No analysis available';
                timeEl.textContent = `${result.processing_time?.toFixed(3)}s`;
                
                // Update RAG indicator
                if (result.rag_metadata?.rag_enabled) {
                    ragEl.textContent = `🧠 RAG: ${result.rag_metadata.context_items_used || 0} items`;
                    ragEl.style.background = 'rgba(40, 167, 69, 0.3)';
                } else {
                    ragEl.textContent = '🧠 RAG: Basic Mode';
                    ragEl.style.background = 'rgba(255, 193, 7, 0.3)';
                }
                
            } catch (error) {
                contentEl.textContent = `Error: ${error.message}`;
                ragEl.textContent = '🧠 RAG: Error';
                ragEl.style.background = 'rgba(220, 53, 69, 0.3)';
            }
        }
        
        // Status functions
        async function refreshAllStatus() {
            await Promise.all([
                checkRAGStatus(),
                checkVectorStatus(),
                checkPromptEngineStatus()
            ]);
        }
        
        async function checkRAGStatus() {
            try {
                const response = await fetch('/rag/status');
                const status = await response.json();
                
                const statusEl = document.getElementById('ragStatus');
                const cardEl = document.getElementById('ragStatusCard');
                
                if (status.status === 'active') {
                    statusEl.innerHTML = '✅ Active';
                    cardEl.className = 'status-card status-active';
                } else {
                    statusEl.innerHTML = '⚠️ Basic Mode';
                    cardEl.className = 'status-card status-warning';
                }
                
            } catch (error) {
                document.getElementById('ragStatus').innerHTML = '❌ Error';
                document.getElementById('ragStatusCard').className = 'status-card status-error';
            }
        }
        
        async function checkVectorStatus() {
            try {
                const response = await fetch('/vector/status');
                const status = await response.json();
                
                const statusEl = document.getElementById('vectorStatus');
                const cardEl = document.getElementById('vectorStatusCard');
                
                if (status.status === 'connected') {
                    statusEl.innerHTML = '✅ Connected';
                    cardEl.className = 'status-card status-active';
                } else {
                    statusEl.innerHTML = '⚠️ Memory Mode';
                    cardEl.className = 'status-card status-warning';
                }
                
            } catch (error) {
                document.getElementById('vectorStatus').innerHTML = '❌ Error';
                document.getElementById('vectorStatusCard').className = 'status-card status-error';
            }
        }
        
        async function checkPromptEngineStatus() {
            try {
                const response = await fetch('/prompt_engine/status');
                const status = await response.json();
                
                const statusEl = document.getElementById('promptEngineStatus');
                const cardEl = document.getElementById('promptEngineCard');
                
                if (status.available) {
                    statusEl.innerHTML = '✅ Connected';
                    cardEl.className = 'status-card status-active';
                } else {
                    statusEl.innerHTML = '⚠️ Unavailable';
                    cardEl.className = 'status-card status-warning';
                }
                
            } catch (error) {
                document.getElementById('promptEngineStatus').innerHTML = '❌ Error';
                document.getElementById('promptEngineCard').className = 'status-card status-error';
            }
        }
        
        async function showRAGDetails() {
            try {
                const response = await fetch('/rag/status');
                const status = await response.json();
                
                let details = `
<h4>RAG Service Details:</h4>
<p><strong>Status:</strong> ${status.status || 'Unknown'}</p>
<p><strong>Total Retrievals:</strong> ${status.total_retrievals || 0}</p>
<p><strong>Cache Hit Rate:</strong> ${((status.cache_hit_rate || 0) * 100).toFixed(1)}%</p>
<p><strong>Successful Augmentations:</strong> ${status.successful_augmentations || 0}</p>
<p><strong>Vector Searches:</strong> ${status.vector_searches || 0}</p>
<p><strong>Collections:</strong> ${(status.collections || []).join(', ') || 'None'}</p>
<p><strong>Embedding Dimension:</strong> ${status.embedding_dimension || 'Unknown'}</p>
                `;
                
                document.getElementById('detailsTitle').textContent = 'RAG Service Details';
                document.getElementById('detailsContent').innerHTML = details;
                document.getElementById('detailsContainer').style.display = 'block';
                
            } catch (error) {
                document.getElementById('detailsContent').textContent = `Error loading RAG details: ${error.message}`;
                document.getElementById('detailsContainer').style.display = 'block';
            }
        }
        
        async function showVectorDetails() {
            try {
                const response = await fetch('/vector/status');
                const status = await response.json();
                
                let details = `
<h4>Vector Database Details:</h4>
<p><strong>Status:</strong> ${status.status || 'Unknown'}</p>
<p><strong>Host:</strong> ${status.host || 'Unknown'}:${status.port || 'Unknown'}</p>
<p><strong>Total Collections:</strong> ${status.total_collections || 0}</p>
<p><strong>Embedding Model:</strong> ${status.embedding_model || 'Unknown'}</p>
<p><strong>Embedding Dimension:</strong> ${status.embedding_dimension || 'Unknown'}</p>
                `;
                
                if (status.collections_detail && status.collections_detail.length > 0) {
                    details += '<h5>Collections:</h5><ul>';
                    status.collections_detail.forEach(col => {
                        details += `<li><strong>${col.name}:</strong> ${col.points_count || 0} points</li>`;
                    });
                    details += '</ul>';
                }
                
                document.getElementById('detailsTitle').textContent = 'Vector Database Details';
                document.getElementById('detailsContent').innerHTML = details;
                document.getElementById('detailsContainer').style.display = 'block';
                
            } catch (error) {
                document.getElementById('detailsContent').textContent = `Error loading vector details: ${error.message}`;
                document.getElementById('detailsContainer').style.display = 'block';
            }
        }
        
        function clearResults() {
            document.getElementById('resultsContainer').style.display = 'none';
            document.getElementById('detailsContainer').style.display = 'none';
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadExampleData();
            
            // Initial status check
            setTimeout(refreshAllStatus, 1000);
            
            // Periodic status refresh
            setInterval(refreshAllStatus, 30000); // Every 30 seconds
        });
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Enhanced analysis endpoint"""
    global agent_statistics
    
    start_time = time.time()
    agent_statistics["total_requests"] += 1
    
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({"error": "Missing input_data field"}), 400
        
        input_data = data['input_data']
        enable_rag = data.get('enable_rag', True)
        
        # Perform enhanced analysis
        analysis = perform_enhanced_analysis(input_data)
        
        # RAG augmentation if available
        rag_metadata = {"rag_enabled": False}
        
        if enable_rag and services_initialized and rag_service:
            try:
                # Run RAG augmentation in new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                augmented_analysis, rag_metadata = loop.run_until_complete(
                    rag_service.augment_prompt(analysis, input_data)
                )
                analysis = augmented_analysis
                agent_statistics["rag_augmented_requests"] += 1
                
                # Store interaction pattern
                loop.run_until_complete(
                    rag_service.store_interaction_pattern(input_data, analysis, analysis, 0.8)
                )
                
                loop.close()
                
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
        if len(interaction_history) > 50:
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
    return jsonify({
        "status": "operational",
        "mode": "rag_enhanced",
        "version": "2.0.0-rag-fixed",
        "timestamp": datetime.now().isoformat(),
        "statistics": agent_statistics,
        "services": {
            "rag_service": "active" if services_initialized and rag_service else "basic_mode",
            "vector_database": "connected" if services_initialized and rag_service else "memory_mode"
        }
    })

@app.route('/rag/status', methods=['GET'])
def get_rag_status():
    """Get RAG service status"""
    try:
        if not services_initialized or not rag_service:
            return jsonify({
                "status": "basic_mode",
                "total_retrievals": 0,
                "cache_hit_rate": 0.0,
                "successful_augmentations": 0,
                "vector_searches": 0,
                "collections": [],
                "embedding_dimension": 384
            })
        
        # Get stats in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        stats = rag_service.get_rag_statistics()
        
        loop.close()
        
        return jsonify({
            "status": "active",
            **stats
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "total_retrievals": 0,
            "cache_hit_rate": 0.0,
            "successful_augmentations": 0,
            "vector_searches": 0,
            "collections": [],
            "embedding_dimension": 384
        })

@app.route('/vector/status', methods=['GET'])
def get_vector_status():
    """Get vector database status"""
    try:
        if not services_initialized or not rag_service:
            return jsonify({
                "status": "memory_mode",
                "host": "localhost",
                "port": 6333,
                "total_collections": 0,
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimension": 384,
                "collections_detail": []
            })
        
        # Get vector status in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        vector_status = loop.run_until_complete(rag_service.get_vector_status())
        
        loop.close()
        
        return jsonify(vector_status)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "host": "localhost",
            "port": 6333
        })

@app.route('/prompt_engine/status', methods=['GET'])
def get_prompt_engine_status():
    """Check prompt engine connectivity"""
    try:
        # Simple connectivity check
        import requests
        response = requests.get("http://localhost:5000/health", timeout=5)
        
        return jsonify({
            "available": response.status_code == 200,
            "status_code": response.status_code
        })
        
    except Exception as e:
        return jsonify({
            "available": False,
            "error": str(e)
        })

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
        "mode": "rag_enhanced_fixed",
        "version": "2.0.0-rag-fixed",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "rag_service": services_initialized and rag_service is not None,
            "vector_database": services_initialized and rag_service is not None,
            "initialization_complete": services_initialized
        }
    })

def perform_enhanced_analysis(input_data):
    """Perform enhanced financial analysis with domain expertise"""
    
    analysis = "=== ENHANCED FINANCIAL ANALYSIS ===\\n\\n"
    
    try:
        # Transaction analysis
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            analysis += f"TRANSACTION SUMMARY:\\n"
            analysis += f"• Total Transactions Analyzed: {len(transactions)}\\n\\n"
            
            # Calculate financial metrics
            total_credits = sum(abs(tx.get("amount", 0)) for tx in transactions 
                              if tx.get("type") == "credit" or tx.get("amount", 0) > 0)
            total_debits = sum(abs(tx.get("amount", 0)) for tx in transactions 
                             if tx.get("type") == "debit" or tx.get("amount", 0) < 0)
            net_cash_flow = total_credits - total_debits
            
            analysis += f"CASH FLOW ANALYSIS:\\n"
            analysis += f"💰 Total Inflows: ${total_credits:,.2f}\\n"
            analysis += f"💸 Total Outflows: ${total_debits:,.2f}\\n"
            analysis += f"📊 Net Cash Flow: ${net_cash_flow:,.2f}\\n\\n"
            
            # Financial health assessment
            if net_cash_flow > 0:
                analysis += f"FINANCIAL HEALTH ASSESSMENT:\\n"
                analysis += f"✅ Positive cash flow indicates strong financial position\\n"
                analysis += f"💡 Recommendation: Consider investment opportunities for surplus funds\\n"
                analysis += f"🎯 Focus: Wealth building and long-term financial planning\\n"
            elif net_cash_flow < 0:
                analysis += f"FINANCIAL HEALTH ASSESSMENT:\\n"
                analysis += f"⚠️ Negative cash flow requires immediate attention\\n"
                analysis += f"💡 Recommendation: Review and optimize expenses, increase income sources\\n"
                analysis += f"🎯 Focus: Expense management and revenue enhancement\\n"
            else:
                analysis += f"FINANCIAL HEALTH ASSESSMENT:\\n"
                analysis += f"📊 Balanced cash flow - maintain current discipline\\n"
                analysis += f"💡 Recommendation: Monitor closely and build emergency reserves\\n"
            
            analysis += "\\n"
            
            # Transaction categorization and insights
            categories = self._categorize_transactions(transactions)
            
            if categories:
                analysis += f"SPENDING BREAKDOWN:\\n"
                total_spending = sum(v for k, v in categories.items() if k != "Income")
                
                for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    if category == "Income":
                        analysis += f"💰 {category}: ${amount:,.2f}\\n"
                    else:
                        percentage = (amount / total_spending * 100) if total_spending > 0 else 0
                        analysis += f"📊 {category}: ${amount:,.2f} ({percentage:.1f}% of spending)\\n"
                
                analysis += "\\n"
                
                # Spending insights
                analysis += f"SPENDING INSIGHTS:\\n"
                largest_category = max((k, v) for k, v in categories.items() if k != "Income")
                analysis += f"🔍 Largest expense category: {largest_category[0]} (${largest_category[1]:,.2f})\\n"
                
                # Check for concerning patterns
                if categories.get("Housing", 0) / total_spending > 0.4 if total_spending > 0 else False:
                    analysis += f"⚠️ Housing costs exceed 40% of spending - consider optimization\\n"
                
                if len([tx for tx in transactions if abs(tx.get("amount", 0)) > 500]) > 3:
                    analysis += f"📈 Multiple large transactions detected - review for accuracy\\n"
                
                analysis += "\\n"
        
        # Account balance analysis
        if "account_balance" in input_data:
            balance = input_data["account_balance"]
            analysis += f"LIQUIDITY ANALYSIS:\\n"
            analysis += f"💼 Current Account Balance: ${balance:,.2f}\\n"
            
            # Liquidity assessment using financial best practices
            if balance > 15000:
                analysis += f"✅ Excellent liquidity position\\n"
                analysis += f"💡 Strategy: Consider diversified investment portfolio\\n"
                analysis += f"🎯 Goal: Wealth accumulation and compound growth\\n"
            elif balance > 5000:
                analysis += f"📊 Good emergency fund coverage\\n"
                analysis += f"💡 Strategy: Maintain reserves while exploring growth opportunities\\n"
                analysis += f"🎯 Goal: Balance safety and growth potential\\n"
            elif balance > 1000:
                analysis += f"⚠️ Moderate liquidity - build emergency reserves\\n"
                analysis += f"💡 Strategy: Focus on increasing savings rate to 3-6 months expenses\\n"
                analysis += f"🎯 Goal: Financial security through adequate reserves\\n"
            else:
                analysis += f"🚨 Critical liquidity shortage\\n"
                analysis += f"💡 Strategy: Immediate expense reduction and income optimization\\n"
                analysis += f"🎯 Goal: Achieve minimum $1,000 emergency buffer\\n"
            
            analysis += "\\n"
        
        # Risk assessment with financial expertise
        analysis += f"RISK ASSESSMENT:\\n"
        
        risk_score = 0
        risk_factors = []
        
        if "account_balance" in input_data and input_data["account_balance"] < 1000:
            risk_score += 3
            risk_factors.append("Insufficient emergency reserves")
        
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            
            # Check for irregular large expenses
            large_expenses = [tx for tx in transactions if tx.get("amount", 0) < -1000]
            if len(large_expenses) > 2:
                risk_score += 2
                risk_factors.append("High frequency of large expenses")
            
            # Check debt payment patterns
            debt_payments = [tx for tx in transactions if any(word in tx.get("description", "").lower() 
                           for word in ["loan", "credit", "payment", "debt"])]
            if len(debt_payments) > len(transactions) * 0.3:
                risk_score += 1
                risk_factors.append("High debt service ratio")
        
        # Risk level determination
        if risk_score >= 4:
            risk_level = "HIGH"
            risk_color = "🔴"
        elif risk_score >= 2:
            risk_level = "MEDIUM"
            risk_color = "🟡"
        else:
            risk_level = "LOW"
            risk_color = "🟢"
        
        analysis += f"{risk_color} Overall Risk Level: {risk_level}\\n"
        
        if risk_factors:
            analysis += f"Risk Factors Identified:\\n"
            for risk in risk_factors:
                analysis += f"  • {risk}\\n"
        else:
            analysis += f"✅ No significant risk factors identified\\n"
        
        analysis += "\\n"
        
        # Strategic recommendations
        analysis += f"STRATEGIC RECOMMENDATIONS:\\n"
        
        if "transactions" in input_data and "account_balance" in input_data:
            balance = input_data["account_balance"]
            transactions = input_data["transactions"]
            
            monthly_expenses = sum(abs(tx.get("amount", 0)) for tx in transactions if tx.get("amount", 0) < 0)
            
            # Emergency fund recommendation
            target_emergency = monthly_expenses * 6
            if balance < target_emergency:
                analysis += f"🎯 Priority 1: Build emergency fund to ${target_emergency:,.2f} (6 months expenses)\\n"
            
            # Savings rate optimization
            monthly_income = sum(tx.get("amount", 0) for tx in transactions if tx.get("amount", 0) > 0)
            if monthly_income > 0:
                savings_rate = ((monthly_income - monthly_expenses) / monthly_income) * 100
                analysis += f"📊 Current Savings Rate: {savings_rate:.1f}%\\n"
                
                if savings_rate < 10:
                    analysis += f"🎯 Priority 2: Increase savings rate to 15-20% minimum\\n"
                elif savings_rate < 20:
                    analysis += f"💡 Good progress: Target 20%+ savings rate for optimal growth\\n"
                else:
                    analysis += f"✅ Excellent savings discipline: Consider investment diversification\\n"
        
        analysis += f"💼 Implement automated savings transfers for consistent wealth building\\n"
        analysis += f"📈 Review and optimize recurring subscriptions and services\\n"
        analysis += f"🎓 Consider financial education to enhance money management skills\\n"
        
        analysis += "\\n=== ANALYSIS COMPLETE ===\\n"
        analysis += "\\n💡 This analysis incorporates established financial principles and best practices."
        
    except Exception as e:
        analysis += f"\\nError during analysis: {str(e)}\\n"
        analysis += "Please verify your input data format and try again."
    
    return analysis

def _categorize_transactions(transactions):
    """Enhanced transaction categorization"""
    categories = {}
    
    for tx in transactions:
        desc = tx.get("description", "").lower()
        amount = abs(tx.get("amount", 0))
        
        # Income categorization
        if any(word in desc for word in ["salary", "payroll", "income", "freelance", "wage"]):
            categories["Income"] = categories.get("Income", 0) + amount
        
        # Housing and utilities
        elif any(word in desc for word in ["rent", "mortgage", "property", "hoa"]):
            categories["Housing"] = categories.get("Housing", 0) + amount
        elif any(word in desc for word in ["utility", "electric", "gas", "water", "internet", "cable"]):
            categories["Utilities"] = categories.get("Utilities", 0) + amount
        
        # Food and dining
        elif any(word in desc for word in ["grocery", "food", "restaurant", "dining", "cafe", "takeout"]):
            categories["Food & Dining"] = categories.get("Food & Dining", 0) + amount
        
        # Transportation
        elif any(word in desc for word in ["gas", "fuel", "uber", "taxi", "transport", "parking", "car"]):
            categories["Transportation"] = categories.get("Transportation", 0) + amount
        
        # Healthcare
        elif any(word in desc for word in ["medical", "doctor", "pharmacy", "health", "dental"]):
            categories["Healthcare"] = categories.get("Healthcare", 0) + amount
        
        # Entertainment and recreation
        elif any(word in desc for word in ["entertainment", "movie", "music", "streaming", "gym", "fitness"]):
            categories["Entertainment"] = categories.get("Entertainment", 0) + amount
        
        # Shopping and retail
        elif any(word in desc for word in ["amazon", "target", "walmart", "shopping", "retail", "store"]):
            categories["Shopping"] = categories.get("Shopping", 0) + amount
        
        # Financial services
        elif any(word in desc for word in ["bank", "fee", "interest", "loan", "credit", "payment"]):
            categories["Financial Services"] = categories.get("Financial Services", 0) + amount
        
        # Default category
        else:
            categories["Other"] = categories.get("Other", 0) + amount
    
    return categories

if __name__ == "__main__":
    print("🚀 Starting RAG-Enhanced Autonomous Financial Analysis Agent...")
    print("🧠 Features: Knowledge Augmentation, Vector Acceleration, Continuous Learning")
    print("🌐 Server: http://localhost:5001")
    print("⚡ Initializing services in background...")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=5001, debug=True)