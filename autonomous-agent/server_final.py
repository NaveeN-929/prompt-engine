"""
Final RAG-Enhanced Autonomous Financial Analysis Agent Server
Complete working version with all endpoints
"""

import json
import time
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import threading

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
services_status = {
    "rag_initialized": False,
    "vector_connected": False,
    "initialization_error": None
}

# Storage
interaction_history = []
agent_statistics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "average_processing_time": 0.0,
    "rag_augmented_requests": 0,
    "total_processing_time": 0.0
}

# RAG statistics (fallback)
rag_stats = {
    "total_retrievals": 0,
    "cache_hits": 0,
    "cache_hit_rate": 0.0,
    "successful_augmentations": 0,
    "vector_searches": 0,
    "collections": ["financial_knowledge", "interaction_patterns", "analysis_templates", "market_data"],
    "embedding_dimension": 384
}

def initialize_rag_service():
    """Initialize RAG service in background"""
    global rag_service, services_status
    
    try:
        logger.info("🚀 Initializing RAG service...")
        
        from core.rag_service_fixed import RAGService
        import asyncio
        
        rag_service = RAGService()
        
        # Initialize in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(rag_service.initialize())
        loop.close()
        
        services_status["rag_initialized"] = True
        services_status["vector_connected"] = True
        logger.info("✅ RAG service initialized successfully")
        
    except Exception as e:
        logger.warning(f"⚠️ RAG initialization failed: {e}")
        services_status["initialization_error"] = str(e)
        services_status["rag_initialized"] = False
        services_status["vector_connected"] = False

# Start initialization in background
threading.Thread(target=initialize_rag_service, daemon=True).start()

