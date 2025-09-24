#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test all core imports"""
    print("🧪 Testing imports...")
    
    try:
        print("   📦 Testing config import...")
        from config import get_config
        config = get_config()
        print("   ✅ Config imported successfully")
        
        print("   📦 Testing core module imports...")
        from core.llm_validator import LLMValidator
        print("   ✅ LLMValidator imported successfully")
        
        from core.quality_assessor import QualityAssessor
        print("   ✅ QualityAssessor imported successfully")
        
        from core.training_data_manager import TrainingDataManager
        print("   ✅ TrainingDataManager imported successfully")
        
        from core.feedback_manager import FeedbackManager
        print("   ✅ FeedbackManager imported successfully")
        
        from core.validation_engine import ValidationEngine
        print("   ✅ ValidationEngine imported successfully")
        
        print("   📦 Testing Flask imports...")
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        print("   ✅ Flask imports successful")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🔧 Testing basic functionality...")
    
    try:
        from config import get_config
        config = get_config()
        
        # Test config access
        print(f"   📋 System name: {config['base']['system']['name']}")
        print(f"   📋 System version: {config['base']['system']['version']}")
        
        # Test validation criteria
        criteria = config['validation_criteria']
        print(f"   📋 Validation criteria count: {len(criteria)}")
        
        print("   ✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Validation System Import Test")
    print("=" * 40)
    
    import_success = test_imports()
    
    if import_success:
        functionality_success = test_basic_functionality()
        
        if functionality_success:
            print("\n✅ All tests passed! You can now run the validation server.")
            print("\nTo start the server, run:")
            print("   python run_validation_server.py")
        else:
            print("\n⚠️ Imports work but functionality test failed.")
    else:
        print("\n❌ Import tests failed. Check your installation.")
        print("\nTry running:")
        print("   python install.py")
        print("or")
        print("   pip install -r requirements-minimal.txt")

