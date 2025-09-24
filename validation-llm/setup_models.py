#!/usr/bin/env python3
"""
Setup script to pull required LLM models for validation system
"""

import subprocess
import sys
import requests
import json
import time
from typing import List, Dict, Any

def run_command(command: str, description: str = "") -> bool:
    """Run a command and return success status"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_ollama_running() -> bool:
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_available_models() -> List[str]:
    """Get list of available models in Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            return [model["name"] for model in models_data.get("models", [])]
        return []
    except:
        return []

def pull_model(model_name: str, use_docker: bool = False) -> bool:
    """Pull a model using Ollama (CLI or Docker)"""
    print(f"📥 Pulling model: {model_name}")
    print(f"   This may take several minutes...")
    
    try:
        if use_docker:
            # Use docker exec to run ollama pull inside the container
            # First, try to find the ollama container
            container_name = find_ollama_container()
            if not container_name:
                print(f"   ❌ Could not find running Ollama container")
                return False
            
            command = f"docker exec {container_name} ollama pull {model_name}"
        else:
            # Use direct ollama command
            command = f"ollama pull {model_name}"
        
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=1800  # 30 minute timeout
        )
        
        if result.returncode == 0:
            print(f"   ✅ Successfully pulled {model_name}")
            return True
        else:
            print(f"   ❌ Failed to pull {model_name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout pulling {model_name} (took more than 30 minutes)")
        return False
    except Exception as e:
        print(f"   ❌ Error pulling {model_name}: {e}")
        return False

