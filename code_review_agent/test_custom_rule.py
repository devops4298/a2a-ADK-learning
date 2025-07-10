#!/usr/bin/env python3
"""
Test script to validate the custom ESLint rule integration.
"""

import sys
import os

# Add the parent directory to the path to fix imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Now import from the code_review_agent package
from code_review_agent.linters.custom_linter import CustomLinter
from code_review_agent.analyzers.file_analyzer import FileAnalyzer
from code_review_agent.fixers.fix_manager import FixManager

def test_console_rule_detection():
    """Test that our custom console rule detects console statements in test files."""
    print("🧪 Testing Console Rule Detection...")
    
    # Sample test content with console statements
    test_content = '''
import { test, expect } from '@playwright/test';

test('sample test', async ({ page }) => {
    console.log('Starting test');
    console.warn('This is a warning');
    console.error('This is an error');
    console.info('Info message');
    console.debug('Debug message');
    
    await page.goto('https://example.com');
    expect(page).toHaveTitle('Example');
});
'''
    
    # Test with CustomLinter directly
    linter = CustomLinter()
    issues = linter.lint_content(test_content, 'test.spec.ts')
    
    console_issues = [issue for issue in issues if issue.rule_id == 'pw-no-console-in-tests']
    
    print(f"✅ Found {len(console_issues)} console issues in test file")
    
    for issue in console_issues:
        print(f"   - Line {issue.line_number}: {issue.description}")
        print(f"     Auto-fixable: {issue.auto_fixable}")
        print(f"     Suggestion: {issue.suggested_fix}")
    
    return len(console_issues) == 5  # Should find 5 console statements

def test_auto_fix_functionality():
    """Test that the auto-fix removes console statements."""
    print("\n🔧 Testing Auto-Fix Functionality...")
    
    test_content = '''
import { test, expect } from '@playwright/test';

test('sample test', async ({ page }) => {
    console.log('This should be removed');
    await page.goto('https://example.com');
    console.warn('This should also be removed');
    expect(page).toHaveTitle('Example');
    console.error('And this too');
});
'''
    
    # Apply auto-fix
    linter = CustomLinter()
    fixed_content = linter.fix_content(test_content, 'test.spec.ts')
    
    # Check that console statements are removed
    console_count_before = test_content.count('console.')
    console_count_after = fixed_content.count('console.')
    
    print(f"✅ Console statements before fix: {console_count_before}")
    print(f"✅ Console statements after fix: {console_count_after}")
    print(f"✅ Successfully removed: {console_count_before - console_count_after} console statements")
    
    if console_count_after == 0:
        print("✅ All console statements successfully removed!")
        return True
    else:
        print("❌ Some console statements remain")
        return False

def test_file_analyzer_integration():
    """Test integration with the main FileAnalyzer."""
    print("\n🔍 Testing FileAnalyzer Integration...")
    
    # Test with our sample file
    sample_file = 'code_review_agent/test_samples/playwright/bad_test.spec.ts'
    
    if not os.path.exists(sample_file):
        print(f"❌ Sample file not found: {sample_file}")
        return False
    
    analyzer = FileAnalyzer()
    issues = analyzer.analyze_file(sample_file)
    
    console_issues = [issue for issue in issues if issue.rule_id == 'pw-no-console-in-tests']
    
    print(f"✅ FileAnalyzer found {len(console_issues)} console issues")
    print(f"✅ Total issues in file: {len(issues)}")
    
    return len(console_issues) > 0

def test_one_click_fix():
    """Test the one-click fix functionality."""
    print("\n⚡ Testing One-Click Fix...")
    
    sample_file = 'code_review_agent/test_samples/playwright/bad_test.spec.ts'
    
    if not os.path.exists(sample_file):
        print(f"❌ Sample file not found: {sample_file}")
        return False
    
    # Read original content
    with open(sample_file, 'r') as f:
        original_content = f.read()
    
    # Analyze first
    analyzer = FileAnalyzer()
    issues = analyzer.analyze_file(sample_file, original_content)
    
    # Apply one-click fix
    fix_manager = FixManager()
    fix_result = fix_manager.one_click_fix(original_content, sample_file, issues)
    
    console_fixes = [fix for fix in fix_result['applied_fixes'] 
                    if 'console' in fix.get('description', '').lower()]
    
    print(f"✅ Applied {len(fix_result['applied_fixes'])} total fixes")
    print(f"✅ Console-related fixes: {len(console_fixes)}")
    print(f"✅ Content changed: {fix_result['content_changed']}")
    
    return fix_result['content_changed']

def main():
    """Run all tests."""
    print("🚀 Testing Custom ESLint Rule Integration\n")
    
    tests = [
        ("Console Rule Detection", test_console_rule_detection),
        ("Auto-Fix Functionality", test_auto_fix_functionality),
        ("FileAnalyzer Integration", test_file_analyzer_integration),
        ("One-Click Fix", test_one_click_fix)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Custom rule integration successful!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
