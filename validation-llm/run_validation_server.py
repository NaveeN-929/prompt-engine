#!/usr/bin/env python3
"""
Simple script to run the validation server with proper path setup
"""

import sys
import os

# Ensure we can import from the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Change to the validation-llm directory
os.chdir(current_dir)

# Now import and run the server
if __name__ == "__main__":
    try:
        from validation_server import start_validation_server
        start_validation_server()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the validation-llm directory")
        print("And that all required packages are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

