# Prompting Engine Demo System

A local demo of a comprehensive Prompting Engine system with template management, prompt generation, LLM integration, feedback collection, and API interface.

## Features

- **Prompt Template System**: Define and manage prompt templates with parameter validation
- **Prompt Generator**: Match requests to templates and render complete prompts
- **LLM Interface**: Real Ollama integration (requires Ollama to be available)
- **ML Feedback System**: Log interactions and provide optimization suggestions
- **API Interface**: Flask backend with CORS support
- **Web Interface**: Simple HTML/JS frontend for testing

## Project Structure

```
prompt-engine/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Flask application
│   ├── models.py               # Pydantic models
│   ├── templates/
│   │   ├── __init__.py
│   │   ├── base.py            # Base template classes
│   │   ├── customer_service.py # Customer service templates
│   │   └── data_analysis.py   # Data analysis templates
│   ├── generators/
│   │   ├── __init__.py
│   │   └── prompt_generator.py # Prompt generation logic
│   ├── llm/
│   │   ├── __init__.py
│   │   └── mock_llm.py        # Ollama LLM interface
│   ├── feedback/
│   │   ├── __init__.py
│   │   └── feedback_system.py # Feedback and optimization
│   └── static/
│       ├── index.html          # Web interface
│       └── script.js           # Frontend JavaScript
├── config.py                   # Configuration settings
├── requirements.txt
├── run.py                      # Application entry point
├── setup_ec2.py               # EC2 Ollama setup script
├── test_api.py                 # API test script
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Ollama running on EC2 (required)

### Installation

1. **Clone or create the project directory**
   ```bash
   mkdir prompt-engine
   cd prompt-engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Ollama (Required)**
   
   Set up your EC2 Ollama connection:
   ```bash
   python setup_ec2.py
   ```
   
   Or manually edit `config.py`:
   ```python
   OLLAMA_HOST = "your-ec2-public-ip.compute.amazonaws.com"
   OLLAMA_PORT = "11434"
   OLLAMA_MODEL = "llama2"
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - API: http://localhost:8000
   - Web Interface: http://localhost:8000/
   - Health Check: http://localhost:8000/health

## Ollama EC2 Setup

### On your EC2 instance:

1. **Install Ollama**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Start Ollama**
   ```bash
   ollama serve
   ```

3. **Pull a model**
   ```bash
   ollama pull llama2
   ```

4. **Configure Security Group**
   - Add inbound rule for port 11434 (TCP)
   - Source: 0.0.0.0/0 (or your specific IP)

### On your local machine:

1. **Run the setup script**
   ```bash
   python setup_ec2.py
   ```

2. **Enter your EC2 details**
   - Host: Your EC2 public IP or domain
   - Port: 11434 (default)
   - Model: llama2 (or your preferred model)

## API Endpoints

### POST /generate
Generate a prompt and get LLM response.

**Request Body:**
```json
{
  "context": "customer_service",
  "data_type": "complaint",
  "input_data": {
    "customer_name": "John Doe",
    "issue_description": "Product arrived damaged",
    "order_number": "ORD-12345"
  }
}
```

**Response:**
```json
{
  "prompt": "Generated prompt text...",
  "response": "LLM response text...",
  "tokens_used": 150,
  "template_used": "customer_service_complaint"
}
```

### GET /feedback
Get optimization suggestions based on interaction history.

**Response:**
```json
{
  "suggestions": [
    "Consider adding more context about product details",
    "Template 'customer_service_complaint' shows high success rate"
  ],
  "interaction_count": 25
}
```

### GET /templates
List all available prompt templates.

### GET /health
Health check with Ollama connection status.

### GET /ollama/models
List available Ollama models.

### GET /ollama/info
Get current Ollama model information.

## Example Usage

### Using curl

```bash
# Generate a customer service response
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "customer_service",
    "data_type": "complaint",
    "input_data": {
      "customer_name": "Jane Smith",
      "issue_description": "Late delivery",
      "order_number": "ORD-67890"
    }
  }'

# Get feedback suggestions
curl -X GET "http://localhost:8000/feedback"

# Check Ollama models
curl -X GET "http://localhost:8000/ollama/models"
```

### Using Python requests

```python
import requests

# Generate prompt and response
response = requests.post("http://localhost:8000/generate", json={
    "context": "data_analysis",
    "data_type": "csv_analysis",
    "input_data": {
        "data_description": "Sales data for Q1 2024",
        "analysis_goal": "Identify top performing products",
        "data_columns": "Product, Sales, Revenue, Region",
        "specific_questions": "Which products have the highest revenue?"
    }
})

print(response.json())

# Get feedback
feedback = requests.get("http://localhost:8000/feedback")
print(feedback.json())
```

## Template System

The system includes predefined templates for:

1. **Customer Service**
   - Complaint handling
   - Refund requests
   - Product inquiries

2. **Data Analysis**
   - CSV data analysis
   - Statistical summaries
   - Trend identification

Each template includes:
- Parameter validation rules
- Default values
- Context-specific instructions
- Response formatting guidelines

## LLM Integration

The system supports:
- **Real Ollama**: Connect to your EC2 Ollama instance
- **Model Management**: List and switch between available models
- **Connection Monitoring**: Health checks for Ollama status

## Feedback System

The feedback system provides:
- Interaction logging
- Performance metrics
- Template effectiveness analysis
- Optimization suggestions
- Usage statistics

## Development

### Adding New Templates

1. Create a new template file in `app/templates/`
2. Inherit from `BaseTemplate`
3. Define parameters and validation rules
4. Register the template in the generator

### Extending the LLM Interface

1. Modify `app/llm/mock_llm.py`
2. Add new model support
3. Implement additional token counting logic

### Customizing the API

1. Add new endpoints in `app/main.py`
2. Create corresponding models in `app/models.py`
3. Update the web interface as needed

## Troubleshooting

### Common Issues

1. **Ollama connection failed**: Check EC2 security group and Ollama service - the system requires Ollama to be available
2. **Port already in use**: Change the port in `config.py`
3. **Import errors**: Ensure all dependencies are installed
4. **CORS issues**: Check browser console for CORS errors

### Debug Mode

Run with debug logging:
```bash
python run.py --debug
```

### Environment Variables

You can override configuration using environment variables:
```bash
export OLLAMA_HOST="your-ec2-ip"
export OLLAMA_PORT="11434"
export OLLAMA_MODEL="llama2"
python run.py
```

## License

This is a demo project for educational purposes. 