@app.route('/')
def index():
    """Main interface"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG-Enhanced Autonomous Agent</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
            min-height: 100vh; 
            color: white;
        }
        .container { 
            max-width: 1200px; 
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
            font-size: 2.5em;
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
        }
        .badge {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
            margin: 5px;
            display: inline-block;
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
            transition: all 0.3s ease;
        }
        .status-active { border-left-color: #28a745; }
        .status-warning { border-left-color: #ffc107; }
        .status-error { border-left-color: #dc3545; }
        .button { 
            background: linear-gradient(45deg, #00d4ff, #0099cc); 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            margin: 5px; 
            font-size: 14px; 
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
        .section {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        textarea { 
            width: 100%; 
            height: 120px; 
            margin: 10px 0; 
            padding: 12px; 
            border: 1px solid rgba(0, 212, 255, 0.3); 
            border-radius: 6px; 
            font-family: 'Courier New', monospace; 
            font-size: 13px;
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
            padding: 12px 20px; 
            font-weight: bold; 
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .result-content { 
            padding: 20px; 
            max-height: 500px; 
            overflow-y: auto; 
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            line-height: 1.5;
            font-size: 13px;
        }
        .rag-indicator {
            background: rgba(255, 107, 107, 0.3);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
        }
        .tabs {
            display: flex;
            margin: 20px 0;
            border-bottom: 2px solid rgba(0, 212, 255, 0.3);
        }
        .tab {
            padding: 10px 20px;
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
            <span class="badge">🚀 Vector Accelerated</span>
            <span class="badge">🧠 Knowledge Augmented</span>
            <span class="badge">⚡ Real-time Analysis</span>
            <p>Advanced AI-powered financial analysis with Retrieval Augmented Generation</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card status-active">
                <strong>🌐 Server</strong><br>
                <span>✅ Running</span>
            </div>
            <div class="status-card" id="ragCard">
                <strong>🧠 RAG Service</strong><br>
                <span id="ragStatus">🔄 Initializing...</span>
            </div>
            <div class="status-card" id="vectorCard">
                <strong>⚡ Vector DB</strong><br>
                <span id="vectorStatus">🔄 Connecting...</span>
            </div>
            <div class="status-card" id="statsCard">
                <strong>📊 Requests</strong><br>
                <span id="statsStatus">0 processed</span>
            </div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('analysis')">🔍 Analysis</div>
            <div class="tab" onclick="switchTab('rag')">🧠 RAG Status</div>
            <div class="tab" onclick="switchTab('vector')">⚡ Vector DB</div>
            <div class="tab" onclick="switchTab('history')">📊 History</div>
        </div>
        
        <div id="analysis" class="tab-content active">
            <div class="section">
                <h3>🔍 RAG-Enhanced Financial Analysis</h3>
                <p>Input financial data for comprehensive analysis with knowledge augmentation:</p>
                <textarea id="analysisData" placeholder='{"transactions": [{"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary"}], "account_balance": 2250.00}'></textarea>
                <br>
                <button class="button" onclick="processAnalysis()">🚀 Analyze with RAG</button>
                <button class="button secondary" onclick="loadExample()">📝 Load Example</button>
                <button class="button secondary" onclick="clearResults()">🗑️ Clear</button>
            </div>
        </div>
        
        <div id="rag" class="tab-content">
            <div class="section">
                <h3>🧠 RAG Service Status</h3>
                <div id="ragDetails">Loading...</div>
                <button class="button" onclick="refreshRAG()">🔄 Refresh</button>
            </div>
        </div>
        
        <div id="vector" class="tab-content">
            <div class="section">
                <h3>⚡ Vector Database Status</h3>
                <div id="vectorDetails">Loading...</div>
                <button class="button" onclick="refreshVector()">🔄 Refresh</button>
            </div>
        </div>
        
        <div id="history" class="tab-content">
            <div class="section">
                <h3>📊 Analysis History</h3>
                <div id="historyDetails">No analyses performed yet.</div>
                <button class="button" onclick="refreshHistory()">🔄 Refresh</button>
                <button class="button secondary" onclick="clearHistory()">🗑️ Clear History</button>
            </div>
        </div>
        
        <div id="resultsContainer" class="result-container">
            <div class="result-header">
                <span>Analysis Results</span>
                <div>
                    <span class="rag-indicator" id="ragIndicator">🧠 RAG: Enabled</span>
                    <span style="margin-left: 10px; font-size: 12px;" id="processingTime"></span>
                </div>
            </div>
            <div id="resultsContent" class="result-content"></div>
        </div>
    </div>
    
    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'rag') refreshRAG();
            if (tabName === 'vector') refreshVector();
            if (tabName === 'history') refreshHistory();
        }
        
        function loadExample() {
            document.getElementById('analysisData').value = JSON.stringify({
                "transactions": [
                    {"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"},
                    {"date": "2024-01-16", "amount": -50.00, "type": "debit", "description": "Grocery shopping"},
                    {"date": "2024-01-17", "amount": -1200.00, "type": "debit", "description": "Rent payment"},
                    {"date": "2024-01-18", "amount": -75.50, "type": "debit", "description": "Utilities"},
                    {"date": "2024-01-20", "amount": 2000.00, "type": "credit", "description": "Freelance income"}
                ],
                "account_balance": 2175.50,
                "customer_id": "CUST_001"
            }, null, 2);
        }
        
        async function processAnalysis() {
            const data = document.getElementById('analysisData').value;
            const container = document.getElementById('resultsContainer');
            const content = document.getElementById('resultsContent');
            const timeEl = document.getElementById('processingTime');
            const ragEl = document.getElementById('ragIndicator');
            
            try {
                container.style.display = 'block';
                content.textContent = '🔄 Processing enhanced analysis...';
                
                const inputData = JSON.parse(data);
                
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ input_data: inputData, enable_rag: true })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    content.textContent = result.analysis || 'Analysis completed successfully';
                    timeEl.textContent = `${result.processing_time?.toFixed(3)}s`;
                    
                    if (result.rag_metadata?.rag_enabled) {
                        ragEl.textContent = `🧠 RAG: ${result.rag_metadata.context_items_used || 0} items`;
                        ragEl.style.background = 'rgba(40, 167, 69, 0.3)';
                    } else {
                        ragEl.textContent = '🧠 RAG: Basic Mode';
                        ragEl.style.background = 'rgba(255, 193, 7, 0.3)';
                    }
                    
                    updateStats();
                } else {
                    content.textContent = `Error: ${result.error || 'Unknown error'}`;
                }
                
            } catch (error) {
                content.textContent = `Error: ${error.message}`;
                ragEl.textContent = '🧠 RAG: Error';
                ragEl.style.background = 'rgba(220, 53, 69, 0.3)';
            }
        }
        
        async function refreshRAG() {
            try {
                const response = await fetch('/rag/status');
                const status = await response.json();
                
                let details = `
                    <h4>RAG Service Details:</h4>
                    <p><strong>Status:</strong> ${status.status || 'Unknown'}</p>
                    <p><strong>Retrievals:</strong> ${status.total_retrievals || 0}</p>
                    <p><strong>Cache Hit Rate:</strong> ${((status.cache_hit_rate || 0) * 100).toFixed(1)}%</p>
                    <p><strong>Augmentations:</strong> ${status.successful_augmentations || 0}</p>
                    <p><strong>Vector Searches:</strong> ${status.vector_searches || 0}</p>
                    <p><strong>Collections:</strong> ${(status.collections || []).join(', ')}</p>
                `;
                
                document.getElementById('ragDetails').innerHTML = details;
                document.getElementById('ragStatus').textContent = 
                    status.status === 'active' ? '✅ Active' : '⚠️ Basic Mode';
                    
            } catch (error) {
                document.getElementById('ragDetails').textContent = `Error: ${error.message}`;
                document.getElementById('ragStatus').textContent = '❌ Error';
            }
        }
        
        async function refreshVector() {
            try {
                const response = await fetch('/vector/status');
                const status = await response.json();
                
                let details = `
                    <h4>Vector Database Details:</h4>
                    <p><strong>Status:</strong> ${status.status || 'Unknown'}</p>
                    <p><strong>Host:</strong> ${status.host || 'localhost'}:${status.port || 6333}</p>
                    <p><strong>Collections:</strong> ${status.total_collections || 0}</p>
                    <p><strong>Model:</strong> ${status.embedding_model || 'all-MiniLM-L6-v2'}</p>
                    <p><strong>Dimensions:</strong> ${status.embedding_dimension || 384}</p>
                `;
                
                if (status.collections_detail) {
                    details += '<h5>Collection Details:</h5><ul>';
                    status.collections_detail.forEach(col => {
                        details += `<li><strong>${col.name}:</strong> ${col.points_count || 0} points</li>`;
                    });
                    details += '</ul>';
                }
                
                document.getElementById('vectorDetails').innerHTML = details;
                document.getElementById('vectorStatus').textContent = 
                    status.status === 'connected' ? '✅ Connected' : '⚠️ Memory Mode';
                    
            } catch (error) {
                document.getElementById('vectorDetails').textContent = `Error: ${error.message}`;
                document.getElementById('vectorStatus').textContent = '❌ Error';
            }
        }
        
        async function refreshHistory() {
            try {
                const response = await fetch('/history');
                const data = await response.json();
                
                if (data.history && data.history.length > 0) {
                    let html = '<h4>Recent Analyses:</h4><ul>';
                    data.history.forEach((item, i) => {
                        html += `<li><strong>Analysis ${i+1}:</strong> ${item.status} (${item.processing_time?.toFixed(3)}s)`;
                        if (item.rag_metadata?.rag_enabled) html += ' 🧠';
                        html += '</li>';
                    });
                    html += '</ul>';
                    document.getElementById('historyDetails').innerHTML = html;
                } else {
                    document.getElementById('historyDetails').innerHTML = '<p>No analyses performed yet.</p>';
                }
                
            } catch (error) {
                document.getElementById('historyDetails').textContent = `Error: ${error.message}`;
            }
        }
        
        async function updateStats() {
            try {
                const response = await fetch('/status');
                const status = await response.json();
                
                document.getElementById('statsStatus').textContent = 
                    `${status.statistics?.total_requests || 0} processed`;
                    
            } catch (error) {
                console.error('Stats update failed:', error);
            }
        }
        
        async function clearHistory() {
            try {
                await fetch('/clear_history', { method: 'DELETE' });
                refreshHistory();
            } catch (error) {
                console.error('Clear history failed:', error);
            }
        }
        
        function clearResults() {
            document.getElementById('resultsContainer').style.display = 'none';
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadExample();
            
            // Status checks
            setTimeout(() => {
                refreshRAG();
                refreshVector();
                updateStats();
            }, 2000);
            
            // Periodic updates
            setInterval(updateStats, 10000);
        });
    </script>
</body>
</html>
    """)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Enhanced analysis endpoint"""
    global agent_statistics, rag_stats
    
    start_time = time.time()
    agent_statistics["total_requests"] += 1
    
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            agent_statistics["failed_requests"] += 1
            return jsonify({"error": "Missing input_data field"}), 400
        
        input_data = data['input_data']
        enable_rag = data.get('enable_rag', True)
        
        # Perform analysis
        analysis = perform_comprehensive_analysis(input_data)
        
        # RAG augmentation if available
        rag_metadata = {"rag_enabled": False}
        
        if enable_rag and services_status["rag_initialized"] and rag_service:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                augmented_analysis, rag_metadata = loop.run_until_complete(
                    rag_service.augment_prompt(analysis, input_data)
                )
                analysis = augmented_analysis
                agent_statistics["rag_augmented_requests"] += 1
                rag_stats["successful_augmentations"] += 1
                
                loop.close()
                
            except Exception as e:
                logger.warning(f"RAG augmentation failed: {e}")
                rag_metadata = {"rag_enabled": False, "error": str(e)}
        
        processing_time = time.time() - start_time
        
        # Update statistics
        agent_statistics["successful_requests"] += 1
        agent_statistics["total_processing_time"] += processing_time
        agent_statistics["average_processing_time"] = (
            agent_statistics["total_processing_time"] / agent_statistics["successful_requests"]
        )
        
        # Create response
        response_data = {
            "request_id": f"req_{int(time.time())}",
            "status": "success",
            "analysis": analysis,
            "processing_time": processing_time,
            "rag_metadata": rag_metadata,
            "input_summary": {
                "transaction_count": len(input_data.get("transactions", [])),
                "has_balance": "account_balance" in input_data
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in history
        interaction_history.append(response_data)
        if len(interaction_history) > 50:
            interaction_history[:] = interaction_history[-40:]
        
        return jsonify(response_data)
        
    except Exception as e:
        agent_statistics["failed_requests"] += 1
        logger.error(f"Analysis error: {e}")
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        "status": "operational",
        "mode": "rag_enhanced",
        "version": "2.0.0-final",
        "timestamp": datetime.now().isoformat(),
        "statistics": agent_statistics,
        "services": {
            "rag_service": "active" if services_status["rag_initialized"] else "basic_mode",
            "vector_database": "connected" if services_status["vector_connected"] else "memory_mode"
        }
    })

@app.route('/rag/status', methods=['GET'])
def get_rag_status():
    """Get RAG service status"""
    try:
        if services_status["rag_initialized"] and rag_service:
            stats = rag_service.get_rag_statistics()
            return jsonify({"status": "active", **stats})
        else:
            return jsonify({
                "status": "basic_mode",
                **rag_stats,
                "error": services_status.get("initialization_error")
            })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e), **rag_stats})

@app.route('/vector/status', methods=['GET'])
def get_vector_status():
    """Get vector database status"""
    try:
        if services_status["vector_connected"] and rag_service:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            vector_status = loop.run_until_complete(rag_service.get_vector_status())
            loop.close()
            return jsonify(vector_status)
        else:
            return jsonify({
                "status": "memory_mode",
                "host": "localhost",
                "port": 6333,
                "total_collections": 4,
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimension": 384,
                "collections_detail": [
                    {"name": "financial_knowledge", "points_count": 0},
                    {"name": "interaction_patterns", "points_count": 0},
                    {"name": "analysis_templates", "points_count": 0},
                    {"name": "market_data", "points_count": 0}
                ],
                "error": services_status.get("initialization_error")
            })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/history', methods=['GET'])
def get_history():
    """Get interaction history"""
    limit = request.args.get('limit', 10, type=int)
    return jsonify({
        "history": interaction_history[-limit:] if interaction_history else [],
        "total_count": len(interaction_history)
    })

@app.route('/clear_history', methods=['DELETE'])
def clear_history():
    """Clear interaction history"""
    global interaction_history
    interaction_history.clear()
    return jsonify({"success": True, "message": "History cleared"})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "mode": "rag_enhanced",
        "version": "2.0.0-final",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "rag_service": services_status["rag_initialized"],
            "vector_database": services_status["vector_connected"],
            "initialization_complete": services_status["rag_initialized"]
        }
    })

def perform_comprehensive_analysis(input_data):
    """Perform comprehensive financial analysis"""
    
    analysis = "=== ENHANCED FINANCIAL ANALYSIS REPORT ===\\n\\n"
    
    try:
        # Executive Summary
        analysis += "EXECUTIVE SUMMARY:\\n"
        analysis += "Comprehensive financial analysis incorporating industry best practices\\n"
        analysis += "and established financial principles for actionable insights.\\n\\n"
        
        # Transaction Analysis
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            analysis += f"TRANSACTION ANALYSIS:\\n"
            analysis += f"📊 Total Transactions: {len(transactions)}\\n\\n"
            
            # Financial Metrics
            credits = sum(abs(tx.get("amount", 0)) for tx in transactions 
                         if tx.get("type") == "credit" or tx.get("amount", 0) > 0)
            debits = sum(abs(tx.get("amount", 0)) for tx in transactions 
                        if tx.get("type") == "debit" or tx.get("amount", 0) < 0)
            net_flow = credits - debits
            
            analysis += f"CASH FLOW METRICS:\\n"
            analysis += f"💰 Total Inflows: ${credits:,.2f}\\n"
            analysis += f"💸 Total Outflows: ${debits:,.2f}\\n"
            analysis += f"📈 Net Cash Flow: ${net_flow:,.2f}\\n\\n"
            
            # Cash Flow Assessment
            if net_flow > 0:
                analysis += f"CASH FLOW HEALTH: ✅ POSITIVE\\n"
                analysis += f"• Strong financial position with surplus funds\\n"
                analysis += f"• Opportunity for investment and wealth building\\n"
                analysis += f"• Recommended action: Optimize surplus allocation\\n\\n"
            elif net_flow < 0:
                analysis += f"CASH FLOW HEALTH: ⚠️ NEGATIVE\\n"
                analysis += f"• Outflows exceed inflows - requires attention\\n"
                analysis += f"• Risk of financial strain if trend continues\\n"
                analysis += f"• Recommended action: Expense optimization review\\n\\n"
            else:
                analysis += f"CASH FLOW HEALTH: 📊 BALANCED\\n"
                analysis += f"• Break-even position with balanced flows\\n"
                analysis += f"• Stable but limited growth potential\\n"
                analysis += f"• Recommended action: Focus on income growth\\n\\n"
            
            # Spending Categories
            categories = categorize_spending(transactions)
            if categories:
                analysis += f"SPENDING BREAKDOWN:\\n"
                total_spending = sum(v for k, v in categories.items() if k != "Income")
                
                for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    if category == "Income":
                        analysis += f"💰 {category}: ${amount:,.2f}\\n"
                    else:
                        pct = (amount / total_spending * 100) if total_spending > 0 else 0
                        analysis += f"📊 {category}: ${amount:,.2f} ({pct:.1f}%)\\n"
                
                analysis += "\\n"
                
                # Spending Insights
                analysis += f"SPENDING INSIGHTS:\\n"
                if total_spending > 0:
                    largest_expense = max((k, v) for k, v in categories.items() if k != "Income")
                    analysis += f"🔍 Largest category: {largest_expense[0]} (${largest_expense[1]:,.2f})\\n"
                    
                    # Check spending ratios
                    housing_pct = categories.get("Housing", 0) / total_spending * 100
                    if housing_pct > 30:
                        analysis += f"⚠️ Housing costs ({housing_pct:.1f}%) exceed recommended 30%\\n"
                    
                    food_pct = categories.get("Food & Dining", 0) / total_spending * 100
                    if food_pct > 15:
                        analysis += f"💡 Food expenses ({food_pct:.1f}%) - consider optimization\\n"
                
                analysis += "\\n"
        
        # Account Balance Analysis
        if "account_balance" in input_data:
            balance = input_data["account_balance"]
            analysis += f"LIQUIDITY ANALYSIS:\\n"
            analysis += f"💼 Current Balance: ${balance:,.2f}\\n\\n"
            
            # Liquidity Assessment
            if balance > 20000:
                analysis += f"LIQUIDITY STATUS: ✅ EXCELLENT\\n"
                analysis += f"• Superior cash reserves for emergencies\\n"
                analysis += f"• Significant investment opportunities available\\n"
                analysis += f"• Consider diversified portfolio allocation\\n"
            elif balance > 10000:
                analysis += f"LIQUIDITY STATUS: ✅ STRONG\\n"
                analysis += f"• Good emergency fund coverage\\n"
                analysis += f"• Adequate reserves for opportunities\\n"
                analysis += f"• Balance safety with growth investments\\n"
            elif balance > 5000:
                analysis += f"LIQUIDITY STATUS: 📊 ADEQUATE\\n"
                analysis += f"• Moderate emergency coverage\\n"
                analysis += f"• Build reserves while maintaining stability\\n"
                analysis += f"• Focus on consistent savings growth\\n"
            elif balance > 1000:
                analysis += f"LIQUIDITY STATUS: ⚠️ LIMITED\\n"
                analysis += f"• Below recommended emergency levels\\n"
                analysis += f"• Priority: Build 3-6 months expense buffer\\n"
                analysis += f"• Limit discretionary spending temporarily\\n"
            else:
                analysis += f"LIQUIDITY STATUS: 🚨 CRITICAL\\n"
                analysis += f"• Immediate liquidity concern\\n"
                analysis += f"• Emergency action required\\n"
                analysis += f"• Focus on expense reduction and income\\n"
            
            analysis += "\\n"
        
        # Risk Assessment
        analysis += f"FINANCIAL RISK ASSESSMENT:\\n"
        risk_score = 0
        risk_factors = []
        
        # Balance risk
        if "account_balance" in input_data:
            balance = input_data["account_balance"]
            if balance < 1000:
                risk_score += 3
                risk_factors.append("Critically low liquidity reserves")
            elif balance < 5000:
                risk_score += 1
                risk_factors.append("Below recommended emergency fund")
        
        # Transaction pattern risks
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            large_debits = [tx for tx in transactions if tx.get("amount", 0) < -1000]
            if len(large_debits) > 3:
                risk_score += 2
                risk_factors.append("High frequency of large expenses")
            
            # Income volatility
            income_txs = [tx for tx in transactions if tx.get("amount", 0) > 0]
            if len(income_txs) < 2:
                risk_score += 1
                risk_factors.append("Limited income diversification")
        
        # Risk level
        if risk_score >= 4:
            risk_level, risk_color = "HIGH", "🔴"
        elif risk_score >= 2:
            risk_level, risk_color = "MEDIUM", "🟡"
        else:
            risk_level, risk_color = "LOW", "🟢"
        
        analysis += f"{risk_color} Risk Level: {risk_level}\\n"
        if risk_factors:
            for factor in risk_factors:
                analysis += f"  • {factor}\\n"
        else:
            analysis += f"✅ No significant risk factors identified\\n"
        
        analysis += "\\n"
        
        # Strategic Recommendations
        analysis += f"STRATEGIC RECOMMENDATIONS:\\n"
        
        if "transactions" in input_data and "account_balance" in input_data:
            balance = input_data["account_balance"]
            monthly_expenses = sum(abs(tx.get("amount", 0)) for tx in input_data["transactions"] 
                                 if tx.get("amount", 0) < 0)
            
            # Emergency fund target
            emergency_target = monthly_expenses * 6
            if balance < emergency_target:
                analysis += f"🎯 Priority 1: Build emergency fund to ${emergency_target:,.2f}\\n"
            
            # Savings rate
            monthly_income = sum(tx.get("amount", 0) for tx in input_data["transactions"] 
                               if tx.get("amount", 0) > 0)
            if monthly_income > 0:
                savings_rate = ((monthly_income - monthly_expenses) / monthly_income) * 100
                analysis += f"📊 Current Savings Rate: {savings_rate:.1f}%\\n"
                
                if savings_rate < 15:
                    analysis += f"🎯 Priority 2: Increase savings rate to 15-20%\\n"
                else:
                    analysis += f"✅ Strong savings discipline maintained\\n"
        
        analysis += f"💼 Automate savings transfers for consistency\\n"
        analysis += f"📈 Review recurring expenses quarterly\\n"
        analysis += f"🎓 Consider financial education opportunities\\n"
        analysis += f"🔄 Implement regular financial health checkups\\n"
        
        analysis += "\\n=== END COMPREHENSIVE ANALYSIS ===\\n"
        analysis += "\\n💡 Analysis based on established financial principles and best practices."
        
    except Exception as e:
        analysis += f"\\nError during analysis: {str(e)}\\n"
        analysis += "Please verify input data format and retry."
    
    return analysis

def categorize_spending(transactions):
    """Categorize transactions for spending analysis"""
    categories = {}
    
    for tx in transactions:
        desc = tx.get("description", "").lower()
        amount = abs(tx.get("amount", 0))
        
        if any(word in desc for word in ["salary", "income", "payroll", "freelance", "wage"]):
            categories["Income"] = categories.get("Income", 0) + amount
        elif any(word in desc for word in ["rent", "mortgage", "property", "housing"]):
            categories["Housing"] = categories.get("Housing", 0) + amount
        elif any(word in desc for word in ["grocery", "food", "restaurant", "dining"]):
            categories["Food & Dining"] = categories.get("Food & Dining", 0) + amount
        elif any(word in desc for word in ["utility", "electric", "gas", "water", "internet"]):
            categories["Utilities"] = categories.get("Utilities", 0) + amount
        elif any(word in desc for word in ["transport", "gas", "uber", "taxi", "car"]):
            categories["Transportation"] = categories.get("Transportation", 0) + amount
        elif any(word in desc for word in ["medical", "health", "doctor", "pharmacy"]):
            categories["Healthcare"] = categories.get("Healthcare", 0) + amount
        elif any(word in desc for word in ["entertainment", "streaming", "gym", "fitness"]):
            categories["Entertainment"] = categories.get("Entertainment", 0) + amount
        elif any(word in desc for word in ["shopping", "amazon", "store", "retail"]):
            categories["Shopping"] = categories.get("Shopping", 0) + amount
        else:
            categories["Other"] = categories.get("Other", 0) + amount
    
    return categories

if __name__ == "__main__":
    print("🚀 Starting RAG-Enhanced Autonomous Financial Analysis Agent")
    print("=" * 60)
    print("🧠 Features: Knowledge Augmentation, Vector Acceleration")
    print("⚡ Real-time Analysis, Continuous Learning")
    print("🌐 Server: http://localhost:5001")
    print("🔄 RAG service initializing in background...")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)