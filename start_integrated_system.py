#!/usr/bin/env python3
"""
Integrated System Startup Script
Starts all services in the correct order for the blocking validation system
"""

import os
import sys
import time
import subprocess
import requests
from datetime import datetime
from typing import List, Dict, Any

class ServiceManager:
    """Manages startup and health checking of all services"""
    
    def __init__(self):
        self.services = {
            "ollama": {
                "name": "Ollama LLM Service",
                "command": ["ollama", "serve"],
                "health_url": "http://localhost:11434/api/tags",
                "port": 11434,
                "startup_time": 10,
                "required": True
            },
            "qdrant": {
                "name": "Qdrant Vector Database", 
                "command": ["docker", "run", "-d", "-p", "6333:6333", "-p", "6334:6334", 
                           "--name", "qdrant_integrated", "qdrant/qdrant"],
                "health_url": "http://localhost:6333/collections",
                "port": 6333,
                "startup_time": 15,
                "required": True
            },
            "prompt_engine": {
                "name": "Prompt Engine",
                "command": [sys.executable, "server.py"],
                "health_url": "http://localhost:5000/system/status",
                "port": 5000,
                "startup_time": 5,
                "required": True,
                "cwd": "."
            },
            "validation_system": {
                "name": "Validation System",
                "command": [sys.executable, "simple_server.py"],
                "health_url": "http://localhost:5002/health",
                "port": 5002,
                "startup_time": 10,
                "required": True,
                "cwd": "validation-llm"
            },
            "autonomous_agent": {
                "name": "Autonomous Agent (with Blocking Validation)",
                "command": [sys.executable, "server_final.py"],
                "health_url": "http://localhost:8000/status",
                "port": 8000,
                "startup_time": 15,
                "required": True,
                "cwd": "autonomous-agent"
            }
        }
        
        self.processes = {}
        self.startup_log = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.startup_log.append(log_entry)
    
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        service = self.services[service_name]
        
        try:
            response = requests.get(service["health_url"], timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_service(self, service_name: str) -> bool:
        """Start a single service"""
        service = self.services[service_name]
        
        self.log(f"Starting {service['name']}...")
        
        # Check if port is available (unless it's Docker)
        if not service_name == "qdrant":
            if not self.check_port_available(service["port"]):
                self.log(f"Port {service['port']} is already in use", "WARNING")
                # Check if service is already running and healthy
                if self.check_service_health(service_name):
                    self.log(f"{service['name']} already running and healthy", "INFO")
                    return True
                else:
                    self.log(f"Port {service['port']} occupied by non-healthy service", "ERROR")
                    return False
        
        try:
            # Handle Docker services differently
            if service_name == "qdrant":
                # Stop existing container if any
                subprocess.run(["docker", "stop", "qdrant_integrated"], 
                             capture_output=True, check=False)
                subprocess.run(["docker", "rm", "qdrant_integrated"], 
                             capture_output=True, check=False)
            
            # Start the service
            kwargs = {}
            if "cwd" in service:
                kwargs["cwd"] = service["cwd"]
            
            if service_name == "qdrant":
                # Docker run returns immediately
                process = subprocess.run(service["command"], **kwargs, capture_output=True, check=True)
                self.log(f"Docker container started: {process.stdout.decode().strip()}")
            else:
                # Start as background process
                process = subprocess.Popen(
                    service["command"], 
                    **kwargs,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.processes[service_name] = process
            
            # Wait for startup
            self.log(f"Waiting {service['startup_time']}s for {service['name']} to start...")
            time.sleep(service["startup_time"])
            
            # Check health
            max_health_checks = 6
            for attempt in range(max_health_checks):
                if self.check_service_health(service_name):
                    self.log(f"✅ {service['name']} started successfully")
                    return True
                
                if attempt < max_health_checks - 1:
                    self.log(f"Health check {attempt + 1}/{max_health_checks} failed, retrying...")
                    time.sleep(5)
            
            self.log(f"❌ {service['name']} failed to start (health check failed)", "ERROR")
            return False
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Failed to start {service['name']}: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Unexpected error starting {service['name']}: {e}", "ERROR")
            return False
    
    def setup_models(self):
        """Setup required models"""
        self.log("Setting up required models...")
        
        # Models for main system
        main_models = ["llama3.1:8b"]
        
        # Models for validation system  
        validation_models = ["mistral:latest"]
        
        all_models = main_models + validation_models
        
        for model in all_models:
            self.log(f"Pulling model: {model}")
            try:
                result = subprocess.run(
                    ["ollama", "pull", model],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout per model
                )
                
                if result.returncode == 0:
                    self.log(f"✅ Model {model} ready")
                else:
                    self.log(f"⚠️ Model {model} pull failed: {result.stderr}", "WARNING")
                    
            except subprocess.TimeoutExpired:
                self.log(f"⚠️ Model {model} pull timed out", "WARNING")
            except Exception as e:
                self.log(f"⚠️ Error pulling model {model}: {e}", "WARNING")
    
    def start_all_services(self) -> bool:
        """Start all services in the correct order"""
        self.log("🚀 Starting Integrated Validation System")
        self.log("=" * 50)
        
        startup_order = ["ollama", "qdrant", "prompt_engine", "validation_system", "autonomous_agent"]
        
        failed_services = []
        
        for service_name in startup_order:
            if not self.start_service(service_name):
                failed_services.append(service_name)
                if self.services[service_name]["required"]:
                    self.log(f"❌ Required service {service_name} failed to start", "ERROR")
                    return False
        
        if failed_services:
            self.log(f"⚠️ Some optional services failed: {failed_services}", "WARNING")
        
        # Setup models after Ollama is running
        if "ollama" not in failed_services:
            self.setup_models()
        
        self.log("✅ All services started successfully!")
        self.log("=" * 50)
        
        # Print service URLs
        self.log("📍 Service URLs:")
        for service_name, service in self.services.items():
            if service_name not in failed_services:
                self.log(f"   {service['name']}: {service['health_url']}")
        
        return True
    
    def stop_all_services(self):
        """Stop all running services"""
        self.log("🛑 Stopping all services...")
        
        # Stop Python processes
        for service_name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=10)
                self.log(f"✅ Stopped {self.services[service_name]['name']}")
            except:
                try:
                    process.kill()
                    self.log(f"⚠️ Force killed {self.services[service_name]['name']}")
                except:
                    pass
        
        # Stop Docker containers
        try:
            subprocess.run(["docker", "stop", "qdrant_integrated"], 
                         capture_output=True, check=False)
            subprocess.run(["docker", "rm", "qdrant_integrated"], 
                         capture_output=True, check=False)
            self.log("✅ Stopped Qdrant container")
        except:
            pass
    
    def run_integration_test(self) -> bool:
        """Run the integration test"""
        self.log("🧪 Running integration test...")
        
        try:
            result = subprocess.run(
                [sys.executable, "validation-llm/examples/complete_integration_test.py"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.log("✅ Integration test PASSED")
                return True
            else:
                self.log("❌ Integration test FAILED")
                self.log(f"Test output: {result.stdout}")
                self.log(f"Test errors: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("⏰ Integration test timed out", "WARNING")
            return False
        except Exception as e:
            self.log(f"❌ Error running integration test: {e}", "ERROR")
            return False

def main():
    """Main execution"""
    manager = ServiceManager()
    
    try:
        # Start all services
        if not manager.start_all_services():
            print("\n❌ Failed to start all required services")
            return 1
        
        print("\n🎉 System started successfully!")
        print("\nTo test the system, run:")
        print("  python validation-llm/examples/complete_integration_test.py")
        
        print("\nTo use the system:")
        print("  curl -X POST http://localhost:8000/analyze \\")
        print("    -H 'Content-Type: application/json' \\")
        print("    -d '{\"input_data\": {\"transactions\": [...]}}'")
        
        # Ask if user wants to run integration test
        print("\n🧪 Run integration test now? (y/n): ", end="")
        if input().lower().startswith('y'):
            test_passed = manager.run_integration_test()
            if test_passed:
                print("\n✅ INTEGRATION COMPLETE - Blocking validation is working!")
            else:
                print("\n⚠️ Integration test failed - check logs above")
        
        print("\nPress Ctrl+C to stop all services...")
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            manager.stop_all_services()
            print("✅ All services stopped")
            return 0
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted during startup")
        manager.stop_all_services()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        manager.stop_all_services()
        return 1

if __name__ == "__main__":
    exit(main())
