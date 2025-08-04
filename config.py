"""
Configuration file for Prompting Engine Demo
"""

import os

# Ollama Configuration
# Update these values for your local or remote Ollama instance
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')  # Local Ollama instance
OLLAMA_PORT = os.getenv('OLLAMA_PORT', '11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')  # Llama 3.1 8B for financial analysis

# Flask Configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

def print_config():
    """Print current configuration"""
    print("Current Configuration:")
    print(f"   Ollama Host: {OLLAMA_HOST}")
    print(f"   Ollama Port: {OLLAMA_PORT}")
    print(f"   Ollama Model: {OLLAMA_MODEL}")
    print(f"   Flask Host: {FLASK_HOST}")
    print(f"   Flask Port: {FLASK_PORT}")
    print(f"   Flask Debug: {FLASK_DEBUG}")
    print("=" * 50)

if __name__ == "__main__":
    print_config()
