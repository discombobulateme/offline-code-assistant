#!/usr/bin/env python3

"""
Test script for Basic Agent
This script verifies that all required modules can be imported correctly
"""

import os
import sys

def test_imports():
    """Test that all required modules can be imported"""
    try:
        # Add the current directory to the path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import modules
        from src.llm_manager import LLMManager
        from src.project_analyzer import ProjectAnalyzer
        from src.code_generator import CodeGenerator
        
        print("✅ All modules imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test that the config file can be loaded"""
    try:
        import yaml
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "config", "config.yaml")
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            print("✅ Config loaded successfully!")
            return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_ollama():
    """Test connection to Ollama"""
    try:
        import ollama
        models = ollama.list()
        print("✅ Ollama connection successful!")
        print(f"Available models: {', '.join([m['name'] for m in models['models']])}")
        return True
    except Exception as e:
        print(f"❌ Ollama connection error: {e}")
        return False

if __name__ == "__main__":
    print("Running Basic Agent tests...\n")
    
    imports_ok = test_imports()
    config_ok = test_config()
    ollama_ok = test_ollama()
    
    print("\nTest results:")
    print(f"Imports: {'✅' if imports_ok else '❌'}")
    print(f"Config: {'✅' if config_ok else '❌'}")
    print(f"Ollama: {'✅' if ollama_ok else '❌'}")
    
    if imports_ok and config_ok and ollama_ok:
        print("\n✅ All tests passed! The agent should work correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.") 