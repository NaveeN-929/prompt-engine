#!/usr/bin/env python3
"""
Prompting Engine Demo - Application Entry Point
"""

import argparse
from app.main import app

def main():
    parser = argparse.ArgumentParser(description="Prompting Engine Demo")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    print("🚀 Starting Prompting Engine Demo...")
    print(f"📡 Server will be available at: http://{args.host}:{args.port}")
    print(f"🌐 Web Interface: http://{args.host}:{args.port}/")
    print("=" * 60)
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )

if __name__ == "__main__":
    main() 