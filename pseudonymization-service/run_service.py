#!/usr/bin/env python3
"""
Run Pseudonymization Service (Flask)
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
    print("🔒 Starting Pseudonymization Service (Flask)")
    print("=" * 70)
    print(f"Host: {settings.HOST}")
    print(f"Port: {settings.PORT}")
    print(f"Documentation: See README.md")
    print("=" * 70)
    
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    )

