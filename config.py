"""
Configuration file for Prompting Engine Demo
"""

import os

# Ollama Configuration
# Update these values for your local or remote Ollama instance
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')  # Local Ollama instance
OLLAMA_PORT = os.getenv('OLLAMA_PORT', '11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral:latest')  # Mistral for efficient prompt generation

# Flask Configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Qdrant Configuration
QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', '6333'))
QDRANT_GRPC_PORT = int(os.getenv('QDRANT_GRPC_PORT', '6334'))

# PAM (Prompt Augmentation Model) Configuration
PAM_HOST = os.getenv('PAM_HOST', 'localhost')
PAM_PORT = int(os.getenv('PAM_PORT', '5005'))
ENABLE_PAM_AUGMENTATION = os.getenv('ENABLE_PAM_AUGMENTATION', 'true').lower() == 'true'

def print_config():
    """Print current configuration"""
    print("Current Configuration:")
    print(f"   Ollama Host: {OLLAMA_HOST}")
    print(f"   Ollama Port: {OLLAMA_PORT}")
    print(f"   Ollama Model: {OLLAMA_MODEL}")
    print(f"   Flask Host: {FLASK_HOST}")
    print(f"   Flask Port: {FLASK_PORT}")
    print(f"   Flask Debug: {FLASK_DEBUG}")
    print(f"   Qdrant Host: {QDRANT_HOST}")
    print(f"   Qdrant Port: {QDRANT_PORT}")
    print(f"   Qdrant gRPC Port: {QDRANT_GRPC_PORT}")
    print(f"   PAM Host: {PAM_HOST}")
    print(f"   PAM Port: {PAM_PORT}")
    print(f"   PAM Enabled: {ENABLE_PAM_AUGMENTATION}")
    print("=" * 50)

if __name__ == "__main__":
    print_config()
