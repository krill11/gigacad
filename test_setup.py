#!/usr/bin/env python3
"""
Test script to verify CoralMaker setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from src.config import config
        print("✅ Configuration module imported")
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from src.onshape_client import OnshapeClient
        print("✅ Onshape client imported")
    except ImportError as e:
        print(f"❌ Failed to import Onshape client: {e}")
        return False
    
    try:
        from src.llm_interface import LLMFactory
        print("✅ LLM interface imported")
    except ImportError as e:
        print(f"❌ Failed to import LLM interface: {e}")
        return False
    
    try:
        from src.ai_agent import CADAgent
        print("✅ AI agent imported")
    except ImportError as e:
        print(f"❌ Failed to import AI agent: {e}")
        return False
    
    return True

def test_config():
    """Test configuration validation"""
    print("\n🔍 Testing configuration...")
    
    try:
        from src.config import config
        
        # Check if .env file exists
        if os.path.exists('.env'):
            print("✅ .env file found")
        else:
            print("⚠️  .env file not found (copy from env.example)")
        
        # Test config validation
        if config.validate():
            print("✅ Configuration validation passed")
            return True
        else:
            print("❌ Configuration validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_dependencies():
    """Test if required packages are installed"""
    print("\n🔍 Testing dependencies...")
    
    required_packages = [
        'requests',
        'python-dotenv',
        'groq',
        'pydantic',
        'fastapi',
        'uvicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 CoralMaker Setup Test")
    print("=" * 40)
    
    all_tests_passed = True
    
    # Test dependencies
    if not test_dependencies():
        all_tests_passed = False
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test configuration
    if not test_config():
        all_tests_passed = False
    
    print("\n" + "=" * 40)
    
    if all_tests_passed:
        print("🎉 All tests passed! CoralMaker is ready to use.")
        print("\nNext steps:")
        print("1. Copy env.example to .env")
        print("2. Add your API keys to .env")
        print("3. Run: python main.py cli")
        print("4. Or run: python main.py web")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Copy env.example to .env and add your API keys")
        print("- Check Python version (3.8+ required)")
        sys.exit(1)

if __name__ == "__main__":
    main() 