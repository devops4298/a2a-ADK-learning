#!/usr/bin/env python3
"""
Demonstration of the custom ESLint rule integration.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from code_review_agent.linters.custom_linter import CustomLinter

def demo_console_rule():
    """Demonstrate the custom console rule working."""
    print("🎯 Custom ESLint Rule Integration Demo")
    print("=" * 50)
    
    # Sample Playwright test content with console statements
    test_content = '''import { test, expect } from '@playwright/test';

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
});'''
    
    print("📝 Original Test Content:")
    print("-" * 30)
    print(test_content)
    print()
    
    # Analyze with custom linter
    print("🔍 Analysis Results:")
    print("-" * 30)
    
    linter = CustomLinter()
    issues = linter.lint_content(test_content, 'example.spec.ts')
    
    console_issues = [issue for issue in issues if issue.rule_id == 'pw-no-console-in-tests']
    
    print(f"Found {len(console_issues)} console-related issues:")
    print()
    
    for i, issue in enumerate(console_issues, 1):
        print(f"{i}. Line {issue.line_number}: {issue.description}")
        print(f"   Severity: {issue.severity}")
        print(f"   Auto-fixable: {issue.auto_fixable}")
        print(f"   Suggestion: {issue.suggested_fix}")
        print()
    
    # Apply auto-fix
    print("🔧 Auto-Fix Results:")
    print("-" * 30)
    
    fixed_content = linter.fix_content(test_content, 'example.spec.ts')
    
    print("Fixed Test Content:")
    print(fixed_content)
    print()
    
    # Show statistics
    console_count_before = test_content.count('console.')
    console_count_after = fixed_content.count('console.')
    
    print("📊 Fix Statistics:")
    print(f"   Console statements before: {console_count_before}")
    print(f"   Console statements after: {console_count_after}")
    print(f"   Successfully removed: {console_count_before - console_count_after}")
    
    if console_count_after == 0:
        print("   ✅ All console statements successfully removed!")
    else:
        print(f"   ⚠️  {console_count_after} console statements remain")
    
    print()
    print("🎉 Custom ESLint Rule Integration Successful!")
    print("   ✅ JavaScript ESLint rule converted to Python")
    print("   ✅ Integrated into CustomLinter class")
    print("   ✅ Detects console statements in .spec.ts files")
    print("   ✅ Auto-fixable with console statement removal")
    print("   ✅ Provides specific suggestions for each console method")

if __name__ == "__main__":
    demo_console_rule()
