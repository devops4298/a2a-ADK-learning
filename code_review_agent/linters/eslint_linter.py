"""
ESLint integration for TypeScript linting.
"""
import json
import tempfile
import os
from typing import List, Dict, Any
from .base_linter import BaseLinter
from ..analyzers.base_analyzer import CodeIssue


class ESLintLinter(BaseLinter):
    """ESLint linter for TypeScript files."""
    
    def __init__(self):
        super().__init__('eslint')
        self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default ESLint configuration for TypeScript/Playwright projects."""
        return {
            "env": {
                "browser": True,
                "es2021": True,
                "node": True
            },
            "extends": [
                "eslint:recommended",
                "@typescript-eslint/recommended"
            ],
            "parser": "@typescript-eslint/parser",
            "parserOptions": {
                "ecmaVersion": 12,
                "sourceType": "module"
            },
            "plugins": [
                "@typescript-eslint"
            ],
            "rules": {
                # TypeScript specific rules
                "@typescript-eslint/no-unused-vars": "warn",
                "@typescript-eslint/no-explicit-any": "warn",
                "@typescript-eslint/explicit-function-return-type": "warn",
                "@typescript-eslint/no-inferrable-types": "off",
                "@typescript-eslint/prefer-const": "warn",
                
                # General JavaScript/TypeScript rules
                "no-console": "warn",
                "no-debugger": "error",
                "no-unused-vars": "off",  # Use TypeScript version instead
                "prefer-const": "warn",
                "no-var": "error",
                "eqeqeq": "error",
                "curly": "error",
                
                # Code style rules
                "indent": ["warn", 2],
                "quotes": ["warn", "single"],
                "semi": ["warn", "always"],
                "comma-dangle": ["warn", "never"],
                "object-curly-spacing": ["warn", "always"],
                "array-bracket-spacing": ["warn", "never"],
                
                # Playwright specific rules (if available)
                "no-await-in-loop": "warn",
                "require-await": "warn"
            },
            "overrides": [
                {
                    "files": ["*.spec.ts", "*.test.ts"],
                    "rules": {
                        "no-console": "off",  # Allow console in tests
                        "@typescript-eslint/no-explicit-any": "off"  # More lenient in tests
                    }
                }
            ]
        }
    
    def lint_content(self, content: str, file_path: str) -> List[CodeIssue]:
        """Lint TypeScript content using ESLint."""
        if not self.is_available():
            return [CodeIssue(
                rule_id='eslint-not-available',
                description='ESLint is not available. Install with: npm install -g eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin',
                severity='warning',
                line_number=1,
                file_path=file_path,
                category='system'
            )]
        
        # Create temporary files for content and config
        temp_file = self._create_temp_file(content, '.ts')
        config_file = self._create_temp_config()
        
        try:
            # Run ESLint
            command = [
                'eslint',
                '--config', config_file,
                '--format', 'json',
                '--no-eslintrc',
                temp_file
            ]
            
            result = self._run_command(command)
            
            if result['return_code'] in [0, 1]:  # 0 = no issues, 1 = issues found
                issues = self._parse_eslint_output(result['stdout'], file_path)
                return issues
            else:
                return [CodeIssue(
                    rule_id='eslint-error',
                    description=f'ESLint error: {result["stderr"]}',
                    severity='error',
                    line_number=1,
                    file_path=file_path,
                    category='system'
                )]
        
        finally:
            self._cleanup_temp_file(temp_file)
            self._cleanup_temp_file(config_file)
    
    def fix_content(self, content: str, file_path: str) -> str:
        """Fix content using ESLint's auto-fix capability."""
        if not self.is_available():
            return content
        
        temp_file = self._create_temp_file(content, '.ts')
        config_file = self._create_temp_config()
        
        try:
            # Run ESLint with --fix
            command = [
                'eslint',
                '--config', config_file,
                '--fix',
                '--no-eslintrc',
                temp_file
            ]
            
            result = self._run_command(command)
            
            # Read the fixed content
            try:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    fixed_content = f.read()
                return fixed_content
            except:
                return content
        
        finally:
            self._cleanup_temp_file(temp_file)
            self._cleanup_temp_file(config_file)
    
    def _create_temp_config(self) -> str:
        """Create a temporary ESLint config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
            return f.name
    
    def _parse_eslint_output(self, output: str, file_path: str) -> List[CodeIssue]:
        """Parse ESLint JSON output into CodeIssue objects."""
        issues = []
        
        try:
            eslint_results = json.loads(output)
            
            for file_result in eslint_results:
                for message in file_result.get('messages', []):
                    issue = CodeIssue(
                        rule_id=message.get('ruleId', 'eslint-unknown'),
                        description=message.get('message', 'Unknown ESLint issue'),
                        severity=self._map_eslint_severity(message.get('severity', 1)),
                        line_number=message.get('line', 1),
                        column=message.get('column', 0),
                        file_path=file_path,
                        auto_fixable=message.get('fix') is not None,
                        category='eslint'
                    )
                    issues.append(issue)
        
        except json.JSONDecodeError:
            pass
        
        return issues
    
    def _map_eslint_severity(self, severity: int) -> str:
        """Map ESLint severity to our standard severity levels."""
        if severity == 2:
            return 'error'
        elif severity == 1:
            return 'warning'
        else:
            return 'info'
    
    def is_available(self) -> bool:
        """Check if ESLint is available."""
        result = self._run_command(['eslint', '--version'])
        return result['return_code'] == 0
    
    def get_available_rules(self) -> List[str]:
        """Get list of available ESLint rules."""
        if not self.is_available():
            return []
        
        result = self._run_command(['eslint', '--print-config', '.'])
        if result['return_code'] == 0:
            try:
                config = json.loads(result['stdout'])
                return list(config.get('rules', {}).keys())
            except:
                pass
        
        return []
    
    def update_config(self, new_rules: Dict[str, Any]):
        """Update ESLint configuration with new rules."""
        self.config['rules'].update(new_rules)
    
    def add_playwright_rules(self):
        """Add Playwright-specific ESLint rules."""
        playwright_rules = {
            "playwright/missing-playwright-await": "error",
            "playwright/no-conditional-in-test": "warn",
            "playwright/no-element-handle": "warn",
            "playwright/no-eval": "error",
            "playwright/no-focused-test": "error",
            "playwright/no-force-option": "warn",
            "playwright/no-page-pause": "warn",
            "playwright/no-restricted-matchers": "warn",
            "playwright/no-skipped-test": "warn",
            "playwright/no-useless-await": "warn",
            "playwright/no-wait-for-timeout": "error",
            "playwright/prefer-web-first-assertions": "warn",
            "playwright/valid-expect": "error"
        }
        
        # Add playwright plugin if not already present
        if "eslint-plugin-playwright" not in self.config.get("plugins", []):
            self.config.setdefault("plugins", []).append("eslint-plugin-playwright")
        
        self.update_config(playwright_rules)
