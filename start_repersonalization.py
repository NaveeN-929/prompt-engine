#!/usr/bin/env python3
"""
Start Repersonalization Service (Port 5004) - Flask
Quick launcher from project root
"""

import sys
import os

# Change to repersonalization service directory
service_dir = os.path.join(os.path.dirname(__file__), 'repersonalization-service')
os.chdir(service_dir)
sys.path.insert(0, service_dir)

if __name__ == "__main__":
    from app.main import app
    
    print("=" * 70)
    print("🔓 Starting Repersonalization Service (Flask)")
    print("=" * 70)
    print("Host: 0.0.0.0")
    print("Port: 5004")
    print("Documentation: See README.md")
    print("=" * 70)
    print("\n✨ Features:")
    print("   - Secure Data Restoration")
    print("   - Integrity Verification")
    print("   - Bulk Repersonalization")
    print("   - GDPR Cleanup Support")
    print("\n💡 Press Ctrl+C to stop")
    print("⚠️  Note: Pseudonymization Service must be running (port 5003)")
    print("=" * 70)
    
    app.run(
        host="0.0.0.0",
        port=5004,
        debug=False
    )

