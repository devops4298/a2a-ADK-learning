"""
Base linter class for all linting functionality.
"""
import subprocess
import json
import tempfile
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from ..analyzers.base_analyzer import CodeIssue


class BaseLinter:
    """Base class for all linters."""
    
    def __init__(self, name: str):
        self.name = name
        self.issues: List[CodeIssue] = []
    
    def lint_content(self, content: str, file_path: str) -> List[CodeIssue]:
        """
        Lint content and return issues found.
        
        Args:
            content: The code content to lint
            file_path: Path to the file (for context)
            
        Returns:
            List of CodeIssue objects
        """
        raise NotImplementedError("Subclasses must implement lint_content method")
    
    def lint_file(self, file_path: str) -> List[CodeIssue]:
        """
        Lint a file and return issues found.
        
        Args:
            file_path: Path to the file to lint
            
        Returns:
            List of CodeIssue objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.lint_content(content, file_path)
        except Exception as e:
            return [CodeIssue(
                rule_id=f'{self.name}-file-error',
                description=f'Could not lint file: {str(e)}',
                severity='error',
                line_number=1,
                file_path=file_path,
                category='system'
            )]
    
    def can_fix(self, issue: CodeIssue) -> bool:
        """Check if this linter can fix a specific issue."""
        return issue.auto_fixable
    
    def fix_content(self, content: str, file_path: str) -> str:
        """
        Fix issues in content and return the fixed content.
        
        Args:
            content: The code content to fix
            file_path: Path to the file (for context)
            
        Returns:
            Fixed content
        """
        raise NotImplementedError("Subclasses must implement fix_content method")
    
    def fix_file(self, file_path: str) -> bool:
        """
        Fix issues in a file.
        
        Args:
            file_path: Path to the file to fix
            
        Returns:
            True if fixes were applied, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            fixed_content = self.fix_content(original_content, file_path)
            
            if fixed_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                return True
            
            return False
        except Exception:
            return False
    
    def _run_command(self, command: List[str], input_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a command and return the result.
        
        Args:
            command: Command to run as list of strings
            input_content: Content to pass to stdin
            
        Returns:
            Dictionary with stdout, stderr, and return_code
        """
        try:
            process = subprocess.run(
                command,
                input=input_content,
                text=True,
                capture_output=True,
                timeout=30
            )
            
            return {
                'stdout': process.stdout,
                'stderr': process.stderr,
                'return_code': process.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': 'Command timed out',
                'return_code': 1
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'return_code': 1
            }
    
    def _create_temp_file(self, content: str, suffix: str = '.ts') -> str:
        """
        Create a temporary file with the given content.
        
        Args:
            content: Content to write to the file
            suffix: File extension
            
        Returns:
            Path to the temporary file
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    def _cleanup_temp_file(self, file_path: str):
        """Clean up a temporary file."""
        try:
            os.unlink(file_path)
        except:
            pass
    
    def _parse_json_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse JSON output from linter tools."""
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []
    
    def _convert_to_code_issue(self, linter_issue: Dict[str, Any], file_path: str) -> CodeIssue:
        """
        Convert a linter-specific issue to a CodeIssue object.
        Override this method in subclasses.
        """
        return CodeIssue(
            rule_id=linter_issue.get('ruleId', f'{self.name}-unknown'),
            description=linter_issue.get('message', 'Unknown issue'),
            severity=self._map_severity(linter_issue.get('severity', 'warning')),
            line_number=linter_issue.get('line', 1),
            column=linter_issue.get('column', 0),
            file_path=file_path,
            auto_fixable=linter_issue.get('fix') is not None,
            category=self.name
        )
    
    def _map_severity(self, linter_severity: Any) -> str:
        """Map linter-specific severity to our standard severity levels."""
        if isinstance(linter_severity, int):
            if linter_severity >= 2:
                return 'error'
            elif linter_severity == 1:
                return 'warning'
            else:
                return 'info'
        elif isinstance(linter_severity, str):
            severity_lower = linter_severity.lower()
            if severity_lower in ['error', 'fatal']:
                return 'error'
            elif severity_lower in ['warn', 'warning']:
                return 'warning'
            else:
                return 'info'
        return 'warning'
    
    def is_available(self) -> bool:
        """Check if the linter tool is available on the system."""
        raise NotImplementedError("Subclasses must implement is_available method")
