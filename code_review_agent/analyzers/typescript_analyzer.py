"""
TypeScript-specific code analyzer.
"""
import re
from typing import List, Dict, Any
from .base_analyzer import BaseAnalyzer, CodeIssue
from ..standards.typescript_standards import TypeScriptStandards


class TypeScriptAnalyzer(BaseAnalyzer):
    """Analyzer for TypeScript code files."""
    
    def __init__(self):
        super().__init__()
        self.standards = TypeScriptStandards()
    
    def _analyze_content(self, content: str, file_path: str):
        """Analyze TypeScript content for code quality issues."""
        self._check_naming_conventions(content, file_path)
        self._check_type_safety(content, file_path)
        self._check_code_structure(content, file_path)
        self._check_imports(content, file_path)
        self._check_error_handling(content, file_path)
    
    def _check_naming_conventions(self, content: str, file_path: str):
        """Check TypeScript naming conventions."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check variable declarations
            var_matches = re.finditer(r'(?:let|const|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
            for match in var_matches:
                var_name = match.group(1)
                
                # Check for constants (all caps)
                if 'const' in line and var_name.isupper():
                    if not self._check_naming_convention(var_name, 'UPPER_SNAKE_CASE'):
                        self._add_issue(
                            'ts-naming-constants',
                            f'Constant "{var_name}" should use UPPER_SNAKE_CASE',
                            'warning',
                            line_num,
                            match.start(1),
                            file_path,
                            auto_fixable=True,
                            category='naming'
                        )
                # Check for regular variables (camelCase)
                elif not var_name.isupper() and not self._check_naming_convention(var_name, 'camelCase'):
                    self._add_issue(
                        'ts-naming-camelcase',
                        f'Variable "{var_name}" should use camelCase',
                        'warning',
                        line_num,
                        match.start(1),
                        file_path,
                        auto_fixable=True,
                        category='naming'
                    )
            
            # Check function declarations
            func_matches = re.finditer(r'(?:function\s+|async\s+function\s+)([a-zA-Z_][a-zA-Z0-9_]*)', line)
            for match in func_matches:
                func_name = match.group(1)
                if not self._check_naming_convention(func_name, 'camelCase'):
                    self._add_issue(
                        'ts-naming-camelcase',
                        f'Function "{func_name}" should use camelCase',
                        'warning',
                        line_num,
                        match.start(1),
                        file_path,
                        auto_fixable=True,
                        category='naming'
                    )
            
            # Check class declarations
            class_matches = re.finditer(r'(?:class|interface)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
            for match in class_matches:
                class_name = match.group(1)
                if not self._check_naming_convention(class_name, 'PascalCase'):
                    self._add_issue(
                        'ts-naming-pascalcase-classes',
                        f'Class/Interface "{class_name}" should use PascalCase',
                        'warning',
                        line_num,
                        match.start(1),
                        file_path,
                        auto_fixable=True,
                        category='naming'
                    )
    
    def _check_type_safety(self, content: str, file_path: str):
        """Check TypeScript type safety issues."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for 'any' type usage
            if re.search(r':\s*any\b', line):
                self._add_issue(
                    'ts-no-any',
                    'Avoid using "any" type, use specific types instead',
                    'warning',
                    line_num,
                    0,
                    file_path,
                    category='type-safety'
                )
            
            # Check for function parameters without types
            func_param_matches = re.finditer(r'function\s+\w+\s*\(([^)]+)\)', line)
            for match in func_param_matches:
                params = match.group(1)
                # Simple check for untyped parameters
                if ':' not in params and params.strip() and not params.strip().startswith('...'):
                    self._add_issue(
                        'ts-explicit-types',
                        'Function parameters should have explicit types',
                        'error',
                        line_num,
                        match.start(),
                        file_path,
                        category='type-safety'
                    )
            
            # Check for potential null/undefined access
            if re.search(r'\w+\.\w+(?!\?)', line) and not re.search(r'\?\.|??', line):
                # This is a simplified check - in practice, you'd need more sophisticated analysis
                if 'user.' in line or 'data.' in line or 'response.' in line:
                    self._add_issue(
                        'ts-strict-null-checks',
                        'Consider using optional chaining (?.) or nullish coalescing (??)',
                        'warning',
                        line_num,
                        0,
                        file_path,
                        suggested_fix='Use optional chaining: obj?.property',
                        category='type-safety'
                    )
    
    def _check_code_structure(self, content: str, file_path: str):
        """Check code structure and organization."""
        lines = content.split('\n')
        
        # Check function length
        functions = self._extract_function_info(content)
        for func in functions:
            if func['length'] > 50:
                self._add_issue(
                    'ts-max-function-length',
                    f'Function is too long ({func["length"]} lines). Consider breaking it down.',
                    'warning',
                    func['line_number'],
                    0,
                    file_path,
                    category='structure'
                )
        
        # Check for let vs const
        for line_num, line in enumerate(lines, 1):
            let_matches = re.finditer(r'let\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line)
            for match in let_matches:
                var_name = match.group(1)
                # Simple heuristic: if variable is not reassigned in the same line or obvious loop
                if '++' not in line and '--' not in line and 'for' not in line:
                    self._add_issue(
                        'ts-prefer-const',
                        f'Variable "{var_name}" is never reassigned, use const instead of let',
                        'warning',
                        line_num,
                        match.start(),
                        file_path,
                        suggested_fix=f'const {var_name}',
                        auto_fixable=True,
                        category='structure'
                    )
    
    def _check_imports(self, content: str, file_path: str):
        """Check import statements and organization."""
        lines = content.split('\n')
        import_lines = []
        
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('import '):
                import_lines.append((line_num, line))
        
        # Check for unused imports (simplified)
        for line_num, import_line in import_lines:
            # Extract imported names
            import_match = re.search(r'import\s+(?:\{([^}]+)\}|\*\s+as\s+(\w+)|(\w+))', import_line)
            if import_match:
                if import_match.group(1):  # Named imports
                    imports = [name.strip() for name in import_match.group(1).split(',')]
                    for imported_name in imports:
                        # Simple check if import is used in the file
                        if imported_name not in content.replace(import_line, ''):
                            self._add_issue(
                                'ts-no-unused-imports',
                                f'Unused import: {imported_name}',
                                'warning',
                                line_num,
                                0,
                                file_path,
                                auto_fixable=True,
                                category='imports'
                            )
    
    def _check_error_handling(self, content: str, file_path: str):
        """Check error handling patterns."""
        lines = content.split('\n')
        
        # Check for async functions without try-catch
        for line_num, line in enumerate(lines, 1):
            if 'async ' in line and 'function' in line:
                # Look for try-catch in the function body (simplified check)
                function_body = self._get_function_body(content, line_num)
                if 'await' in function_body and 'try' not in function_body:
                    self._add_issue(
                        'ts-proper-error-handling',
                        'Async function with await should include proper error handling',
                        'error',
                        line_num,
                        0,
                        file_path,
                        suggested_fix='Wrap await calls in try-catch blocks',
                        category='error-handling'
                    )
    
    def _get_function_body(self, content: str, start_line: int) -> str:
        """Extract function body starting from a given line."""
        lines = content.split('\n')
        if start_line > len(lines):
            return ""
        
        body_lines = []
        brace_count = 0
        started = False
        
        for i in range(start_line - 1, len(lines)):
            line = lines[i]
            if '{' in line:
                started = True
            if started:
                body_lines.append(line)
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    break
        
        return '\n'.join(body_lines)

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis results."""
        return {
            'total_issues': len(self.issues),
            'errors': len([i for i in self.issues if i.severity == 'error']),
            'warnings': len([i for i in self.issues if i.severity == 'warning']),
            'info': len([i for i in self.issues if i.severity == 'info']),
            'auto_fixable': len([i for i in self.issues if i.auto_fixable]),
            'categories': list(set(i.category for i in self.issues))
        }
