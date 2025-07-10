#!/usr/bin/env python3
"""
Test script for enhanced prompts and ADK-powered code review capabilities.
"""

import requests
import json

def test_enhanced_chat_prompts():
    """Test the enhanced chat prompts with various scenarios."""
    
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Enhanced Chat Prompts with ADK Integration")
    print("=" * 70)
    
    # Sample TypeScript code with various issues
    sample_typescript = '''
import React, { useState } from 'react';

function UserProfile(props: any) {
    const [user, setUser] = useState();
    
    const fetchUser = async (id) => {
        console.log('Fetching user:', id);
        const response = await fetch(`/api/users/${id}`);
        return response.json();
    };
    
    const handleClick = () => {
        console.warn('Button clicked');
        fetchUser(props.userId).then(userData => {
            setUser(userData);
        });
    };
    
    return (
        <div onClick={handleClick}>
            <h1>{user?.name}</h1>
            <p>{user?.email}</p>
        </div>
    );
}

export default UserProfile;
'''
    
    # Sample Playwright test with issues
    sample_playwright = '''
import { test, expect } from '@playwright/test';

test('user login test', async ({ page }) => {
    console.log('Starting login test');
    
    await page.goto('https://example.com/login');
    await page.waitForTimeout(2000);
    
    await page.click('#username');
    await page.fill('#username', 'testuser');
    console.warn('Username filled');
    
    await page.click('.password-input');
    await page.fill('.password-input', 'password123');
    
    await page.click('//button[@type="submit"]');
    console.error('Login button clicked');
    
    await page.waitForTimeout(3000);
    expect(await page.isVisible('#dashboard')).toBe(true);
});
'''
    
    # Test scenarios with enhanced prompts
    test_scenarios = [
        {
            "name": "Comprehensive TypeScript Analysis",
            "prompt": """As an expert TypeScript code reviewer running on an ADK server, perform a comprehensive analysis of this React component including:
- Type safety and TypeScript best practices
- React patterns and performance considerations
- Code organization and maintainability
- Auto-fixable issues and manual improvements
- Security and accessibility concerns

Please provide structured feedback with explanations.""",
            "context": {
                "content": sample_typescript,
                "file_path": "components/UserProfile.tsx"
            }
        },
        {
            "name": "Playwright Test Review",
            "prompt": """Review this Playwright test file for:
- Test structure and naming conventions
- Locator strategies and wait patterns
- Console statement removal opportunities
- Assertion quality and test reliability
- Best practices compliance

Identify both auto-fixable issues and manual improvements needed.""",
            "context": {
                "content": sample_playwright,
                "file_path": "tests/login.spec.ts"
            }
        },
        {
            "name": "Educational Code Review",
            "prompt": """Explain the issues in this code and teach me:
- Why each issue is problematic
- How to fix them properly
- Best practices to prevent similar issues
- Modern TypeScript/React patterns
- Framework-specific recommendations

Focus on educational value and learning.""",
            "context": {
                "content": sample_typescript,
                "file_path": "components/UserProfile.tsx"
            }
        },
        {
            "name": "Auto-Fix Focused Review",
            "prompt": """Identify all auto-fixable issues in this code and explain:
- What can be automatically corrected
- What requires manual attention
- Priority order for fixes
- Expected impact of each fix
- Next steps after auto-fixes are applied""",
            "context": {
                "content": sample_playwright,
                "file_path": "tests/login.spec.ts"
            }
        },
        {
            "name": "Framework Standards Check",
            "prompt": """Check this code against TypeScript and React best practices:
- Type safety compliance
- Modern React patterns usage
- Performance optimization opportunities
- Code organization standards
- Maintainability considerations

Provide specific recommendations with examples.""",
            "context": {
                "content": sample_typescript,
                "file_path": "components/UserProfile.tsx"
            }
        }
    ]
    
    # Run test scenarios
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔍 Test {i}: {scenario['name']}")
        print("-" * 50)
        
        try:
            response = requests.post(f"{base_url}/chat", json={
                "message": scenario["prompt"],
                "context": scenario["context"]
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    print("✅ Enhanced chat response received!")
                    print(f"📝 Response length: {len(result['response'])} characters")
                    print(f"🎯 Intent detected: {result.get('intent', 'unknown')}")
                    
                    # Show first part of response
                    response_preview = result['response'][:300]
                    print(f"\n📋 Response Preview:")
                    print(f"{response_preview}...")
                    
                    # Show suggestions if available
                    if result.get('suggestions'):
                        print(f"\n💡 Suggestions ({len(result['suggestions'])}):")
                        for suggestion in result['suggestions'][:3]:
                            print(f"   • {suggestion}")
                    
                    # Show follow-up actions if available
                    if result.get('follow_up_actions'):
                        print(f"\n🎯 Follow-up Actions ({len(result['follow_up_actions'])}):")
                        for action in result['follow_up_actions'][:3]:
                            print(f"   • {action}")
                
                else:
                    print(f"❌ Chat failed: {result.get('error', 'Unknown error')}")
            
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
        
        except requests.exceptions.Timeout:
            print("⏰ Request timed out (this is normal for complex analysis)")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Test simple prompts
    print(f"\n🚀 Testing Simple Prompts")
    print("-" * 30)
    
    simple_prompts = [
        "help",
        "show me typescript standards",
        "what are playwright best practices?",
        "explain this error",
        "how should I structure my tests?"
    ]
    
    for prompt in simple_prompts:
        try:
            response = requests.post(f"{base_url}/chat", json={
                "message": prompt,
                "context": {}
            }, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ '{prompt}' - Response: {len(result['response'])} chars")
                else:
                    print(f"❌ '{prompt}' - Error: {result.get('error', 'Unknown')}")
            else:
                print(f"❌ '{prompt}' - HTTP {response.status_code}")
        
        except Exception as e:
            print(f"❌ '{prompt}' - Error: {str(e)}")
    
    print("\n" + "=" * 70)
    print("🎉 Enhanced Prompt Testing Complete!")
    print("\n📋 VS Code Usage Instructions:")
    print("1. Open VS Code with your TypeScript/Playwright project")
    print("2. Open Copilot Chat (Ctrl/Cmd + Shift + I)")
    print("3. Select code and use any of the enhanced prompts:")
    print("   • 'Perform comprehensive code review of this file'")
    print("   • 'Review this Playwright test for best practices'")
    print("   • 'Explain issues and teach me improvements'")
    print("   • 'Identify all auto-fixable issues'")
    print("4. Get detailed, educational, and actionable feedback!")
    
    print("\n🔧 Server Status:")
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✅ Server healthy: {health_data['name']}")
            print(f"   🤖 Agent ID: {health_data['agent_id']}")
        else:
            print(f"   ⚠️  Server status: {health_response.status_code}")
    except Exception as e:
        print(f"   ❌ Server check failed: {e}")


if __name__ == "__main__":
    test_enhanced_chat_prompts()
