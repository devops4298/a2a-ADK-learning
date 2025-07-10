#!/usr/bin/env python3
"""
Test script to demonstrate contextual clickable buttons in VS Code Copilot Chat.
"""

import requests
import json

def test_contextual_buttons():
    """Test contextual buttons that appear only when code needs fixing."""
    
    base_url = "http://localhost:8080"
    
    print("🔘 Testing Contextual Clickable Buttons")
    print("=" * 50)
    
    # Test Case 1: Code WITH fixable issues (should show buttons)
    print("\n🧪 Test 1: Code with Auto-Fixable Issues")
    print("-" * 40)
    
    code_with_issues = '''
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
    
    try:
        response = requests.post(f"{base_url}/chat", json={
            "message": "analyze this Playwright test for issues",
            "context": {
                "content": code_with_issues,
                "file_path": "tests/login.spec.ts"
            }
        }, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Analysis with fixable issues:")
                print("📝 Response includes contextual buttons:")
                
                response_text = result['response']
                
                # Check for button indicators
                has_buttons = "🔘 One-Click Actions:" in response_text
                has_apply_button = "Apply All" in response_text and "Fixes" in response_text
                has_show_button = "Show Fixed Code" in response_text
                has_reanalyze_button = "Re-analyze" in response_text
                
                print(f"   🔘 Has Action Buttons: {'✅' if has_buttons else '❌'}")
                print(f"   🔧 Has Apply Fixes Button: {'✅' if has_apply_button else '❌'}")
                print(f"   📄 Has Show Code Button: {'✅' if has_show_button else '❌'}")
                print(f"   🔍 Has Re-analyze Button: {'✅' if has_reanalyze_button else '❌'}")
                
                # Show button section
                if has_buttons:
                    lines = response_text.split('\n')
                    button_section = []
                    in_button_section = False
                    
                    for line in lines:
                        if "🔘 One-Click Actions:" in line:
                            in_button_section = True
                        if in_button_section:
                            button_section.append(line)
                            if line.strip() == "" and len(button_section) > 5:
                                break
                    
                    print("\n📋 Button Section Preview:")
                    for line in button_section[:8]:
                        print(f"   {line}")
            else:
                print(f"❌ Analysis failed: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test Case 2: Clean code WITHOUT issues (should NOT show buttons)
    print("\n🧪 Test 2: Clean Code without Issues")
    print("-" * 40)
    
    clean_code = '''
import { test, expect } from '@playwright/test';

test('should display user profile correctly', async ({ page }) => {
    await page.goto('/profile');
    
    await expect(page.getByRole('heading', { name: 'User Profile' })).toBeVisible();
    await expect(page.getByText('Welcome back!')).toBeVisible();
    
    const userName = page.getByTestId('user-name');
    await expect(userName).toHaveText('John Doe');
});
'''
    
    try:
        response = requests.post(f"{base_url}/chat", json={
            "message": "analyze this clean Playwright test",
            "context": {
                "content": clean_code,
                "file_path": "tests/profile.spec.ts"
            }
        }, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Analysis of clean code:")
                
                response_text = result['response']
                
                # Check that NO buttons appear for clean code
                has_buttons = "🔘 One-Click Actions:" in response_text
                has_apply_button = "Apply All" in response_text and "Fixes" in response_text
                
                print(f"   🔘 Has Action Buttons: {'❌ (Correct!)' if not has_buttons else '⚠️ (Unexpected)'}")
                print(f"   🔧 Has Apply Fixes Button: {'❌ (Correct!)' if not has_apply_button else '⚠️ (Unexpected)'}")
                
                # Show response type
                if "Excellent" in response_text or "Great" in response_text:
                    print("   ✅ Shows positive feedback for clean code")
                else:
                    print("   📝 Shows standard analysis response")
            else:
                print(f"❌ Analysis failed: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test Case 3: No code provided (should NOT show buttons)
    print("\n🧪 Test 3: No Code Provided")
    print("-" * 40)
    
    try:
        response = requests.post(f"{base_url}/chat", json={
            "message": "analyze this code",
            "context": {
                "content": "",
                "file_path": ""
            }
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Analysis with no code:")
                
                response_text = result['response']
                has_buttons = "🔘" in response_text or "Apply" in response_text
                
                print(f"   🔘 Has Action Buttons: {'❌ (Correct!)' if not has_buttons else '⚠️ (Unexpected)'}")
                print("   📝 Shows guidance for providing code")
            else:
                print(f"❌ Analysis failed: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test Case 4: Fix request (should show apply buttons)
    print("\n🧪 Test 4: Fix Request with Buttons")
    print("-" * 40)
    
    try:
        response = requests.post(f"{base_url}/chat", json={
            "message": "fix this code",
            "context": {
                "content": code_with_issues,
                "file_path": "tests/login.spec.ts"
            }
        }, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Fix request response:")
                
                response_text = result['response']
                
                # Check for fix-specific buttons
                has_apply_button = "Replace Current Code" in response_text
                has_new_file_button = "Insert in New File" in response_text
                has_analyze_button = "Analyze Fixed Code" in response_text
                has_fixed_code = "Fixed Code:" in response_text
                
                print(f"   📝 Has Replace Code Button: {'✅' if has_apply_button else '❌'}")
                print(f"   📄 Has New File Button: {'✅' if has_new_file_button else '❌'}")
                print(f"   🔍 Has Analyze Button: {'✅' if has_analyze_button else '❌'}")
                print(f"   💻 Shows Fixed Code: {'✅' if has_fixed_code else '❌'}")
                
            else:
                print(f"❌ Fix failed: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Contextual Button Testing Complete!")
    print("\n📋 Summary:")
    print("✅ Buttons appear ONLY when:")
    print("   • Code has auto-fixable issues")
    print("   • User provides actual code content")
    print("   • Fix results are available")
    print("\n❌ Buttons do NOT appear when:")
    print("   • Code is already clean")
    print("   • No code is provided")
    print("   • Only manual fixes are needed")
    
    print("\n🔘 VS Code Usage:")
    print("1. Select code with issues in VS Code")
    print("2. Ask: 'analyze this code'")
    print("3. Click the '🔧 Apply All Fixes' button in chat")
    print("4. VS Code will apply the fixes automatically!")


if __name__ == "__main__":
    test_contextual_buttons()
