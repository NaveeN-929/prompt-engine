#!/usr/bin/env python3
"""
Docker-specific setup script for Ollama models - Prompt Engine
"""

import subprocess
import sys
import requests
import json
import time
from typing import List, Dict, Any

def find_ollama_container() -> str:
    """Find the running Ollama container"""
    try:
        print("🔍 Looking for Ollama container...")
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
        
        print("   ❌ No Ollama container found")
        return None
        
    except Exception as e:
        print(f"   ❌ Error finding container: {e}")
        return None

def get_available_models() -> List[str]:
    """Get list of available models from Ollama API"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            return [model["name"] for model in models_data.get("models", [])]
        return []
    except:
        return []

def pull_model_docker(container_name: str, model_name: str) -> bool:
    """Pull a model using docker exec"""
    print(f"📥 Pulling {model_name} in container {container_name}")
    print("   This may take several minutes...")
    
    try:
        command = f"docker exec {container_name} ollama pull {model_name}"
        
        # Run the command with real-time output
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"   {output.strip()}")
        
        rc = process.poll()
        if rc == 0:
            print(f"   ✅ Successfully pulled {model_name}")
            return True
        else:
            stderr = process.stderr.read()
            print(f"   ❌ Failed to pull {model_name}")
            if stderr:
                print(f"   Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error pulling {model_name}: {e}")
        return False

def main():
    """Main setup function for Docker-based Ollama - Prompt Engine"""
    print("🚀 Prompt Engine Docker Ollama Model Setup")
    print("=" * 50)
    
    # Find Ollama container
    container_name = find_ollama_container()
    if not container_name:
        print("\n❌ Could not find running Ollama container!")
        print("\nPlease ensure Ollama is running in Docker:")
        print("   docker run -d -p 11434:11434 --name ollama ollama/ollama")
        print("   # or")
        print("   docker-compose up ollama")
        return False
    
    # Check API accessibility
    print("\n🔍 Testing Ollama API...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            print("   ✅ Ollama API is accessible")
        else:
            print(f"   ❌ Ollama API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot reach Ollama API: {e}")
        print("   Make sure port 11434 is exposed: docker run -p 11434:11434 ...")
        return False
    
    # Get current models
    print("\n📋 Checking current models...")
    current_models = get_available_models()
    print(f"   Currently available: {len(current_models)} models")
    for model in current_models:
        print(f"      • {model}")
    
    # Define required models for Prompt Engine
    required_models = ["mistral:latest"]  # Primary model for prompt engine
    alternative_models = ["llama3.1:8b", "llama3.2:3b", "phi3:3.8b"]
    
    print(f"\n🎯 Required models for Prompt Engine:")
    for model in required_models:
        print(f"   • {model}")
    
    # Check which models need to be pulled
    models_to_pull = []
    for model in required_models:
        if model not in current_models:
            models_to_pull.append(model)
        else:
            print(f"   ✅ {model} already available")
    
    if not models_to_pull:
        print("\n🎉 All required models are already available!")
        return True
    
    # Confirm download
    print(f"\n📥 Need to download {len(models_to_pull)} models:")
    for model in models_to_pull:
        print(f"   • {model}")
    
    print("\n⚠️ Warning: This will download several GB of data")
    try:
        confirm = input("Continue with download? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Download cancelled")
            return False
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted")
        return False
    
    # Pull required models
    success_count = 0
    for model in models_to_pull:
        if pull_model_docker(container_name, model):
            success_count += 1
        else:
            print(f"⚠️ Failed to pull {model}")
    
    # Try alternatives if needed
    if success_count == 0:
        print("\n⚠️ No required models could be pulled, trying alternatives...")
        for alt_model in alternative_models:
            if alt_model not in current_models:
                if pull_model_docker(container_name, alt_model):
                    print(f"✅ Successfully pulled alternative: {alt_model}")
                    print("💡 Update config.py to use this model")
                    success_count = 1
                    break
    
    # Final verification
    print("\n🔍 Final verification...")
    final_models = get_available_models()
    
    prompt_engine_ready = False
    for model in required_models:
        if model in final_models:
            print(f"✅ Prompt Engine model ready: {model}")
            prompt_engine_ready = True
            break
    
    if not prompt_engine_ready:
        for model in alternative_models:
            if model in final_models:
                print(f"✅ Alternative model available: {model}")
                prompt_engine_ready = True
                break
    
    if prompt_engine_ready:
        print("\n🎉 Prompt Engine model setup completed!")
        print("\nNext steps:")
        print("1. Start prompt engine: python main.py")
        print("2. Test prompt engine: curl http://localhost:5000/system/status")
        print("3. Test generation: curl -X POST http://localhost:5000/generate")
        return True
    else:
        print("\n❌ Model setup failed")
        print("Please check Docker logs: docker logs", container_name)
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
