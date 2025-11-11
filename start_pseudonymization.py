#!/usr/bin/env python3
"""
Start Pseudonymization Service (Port 5003) - Flask
Quick launcher from project root
"""

import sys
import os

# Change to pseudonymization service directory
service_dir = os.path.join(os.path.dirname(__file__), 'pseudonymization-service')
os.chdir(service_dir)
sys.path.insert(0, service_dir)

if __name__ == "__main__":
    from app.main import app
    
    print("=" * 70)
    print("🔒 Starting Pseudonymization Service (Flask)")
    print("=" * 70)
    print("Host: 0.0.0.0")
    print("Port: 5003")
    print("Documentation: See README.md")
    print("=" * 70)
    print("\n✨ Features:")
    print("   - Automatic PII Detection (20+ types)")
    print("   - Type-specific Tokenization")
    print("   - Field-level Security")
    print("   - GDPR Compliant")
    print("\n💡 Press Ctrl+C to stop")
    print("=" * 70)
    
    app.run(
        host="0.0.0.0",
        port=5003,
        debug=False
    )

