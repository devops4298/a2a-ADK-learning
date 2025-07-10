"""
Playwright-specific code analyzer.
"""
import re
from typing import List, Dict, Any
from .base_analyzer import BaseAnalyzer, CodeIssue
from ..standards.playwright_standards import PlaywrightStandards


class PlaywrightAnalyzer(BaseAnalyzer):
    """Analyzer for Playwright test files."""
    
    def __init__(self):
        super().__init__()
        self.standards = PlaywrightStandards()
    
    def _analyze_content(self, content: str, file_path: str):
        """Analyze Playwright test content for best practices."""
        self._check_page_object_patterns(content, file_path)
        self._check_locator_practices(content, file_path)
        self._check_waiting_patterns(content, file_path)
        self._check_test_structure(content, file_path)
        self._check_assertions(content, file_path)
        self._check_performance_patterns(content, file_path)
    
    def _check_page_object_patterns(self, content: str, file_path: str):
        """Check for Page Object Model usage."""
        lines = content.split('\n')
        
        # Check if file is a page object
        if 'page' in file_path.lower() or 'Page' in file_path:
            # Check class naming convention
            class_matches = re.finditer(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
            for match in class_matches:
                class_name = match.group(1)
                if not class_name.endswith('Page'):
                    line_num = content[:match.start()].count('\n') + 1
                    self._add_issue(
                        'pw-page-object-naming',
                        f'Page object class "{class_name}" should end with "Page" suffix',
                        'warning',
                        line_num,
                        match.start(),
                        file_path,
                        suggested_fix=f'{class_name}Page',
                        auto_fixable=True,
                        category='naming'
                    )
        
        # Check for direct page interactions in test files
        if '.spec.ts' in file_path or '.test.ts' in file_path:
            for line_num, line in enumerate(lines, 1):
                # Look for direct page.click, page.fill, etc. in test files
                if re.search(r'page\.(click|fill|type|selectOption)\s*\(', line):
                    self._add_issue(
                        'pw-page-object-pattern',
                        'Consider using Page Object Model instead of direct page interactions',
                        'warning',
                        line_num,
                        0,
                        file_path,
                        suggested_fix='Move interaction to a page object method',
                        category='architecture'
                    )
    
    def _check_locator_practices(self, content: str, file_path: str):
        """Check locator best practices."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for CSS selectors instead of semantic locators
            css_selector_patterns = [
                r'page\.locator\(["\'][\.\#][^"\']*["\']',  # CSS class/id selectors
                r'page\.locator\(["\'][^"\']*\[[^"\']*\][^"\']*["\']'  # Attribute selectors
            ]
            
            for pattern in css_selector_patterns:
                if re.search(pattern, line):
                    self._add_issue(
                        'pw-stable-locators',
                        'Use stable locators (getByTestId, getByRole, getByText) instead of CSS selectors',
                        'error',
                        line_num,
                        0,
                        file_path,
                        suggested_fix='Use page.getByTestId() or page.getByRole()',
                        category='locators'
                    )
            
            # Check for XPath usage
            if re.search(r'page\.locator\(["\']//[^"\']*["\']', line):
                self._add_issue(
                    'pw-no-xpath',
                    'Avoid XPath locators, use Playwright semantic locators instead',
                    'warning',
                    line_num,
                    0,
                    file_path,
                    suggested_fix='Use page.getByRole() or page.getByText()',
                    category='locators'
                )
            
            # Check for complex locators that should be stored in variables
            locator_match = re.search(r'page\.locator\(["\']([^"\']{30,})["\']', line)
            if locator_match:
                self._add_issue(
                    'pw-locator-variables',
                    'Complex locators should be stored in variables for reusability',
                    'warning',
                    line_num,
                    0,
                    file_path,
                    suggested_fix='const elementLocator = page.locator(...)',
                    category='locators'
                )
    
    def _check_waiting_patterns(self, content: str, file_path: str):
        """Check waiting and timing patterns."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for hard waits
            if re.search(r'page\.waitForTimeout\s*\(', line):
                self._add_issue(
                    'pw-explicit-waits',
                    'Avoid hard waits (waitForTimeout), use explicit waits instead',
                    'error',
                    line_num,
                    0,
                    file_path,
                    suggested_fix='Use page.waitForSelector() or page.waitForLoadState()',
                    category='waits'
                )
            
            # Check for sleep or setTimeout
            if re.search(r'(sleep|setTimeout)\s*\(', line):
                self._add_issue(
                    'pw-explicit-waits',
                    'Avoid sleep/setTimeout, use Playwright waiting methods',
                    'error',
                    line_num,
                    0,
                    file_path,
                    suggested_fix='Use Playwright auto-waiting or explicit waits',
                    category='waits'
                )
    
    def _check_test_structure(self, content: str, file_path: str):
        """Check test structure and organization."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check test naming
            test_match = re.search(r'test\s*\(\s*["\']([^"\']+)["\']', line)
            if test_match:
                test_name = test_match.group(1)
                if len(test_name) < 10 or not any(word in test_name.lower() for word in ['should', 'when', 'given']):
                    self._add_issue(
                        'pw-descriptive-test-names',
                        'Test names should be descriptive and follow Given-When-Then pattern',
                        'warning',
                        line_num,
                        test_match.start(),
                        file_path,
                        suggested_fix='Use descriptive names like "should login successfully with valid credentials"',
                        category='test-structure'
                    )
        
        # Check for test isolation
        if 'beforeAll' in content and 'login' in content.lower():
            self._add_issue(
                'pw-test-isolation',
                'Avoid shared state in beforeAll, use beforeEach for test isolation',
                'error',
                1,
                0,
                file_path,
                suggested_fix='Move setup to beforeEach for better test isolation',
                category='test-structure'
            )
    
    def _check_assertions(self, content: str, file_path: str):
        """Check assertion patterns."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for generic assertions instead of Playwright assertions
            if re.search(r'assert\s*\(', line) and 'expect' not in line:
                self._add_issue(
                    'pw-proper-assertions',
                    'Use Playwright assertions (expect) instead of generic assertions',
                    'warning',
                    line_num,
                    0,
                    file_path,
                    suggested_fix='Use await expect(locator).toBeVisible() instead',
                    auto_fixable=True,
                    category='assertions'
                )
            
            # Check for boolean assertions that could be more specific
            if re.search(r'expect\([^)]+\)\.toBe\(true\)', line):
                self._add_issue(
                    'pw-proper-assertions',
                    'Use specific Playwright assertions instead of toBe(true)',
                    'warning',
                    line_num,
                    0,
                    file_path,
                    suggested_fix='Use toBeVisible(), toBeEnabled(), etc.',
                    category='assertions'
                )
    
    def _check_performance_patterns(self, content: str, file_path: str):
        """Check performance-related patterns."""
        lines = content.split('\n')
        
        # Check for browser context usage
        if 'browser.newPage()' in content and 'context' not in content:
            self._add_issue(
                'pw-browser-context',
                'Use browser contexts for test isolation instead of new browser instances',
                'warning',
                1,
                0,
                file_path,
                suggested_fix='Use context.newPage() instead of browser.newPage()',
                category='performance'
            )
        
        # Check for parallel execution configuration
        if '.spec.ts' in file_path and 'test.describe.configure' not in content:
            self._add_issue(
                'pw-parallel-execution',
                'Consider configuring tests for parallel execution',
                'info',
                1,
                0,
                file_path,
                suggested_fix='Add test.describe.configure({ mode: "parallel" })',
                category='performance'
            )
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the Playwright analysis results."""
        return {
            'total_issues': len(self.issues),
            'errors': len([i for i in self.issues if i.severity == 'error']),
            'warnings': len([i for i in self.issues if i.severity == 'warning']),
            'info': len([i for i in self.issues if i.severity == 'info']),
            'auto_fixable': len([i for i in self.issues if i.auto_fixable]),
            'categories': list(set(i.category for i in self.issues)),
            'locator_issues': len([i for i in self.issues if i.category == 'locators']),
            'wait_issues': len([i for i in self.issues if i.category == 'waits'])
        }
