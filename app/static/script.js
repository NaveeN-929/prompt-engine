// Prompting Engine Demo - Frontend JavaScript

// API base URL
const API_BASE = window.location.origin;

// Global variables for agentic functionality
let lastGenerationResult = null;

// Example input data for banking templates
const bankingExampleInputs = {
    'core_banking_transaction_history': {
        "transactions": [
            {"date": "2024-01-15", "amount": 1500.00, "type": "credit", "description": "Salary deposit"},
            {"date": "2024-01-16", "amount": -50.00, "type": "debit", "description": "Grocery shopping"},
            {"date": "2024-01-17", "amount": -1200.00, "type": "debit", "description": "Rent payment"}
        ]
    },
    'lending_decision_cash_flow': {
        "monthly_data": [
            {"month": "Jan", "revenue": 45000, "expenses": 35000},
            {"month": "Feb", "revenue": 48000, "expenses": 37000},
            {"month": "Mar", "revenue": 52000, "expenses": 39000}
        ]
    },
    'loan_approval_credit': {
        "borrower_name": "John Smith",
        "credit_score": 720,
        "annual_income": 85000,
        "debt_to_income_ratio": 0.35,
        "loan_amount": 250000
    },
    'card_data_transactions': {
        "card_transactions": [
            {"merchant": "Amazon", "amount": 129.99, "category": "Online Shopping"},
            {"merchant": "Shell", "amount": 45.00, "category": "Gas Station"},
            {"merchant": "Starbucks", "amount": 8.50, "category": "Coffee Shop"}
        ]
    }
};

// Example input data for different templates
const exampleInputs = {
    'customer_service_complaint': {
        "customer_name": "John Doe",
        "issue_description": "Product arrived damaged",
        "order_number": "ORD-12345",
        "product_name": "Wireless Headphones"
    },
    'customer_service_refund': {
        "customer_name": "Jane Smith",
        "refund_reason": "Changed mind about purchase",
        "order_number": "ORD-67890",
        "purchase_date": "2024-01-15",
        "product_name": "Smart Watch"
    },
    'customer_service_product_inquiry': {
        "customer_name": "Mike Johnson",
        "product_name": "Gaming Laptop",
        "inquiry_type": "specifications",
        "specific_question": "What are the graphics card options?"
    },
    'data_analysis_csv': {
        "data_description": "Sales data for Q1 2024",
        "analysis_goal": "Identify top performing products",
        "data_columns": "Product, Sales, Revenue, Region",
        "specific_questions": "Which products have the highest revenue?"
    },
    'data_analysis_statistical': {
        "data_description": "Customer satisfaction scores",
        "analysis_type": "descriptive statistics",
        "variables": "Satisfaction Score, Response Time, Support Quality",
        "sample_size": "1000 responses"
    },
    'data_analysis_trend': {
        "data_description": "Monthly sales data for 2023",
        "trend_period": "12 months",
        "key_metrics": "Revenue, Units Sold, Customer Acquisition",
        "seasonality": "Quarterly patterns"
    }
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    toggleGenerationOptions(); // Initialize generation-specific fields
    updateExampleInput();
});

// Setup event listeners
function setupEventListeners() {
    // Form submission handler
    document.getElementById('generateForm').addEventListener('submit', function(e) {
        e.preventDefault();
        generatePrompt();
    });
}

// Toggle generation options based on type
function toggleGenerationOptions() {
    const type = document.getElementById('generationType').value;
    const reasoningOptions = document.getElementById('reasoningOptions');
    const hintFields = document.getElementById('hintFields');
    
    // Show reasoning steps only for reasoning type
    reasoningOptions.style.display = type === 'reasoning' ? 'block' : 'none';
    
    // Hide hint fields for autonomous mode (it should auto-detect everything)
    hintFields.style.display = type === 'autonomous' ? 'none' : 'block';
    
    updateExampleInput();
}

// Update example input based on current selections
function updateExampleInput() {
    const inputDataField = document.getElementById('inputData');
    
    // Always use a default banking example since we're in pure agentic mode
    inputDataField.value = JSON.stringify(bankingExampleInputs['core_banking_transaction_history'], null, 2);
}

// Update example input based on selected template
function updateExampleInput() {
    const context = document.getElementById('context').value;
    const dataType = document.getElementById('dataType').value;
    const inputDataTextarea = document.getElementById('inputData');
    
    if (context && dataType) {
        const templateKey = `${context}_${dataType}`;
        const example = exampleInputs[templateKey];
        
        if (example) {
            inputDataTextarea.value = JSON.stringify(example, null, 2);
        } else {
            inputDataTextarea.value = '{"key": "value"}';
        }
    }
}

// Generate prompt and get response (Pure Agentic)
async function generatePrompt() {
    const generationType = document.getElementById('generationType').value;
    const inputDataText = document.getElementById('inputData').value;
    
    // Validate input data
    if (!inputDataText) {
        showError('Please provide input data.');
        return;
    }
    
    // Parse JSON input data
    let inputData;
    try {
        inputData = JSON.parse(inputDataText);
    } catch (e) {
        showError('Invalid JSON in input data. Please check the format.');
        return;
    }
    
    // Prepare request payload for pure agentic generation
    let requestBody = { 
        input_data: inputData,
        generation_type: generationType
    };
    
    // Add optional hints if not autonomous mode
    if (generationType !== 'autonomous') {
        const contextHint = document.getElementById('contextHint').value;
        const dataTypeHint = document.getElementById('dataTypeHint').value;
        
        if (contextHint) requestBody.context = contextHint;
        if (dataTypeHint) requestBody.data_type = dataTypeHint;
    }
    
    // Add reasoning steps if reasoning mode
    if (generationType === 'reasoning') {
        const steps = document.getElementById('reasoningSteps').value;
        requestBody.reasoning_steps = parseInt(steps);
    }
    
    // Show loading state
    showLoading(true);
    hideResults();
    
    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to generate prompt');
        }
        
        const result = await response.json();
        lastGenerationResult = { result, inputData, generationType };
        displayResults(result);
        showSuccess(`🚀 ${result.vector_accelerated ? 'Vector-accelerated' : 'AI-powered'} prompt generated successfully!`);
        
    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Display results
