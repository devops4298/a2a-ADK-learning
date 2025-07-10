#!/usr/bin/env python3
"""
VS Code Integration Test Script
This script demonstrates how to interact with your code review agent.
"""

import requests
import json

def test_agent_integration():
    """Test the agent with sample TypeScript/Playwright code."""
    
    base_url = "http://localhost:8080"
    
    print("🧪 Testing VS Code Integration with Code Review Agent")
    print("=" * 60)
    
    # Sample TypeScript code with issues
    sample_code = '''
import { test, expect } from '@playwright/test';

test('login test', async ({ page }) => {
    console.log('Starting login test');
    console.warn('This is a warning message');
    console.error('This is an error message for debugging');
    
    await page.goto('https://example.com/login');
    console.info('Navigated to login page');
    
    await page.click('#username');
    await page.fill('#username', 'testuser');
    console.debug('Filled username field');
    
    expect(page).toHaveTitle('Example');
});
'''
    
    print("📝 Sample Code to Analyze:")
    print("-" * 30)
    print(sample_code)
    print()
    
    # Test 1: Analyze Code
    print("🔍 Test 1: Code Analysis")
    print("-" * 30)
    
    try:
        response = requests.post(f"{base_url}/analyze", json={
            "content": sample_code,
            "file_path": "login.spec.ts"
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis successful!")
            print(f"   Total issues found: {result['total_issues']}")
            print(f"   Auto-fixable issues: {result['auto_fixable_count']}")
            
            # Show first few issues
            for i, issue in enumerate(result['issues'][:3], 1):
                print(f"   {i}. Line {issue['line_number']}: {issue['description']}")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Analysis error: {e}")
    
    print()
    
    # Test 2: Auto-Fix Code
    print("🔧 Test 2: Auto-Fix")
    print("-" * 30)
    
    try:
        response = requests.post(f"{base_url}/fix", json={
            "content": sample_code,
            "file_path": "login.spec.ts"
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Auto-fix successful!")
            print(f"   Content changed: {result['content_changed']}")
            print(f"   Applied fixes: {len(result['applied_fixes'])}")
            
            if result['content_changed']:
                print("\n📄 Fixed Code:")
                print("-" * 20)
                print(result['fixed_content'])
        else:
            print(f"❌ Auto-fix failed: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Auto-fix error: {e}")
    
    print()
    
    # Test 3: Chat Interface
    print("💬 Test 3: Chat Interface")
    print("-" * 30)
    
    chat_messages = [
        "help",
        "analyze this code",
        "show me typescript standards",
        "what are playwright best practices?"
    ]
    
    for message in chat_messages:
        try:
            response = requests.post(f"{base_url}/chat", json={
                "message": message,
                "context": {
                    "content": sample_code,
                    "file_path": "login.spec.ts"
                }
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Chat: '{message}'")
                print(f"   Response: {result['response'][:100]}...")
            else:
                print(f"❌ Chat failed for '{message}': {response.status_code}")
        
        except Exception as e:
            print(f"❌ Chat error for '{message}': {e}")
    
    print()
    
    # Test 4: Standards
    print("📋 Test 4: Coding Standards")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/standards?category=playwright")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Standards retrieved!")
            print(f"   Total standards: {result['total_count']}")
            print(f"   Categories: {', '.join(result['categories'])}")
            
            # Show first few standards
            for i, standard in enumerate(result['standards'][:3], 1):
                auto_fix = "🔧" if standard['auto_fixable'] else "👁️"
                print(f"   {i}. {auto_fix} {standard['rule_id']}: {standard['description'][:50]}...")
        else:
            print(f"❌ Standards failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Standards error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Integration Testing Complete!")
    print("\n📋 How to Use in VS Code:")
    print("1. Open VS Code with your TypeScript/Playwright project")
    print("2. Open Copilot Chat (Ctrl/Cmd + Shift + I)")
    print("3. Try these commands:")
    print("   • 'Analyze this TypeScript file'")
    print("   • 'Fix issues in this Playwright test'")
    print("   • 'Show me coding standards'")
    print("   • 'Help me improve this code'")


if __name__ == "__main__":
    test_agent_integration()
