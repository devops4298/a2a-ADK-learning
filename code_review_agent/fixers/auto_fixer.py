"""
Automated code fixing functionality.
"""
import re
from typing import List, Dict, Any, Tuple
from ..analyzers.base_analyzer import CodeIssue
from ..linters.linter_manager import LinterManager


class AutoFixer:
    """Handles automated fixing of code issues."""
    
    def __init__(self):
        self.linter_manager = LinterManager()
        self.fix_patterns = self._initialize_fix_patterns()
    
    def _initialize_fix_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for automated fixes."""
        return {
            # TypeScript fixes
            'ts-prefer-const': {
                'pattern': r'\blet\s+(\w+)\s*=\s*([^;]+);',
                'replacement': r'const \1 = \2;',
                'condition': lambda match, content: self._is_never_reassigned(match.group(1), content)
            },
            'ts-no-console-log': {
                'pattern': r'console\.log\s*\([^)]*\);\s*\n?',
                'replacement': '',
                'condition': None
            },
            'ts-add-semicolon': {
                'pattern': r'(\w+.*[^;])\s*\n',
                'replacement': r'\1;\n',
                'condition': lambda match, content: self._should_add_semicolon(match.group(1))
            },
            
            # Naming convention fixes
            'ts-naming-camelcase': {
                'pattern': r'\b([a-z]+)_([a-z]+)\b',
                'replacement': lambda m: m.group(1) + m.group(2).capitalize(),
                'condition': lambda match, content: self._is_variable_name(match, content)
            },
            'ts-naming-constants': {
                'pattern': r'\bconst\s+([a-z][a-zA-Z0-9]*)\s*=',
                'replacement': lambda m: f'const {self._to_upper_snake_case(m.group(1))} =',
                'condition': lambda match, content: self._is_constant_value(match, content)
            },
            
            # Import fixes
            'ts-remove-unused-import': {
                'pattern': r'import\s+\{[^}]*\b(\w+)\b[^}]*\}\s+from\s+[^;]+;',
                'replacement': lambda m: self._remove_unused_from_import(m.group(0), m.group(1)),
                'condition': lambda match, content: not self._is_import_used(match.group(1), content)
            },
            
            # Playwright fixes
            'pw-stable-locators': {
                'pattern': r'page\.locator\(["\']([^"\']*#[^"\']*)["\']',
                'replacement': r'page.getByTestId("\1")',
                'condition': lambda match, content: '#' in match.group(1)
            },
            'pw-proper-assertions': {
                'pattern': r'assert\s*\(\s*await\s+([^)]+)\.isVisible\(\)\s*\)',
                'replacement': r'await expect(\1).toBeVisible()',
                'condition': None
            },
            
            # Formatting fixes
            'prettier-quotes': {
                'pattern': r'"([^"]*)"',
                'replacement': r"'\1'",
                'condition': lambda match, content: not self._is_in_json_context(match, content)
            },
            'prettier-spacing': {
                'pattern': r'(\w+)\s*:\s*(\w+)',
                'replacement': r'\1: \2',
                'condition': None
            }
        }
    
    def fix_content(self, content: str, file_path: str, issues: List[CodeIssue]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Automatically fix issues in content.
        
        Args:
            content: Original content
            file_path: Path to the file
            issues: List of issues to fix
            
        Returns:
            Tuple of (fixed_content, list_of_applied_fixes)
        """
        fixed_content = content
        applied_fixes = []
        
        # First, apply linter-based fixes
        linter_fixed = self.linter_manager.fix_content(content, file_path)
        if linter_fixed != content:
            applied_fixes.append({
                'type': 'linter_fix',
                'description': 'Applied automated linter fixes',
                'tool': 'linter_manager'
            })
            fixed_content = linter_fixed
        
        # Then apply pattern-based fixes for auto-fixable issues
        auto_fixable_issues = [issue for issue in issues if issue.auto_fixable]
        
        for issue in auto_fixable_issues:
            fix_result = self._apply_issue_fix(fixed_content, issue, file_path)
            if fix_result['success']:
                fixed_content = fix_result['content']
                applied_fixes.append({
                    'type': 'pattern_fix',
                    'rule_id': issue.rule_id,
                    'description': fix_result['description'],
                    'line_number': issue.line_number
                })
        
        return fixed_content, applied_fixes
    
    def _apply_issue_fix(self, content: str, issue: CodeIssue, file_path: str) -> Dict[str, Any]:
        """Apply a fix for a specific issue."""
        rule_id = issue.rule_id
        
        if rule_id in self.fix_patterns:
            pattern_info = self.fix_patterns[rule_id]
            return self._apply_pattern_fix(content, pattern_info, issue)
        
        # Try generic fixes based on issue type
        return self._apply_generic_fix(content, issue)
    
    def _apply_pattern_fix(self, content: str, pattern_info: Dict[str, Any], issue: CodeIssue) -> Dict[str, Any]:
        """Apply a pattern-based fix."""
        pattern = pattern_info['pattern']
        replacement = pattern_info['replacement']
        condition = pattern_info.get('condition')
        
        lines = content.split('\n')
        if issue.line_number <= len(lines):
            line = lines[issue.line_number - 1]
            
            match = re.search(pattern, line)
            if match:
                # Check condition if provided
                if condition and not condition(match, content):
                    return {'success': False, 'reason': 'Condition not met'}
                
                # Apply replacement
                if callable(replacement):
                    new_line = replacement(match)
                else:
                    new_line = re.sub(pattern, replacement, line)
                
                lines[issue.line_number - 1] = new_line
                fixed_content = '\n'.join(lines)
                
                return {
                    'success': True,
                    'content': fixed_content,
                    'description': f'Applied pattern fix for {issue.rule_id}'
                }
        
        return {'success': False, 'reason': 'Pattern not found'}
    
    def _apply_generic_fix(self, content: str, issue: CodeIssue) -> Dict[str, Any]:
        """Apply generic fixes based on issue characteristics."""
        if 'unused' in issue.description.lower() and 'import' in issue.description.lower():
            return self._fix_unused_import(content, issue)
        elif 'semicolon' in issue.description.lower():
            return self._fix_missing_semicolon(content, issue)
        elif 'spacing' in issue.description.lower():
            return self._fix_spacing_issue(content, issue)
        elif 'quote' in issue.description.lower():
            return self._fix_quote_style(content, issue)
        
        return {'success': False, 'reason': 'No generic fix available'}
    
    def _fix_unused_import(self, content: str, issue: CodeIssue) -> Dict[str, Any]:
        """Fix unused import statements."""
        lines = content.split('\n')
        if issue.line_number <= len(lines):
            line = lines[issue.line_number - 1]
            
            # Simple approach: comment out the unused import
            if line.strip().startswith('import'):
                lines[issue.line_number - 1] = f'// {line}'
                return {
                    'success': True,
                    'content': '\n'.join(lines),
                    'description': 'Commented out unused import'
                }
        
        return {'success': False, 'reason': 'Could not fix unused import'}
    
    def _fix_missing_semicolon(self, content: str, issue: CodeIssue) -> Dict[str, Any]:
        """Fix missing semicolons."""
        lines = content.split('\n')
        if issue.line_number <= len(lines):
            line = lines[issue.line_number - 1]
            
            if not line.rstrip().endswith(';'):
                lines[issue.line_number - 1] = line.rstrip() + ';'
                return {
                    'success': True,
                    'content': '\n'.join(lines),
                    'description': 'Added missing semicolon'
                }
        
        return {'success': False, 'reason': 'Could not add semicolon'}
    
    def _fix_spacing_issue(self, content: str, issue: CodeIssue) -> Dict[str, Any]:
        """Fix spacing issues."""
        lines = content.split('\n')
        if issue.line_number <= len(lines):
            line = lines[issue.line_number - 1]
            
            # Fix common spacing issues
            fixed_line = re.sub(r'(\w+)\s*:\s*(\w+)', r'\1: \2', line)  # Object property spacing
            fixed_line = re.sub(r'(\w+)\s*=\s*(\w+)', r'\1 = \2', fixed_line)  # Assignment spacing
            fixed_line = re.sub(r'(\w+)\s*\(\s*(\w+)', r'\1(\2', fixed_line)  # Function call spacing
            
            if fixed_line != line:
                lines[issue.line_number - 1] = fixed_line
                return {
                    'success': True,
                    'content': '\n'.join(lines),
                    'description': 'Fixed spacing issues'
                }
        
        return {'success': False, 'reason': 'Could not fix spacing'}
    
    def _fix_quote_style(self, content: str, issue: CodeIssue) -> Dict[str, Any]:
        """Fix quote style consistency."""
        lines = content.split('\n')
        if issue.line_number <= len(lines):
            line = lines[issue.line_number - 1]
            
            # Convert double quotes to single quotes (common preference)
            fixed_line = re.sub(r'"([^"]*)"', r"'\1'", line)
            
            if fixed_line != line:
                lines[issue.line_number - 1] = fixed_line
                return {
                    'success': True,
                    'content': '\n'.join(lines),
                    'description': 'Fixed quote style'
                }
        
        return {'success': False, 'reason': 'Could not fix quotes'}
    
    # Helper methods for conditions
    def _is_never_reassigned(self, var_name: str, content: str) -> bool:
        """Check if a variable is never reassigned."""
        # Simple heuristic: look for assignment patterns
        assignment_pattern = f'{var_name}\\s*='
        matches = re.findall(assignment_pattern, content)
        return len(matches) <= 1  # Only the initial declaration
    
    def _should_add_semicolon(self, line: str) -> bool:
        """Check if a semicolon should be added to a line."""
        line = line.strip()
        if not line or line.endswith((';', '{', '}', ':')):
            return False
        if line.startswith(('if', 'for', 'while', 'function', 'class')):
            return False
        return True
    
    def _is_variable_name(self, match, content: str) -> bool:
        """Check if the match is a variable name (not a property)."""
        # Simple check: ensure it's not after a dot
        start_pos = match.start()
        if start_pos > 0 and content[start_pos - 1] == '.':
            return False
        return True
    
    def _is_constant_value(self, match, content: str) -> bool:
        """Check if the value appears to be a constant."""
        # Look at the assigned value
        line = content.split('\n')[content[:match.start()].count('\n')]
        if re.search(r'=\s*[A-Z_][A-Z0-9_]*\s*[;\n]', line):
            return True
        if re.search(r'=\s*\d+\s*[;\n]', line):
            return True
        return False
    
    def _to_upper_snake_case(self, name: str) -> str:
        """Convert camelCase to UPPER_SNAKE_CASE."""
        return re.sub(r'([a-z])([A-Z])', r'\1_\2', name).upper()
    
    def _is_import_used(self, import_name: str, content: str) -> bool:
        """Check if an imported name is used in the content."""
        # Remove the import statement and check if the name appears
        import_removed = re.sub(r'import\s+[^;]+;', '', content)
        return import_name in import_removed
    
    def _remove_unused_from_import(self, import_statement: str, unused_name: str) -> str:
        """Remove an unused name from an import statement."""
        # Simple implementation - in practice, this would be more sophisticated
        return import_statement.replace(f', {unused_name}', '').replace(f'{unused_name}, ', '')
    
    def _is_in_json_context(self, match, content: str) -> bool:
        """Check if the match is within a JSON context."""
        # Simple heuristic: check if we're in a .json file or JSON-like structure
        return '.json' in content or 'JSON.parse' in content
    
    def get_fixable_issues_count(self, issues: List[CodeIssue]) -> Dict[str, int]:
        """Get count of fixable issues by type."""
        counts = {
            'auto_fixable': 0,
            'pattern_fixable': 0,
            'linter_fixable': 0,
            'manual_only': 0
        }
        
        for issue in issues:
            if issue.auto_fixable:
                counts['auto_fixable'] += 1
            elif issue.rule_id in self.fix_patterns:
                counts['pattern_fixable'] += 1
            elif issue.category in ['eslint', 'prettier']:
                counts['linter_fixable'] += 1
            else:
                counts['manual_only'] += 1
        
        return counts
