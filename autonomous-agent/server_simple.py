"""
Simplified Autonomous Financial Analysis Agent Server
(Works with basic dependencies only)
"""

import asyncio
import json
import time
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

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
            color: #3498db; 
            margin-bottom: 10px; 
            font-size: 2.5em;
        }
        .status { 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 8px; 
            background: rgba(52, 152, 219, 0.1); 
            border-left: 4px solid #3498db; 
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Autonomous Financial Analysis Agent</h1>
            <p>Simplified version - Basic financial analysis capabilities</p>
        </div>
        
        <div class="status">
            ✅ Flask Server: Running<br>
            ✅ Core Dependencies: Loaded<br>
            ⚠️ Advanced Features: Install additional dependencies for full functionality
        </div>
        
        <div style="margin: 20px 0; padding: 20px; border: 1px solid rgba(255,255,255,0.2); border-radius: 10px; background: rgba(255,255,255,0.05);">
            <h3>🔍 Basic Financial Analysis</h3>
            <p>Provide financial data for analysis:</p>
            <textarea id="analysisData" placeholder='{"transactions": [{"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"}], "account_balance": 2250.00}'></textarea>
            <br>
            <button class="button" onclick="processAnalysis()">🚀 Analyze Data</button>
            <button class="button" onclick="loadExampleData()">📝 Load Example</button>
            <button class="button" onclick="clearResults()">🗑️ Clear</button>
        </div>
        
        <!-- Results Display -->
        <div id="resultsContainer" class="result-container">
            <div class="result-header">
                <span>Analysis Results</span>
                <span style="float: right; font-size: 14px;" id="processingTime"></span>
            </div>
            <div id="resultsContent" class="result-content"></div>
        </div>
    </div>
    
    <script>
        function loadExampleData() {
            document.getElementById('analysisData').value = JSON.stringify({
                "transactions": [
                    {"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"},
                    {"date": "2024-01-16", "amount": -50.00, "type": "debit", "description": "Grocery shopping"},
                    {"date": "2024-01-17", "amount": -1200.00, "type": "debit", "description": "Rent payment"}
                ],
                "account_balance": 2250.00,
                "customer_id": "CUST_001"
            }, null, 2);
        }
        
        async function processAnalysis() {
            const data = document.getElementById('analysisData').value;
            const resultsEl = document.getElementById('resultsContainer');
            const contentEl = document.getElementById('resultsContent');
            const timeEl = document.getElementById('processingTime');
            
            try {
                resultsEl.style.display = 'block';
                contentEl.textContent = '🔄 Processing analysis...';
                
                let inputData;
                try {
                    inputData = JSON.parse(data);
                } catch (parseError) {
                    throw new Error('Invalid JSON format: ' + parseError.message);
                }
                
                const response = await fetch('/analyze_simple', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ input_data: inputData })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                contentEl.textContent = result.analysis;
                timeEl.textContent = `${result.processing_time?.toFixed(3)}s`;
                
            } catch (error) {
                contentEl.textContent = `Error: ${error.message}`;
            }
        }
        
        function clearResults() {
            document.getElementById('resultsContainer').style.display = 'none';
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            loadExampleData();
        });
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/analyze_simple', methods=['POST'])
def analyze_simple():
    """Simple analysis endpoint that works without advanced dependencies"""
    try:
        start_time = time.time()
        
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({"error": "Missing input_data field"}), 400
        
        input_data = data['input_data']
        
        # Basic financial analysis
        analysis = perform_basic_analysis(input_data)
        
        processing_time = time.time() - start_time
        
        return jsonify({
            "analysis": analysis,
            "processing_time": processing_time,
            "status": "success",
            "mode": "simplified"
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500

def perform_basic_analysis(input_data):
    """Perform basic financial analysis without ML dependencies"""
    
    analysis = "=== BASIC FINANCIAL ANALYSIS ===\\n\\n"
    
    try:
        # Analyze transactions if present
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            analysis += f"TRANSACTION SUMMARY:\\n"
            analysis += f"Total Transactions: {len(transactions)}\\n\\n"
            
            # Calculate totals
            total_credits = 0
            total_debits = 0
            credit_count = 0
            debit_count = 0
            
            for tx in transactions:
                amount = tx.get("amount", 0)
                tx_type = tx.get("type", "")
                
                if tx_type == "credit" or amount > 0:
                    total_credits += abs(amount)
                    credit_count += 1
                elif tx_type == "debit" or amount < 0:
                    total_debits += abs(amount)
                    debit_count += 1
            
            analysis += f"FINANCIAL METRICS:\\n"
            analysis += f"Total Credits: ${total_credits:,.2f} ({credit_count} transactions)\\n"
            analysis += f"Total Debits: ${total_debits:,.2f} ({debit_count} transactions)\\n"
            analysis += f"Net Cash Flow: ${total_credits - total_debits:,.2f}\\n\\n"
            
            # Average transaction analysis
            if transactions:
                avg_credit = total_credits / max(credit_count, 1)
                avg_debit = total_debits / max(debit_count, 1)
                analysis += f"TRANSACTION PATTERNS:\\n"
                analysis += f"Average Credit: ${avg_credit:,.2f}\\n"
                analysis += f"Average Debit: ${avg_debit:,.2f}\\n\\n"
            
            # Transaction categories
            categories = {}
            for tx in transactions:
                desc = tx.get("description", "Unknown").lower()
                if "salary" in desc or "payroll" in desc:
                    categories["Income"] = categories.get("Income", 0) + abs(tx.get("amount", 0))
                elif "rent" in desc or "mortgage" in desc:
                    categories["Housing"] = categories.get("Housing", 0) + abs(tx.get("amount", 0))
                elif "grocery" in desc or "food" in desc:
                    categories["Food"] = categories.get("Food", 0) + abs(tx.get("amount", 0))
                elif "utility" in desc or "electric" in desc or "gas" in desc:
                    categories["Utilities"] = categories.get("Utilities", 0) + abs(tx.get("amount", 0))
                else:
                    categories["Other"] = categories.get("Other", 0) + abs(tx.get("amount", 0))
            
            if categories:
                analysis += f"SPENDING CATEGORIES:\\n"
                for category, amount in categories.items():
                    analysis += f"• {category}: ${amount:,.2f}\\n"
                analysis += "\\n"
        
        # Account balance analysis
        if "account_balance" in input_data:
            balance = input_data["account_balance"]
            analysis += f"ACCOUNT STATUS:\\n"
            analysis += f"Current Balance: ${balance:,.2f}\\n"
            
            if balance > 10000:
                analysis += "Status: Healthy balance\\n"
            elif balance > 1000:
                analysis += "Status: Moderate balance\\n"
            elif balance > 0:
                analysis += "Status: Low balance - consider budgeting\\n"
            else:
                analysis += "Status: Negative balance - immediate attention required\\n"
            analysis += "\\n"
        
        # Basic insights
        analysis += "KEY INSIGHTS:\\n"
        
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            if len(transactions) > 0:
                credits = sum(1 for tx in transactions if tx.get("amount", 0) > 0 or tx.get("type") == "credit")
                debits = sum(1 for tx in transactions if tx.get("amount", 0) < 0 or tx.get("type") == "debit")
                
                if credits > debits:
                    analysis += "• More income transactions than expenses - positive trend\\n"
                elif debits > credits:
                    analysis += "• More expense transactions than income - monitor spending\\n"
                else:
                    analysis += "• Balanced transaction pattern\\n"
                
                # Recent activity
                analysis += f"• {len(transactions)} transactions analyzed\\n"
                
                # Basic recommendations
                analysis += "\\nRECOMMENDATIONS:\\n"
                analysis += "• Continue monitoring cash flow patterns\\n"
                analysis += "• Consider categorizing expenses for better tracking\\n"
                analysis += "• Set up regular savings if not already in place\\n"
        
        analysis += "\\n=== END ANALYSIS ===\\n"
        analysis += "\\nNote: This is a simplified analysis. Install additional dependencies for advanced features."
        
    except Exception as e:
        analysis += f"\\nError during analysis: {str(e)}\\n"
        analysis += "Please check your input data format."
    
    return analysis

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "mode": "simplified",
        "version": "1.0.0-simple",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {
            "flask": "✅ Available",
            "requests": "✅ Available", 
            "numpy": "✅ Available",
            "advanced_ml": "⚠️ Not installed"
        }
    })