function displayResults(result) {
    document.getElementById('promptResult').textContent = result.prompt;
    document.getElementById('responseResult').textContent = result.response;
    document.getElementById('tokensUsed').textContent = result.tokens_used;
    document.getElementById('processingTime').textContent = `${result.processing_time.toFixed(2)}s`;
    document.getElementById('templateUsed').textContent = result.template_used;
    
    document.getElementById('results').style.display = 'block';
}

// Load feedback and analytics
async function loadFeedback() {
    const resultsDiv = document.getElementById('feedbackResults');
    resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading feedback...</p></div>';
    
    try {
        const response = await fetch(`${API_BASE}/feedback`);
        
        if (!response.ok) {
            throw new Error('Failed to load feedback');
        }
        
        const feedback = await response.json();
        displayFeedback(feedback);
        
    } catch (error) {
        resultsDiv.innerHTML = `<div class="error">Error loading feedback: ${error.message}</div>`;
    }
}

// Display feedback results
function displayFeedback(feedback) {
    const resultsDiv = document.getElementById('feedbackResults');
    
    let html = '<div class="result-section">';
    html += '<h3>📊 Performance Metrics</h3>';
    html += '<div class="metrics">';
    html += `<div class="metric"><div class="metric-value">${feedback.interaction_count}</div><div class="metric-label">Total Interactions</div></div>`;
    
    if (feedback.performance_metrics) {
        const metrics = feedback.performance_metrics;
        if (metrics.recent_interactions !== undefined) {
            html += `<div class="metric"><div class="metric-value">${metrics.recent_interactions}</div><div class="metric-label">Recent Interactions</div></div>`;
        }
        if (metrics.template_diversity !== undefined) {
            html += `<div class="metric"><div class="metric-value">${metrics.template_diversity}</div><div class="metric-label">Template Diversity</div></div>`;
        }
        if (metrics.avg_tokens_per_interaction !== undefined) {
            html += `<div class="metric"><div class="metric-value">${metrics.avg_tokens_per_interaction.toFixed(0)}</div><div class="metric-label">Avg Tokens</div></div>`;
        }
    }
    html += '</div></div>';
    
    html += '<div class="result-section">';
    html += '<h3>💡 Optimization Suggestions</h3>';
    html += '<div class="result-content">';
    
    if (feedback.suggestions && feedback.suggestions.length > 0) {
        feedback.suggestions.forEach((suggestion, index) => {
            html += `${index + 1}. ${suggestion}\n\n`;
        });
    } else {
        html += 'No suggestions available yet. Start using the system to get personalized recommendations.';
    }
    
    html += '</div></div>';
    
    resultsDiv.innerHTML = html;
}

// Load templates
async function loadTemplates() {
    const resultsDiv = document.getElementById('templatesResults');
    resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading templates...</p></div>';
    
    try {
        const response = await fetch(`${API_BASE}/templates`);
        
        if (!response.ok) {
            throw new Error('Failed to load templates');
        }
        
        const templates = await response.json();
        displayTemplates(templates);
        
    } catch (error) {
        resultsDiv.innerHTML = `<div class="error">Error loading templates: ${error.message}</div>`;
    }
}

// Display templates
function displayTemplates(templates) {
    const resultsDiv = document.getElementById('templatesResults');
    
    let html = '<div class="result-section">';
    html += '<h3>📋 Available Templates</h3>';
    
    if (templates.templates && templates.templates.length > 0) {
        templates.templates.forEach(template => {
            html += '<div style="margin-bottom: 20px; padding: 15px; border: 1px solid #e1e5e9; border-radius: 8px;">';
            html += `<h4 style="color: #667eea; margin-bottom: 10px;">${template.name}</h4>`;
            html += `<p><strong>Category:</strong> ${template.category}</p>`;
            html += `<p><strong>Description:</strong> ${template.description}</p>`;
            html += `<p><strong>Parameters:</strong> ${template.parameters.join(', ')}</p>`;
            
            if (template.examples && template.examples.length > 0) {
                html += '<p><strong>Example:</strong></p>';
                html += '<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-size: 12px;">';
                html += JSON.stringify(template.examples[0], null, 2);
                html += '</pre>';
            }
            
            html += '</div>';
        });
    } else {
        html += '<p>No templates available.</p>';
    }
    
    html += '</div>';
    resultsDiv.innerHTML = html;
}

// Tab switching functionality
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
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Add active class to clicked tab
    event.target.classList.add('active');
}

// Utility functions
function showLoading(show) {
    const loading = document.getElementById('loading');
    const generateBtn = document.getElementById('generateBtn');
    
    if (show) {
        loading.style.display = 'block';
        generateBtn.disabled = true;
    } else {
        loading.style.display = 'none';
        generateBtn.disabled = false;
    }
}

function hideResults() {
    document.getElementById('results').style.display = 'none';
}

function showError(message) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<div class="error">${message}</div>`;
    resultsDiv.style.display = 'block';
}

function showSuccess(message) {
    // You could add a success notification here
    console.log(message);
}

// Health check on page load
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            console.log('✅ API is healthy');
        } else {
            console.warn('⚠️ API health check failed');
        }
    } catch (error) {
        console.error('❌ API health check error:', error);
    }
}

// Run health check when page loads
checkHealth(); 