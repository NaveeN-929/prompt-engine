#!/usr/bin/env python3
"""
Run PAM (Prompt Augmentation Model) Service
Start the service directly without Docker
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from app.main import app
    from app.config import settings
    
    print("=" * 70)
    print("🔍 Starting PAM (Prompt Augmentation Model) Service")
    print("=" * 70)
    print(f"Host: {settings.HOST}")
    print(f"Port: {settings.PORT}")
    print(f"Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
    print(f"Ollama: {settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}")
    print(f"Web Scraping: {'Enabled' if settings.ENABLE_WEB_SCRAPING else 'Disabled'}")
    print(f"LLM Research: {'Enabled' if settings.ENABLE_LLM_RESEARCH else 'Disabled'}")
    print(f"Caching: {'Enabled' if settings.ENABLE_CACHING else 'Disabled'}")
    print("=" * 70)
    
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    )