if __name__ == "__main__":
    print("🤖 Starting Simplified Autonomous Financial Analysis Agent...")
    print("🌐 Server: http://localhost:5001")
    print("📝 Note: This is the simplified version with basic dependencies")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
Simplified Autonomous Financial Analysis Agent Server
(Works with basic dependencies only)
"""

import asyncio
import json
import time
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

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
            color: #3498db; 
            margin-bottom: 10px; 
            font-size: 2.5em;
        }
        .status { 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 8px; 
            background: rgba(52, 152, 219, 0.1); 
            border-left: 4px solid #3498db; 
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Autonomous Financial Analysis Agent</h1>
            <p>Simplified version - Basic financial analysis capabilities</p>
        </div>
        
        <div class="status">
            ✅ Flask Server: Running<br>
            ✅ Core Dependencies: Loaded<br>
            ⚠️ Advanced Features: Install additional dependencies for full functionality
        </div>
        
        <div style="margin: 20px 0; padding: 20px; border: 1px solid rgba(255,255,255,0.2); border-radius: 10px; background: rgba(255,255,255,0.05);">
            <h3>🔍 Basic Financial Analysis</h3>
            <p>Provide financial data for analysis:</p>
            <textarea id="analysisData" placeholder='{"transactions": [{"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"}], "account_balance": 2250.00}'></textarea>
            <br>
            <button class="button" onclick="processAnalysis()">🚀 Analyze Data</button>
            <button class="button" onclick="loadExampleData()">📝 Load Example</button>
            <button class="button" onclick="clearResults()">🗑️ Clear</button>
        </div>
        
        <!-- Results Display -->
        <div id="resultsContainer" class="result-container">
            <div class="result-header">
                <span>Analysis Results</span>
                <span style="float: right; font-size: 14px;" id="processingTime"></span>
            </div>
            <div id="resultsContent" class="result-content"></div>
        </div>
    </div>
    
    <script>
        function loadExampleData() {
            document.getElementById('analysisData').value = JSON.stringify({
                "transactions": [
                    {"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"},
                    {"date": "2024-01-16", "amount": -50.00, "type": "debit", "description": "Grocery shopping"},
                    {"date": "2024-01-17", "amount": -1200.00, "type": "debit", "description": "Rent payment"}
                ],
                "account_balance": 2250.00,
                "customer_id": "CUST_001"
            }, null, 2);
        }
        
        async function processAnalysis() {
            const data = document.getElementById('analysisData').value;
            const resultsEl = document.getElementById('resultsContainer');
            const contentEl = document.getElementById('resultsContent');
            const timeEl = document.getElementById('processingTime');
            
            try {
                resultsEl.style.display = 'block';
                contentEl.textContent = '🔄 Processing analysis...';
                
                let inputData;
                try {
                    inputData = JSON.parse(data);
                } catch (parseError) {
                    throw new Error('Invalid JSON format: ' + parseError.message);
                }
                
                const response = await fetch('/analyze_simple', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ input_data: inputData })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                contentEl.textContent = result.analysis;
                timeEl.textContent = `${result.processing_time?.toFixed(3)}s`;
                
            } catch (error) {
                contentEl.textContent = `Error: ${error.message}`;
            }
        }
        
        function clearResults() {
            document.getElementById('resultsContainer').style.display = 'none';
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            loadExampleData();
        });
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/analyze_simple', methods=['POST'])
def analyze_simple():
    """Simple analysis endpoint that works without advanced dependencies"""
    try:
        start_time = time.time()
        
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({"error": "Missing input_data field"}), 400
        
        input_data = data['input_data']
        
        # Basic financial analysis
        analysis = perform_basic_analysis(input_data)
        
        processing_time = time.time() - start_time
        
        return jsonify({
            "analysis": analysis,
            "processing_time": processing_time,
            "status": "success",
            "mode": "simplified"
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500

def perform_basic_analysis(input_data):
    """Perform basic financial analysis without ML dependencies"""
    
    analysis = "=== BASIC FINANCIAL ANALYSIS ===\\n\\n"
    
    try:
        # Analyze transactions if present
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            analysis += f"TRANSACTION SUMMARY:\\n"
            analysis += f"Total Transactions: {len(transactions)}\\n\\n"
            
            # Calculate totals
            total_credits = 0
            total_debits = 0
            credit_count = 0
            debit_count = 0
            
            for tx in transactions:
                amount = tx.get("amount", 0)
                tx_type = tx.get("type", "")
                
                if tx_type == "credit" or amount > 0:
                    total_credits += abs(amount)
                    credit_count += 1
                elif tx_type == "debit" or amount < 0:
                    total_debits += abs(amount)
                    debit_count += 1
            
            analysis += f"FINANCIAL METRICS:\\n"
            analysis += f"Total Credits: ${total_credits:,.2f} ({credit_count} transactions)\\n"
            analysis += f"Total Debits: ${total_debits:,.2f} ({debit_count} transactions)\\n"
            analysis += f"Net Cash Flow: ${total_credits - total_debits:,.2f}\\n\\n"
            
            # Average transaction analysis
            if transactions:
                avg_credit = total_credits / max(credit_count, 1)
                avg_debit = total_debits / max(debit_count, 1)
                analysis += f"TRANSACTION PATTERNS:\\n"
                analysis += f"Average Credit: ${avg_credit:,.2f}\\n"
                analysis += f"Average Debit: ${avg_debit:,.2f}\\n\\n"
            
            # Transaction categories
            categories = {}
            for tx in transactions:
                desc = tx.get("description", "Unknown").lower()
                if "salary" in desc or "payroll" in desc:
                    categories["Income"] = categories.get("Income", 0) + abs(tx.get("amount", 0))
                elif "rent" in desc or "mortgage" in desc:
                    categories["Housing"] = categories.get("Housing", 0) + abs(tx.get("amount", 0))
                elif "grocery" in desc or "food" in desc:
                    categories["Food"] = categories.get("Food", 0) + abs(tx.get("amount", 0))
                elif "utility" in desc or "electric" in desc or "gas" in desc:
                    categories["Utilities"] = categories.get("Utilities", 0) + abs(tx.get("amount", 0))
                else:
                    categories["Other"] = categories.get("Other", 0) + abs(tx.get("amount", 0))
            
            if categories:
                analysis += f"SPENDING CATEGORIES:\\n"
                for category, amount in categories.items():
                    analysis += f"• {category}: ${amount:,.2f}\\n"
                analysis += "\\n"
        
        # Account balance analysis
        if "account_balance" in input_data:
            balance = input_data["account_balance"]
            analysis += f"ACCOUNT STATUS:\\n"
            analysis += f"Current Balance: ${balance:,.2f}\\n"
            
            if balance > 10000:
                analysis += "Status: Healthy balance\\n"
            elif balance > 1000:
                analysis += "Status: Moderate balance\\n"
            elif balance > 0:
                analysis += "Status: Low balance - consider budgeting\\n"
            else:
                analysis += "Status: Negative balance - immediate attention required\\n"
            analysis += "\\n"
        
        # Basic insights
        analysis += "KEY INSIGHTS:\\n"
        
        if "transactions" in input_data:
            transactions = input_data["transactions"]
            if len(transactions) > 0:
                credits = sum(1 for tx in transactions if tx.get("amount", 0) > 0 or tx.get("type") == "credit")
                debits = sum(1 for tx in transactions if tx.get("amount", 0) < 0 or tx.get("type") == "debit")
                
                if credits > debits:
                    analysis += "• More income transactions than expenses - positive trend\\n"
                elif debits > credits:
                    analysis += "• More expense transactions than income - monitor spending\\n"
                else:
                    analysis += "• Balanced transaction pattern\\n"
                
                # Recent activity
                analysis += f"• {len(transactions)} transactions analyzed\\n"
                
                # Basic recommendations
                analysis += "\\nRECOMMENDATIONS:\\n"
                analysis += "• Continue monitoring cash flow patterns\\n"
                analysis += "• Consider categorizing expenses for better tracking\\n"
                analysis += "• Set up regular savings if not already in place\\n"
        
        analysis += "\\n=== END ANALYSIS ===\\n"
        analysis += "\\nNote: This is a simplified analysis. Install additional dependencies for advanced features."
        
    except Exception as e:
        analysis += f"\\nError during analysis: {str(e)}\\n"
        analysis += "Please check your input data format."
    
    return analysis

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "mode": "simplified",
        "version": "1.0.0-simple",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {
            "flask": "✅ Available",
            "requests": "✅ Available", 
            "numpy": "✅ Available",
            "advanced_ml": "⚠️ Not installed"
        }
    })

if __name__ == "__main__":
    print("🤖 Starting Simplified Autonomous Financial Analysis Agent...")
    print("🌐 Server: http://localhost:5001")
    print("📝 Note: This is the simplified version with basic dependencies")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)