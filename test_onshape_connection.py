#!/usr/bin/env python3
"""
Test script to debug Onshape API connection
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_env_vars():
    """Test if environment variables are loaded correctly"""
    print("🔍 Environment Variables Check:")
    print("=" * 50)
    
    required_vars = [
        "ONSHAPE_ACCESS_KEY",
        "ONSHAPE_SECRET_KEY", 
        "ONSHAPE_BASE_URL"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask the secret key for security
            if "SECRET" in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print()

def test_onshape_client():
    """Test the Onshape client directly"""
    print("🔧 Testing Onshape Client:")
    print("=" * 50)
    
    try:
        from src.onshape_client import OnshapeClient
        
        # Create client
        client = OnshapeClient()
        print("✅ OnshapeClient created successfully")
        
        # Test connection
        print("\n🔄 Testing API connection...")
        if client.test_connection():
            print("✅ Connection successful!")
            
            # Try to get documents
            print("\n📄 Testing document retrieval...")
            try:
                documents = client.get_documents()
                print(f"✅ Retrieved {len(documents)} documents")
                if documents:
                    print("Sample document:")
                    doc = documents[0]
                    print(f"  - Name: {doc.get('name', 'N/A')}")
                    print(f"  - ID: {doc.get('id', 'N/A')}")
                    print(f"  - Type: {doc.get('type', 'N/A')}")
            except Exception as e:
                print(f"❌ Document retrieval failed: {str(e)}")
                
        else:
            print("❌ Connection failed!")
            
    except Exception as e:
        print(f"❌ Failed to create OnshapeClient: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

def test_ai_agent():
    """Test the AI agent initialization"""
    print("\n🤖 Testing AI Agent:")
    print("=" * 50)
    
    try:
        from src.ai_agent import CADAgent
        
        # Test agent creation
        print("🔄 Creating AI agent...")
        agent = CADAgent(llm_type="groq")
        print("✅ AI agent created successfully!")
        
        # Test status
        print("\n📊 Testing agent status...")
        status = agent.get_status()
        print(f"✅ Status retrieved: {status}")
        
    except Exception as e:
        print(f"❌ Failed to create AI agent: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("🚀 Onshape API Connection Test")
    print("=" * 60)
    
    # Test environment variables
    test_env_vars()
    
    # Test Onshape client
    test_onshape_client()
    
    # Test AI agent
    test_ai_agent()
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    main() 