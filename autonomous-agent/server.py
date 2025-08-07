"""
Autonomous Financial Analysis Agent Server
"""

import asyncio
import json
import time
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

from core.autonomous_agent import AutonomousAgent
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global agent instance
agent = None

@app.before_first_request
async def initialize_agent():
    """Initialize the autonomous agent on first request"""
    global agent
    if agent is None:
        logger.info("Initializing Autonomous Financial Analysis Agent...")
        agent = AutonomousAgent()
        await agent.initialize()
        logger.info("Agent initialization completed")

@app.route('/')
def index():
    """Serve the main interface"""
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Financial Analysis Agent</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
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
            color: #3498db; 
            margin-bottom: 10px; 
            font-size: 2.5em;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .feature-card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .feature-card h3 {
            color: #e74c3c;
            margin-bottom: 15px;
        }
        .section { 
            margin: 20px 0; 
            padding: 20px; 
            border: 1px solid rgba(255,255,255,0.2); 
            border-radius: 10px; 
            background: rgba(255,255,255,0.05); 
        }
        .button { 
            background: linear-gradient(45deg, #3498db, #2980b9); 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            margin: 5px; 
            font-size: 16px; 
            font-weight: bold;
            transition: transform 0.2s;
        }
        .button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4); 
        }
        textarea { 
            width: 100%; 
            height: 150px; 
            margin: 10px 0; 
            padding: 15px; 
            border: 1px solid rgba(255,255,255,0.3); 
            border-radius: 8px; 
            font-family: 'Courier New', monospace; 
            font-size: 14px;
            background: rgba(255,255,255,0.1);
            color: white;
        }
        .result-container { 
            background: rgba(46, 204, 113, 0.1); 
            border: 2px solid #2ecc71; 
            border-radius: 10px; 
            margin: 20px 0; 
            overflow: hidden;
            display: none;
        }
        .result-header { 
            background: #2ecc71; 
            color: white; 
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
        .confidence-indicator {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }
        .confidence-high { background: #2ecc71; color: white; }
        .confidence-medium { background: #f39c12; color: white; }
        .confidence-low { background: #e74c3c; color: white; }
        .loading { 
            text-align: center; 
            padding: 40px; 
            font-size: 18px; 
        }
        .status { 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 8px; 
            background: rgba(52, 152, 219, 0.1); 
            border-left: 4px solid #3498db; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Autonomous Financial Analysis Agent</h1>
            <p>Next-generation AI-powered financial analysis with anti-hallucination technology</p>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <h3>🧠 Autonomous Processing</h3>
                <p>Multi-step reasoning with automatic validation and fact-checking</p>
            </div>
            <div class="feature-card">
                <h3>🛡️ Hallucination Prevention</h3>
                <p>Advanced detection systems prevent false information generation</p>
            </div>
            <div class="feature-card">
                <h3>📊 Confidence Scoring</h3>
                <p>Every response includes detailed confidence and reliability metrics</p>
            </div>
            <div class="feature-card">
                <h3>🔗 Prompt Engine Integration</h3>
                <p>Seamlessly integrates with the existing prompt-engine for optimal results</p>
            </div>
        </div>
        
        <div class="section">
            <h3>🔍 Autonomous Financial Analysis</h3>
            <p>Provide financial data for comprehensive autonomous analysis:</p>
            <textarea id="analysisData" placeholder='{"transactions": [{"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"}], "account_balance": 2250.00}'></textarea>
            <br>
            <button class="button" onclick="processAnalysis()">🚀 Process Autonomous Analysis</button>
            <button class="button" onclick="loadExampleData()">📝 Load Example</button>
            <button class="button" onclick="clearResults()">🗑️ Clear</button>
        </div>
        
        <div class="section">
            <h3>⚙️ Agent Status</h3>
            <div class="status" id="agentStatus">Loading agent status...</div>
            <button class="button" onclick="refreshStatus()">🔄 Refresh Status</button>
        </div>
        
        <!-- Results Display -->
        <div id="resultsContainer" class="result-container">
            <div class="result-header">
                <span>Autonomous Analysis Results</span>
                <span id="confidenceIndicator" class="confidence-indicator"></span>
                <span style="float: right; font-size: 14px;" id="processingTime"></span>
            </div>
            <div id="resultsContent" class="result-content"></div>
        </div>
        
        <!-- Loading Indicator -->
        <div id="loadingIndicator" class="loading" style="display: none;">
            🔄 Processing autonomous analysis... This may take a moment...
        </div>
    </div>
    
    <script>
        async function loadExampleData() {
            document.getElementById('analysisData').value = JSON.stringify({
                "transactions": [
                    {"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"},
                    {"date": "2024-01-16", "amount": -50.00, "type": "debit", "description": "Grocery shopping"},
                    {"date": "2024-01-17", "amount": -1200.00, "type": "debit", "description": "Rent payment"},
                    {"date": "2024-01-18", "amount": -75.50, "type": "debit", "description": "Utilities"},
                    {"date": "2024-01-20", "amount": 2000.00, "type": "credit", "description": "Freelance payment"}
                ],
                "account_balance": 2175.50,
                "customer_id": "CUST_001",
                "account_type": "checking"
            }, null, 2);
        }
        
        async function processAnalysis() {
            const data = document.getElementById('analysisData').value;
            const loadingEl = document.getElementById('loadingIndicator');
            const resultsEl = document.getElementById('resultsContainer');
            const contentEl = document.getElementById('resultsContent');
            const timeEl = document.getElementById('processingTime');
            const confidenceEl = document.getElementById('confidenceIndicator');
            
            try {
                // Show loading
                loadingEl.style.display = 'block';
                resultsEl.style.display = 'none';
                
                // Parse input data
                let inputData;
                try {
                    inputData = JSON.parse(data);
                } catch (parseError) {
                    throw new Error('Invalid JSON format: ' + parseError.message);
                }
                
                // Make request to autonomous agent
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        input_data: inputData,
                        request_config: {
                            generation_type: "autonomous"
                        }
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                
                // Display results
                loadingEl.style.display = 'none';
                resultsEl.style.display = 'block';
                
                // Format the analysis result
                const formattedResult = formatAnalysisResult(result);
                contentEl.textContent = formattedResult;
                
                // Update metadata
                timeEl.textContent = `${result.processing_time?.toFixed(3)}s`;
                
                // Update confidence indicator
                const confidence = result.confidence_score?.confidence_level || 'unknown';
                confidenceEl.textContent = confidence.toUpperCase();
                confidenceEl.className = `confidence-indicator confidence-${confidence}`;
                
            } catch (error) {
                loadingEl.style.display = 'none';
                resultsEl.style.display = 'block';
                contentEl.textContent = `Error: ${error.message}`;
                confidenceEl.textContent = 'ERROR';
                confidenceEl.className = 'confidence-indicator confidence-low';
            }
        }
        
        function formatAnalysisResult(result) {
            let formatted = `=== AUTONOMOUS FINANCIAL ANALYSIS ===\\n\\n`;
            
            // Core analysis
            formatted += `ANALYSIS:\\n${result.analysis || 'No analysis available'}\\n\\n`;
            
            // Confidence information
            if (result.confidence_score) {
                formatted += `CONFIDENCE ASSESSMENT:\\n`;
                formatted += `Overall Score: ${result.confidence_score.overall_score?.toFixed(3)} (${result.confidence_score.confidence_level})\\n`;
                
                if (result.confidence_score.component_scores) {
                    formatted += `Component Scores:\\n`;
                    for (const [component, score] of Object.entries(result.confidence_score.component_scores)) {
                        formatted += `  • ${component.replace('_', ' ')}: ${score.toFixed(3)}\\n`;
                    }
                }
                formatted += `\\n`;
            }
            
            // Validation results
            if (result.validation_result) {
                formatted += `VALIDATION STATUS: ${result.validation_result.passed ? 'PASSED' : 'FAILED'}\\n`;
                
                if (result.validation_result.hallucination_result?.is_hallucinated) {
                    formatted += `⚠️ Hallucination detected: ${result.validation_result.hallucination_result.type}\\n`;
                }
                formatted += `\\n`;
            }
            
            // Quality indicators
            if (result.reliability_indicators) {
                formatted += `RELIABILITY INDICATORS:\\n`;
                for (const [key, value] of Object.entries(result.reliability_indicators)) {
                    formatted += `  • ${key.replace('_', ' ')}: ${value}\\n`;
                }
                formatted += `\\n`;
            }
            
            // Processing metadata
            if (result.agent_metadata) {
                formatted += `PROCESSING METADATA:\\n`;
                formatted += `Agent Version: ${result.agent_metadata.version}\\n`;
                formatted += `Vector Enhanced: ${result.agent_metadata.vector_enhanced ? 'Yes' : 'No'}\\n`;
                formatted += `Quality Passed: ${result.agent_metadata.quality_passed ? 'Yes' : 'No'}\\n`;
                formatted += `Processing Time: ${result.processing_time?.toFixed(3)}s\\n`;
            }
            
            return formatted;
        }
        
        async function refreshStatus() {
            try {
                const response = await fetch('/status');
                const status = await response.json();
                
                let statusHtml = `
                    <strong>Agent Status:</strong> ${status.agent_info?.initialized ? '✅ Operational' : '❌ Not Initialized'}<br>
                    <strong>Version:</strong> ${status.agent_info?.version}<br>
                    <strong>Success Rate:</strong> ${(status.statistics?.success_rate * 100).toFixed(1)}%<br>
                    <strong>Total Requests:</strong> ${status.statistics?.total_requests}<br>
                    <strong>Avg Processing Time:</strong> ${status.statistics?.average_processing_time?.toFixed(3)}s<br>
                    <strong>Avg Quality Score:</strong> ${status.statistics?.average_quality_score?.toFixed(3)}
                `;
                
                document.getElementById('agentStatus').innerHTML = statusHtml;
            } catch (error) {
                document.getElementById('agentStatus').innerHTML = `❌ Error loading status: ${error.message}`;
            }
        }
        
        function clearResults() {
            document.getElementById('resultsContainer').style.display = 'none';
            document.getElementById('loadingIndicator').style.display = 'none';
        }
        
        // Load status on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadExampleData();
            refreshStatus();
        });
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/analyze', methods=['POST'])
async def analyze():
    """Main autonomous analysis endpoint"""
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({"error": "Missing input_data field"}), 400
        
        input_data = data['input_data']
        request_config = data.get('request_config', {})
        
        # Process with autonomous agent
        result = await agent.process_autonomous_request(input_data, request_config)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
async def get_status():
    """Get agent status"""
    try:
        if agent:
            status = agent.get_agent_status()
            return jsonify(status)
        else:
            return jsonify({"error": "Agent not initialized"}), 503
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
async def get_history():
    """Get interaction history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = await agent.get_interaction_history(limit)
        return jsonify({"history": history})
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear_history', methods=['DELETE'])
async def clear_history():
    """Clear interaction history"""
    try:
        success = await agent.clear_history()
        return jsonify({"success": success})
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    config = get_config()
    
    return jsonify({
        "status": "healthy",
        "agent_initialized": agent is not None and agent.is_initialized,
        "version": config["agent"]["version"],
        "timestamp": datetime.now().isoformat(),
        "capabilities": list(config["agent"]["capabilities"].keys()) if agent else []
    })

if __name__ == "__main__":
    config = get_config()
    
    print("🤖 Starting Autonomous Financial Analysis Agent...")
    print(f"🌐 Server: http://{config['prompt_engine']['host']}:{config['agent']['port'] if 'port' in config['agent'] else 5001}")
    print("=" * 60)
    
    # Initialize the agent
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    agent = AutonomousAgent()
    loop.run_until_complete(agent.initialize())
    
    app.run(
        host=config["flask"]["host"],
        port=config["flask"]["port"], 
        debug=config["flask"]["debug"]
    )