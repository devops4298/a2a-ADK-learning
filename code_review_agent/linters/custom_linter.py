"""
Custom linter for project-specific rules and patterns.
"""
import re
from typing import List, Dict, Any
from .base_linter import BaseLinter
from ..analyzers.base_analyzer import CodeIssue


class CustomLinter(BaseLinter):
    """Custom linter for project-specific rules."""
    
    def __init__(self):
        super().__init__('custom')
        self.custom_rules = self._initialize_custom_rules()
    
    def _initialize_custom_rules(self) -> List[Dict[str, Any]]:
        """Initialize custom linting rules."""
        return [
            # Playwright-specific custom rules
            {
                'id': 'pw-no-hardcoded-selectors',
                'pattern': r'page\.locator\(["\'][^"\']*#[^"\']*["\']',
                'message': 'Avoid hardcoded CSS ID selectors, use data-testid instead',
                'severity': 'warning',
                'category': 'playwright',
                'auto_fixable': False,
                'suggestion': 'Use page.getByTestId("element-id") instead'
            },
            {
                'id': 'pw-no-sleep-in-tests',
                'pattern': r'(sleep|setTimeout|delay)\s*\(',
                'message': 'Avoid sleep/setTimeout in tests, use Playwright waiting methods',
                'severity': 'error',
                'category': 'playwright',
                'auto_fixable': False,
                'suggestion': 'Use page.waitForSelector() or expect().toBeVisible()'
            },
            {
                'id': 'pw-consistent-test-structure',
                'pattern': r'test\s*\(\s*["\'][^"\']{1,10}["\']',
                'message': 'Test names should be descriptive (more than 10 characters)',
                'severity': 'warning',
                'category': 'playwright',
                'auto_fixable': False,
                'suggestion': 'Use descriptive test names like "should login with valid credentials"'
            },
            
            # TypeScript custom rules
            {
                'id': 'ts-no-magic-numbers',
                'pattern': r'(?<![\w\.])\d{2,}(?![\w\.])',
                'message': 'Avoid magic numbers, use named constants',
                'severity': 'warning',
                'category': 'typescript',
                'auto_fixable': False,
                'suggestion': 'Define constants: const MAX_RETRIES = 3'
            },
            {
                'id': 'ts-consistent-error-handling',
                'pattern': r'catch\s*\(\s*\w+\s*\)\s*\{\s*\}',
                'message': 'Empty catch blocks should be avoided',
                'severity': 'error',
                'category': 'typescript',
                'auto_fixable': False,
                'suggestion': 'Add proper error handling or logging'
            },
            {
                'id': 'ts-no-console-log',
                'pattern': r'console\.log\s*\(',
                'message': 'Remove console.log statements before committing',
                'severity': 'warning',
                'category': 'typescript',
                'auto_fixable': True,
                'suggestion': 'Use proper logging or remove debug statements'
            },

            # Converted from JavaScript ESLint rule: no-console-in-tests
            {
                'id': 'pw-no-console-in-tests',
                'pattern': r'console\.(log|warn|error|info|debug)\s*\(',
                'message': 'Avoid using console statements in Playwright tests. Use `test.step` or `reporter` for debugging/logging.',
                'severity': 'warning',
                'category': 'playwright',
                'auto_fixable': True,
                'suggestion': 'Replace with test.step() for debugging or remove console statements'
            },
            
            # Cucumber custom rules
            {
                'id': 'cucumber-step-length',
                'pattern': r'(Given|When|Then|And|But)\s+.{100,}',
                'message': 'Gherkin steps should be concise (under 100 characters)',
                'severity': 'warning',
                'category': 'cucumber',
                'auto_fixable': False,
                'suggestion': 'Break long steps into multiple shorter steps'
            },
            {
                'id': 'cucumber-no-technical-details',
                'pattern': r'(Given|When|Then|And|But).*\b(API|HTTP|JSON|XML|database|DB)\b',
                'message': 'Avoid technical implementation details in Gherkin steps',
                'severity': 'warning',
                'category': 'cucumber',
                'auto_fixable': False,
                'suggestion': 'Focus on business behavior, not technical implementation'
            },
            
            # General project rules
            {
                'id': 'project-todo-comments',
                'pattern': r'(TODO|FIXME|HACK|XXX):',
                'message': 'TODO/FIXME comments should be tracked in issue tracker',
                'severity': 'info',
                'category': 'maintenance',
                'auto_fixable': False,
                'suggestion': 'Create tickets for TODO items and reference them'
            },
            {
                'id': 'project-no-sensitive-data',
                'pattern': r'(password|secret|key|token)\s*[:=]\s*["\'][^"\']+["\']',
                'message': 'Potential sensitive data in code',
                'severity': 'error',
                'category': 'security',
                'auto_fixable': False,
                'suggestion': 'Use environment variables for sensitive data'
            },
            {
                'id': 'project-consistent-naming',
                'pattern': r'(test|spec).*\.(js|ts)$',
                'message': 'Test files should follow consistent naming convention',
                'severity': 'info',
                'category': 'naming',
                'auto_fixable': False,
                'suggestion': 'Use .spec.ts or .test.ts consistently'
            }
        ]
    
    def lint_content(self, content: str, file_path: str) -> List[CodeIssue]:
        """Apply custom linting rules to content."""
        issues = []
        lines = content.split('\n')
        
        # Apply rules based on file type
        applicable_rules = self._get_applicable_rules(file_path)
        
        for rule in applicable_rules:
            issues.extend(self._apply_rule(rule, content, lines, file_path))
        
        return issues
    
    def _get_applicable_rules(self, file_path: str) -> List[Dict[str, Any]]:
        """Get rules applicable to the file type."""
        applicable_rules = []

        for rule in self.custom_rules:
            category = rule.get('category', '')
            rule_id = rule.get('id', '')

            # Apply rules based on file type and category
            if category == 'playwright' and ('.spec.ts' in file_path or '.test.ts' in file_path):
                applicable_rules.append(rule)
            elif category == 'typescript' and file_path.endswith(('.ts', '.js')):
                # Skip the general console.log rule for test files if we have the specific Playwright rule
                if rule_id == 'ts-no-console-log' and ('.spec.ts' in file_path or '.test.ts' in file_path):
                    continue  # Let the Playwright-specific rule handle this
                applicable_rules.append(rule)
            elif category == 'cucumber' and file_path.endswith('.feature'):
                applicable_rules.append(rule)
            elif category in ['maintenance', 'security', 'naming']:
                applicable_rules.append(rule)

        return applicable_rules
    
    def _apply_rule(self, rule: Dict[str, Any], content: str, lines: List[str], file_path: str) -> List[CodeIssue]:
        """Apply a single rule to the content."""
        issues = []
        pattern = rule['pattern']
        rule_id = rule['id']

        # Apply rule line by line
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(pattern, line, re.IGNORECASE)

            for match in matches:
                # Skip if it's in a comment (simple check)
                if self._is_in_comment(line, match.start()):
                    continue

                # Special handling for console rules in test files
                if rule_id == 'pw-no-console-in-tests':
                    # Extract the console method for more specific messaging
                    console_method = match.group(1) if match.groups() else 'log'
                    custom_message = f'Avoid using console.{console_method}() in Playwright tests. Use `test.step()` or `reporter` for debugging/logging.'
                    custom_suggestion = f'Replace console.{console_method}() with test.step() or remove for production'
                else:
                    custom_message = rule['message']
                    custom_suggestion = rule.get('suggestion')

                issue = CodeIssue(
                    rule_id=rule['id'],
                    description=custom_message,
                    severity=rule['severity'],
                    line_number=line_num,
                    column=match.start(),
                    file_path=file_path,
                    auto_fixable=rule.get('auto_fixable', False),
                    category=rule.get('category', 'custom'),
                    suggested_fix=custom_suggestion
                )
                issues.append(issue)

        return issues
    
    def _is_in_comment(self, line: str, position: int) -> bool:
        """Check if a position in a line is within a comment."""
        # Simple check for single-line comments
        comment_start = line.find('//')
        if comment_start != -1 and position > comment_start:
            return True
        
        # Check for multi-line comment start
        if '/*' in line[:position]:
            return True
        
        return False
    
    def fix_content(self, content: str, file_path: str) -> str:
        """Apply auto-fixes for custom rules."""
        fixed_content = content
        
        # Apply auto-fixable rules
        for rule in self.custom_rules:
            if rule.get('auto_fixable', False):
                fixed_content = self._apply_auto_fix(rule, fixed_content)
        
        return fixed_content
    
    def _apply_auto_fix(self, rule: Dict[str, Any], content: str) -> str:
        """Apply auto-fix for a specific rule."""
        rule_id = rule['id']

        if rule_id == 'ts-no-console-log':
            # Remove console.log statements
            return re.sub(r'console\.log\s*\([^)]*\);\s*\n?', '', content)
        elif rule_id == 'pw-no-console-in-tests':
            # Remove all console statements in Playwright tests
            # Pattern matches: console.log, console.warn, console.error, console.info, console.debug
            return re.sub(r'console\.(log|warn|error|info|debug)\s*\([^)]*\);\s*\n?', '', content)

        # Add more auto-fixes as needed
        return content
    
    def add_custom_rule(self, rule: Dict[str, Any]):
        """Add a new custom rule."""
        required_fields = ['id', 'pattern', 'message', 'severity', 'category']
        
        if all(field in rule for field in required_fields):
            self.custom_rules.append(rule)
        else:
            raise ValueError(f"Rule must contain all required fields: {required_fields}")
    
    def remove_custom_rule(self, rule_id: str):
        """Remove a custom rule by ID."""
        self.custom_rules = [rule for rule in self.custom_rules if rule['id'] != rule_id]
    
    def get_rules_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all rules for a specific category."""
        return [rule for rule in self.custom_rules if rule.get('category') == category]
    
    def is_available(self) -> bool:
        """Custom linter is always available."""
        return True
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """Get statistics about custom rules."""
        categories = {}
        severities = {}
        auto_fixable_count = 0
        
        for rule in self.custom_rules:
            category = rule.get('category', 'unknown')
            severity = rule.get('severity', 'unknown')
            
            categories[category] = categories.get(category, 0) + 1
            severities[severity] = severities.get(severity, 0) + 1
            
            if rule.get('auto_fixable', False):
                auto_fixable_count += 1
        
        return {
            'total_rules': len(self.custom_rules),
            'categories': categories,
            'severities': severities,
            'auto_fixable': auto_fixable_count,
            'manual_fix_required': len(self.custom_rules) - auto_fixable_count
        }
