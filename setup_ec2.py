#!/usr/bin/env python3
"""
Setup script for configuring Ollama EC2 connection
"""

import os
import sys
import requests
import json

def test_ollama_connection(host, port, model):
    """Test connection to Ollama instance"""
    base_url = f"http://{host}:{port}"
    
    print(f"Testing connection to {base_url}...")
    
    try:
        # Test basic connection
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        if response.status_code == 200:
            print("Connection successful!")
            
            # Get available models
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            print(f"Available models: {', '.join(model_names)}")
            
            # Check if specified model is available
            if model in model_names:
                print(f"Model '{model}' is available")
                return True
            else:
                print(f"WARNING: Model '{model}' not found. Available models: {', '.join(model_names)}")
                return False
        else:
            print(f"Connection failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to Ollama. Please check:")
        print("   1. EC2 instance is running")
        print("   2. Ollama is installed and running on EC2")
        print("   3. Security group allows inbound traffic on port 11434")
        print("   4. Host and port are correct")
        return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def update_config(host, port, model):
    """Update the config.py file with new settings"""
    config_content = f'''"""
Configuration file for Prompting Engine Demo
"""

import os

# Ollama Configuration
# Update these values for your EC2 instance
OLLAMA_HOST = os.getenv('OLLAMA_HOST', '{host}')  # Your EC2 public IP or domain
OLLAMA_PORT = os.getenv('OLLAMA_PORT', '{port}')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', '{model}')

# Flask Configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '8000'))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

def print_config():
    """Print current configuration"""
    print("Current Configuration:")
    print(f"   Ollama Host: {{OLLAMA_HOST}}")
    print(f"   Ollama Port: {{OLLAMA_PORT}}")
    print(f"   Ollama Model: {{OLLAMA_MODEL}}")
    print(f"   Flask Host: {{FLASK_HOST}}")
    print(f"   Flask Port: {{FLASK_PORT}}")
    print(f"   Flask Debug: {{FLASK_DEBUG}}")
    print("=" * 50)

if __name__ == "__main__":
    print_config()
'''
    
    try:
        with open("config.py", "w", encoding='utf-8') as f:
            f.write(config_content)
        print("Configuration updated successfully!")
        return True
    except Exception as e:
        print(f"Failed to update configuration: {e}")
        return False

def main():
    """Main setup function"""
    print("Ollama EC2 Setup")
    print("=" * 50)
    
    # Get current configuration
    try:
        from config import OLLAMA_HOST, OLLAMA_PORT, OLLAMA_MODEL
        print(f"Current configuration:")
        print(f"   Host: {OLLAMA_HOST}")
        print(f"   Port: {OLLAMA_PORT}")
        print(f"   Model: {OLLAMA_MODEL}")
        print()
    except ImportError:
        print("No existing configuration found.")
        print()
    
    # Get new configuration
    print("Please enter your EC2 Ollama configuration:")
    
    host = input("EC2 Host (IP or domain): ").strip()
    if not host:
        print("ERROR: Host is required")
        return
    
    port = input("Port (default: 11434): ").strip() or "11434"
    model = input("Model name (default: llama2): ").strip() or "llama2"
    
    print()
    print(f"Testing connection with:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Model: {model}")
    print()
    
    # Test connection
    if test_ollama_connection(host, port, model):
        # Update configuration
        if update_config(host, port, model):
            print()
            print("Setup completed successfully!")
            print()
            print("Next steps:")
            print("1. Run the application: python run.py")
            print("2. Test the API: python test_api.py")
            print("3. Open web interface: http://localhost:8000")
        else:
            print("Setup failed - could not update configuration")
    else:
        print("Setup failed - could not connect to Ollama")
        print()
        print("Troubleshooting tips:")
        print("1. Make sure your EC2 instance is running")
        print("2. Install Ollama on EC2: curl -fsSL https://ollama.ai/install.sh | sh")
        print("3. Start Ollama on EC2: ollama serve")
        print("4. Pull a model on EC2: ollama pull llama2")
        print("5. Configure security group to allow inbound traffic on port 11434")
        print("6. Make sure you're using the correct public IP or domain")

if __name__ == "__main__":
    main() 