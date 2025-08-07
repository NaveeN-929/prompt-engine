#!/usr/bin/env python3
"""
Setup script for Autonomous Financial Analysis Agent
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Autonomous Financial Analysis Agent")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python dependencies"):
        print("\n💡 Try running this manually:")
        print(f"   {sys.executable} -m pip install -r requirements.txt")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('env.template'):
            try:
                with open('env.template', 'r') as template:
                    content = template.read()
                with open('.env', 'w') as env_file:
                    env_file.write(content)
                print("✅ Created .env file from template")
            except Exception as e:
                print(f"⚠️ Could not create .env file: {e}")
        else:
            print("⚠️ env.template not found, skipping .env creation")
    else:
        print("✅ .env file already exists")
    
    # Create logs directory
    try:
        os.makedirs('logs', exist_ok=True)
        print("✅ Created logs directory")
    except Exception as e:
        print(f"⚠️ Could not create logs directory: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("\n🚀 To start the agent:")
    print("   python run_agent.py")
    print("\n🧪 To test the agent:")
    print("   python test_agent.py")
    print("\n🌐 Web interface will be available at:")
    print("   http://localhost:5001")
    print("\n📝 Remember to:")
    print("   1. Edit .env file with your configuration")
    print("   2. Ensure your prompt-engine is running on port 5000")
    print("   3. Ensure Ollama/LLM service is available")

if __name__ == "__main__":
    main()
"""
Setup script for Autonomous Financial Analysis Agent
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Autonomous Financial Analysis Agent")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python dependencies"):
        print("\n💡 Try running this manually:")
        print(f"   {sys.executable} -m pip install -r requirements.txt")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('env.template'):
            try:
                with open('env.template', 'r') as template:
                    content = template.read()
                with open('.env', 'w') as env_file:
                    env_file.write(content)
                print("✅ Created .env file from template")
            except Exception as e:
                print(f"⚠️ Could not create .env file: {e}")
        else:
            print("⚠️ env.template not found, skipping .env creation")
    else:
        print("✅ .env file already exists")
    
    # Create logs directory
    try:
        os.makedirs('logs', exist_ok=True)
        print("✅ Created logs directory")
    except Exception as e:
        print(f"⚠️ Could not create logs directory: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("\n🚀 To start the agent:")
    print("   python run_agent.py")
    print("\n🧪 To test the agent:")
    print("   python test_agent.py")
    print("\n🌐 Web interface will be available at:")
    print("   http://localhost:5001")
    print("\n📝 Remember to:")
    print("   1. Edit .env file with your configuration")
    print("   2. Ensure your prompt-engine is running on port 5000")
    print("   3. Ensure Ollama/LLM service is available")

if __name__ == "__main__":
    main()