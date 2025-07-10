"""
Base analyzer class for code analysis functionality.
"""
import re
import ast
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodeIssue:
    """Represents a code quality issue found during analysis."""
    rule_id: str
    description: str
    severity: str  # 'error', 'warning', 'info'
    line_number: int
    column: int = 0
    file_path: str = ""
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False
    category: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary format."""
        return {
            'rule_id': self.rule_id,
            'description': self.description,
            'severity': self.severity,
            'line_number': self.line_number,
            'column': self.column,
            'file_path': self.file_path,
            'suggested_fix': self.suggested_fix,
            'auto_fixable': self.auto_fixable,
            'category': self.category
        }


class BaseAnalyzer:
    """Base class for all code analyzers."""
    
    def __init__(self):
        self.issues: List[CodeIssue] = []
    
    def analyze_file(self, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze a file and return list of issues found."""
        self.issues = []
        self._analyze_content(content, file_path)
        return self.issues
    
    def _analyze_content(self, content: str, file_path: str):
        """Override this method in subclasses to implement specific analysis."""
        raise NotImplementedError("Subclasses must implement _analyze_content method")
    
    def _add_issue(self, rule_id: str, description: str, severity: str, 
                   line_number: int, column: int = 0, file_path: str = "",
                   suggested_fix: Optional[str] = None, auto_fixable: bool = False,
                   category: str = ""):
        """Add an issue to the issues list."""
        issue = CodeIssue(
            rule_id=rule_id,
            description=description,
            severity=severity,
            line_number=line_number,
            column=column,
            file_path=file_path,
            suggested_fix=suggested_fix,
            auto_fixable=auto_fixable,
            category=category
        )
        self.issues.append(issue)
    
    def _get_line_content(self, content: str, line_number: int) -> str:
        """Get the content of a specific line."""
        lines = content.split('\n')
        if 0 <= line_number - 1 < len(lines):
            return lines[line_number - 1]
        return ""
    
    def _count_lines(self, content: str) -> int:
        """Count the number of lines in content."""
        return len(content.split('\n'))
    
    def _find_pattern_in_lines(self, content: str, pattern: str, flags: int = 0) -> List[Dict[str, Any]]:
        """Find a regex pattern in content and return matches with line numbers."""
        matches = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for match in re.finditer(pattern, line, flags):
                matches.append({
                    'line_number': line_num,
                    'column': match.start(),
                    'match': match.group(),
                    'line_content': line
                })
        
        return matches
    
    def _is_comment_line(self, line: str) -> bool:
        """Check if a line is a comment."""
        stripped = line.strip()
        return stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*')
    
    def _is_empty_line(self, line: str) -> bool:
        """Check if a line is empty or contains only whitespace."""
        return line.strip() == ""
    
    def _extract_function_info(self, content: str) -> List[Dict[str, Any]]:
        """Extract function information from content."""
        functions = []
        
        # Pattern to match function declarations
        function_pattern = r'(?:async\s+)?(?:function\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{'
        
        matches = self._find_pattern_in_lines(content, function_pattern, re.MULTILINE)
        
        for match in matches:
            # Count lines in function body (simplified)
            lines_after = content.split('\n')[match['line_number']:]
            brace_count = 0
            function_lines = 0
            
            for line in lines_after:
                function_lines += 1
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    break
            
            functions.append({
                'name': match['match'],
                'line_number': match['line_number'],
                'length': function_lines
            })
        
        return functions
    
    def _check_naming_convention(self, name: str, convention: str) -> bool:
        """Check if a name follows a specific naming convention."""
        if convention == 'camelCase':
            return re.match(r'^[a-z][a-zA-Z0-9]*$', name) is not None
        elif convention == 'PascalCase':
            return re.match(r'^[A-Z][a-zA-Z0-9]*$', name) is not None
        elif convention == 'UPPER_SNAKE_CASE':
            return re.match(r'^[A-Z][A-Z0-9_]*$', name) is not None
        elif convention == 'snake_case':
            return re.match(r'^[a-z][a-z0-9_]*$', name) is not None
        return False
