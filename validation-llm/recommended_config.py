
# Recommended model configuration based on available models:

VALIDATION_LLM_CONFIG = {
    "primary_validator": {
        "model_name": "mistral:latest",
        "host": "http://localhost:11434",
        "max_tokens": 2000,
        "temperature": 0.1,
        "timeout": 30
    },
    "speed_validator": {
        "model_name": "mistral:latest",
        "host": "http://localhost:11434", 
        "max_tokens": 1000,
        "temperature": 0.2,
        "timeout": 15
    }
}