def find_ollama_container() -> str:
    """Find the running Ollama container name"""
    try:
        # Look for running containers with ollama in the name or image
        result = subprocess.run(
            "docker ps --format \"{{.Names}} {{.Image}}\"", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'ollama' in line.lower():
                    container_name = line.split()[0]
                    print(f"   🐳 Found Ollama container: {container_name}")
                    return container_name
        
        return None
        
    except Exception as e:
        print(f"   ❌ Error finding Ollama container: {e}")
        return None

def detect_ollama_setup() -> Dict[str, Any]:
    """Detect how Ollama is set up (Docker or CLI)"""
    setup_info = {
        "method": None,
        "available": False,
        "container_name": None
    }
    
    # First, try direct ollama command
    try:
        result = subprocess.run("ollama --version", shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            setup_info["method"] = "cli"
            setup_info["available"] = True
            print("🔍 Detected Ollama CLI installation")
            return setup_info
    except:
        pass
    
    # If CLI not available, check for Docker container
    container_name = find_ollama_container()
    if container_name:
        setup_info["method"] = "docker"
        setup_info["available"] = True
        setup_info["container_name"] = container_name
        print(f"🐳 Detected Ollama Docker container: {container_name}")
        return setup_info
    
    print("❌ Could not detect Ollama installation (neither CLI nor Docker)")
    return setup_info

def setup_validation_models():
    """Setup the required models for validation system"""
    print("🚀 Setting up Validation LLM Models")
    print("=" * 50)
    
    # Detect Ollama setup method
    print("🔍 Detecting Ollama installation...")
    ollama_setup = detect_ollama_setup()
    
    if not ollama_setup["available"]:
        print("❌ Ollama is not available!")
        print("Please ensure Ollama is running:")
        print("   Docker: docker run -d -p 11434:11434 ollama/ollama")
        print("   CLI: ollama serve")
        return False
    
    # Check if Ollama API is responding
    print("🔍 Checking Ollama service...")
    if not check_ollama_running():
        print("❌ Ollama API is not responding!")
        print(f"Detected {ollama_setup['method']} setup but API not accessible")
        return False
    
    print(f"✅ Ollama service is running ({ollama_setup['method']} method)")
    
    # Get current models
    print("\n📋 Checking available models...")
    available_models = get_available_models()
    print(f"Currently available models: {len(available_models)}")
    for model in available_models:
        print(f"   • {model}")
    
    # Required models for validation
    required_models = [
        "llama3.2:3b",  # Primary validation model
        "llama3.2:1b"   # Speed validation model
    ]
    
    # Alternative models if the above aren't available
    alternative_models = [
        "llama3.1:8b",  # Fallback to main project model
        "llama2:7b",    # Another fallback
        "phi3:3.8b"     # Smaller alternative
    ]
    
    print(f"\n🎯 Required models for validation:")
    for model in required_models:
        print(f"   • {model}")
    
    # Check which models need to be pulled
    models_to_pull = []
    for model in required_models:
        if model not in available_models:
            models_to_pull.append(model)
        else:
            print(f"✅ {model} already available")
    
    # Pull missing models
    if models_to_pull:
        print(f"\n📥 Need to pull {len(models_to_pull)} models:")
        for model in models_to_pull:
            print(f"   • {model}")
        
        print("\n⚠️ Warning: Downloading models may take significant time and bandwidth")
        print("Each model can be several GB in size")
        
        # Ask for confirmation
        try:
            confirm = input("\nProceed with model download? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("❌ Model setup cancelled")
                return False
        except KeyboardInterrupt:
            print("\n❌ Setup interrupted")
            return False
        
        # Pull each required model using detected method
        use_docker = ollama_setup["method"] == "docker"
        success_count = 0
        for model in models_to_pull:
            if pull_model(model, use_docker=use_docker):
                success_count += 1
            else:
                print(f"⚠️ Failed to pull {model}, will try alternatives")
        
        if success_count == 0:
            print("\n⚠️ No required models could be pulled, trying alternatives...")
            
            # Try alternative models using detected method
            for alt_model in alternative_models:
                if alt_model not in available_models:
                    if pull_model(alt_model, use_docker=use_docker):
                        print(f"✅ Successfully pulled alternative model: {alt_model}")
                        print("💡 You may need to update config.py to use this model")
                        break
                else:
                    print(f"✅ Alternative model {alt_model} already available")
                    break
    
    # Final check
    print("\n🔍 Final model check...")
    final_models = get_available_models()
    
    validation_ready = False
    for model in required_models:
        if model in final_models:
            print(f"✅ Validation model ready: {model}")
            validation_ready = True
            break
    
    if not validation_ready:
        for model in alternative_models:
            if model in final_models:
                print(f"✅ Alternative validation model available: {model}")
                print(f"💡 Update config.py to use: {model}")
                validation_ready = True
                break
    
    if validation_ready:
        print("\n🎉 Model setup completed successfully!")
        print("\nNext steps:")
        print("1. Verify your config.py has the correct model names")
        print("2. Start the validation server: python simple_server.py")
        print("3. Test the validation endpoint")
        return True
    else:
        print("\n❌ Model setup failed")
        print("Please check your internet connection and Ollama installation")
        return False

def create_model_config():
    """Create a model configuration file"""
    print("\n📄 Creating model configuration...")
    
    available_models = get_available_models()
    
    # Find best models for validation
    primary_model = None
    speed_model = None
    
    # Preferred models in order of preference
    preferred_primary = ["llama3.2:3b", "llama3.1:8b", "llama2:7b", "phi3:3.8b"]
    preferred_speed = ["llama3.2:1b", "llama3.2:3b", "phi3:3.8b"]
    
    for model in preferred_primary:
        if model in available_models:
            primary_model = model
            break
    
    for model in preferred_speed:
        if model in available_models:
            speed_model = model
            break
    
    if primary_model and speed_model:
        config_update = f"""
# Recommended model configuration based on available models:

VALIDATION_LLM_CONFIG = {{
    "primary_validator": {{
        "model_name": "{primary_model}",
        "host": "http://localhost:11434",
        "max_tokens": 2000,
        "temperature": 0.1,
        "timeout": 30
    }},
    "speed_validator": {{
        "model_name": "{speed_model}",
        "host": "http://localhost:11434", 
        "max_tokens": 1000,
        "temperature": 0.2,
        "timeout": 15
    }}
}}
"""
        
        with open("recommended_config.py", "w") as f:
            f.write(config_update)
        
        print(f"✅ Created recommended_config.py")
        print(f"   Primary model: {primary_model}")
        print(f"   Speed model: {speed_model}")

def main():
    """Main setup function"""
    try:
        success = setup_validation_models()
        
        if success:
            create_model_config()
            print("\n🎉 Setup completed successfully!")
        else:
            print("\n❌ Setup failed - please check the errors above")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
