#!/usr/bin/env python3
"""
Simple test script for the Code Review Agent server.
"""

import requests
import json

def test_server():
    """Test the running server."""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Code Review Agent Server")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test agent info
    try:
        response = requests.get(f"{base_url}/agent")
        print(f"✅ Agent Info: {response.status_code}")
        agent_info = response.json()
        print(f"   Agent: {agent_info['name']}")
        print(f"   Capabilities: {', '.join(agent_info['capabilities'])}")
    except Exception as e:
        print(f"❌ Agent Info Failed: {e}")
    
    # Test chat endpoint
    try:
        chat_data = {
            "message": "help",
            "context": {}
        }
        response = requests.post(f"{base_url}/chat", json=chat_data)
        print(f"✅ Chat Test: {response.status_code}")
        if response.status_code == 200:
            chat_response = response.json()
            print(f"   Response: {chat_response['response'][:100]}...")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Chat Test Failed: {e}")
    
    # Test standards endpoint
    try:
        response = requests.get(f"{base_url}/standards")
        print(f"✅ Standards Test: {response.status_code}")
        if response.status_code == 200:
            standards = response.json()
            print(f"   Found {standards['total_count']} standards")
            print(f"   Categories: {', '.join(standards['categories'])}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Standards Test Failed: {e}")
    
    print("\n🎉 Server testing complete!")
    print("\n📋 VS Code Integration Instructions:")
    print("1. The server is running and ready for VS Code Copilot Chat")
    print("2. Configure VS Code to use this agent endpoint:")
    print(f"   - Agent URL: {base_url}")
    print("   - Agent ID: ts-playwright-cucumber-reviewer")
    print("3. Use in Copilot Chat with commands like:")
    print("   - 'Analyze this TypeScript code'")
    print("   - 'Fix issues in this file'")
    print("   - 'Show me coding standards'")

if __name__ == "__main__":
    test_server()
