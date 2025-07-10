"""
Linter manager that coordinates all linting tools.
"""
from typing import List, Dict, Any, Optional
from .eslint_linter import ESLintLinter
from .prettier_linter import PrettierLinter
from .custom_linter import CustomLinter
from ..analyzers.base_analyzer import CodeIssue


class LinterManager:
    """Manages and coordinates all linting tools."""
    
    def __init__(self):
        self.eslint = ESLintLinter()
        self.prettier = PrettierLinter()
        self.custom = CustomLinter()
        self.all_issues: List[CodeIssue] = []
    
    def lint_content(self, content: str, file_path: str, 
                    linters: Optional[List[str]] = None) -> List[CodeIssue]:
        """
        Lint content using specified linters.
        
        Args:
            content: Code content to lint
            file_path: Path to the file (for context)
            linters: List of linter names to use (default: all applicable)
            
        Returns:
            List of all issues found
        """
        all_issues = []
        
        # Determine which linters to run
        if linters is None:
            linters = self._get_applicable_linters(file_path)
        
        # Run each linter
        for linter_name in linters:
            try:
                if linter_name == 'eslint' and self._should_run_eslint(file_path):
                    issues = self.eslint.lint_content(content, file_path)
                    all_issues.extend(issues)
                
                elif linter_name == 'prettier' and self._should_run_prettier(file_path):
                    issues = self.prettier.lint_content(content, file_path)
                    all_issues.extend(issues)
                
                elif linter_name == 'custom':
                    issues = self.custom.lint_content(content, file_path)
                    all_issues.extend(issues)
                    
            except Exception as e:
                # Add error issue if linter fails
                all_issues.append(CodeIssue(
                    rule_id=f'{linter_name}-error',
                    description=f'Linter {linter_name} failed: {str(e)}',
                    severity='error',
                    line_number=1,
                    file_path=file_path,
                    category='system'
                ))
        
        self.all_issues = all_issues
        return all_issues
    
    def fix_content(self, content: str, file_path: str, 
                   linters: Optional[List[str]] = None) -> str:
        """
        Fix content using specified linters.
        
        Args:
            content: Code content to fix
            file_path: Path to the file (for context)
            linters: List of linter names to use for fixing
            
        Returns:
            Fixed content
        """
        fixed_content = content
        
        if linters is None:
            linters = self._get_applicable_linters(file_path)
        
        # Apply fixes in order: custom -> eslint -> prettier
        fix_order = ['custom', 'eslint', 'prettier']
        
        for linter_name in fix_order:
            if linter_name in linters:
                try:
                    if linter_name == 'custom':
                        fixed_content = self.custom.fix_content(fixed_content, file_path)
                    elif linter_name == 'eslint' and self._should_run_eslint(file_path):
                        fixed_content = self.eslint.fix_content(fixed_content, file_path)
                    elif linter_name == 'prettier' and self._should_run_prettier(file_path):
                        fixed_content = self.prettier.fix_content(fixed_content, file_path)
                except Exception:
                    # Continue with other linters if one fails
                    continue
        
        return fixed_content
    
    def _get_applicable_linters(self, file_path: str) -> List[str]:
        """Get list of linters applicable to the file type."""
        linters = ['custom']  # Custom linter always runs
        
        if self._should_run_eslint(file_path):
            linters.append('eslint')
        
        if self._should_run_prettier(file_path):
            linters.append('prettier')
        
        return linters
    
    def _should_run_eslint(self, file_path: str) -> bool:
        """Check if ESLint should run on this file."""
        return file_path.endswith(('.ts', '.js', '.tsx', '.jsx'))
    
    def _should_run_prettier(self, file_path: str) -> bool:
        """Check if Prettier should run on this file."""
        return self.prettier.can_format_file(file_path)
    
    def get_linter_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all linters."""
        return {
            'eslint': {
                'available': self.eslint.is_available(),
                'name': 'ESLint',
                'description': 'TypeScript/JavaScript linting',
                'supported_files': ['.ts', '.js', '.tsx', '.jsx']
            },
            'prettier': {
                'available': self.prettier.is_available(),
                'name': 'Prettier',
                'description': 'Code formatting',
                'supported_files': self.prettier.get_supported_languages()
            },
            'custom': {
                'available': self.custom.is_available(),
                'name': 'Custom Rules',
                'description': 'Project-specific linting rules',
                'supported_files': ['all']
            }
        }
    
    def get_auto_fixable_issues(self) -> List[CodeIssue]:
        """Get all issues that can be automatically fixed."""
        return [issue for issue in self.all_issues if issue.auto_fixable]
    
    def get_issues_by_linter(self, linter_name: str) -> List[CodeIssue]:
        """Get issues from a specific linter."""
        return [issue for issue in self.all_issues if issue.category == linter_name]
    
    def get_critical_issues(self) -> List[CodeIssue]:
        """Get all critical (error severity) issues."""
        return [issue for issue in self.all_issues if issue.severity == 'error']
    
    def generate_fix_summary(self, original_content: str, fixed_content: str) -> Dict[str, Any]:
        """Generate a summary of fixes applied."""
        if original_content == fixed_content:
            return {
                'fixes_applied': False,
                'changes_count': 0,
                'summary': 'No fixes were applied'
            }
        
        original_lines = original_content.split('\n')
        fixed_lines = fixed_content.split('\n')
        
        changes = []
        max_lines = max(len(original_lines), len(fixed_lines))
        
        for i in range(max_lines):
            original_line = original_lines[i] if i < len(original_lines) else ''
            fixed_line = fixed_lines[i] if i < len(fixed_lines) else ''
            
            if original_line != fixed_line:
                changes.append({
                    'line_number': i + 1,
                    'original': original_line,
                    'fixed': fixed_line,
                    'change_type': self._classify_change(original_line, fixed_line)
                })
        
        return {
            'fixes_applied': True,
            'changes_count': len(changes),
            'changes': changes[:10],  # Limit to first 10 changes
            'summary': f'{len(changes)} lines were modified'
        }
    
    def _classify_change(self, original: str, fixed: str) -> str:
        """Classify the type of change made."""
        if not original and fixed:
            return 'line_added'
        elif original and not fixed:
            return 'line_removed'
        elif original.strip() == fixed.strip():
            return 'whitespace_change'
        elif original.replace(' ', '') == fixed.replace(' ', ''):
            return 'spacing_change'
        else:
            return 'content_change'
    
    def configure_eslint(self, rules: Dict[str, Any]):
        """Configure ESLint rules."""
        self.eslint.update_config(rules)
    
    def configure_prettier(self, config: Dict[str, Any]):
        """Configure Prettier settings."""
        self.prettier.update_config(config)
    
    def add_custom_rule(self, rule: Dict[str, Any]):
        """Add a custom linting rule."""
        self.custom.add_custom_rule(rule)
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive linting report."""
        if not self.all_issues:
            return {
                'status': 'clean',
                'message': 'No issues found'
            }
        
        # Group issues by severity and category
        severity_counts = {}
        category_counts = {}
        linter_counts = {}
        
        for issue in self.all_issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
            
            # Determine linter from category or rule_id
            linter = issue.category if issue.category in ['eslint', 'prettier', 'custom'] else 'analyzer'
            linter_counts[linter] = linter_counts.get(linter, 0) + 1
        
        # Calculate overall score
        total_issues = len(self.all_issues)
        error_count = severity_counts.get('error', 0)
        warning_count = severity_counts.get('warning', 0)
        
        # Score calculation: errors are weighted more heavily
        score = max(0, 100 - (error_count * 10 + warning_count * 5))
        
        return {
            'total_issues': total_issues,
            'severity_breakdown': severity_counts,
            'category_breakdown': category_counts,
            'linter_breakdown': linter_counts,
            'auto_fixable_count': len(self.get_auto_fixable_issues()),
            'quality_score': score,
            'status': 'needs_attention' if error_count > 0 else 'good' if warning_count < 5 else 'fair',
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on found issues."""
        recommendations = []
        
        error_count = len([i for i in self.all_issues if i.severity == 'error'])
        warning_count = len([i for i in self.all_issues if i.severity == 'warning'])
        auto_fixable_count = len(self.get_auto_fixable_issues())
        
        if error_count > 0:
            recommendations.append(f"Fix {error_count} critical error(s) immediately")
        
        if auto_fixable_count > 0:
            recommendations.append(f"Run auto-fix to resolve {auto_fixable_count} issue(s) automatically")
        
        if warning_count > 10:
            recommendations.append("Consider addressing warnings to improve code quality")
        
        # Linter-specific recommendations
        eslint_issues = len(self.get_issues_by_linter('eslint'))
        prettier_issues = len(self.get_issues_by_linter('prettier'))
        
        if eslint_issues > 5:
            recommendations.append("Review ESLint configuration for your project needs")
        
        if prettier_issues > 0:
            recommendations.append("Set up Prettier in your IDE for automatic formatting")
        
        return recommendations
