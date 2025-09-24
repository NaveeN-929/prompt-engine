"""
Smart installer for Response Validation LLM System
Handles version compatibility issues automatically
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors gracefully"""
    print(f"📦 {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ⚠️ Warning: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def install_package(package, fallback_versions=None):
    """Install a package with fallback versions"""
    if run_command(f"pip install {package}", f"Installing {package}"):
        return True
    
    if fallback_versions:
        for version in fallback_versions:
            print(f"   🔄 Trying fallback version: {version}")
            if run_command(f"pip install {version}", f"Installing {version}"):
                return True
    
    return False

def main():
    """Main installation function"""
    print("🚀 Installing Response Validation LLM System")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    # Install core packages
    core_packages = [
        ("Flask>=2.3.0", ["Flask==2.3.3", "Flask>=2.2.0", "Flask>=2.1.0"]),
        ("Flask-CORS>=4.0.0", ["Flask-CORS==4.0.0", "Flask-CORS>=3.0.0"]),
        ("requests>=2.30.0", ["requests==2.31.0", "requests>=2.28.0"]),
        ("numpy>=1.21.0", ["numpy>=1.21.0", "numpy>=1.19.0"]),
        ("pandas>=1.5.0", ["pandas>=1.5.0", "pandas>=1.3.0"]),
        ("python-dateutil>=2.8.0", ["python-dateutil>=2.8.0"])
    ]
    
    print("\n📦 Installing core packages...")
    for package, fallbacks in core_packages:
        if not install_package(package, fallbacks):
            print(f"⚠️ Warning: Could not install {package}")
    
    # Install vector database client
    print("\n🗄️ Installing vector database client...")
    qdrant_versions = [
        "qdrant-client>=1.7.1,<2.0.0",
        "qdrant-client>=1.7.1",
        "qdrant-client>=1.6.0",
        "qdrant-client>=1.5.0",
        "qdrant-client>=1.0.0"
    ]
    
    qdrant_installed = False
    for version in qdrant_versions:
        if install_package(version):
            qdrant_installed = True
            break
    
    if not qdrant_installed:
        print("⚠️ Warning: Could not install qdrant-client. Vector database features will be limited.")
    
    # Install optional NLP packages
    print("\n🧠 Installing optional NLP packages...")
    optional_packages = [
        ("sentence-transformers>=2.0.0", ["sentence-transformers>=2.0.0", "sentence-transformers>=1.0.0"]),
        ("transformers>=4.30.0", ["transformers>=4.30.0", "transformers>=4.20.0"])
    ]
    
    for package, fallbacks in optional_packages:
        if not install_package(package, fallbacks):
            print(f"⚠️ Note: {package} not installed - some features may be limited")
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    directories = [
        "training_data",
        "training_data/exemplary",
        "training_data/high_quality",
        "training_data/acceptable",
        "training_data/exports",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {directory}")
    
    # Test imports
    print("\n🧪 Testing imports...")
    test_imports = [
        ("flask", "Flask"),
        ("flask_cors", "Flask-CORS"),
        ("requests", "Requests"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas")
    ]
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"   ✅ {name} imported successfully")
        except ImportError:
            print(f"   ⚠️ {name} import failed")
    
    # Test optional imports
    optional_imports = [
        ("qdrant_client", "Qdrant Client"),
        ("sentence_transformers", "Sentence Transformers")
    ]
    
    for module, name in optional_imports:
        try:
            __import__(module)
            print(f"   ✅ {name} (optional) imported successfully")
        except ImportError:
            print(f"   ⚠️ {name} (optional) not available")
    
    print("\n🎉 Installation completed!")
    print("\nNext steps:")
    print("1. Ensure required services are running:")
    print("   - Ollama LLM service (for validation)")
    print("   - Qdrant vector database (optional)")
    print("2. Run setup: python setup.py")
    print("3. Start validation server: python validation_server.py")
    print("\nFor minimal installation issues, try:")
    print("   pip install -r requirements-minimal.txt")

if __name__ == "__main__":
    main()

