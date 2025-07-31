#!/usr/bin/env python3
"""
Quick Start Script for Prompting Engine Demo
"""

import subprocess
import sys
import time
import os
import requests

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ is required.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting Prompting Engine Demo server...")
    
    # Check if run.py exists
    if not os.path.exists("run.py"):
        print("❌ run.py not found")
        return False
    
    # Start server in background
    try:
        process = subprocess.Popen(
            [sys.executable, "run.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                print("📡 Server is running at: http://localhost:8000")
                print("📚 API Documentation: http://localhost:8000/docs")
                print("🌐 Web Interface: http://localhost:8000/")
                print("\n" + "=" * 60)
                print("🎉 Prompting Engine Demo is ready!")
                print("=" * 60)
                return process
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                process.terminate()
                return None
        except requests.exceptions.RequestException:
            print("❌ Server health check failed - server may not be running")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def run_tests():
    """Run API tests"""
    print("\n🧪 Running API tests...")
    
    if not os.path.exists("test_api.py"):
        print("❌ test_api.py not found")
        return False
    
    return run_command(f"{sys.executable} test_api.py", "Running API tests")

def main():
    """Main quick start function"""
    print("🚀 Prompting Engine Demo - Quick Start")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies. Please check the error messages above.")
        sys.exit(1)
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("\n❌ Failed to start server. Please check the error messages above.")
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    print("\n🎯 Next steps:")
    print("1. Open your browser and go to: http://localhost:8000")
    print("2. Try the web interface to generate prompts")
    print("3. Check the API documentation at: http://localhost:8000/docs")
    print("4. Press Ctrl+C to stop the server when done")
    
    try:
        # Keep the server running
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        server_process.terminate()
        print("✅ Server stopped")

if __name__ == "__main__":
    main() 