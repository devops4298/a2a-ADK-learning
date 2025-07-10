"""
Prettier integration for code formatting.
"""
import json
import tempfile
from typing import List, Dict, Any
from .base_linter import BaseLinter
from ..analyzers.base_analyzer import CodeIssue


class PrettierLinter(BaseLinter):
    """Prettier formatter for TypeScript and other files."""
    
    def __init__(self):
        super().__init__('prettier')
        self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default Prettier configuration."""
        return {
            "semi": True,
            "trailingComma": "es5",
            "singleQuote": True,
            "printWidth": 100,
            "tabWidth": 2,
            "useTabs": False,
            "bracketSpacing": True,
            "bracketSameLine": False,
            "arrowParens": "avoid",
            "endOfLine": "lf",
            "quoteProps": "as-needed",
            "jsxSingleQuote": True,
            "proseWrap": "preserve",
            "htmlWhitespaceSensitivity": "css",
            "embeddedLanguageFormatting": "auto"
        }
    
    def lint_content(self, content: str, file_path: str) -> List[CodeIssue]:
        """Check if content is properly formatted using Prettier."""
        if not self.is_available():
            return [CodeIssue(
                rule_id='prettier-not-available',
                description='Prettier is not available. Install with: npm install -g prettier',
                severity='warning',
                line_number=1,
                file_path=file_path,
                category='system'
            )]
        
        # Create temporary files
        temp_file = self._create_temp_file(content, self._get_file_extension(file_path))
        config_file = self._create_temp_config()
        
        try:
            # Check if file is formatted
            command = [
                'prettier',
                '--config', config_file,
                '--check',
                temp_file
            ]
            
            result = self._run_command(command)
            
            if result['return_code'] != 0:
                # File is not properly formatted
                return [CodeIssue(
                    rule_id='prettier-formatting',
                    description='File is not properly formatted according to Prettier rules',
                    severity='warning',
                    line_number=1,
                    file_path=file_path,
                    auto_fixable=True,
                    category='formatting',
                    suggested_fix='Run Prettier to format the file'
                )]
            
            return []  # No formatting issues
        
        finally:
            self._cleanup_temp_file(temp_file)
            self._cleanup_temp_file(config_file)
    
    def fix_content(self, content: str, file_path: str) -> str:
        """Format content using Prettier."""
        if not self.is_available():
            return content
        
        temp_file = self._create_temp_file(content, self._get_file_extension(file_path))
        config_file = self._create_temp_config()
        
        try:
            # Format the file
            command = [
                'prettier',
                '--config', config_file,
                '--write',
                temp_file
            ]
            
            result = self._run_command(command)
            
            if result['return_code'] == 0:
                # Read the formatted content
                try:
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        formatted_content = f.read()
                    return formatted_content
                except:
                    return content
            
            return content
        
        finally:
            self._cleanup_temp_file(temp_file)
            self._cleanup_temp_file(config_file)
    
    def format_content_direct(self, content: str, file_path: str) -> str:
        """Format content directly using Prettier stdin/stdout."""
        if not self.is_available():
            return content
        
        config_file = self._create_temp_config()
        
        try:
            # Use stdin/stdout for formatting
            command = [
                'prettier',
                '--config', config_file,
                '--stdin-filepath', file_path
            ]
            
            result = self._run_command(command, input_content=content)
            
            if result['return_code'] == 0 and result['stdout']:
                return result['stdout']
            
            return content
        
        finally:
            self._cleanup_temp_file(config_file)
    
    def _create_temp_config(self) -> str:
        """Create a temporary Prettier config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
            return f.name
    
    def _get_file_extension(self, file_path: str) -> str:
        """Get appropriate file extension for temporary file."""
        if file_path.endswith('.ts'):
            return '.ts'
        elif file_path.endswith('.js'):
            return '.js'
        elif file_path.endswith('.json'):
            return '.json'
        elif file_path.endswith('.md'):
            return '.md'
        elif file_path.endswith('.yml') or file_path.endswith('.yaml'):
            return '.yml'
        else:
            return '.ts'  # Default to TypeScript
    
    def is_available(self) -> bool:
        """Check if Prettier is available."""
        result = self._run_command(['prettier', '--version'])
        return result['return_code'] == 0
    
    def check_formatting_issues(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Get detailed formatting issues by comparing original and formatted content."""
        formatted_content = self.format_content_direct(content, file_path)
        
        if formatted_content == content:
            return []
        
        # Simple line-by-line comparison
        original_lines = content.split('\n')
        formatted_lines = formatted_content.split('\n')
        
        issues = []
        max_lines = max(len(original_lines), len(formatted_lines))
        
        for i in range(max_lines):
            original_line = original_lines[i] if i < len(original_lines) else ''
            formatted_line = formatted_lines[i] if i < len(formatted_lines) else ''
            
            if original_line != formatted_line:
                issues.append({
                    'line_number': i + 1,
                    'original': original_line,
                    'formatted': formatted_line,
                    'type': self._classify_formatting_issue(original_line, formatted_line)
                })
        
        return issues
    
    def _classify_formatting_issue(self, original: str, formatted: str) -> str:
        """Classify the type of formatting issue."""
        if len(original.strip()) == 0 and len(formatted.strip()) == 0:
            return 'whitespace'
        elif original.strip() == formatted.strip():
            return 'indentation'
        elif original.replace(' ', '') == formatted.replace(' ', ''):
            return 'spacing'
        elif original.replace('"', "'") == formatted.replace('"', "'"):
            return 'quotes'
        elif original.rstrip(';') == formatted.rstrip(';'):
            return 'semicolon'
        else:
            return 'formatting'
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update Prettier configuration."""
        self.config.update(new_config)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of languages supported by Prettier."""
        if not self.is_available():
            return []
        
        result = self._run_command(['prettier', '--support-info'])
        if result['return_code'] == 0:
            try:
                support_info = json.loads(result['stdout'])
                languages = support_info.get('languages', [])
                return [lang.get('name', '') for lang in languages]
            except:
                pass
        
        # Default supported languages
        return [
            'JavaScript', 'TypeScript', 'JSON', 'CSS', 'SCSS', 
            'HTML', 'Markdown', 'YAML', 'GraphQL'
        ]
    
    def can_format_file(self, file_path: str) -> bool:
        """Check if Prettier can format a specific file type."""
        supported_extensions = [
            '.js', '.jsx', '.ts', '.tsx', '.json', '.css', '.scss', 
            '.less', '.html', '.md', '.yml', '.yaml', '.graphql'
        ]
        
        return any(file_path.endswith(ext) for ext in supported_extensions)
