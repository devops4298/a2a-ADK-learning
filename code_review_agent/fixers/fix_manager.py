"""
Fix manager that coordinates automated and manual fixing.
"""
from typing import List, Dict, Any, Tuple, Optional
from .auto_fixer import AutoFixer
from .manual_fixer import ManualFixer
from ..analyzers.base_analyzer import CodeIssue


class FixManager:
    """Manages both automated and manual fixing processes."""
    
    def __init__(self):
        self.auto_fixer = AutoFixer()
        self.manual_fixer = ManualFixer()
    
    def one_click_fix(self, content: str, file_path: str, issues: List[CodeIssue]) -> Dict[str, Any]:
        """
        Perform one-click fix: apply all possible automated fixes and provide manual suggestions.
        
        Args:
            content: Original file content
            file_path: Path to the file
            issues: List of issues to fix
            
        Returns:
            Comprehensive fix result with automated fixes and manual suggestions
        """
        # Separate auto-fixable and manual issues
        auto_fixable_issues = [issue for issue in issues if issue.auto_fixable]
        manual_issues = [issue for issue in issues if not issue.auto_fixable]
        
        # Apply automated fixes
        fixed_content, applied_fixes = self.auto_fixer.fix_content(content, file_path, auto_fixable_issues)
        
        # Generate manual suggestions
        manual_suggestions = self.manual_fixer.get_manual_suggestions(manual_issues)
        
        # Calculate fix statistics
        fix_stats = self._calculate_fix_statistics(issues, applied_fixes, manual_suggestions)
        
        return {
            'original_content': content,
            'fixed_content': fixed_content,
            'content_changed': fixed_content != content,
            'applied_fixes': applied_fixes,
            'manual_suggestions': manual_suggestions,
            'fix_statistics': fix_stats,
            'next_steps': self._generate_next_steps(applied_fixes, manual_suggestions),
            'quality_improvement': self._calculate_quality_improvement(issues, applied_fixes)
        }
    
    def fix_file(self, file_path: str, issues: Optional[List[CodeIssue]] = None) -> Dict[str, Any]:
        """
        Fix a file directly, reading content and writing back fixes.
        
        Args:
            file_path: Path to the file to fix
            issues: Optional list of issues (will analyze if not provided)
            
        Returns:
            Fix result with file modification status
        """
        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # If no issues provided, we need to analyze first
            if issues is None:
                from ..analyzers.file_analyzer import FileAnalyzer
                analyzer = FileAnalyzer()
                issues = analyzer.analyze_file(file_path, original_content)
            
            # Apply one-click fix
            fix_result = self.one_click_fix(original_content, file_path, issues)
            
            # Write back fixed content if changes were made
            if fix_result['content_changed']:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fix_result['fixed_content'])
                
                fix_result['file_modified'] = True
                fix_result['backup_created'] = self._create_backup(file_path, original_content)
            else:
                fix_result['file_modified'] = False
                fix_result['backup_created'] = False
            
            return fix_result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_modified': False
            }
    
    def fix_directory(self, directory_path: str, file_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Apply one-click fix to all files in a directory.
        
        Args:
            directory_path: Path to directory
            file_patterns: File patterns to include
            
        Returns:
            Summary of fixes applied across all files
        """
        from ..analyzers.file_analyzer import FileAnalyzer
        from pathlib import Path
        
        analyzer = FileAnalyzer()
        
        # Analyze all files in directory
        analysis_results = analyzer.analyze_directory(directory_path, file_patterns)
        
        fix_results = {}
        total_fixes = 0
        total_suggestions = 0
        modified_files = []
        
        for file_path, issues in analysis_results.items():
            if file_path != 'error':  # Skip error entries
                fix_result = self.fix_file(file_path, issues)
                fix_results[file_path] = fix_result
                
                if fix_result.get('file_modified', False):
                    modified_files.append(file_path)
                
                total_fixes += len(fix_result.get('applied_fixes', []))
                total_suggestions += len(fix_result.get('manual_suggestions', []))
        
        return {
            'directory': directory_path,
            'files_processed': len(fix_results),
            'files_modified': len(modified_files),
            'modified_files': modified_files,
            'total_automated_fixes': total_fixes,
            'total_manual_suggestions': total_suggestions,
            'file_results': fix_results,
            'summary': self._generate_directory_summary(fix_results)
        }
    
    def preview_fixes(self, content: str, file_path: str, issues: List[CodeIssue]) -> Dict[str, Any]:
        """
        Preview what fixes would be applied without actually applying them.
        
        Args:
            content: File content
            file_path: Path to file
            issues: Issues to fix
            
        Returns:
            Preview of fixes that would be applied
        """
        # Get auto-fixable issues
        auto_fixable_issues = [issue for issue in issues if issue.auto_fixable]
        manual_issues = [issue for issue in issues if not issue.auto_fixable]
        
        # Preview automated fixes
        fixed_content, applied_fixes = self.auto_fixer.fix_content(content, file_path, auto_fixable_issues)
        
        # Generate diff preview
        diff_preview = self._generate_diff_preview(content, fixed_content)
        
        # Get manual suggestions
        manual_suggestions = self.manual_fixer.get_manual_suggestions(manual_issues)
        
        return {
            'will_modify_content': fixed_content != content,
            'automated_fixes_count': len(applied_fixes),
            'manual_suggestions_count': len(manual_suggestions),
            'diff_preview': diff_preview,
            'applied_fixes': applied_fixes,
            'manual_suggestions': manual_suggestions,
            'fix_statistics': self._calculate_fix_statistics(issues, applied_fixes, manual_suggestions)
        }
    
    def _calculate_fix_statistics(self, all_issues: List[CodeIssue], 
                                applied_fixes: List[Dict[str, Any]], 
                                manual_suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive fix statistics."""
        total_issues = len(all_issues)
        auto_fixed = len(applied_fixes)
        manual_required = len(manual_suggestions)
        
        # Calculate by severity
        severity_stats = {}
        for severity in ['error', 'warning', 'info']:
            severity_issues = [i for i in all_issues if i.severity == severity]
            severity_stats[severity] = {
                'total': len(severity_issues),
                'auto_fixed': len([f for f in applied_fixes 
                                 if any(i.severity == severity for i in all_issues 
                                       if i.rule_id == f.get('rule_id'))]),
                'manual_required': len([s for s in manual_suggestions 
                                      if s.get('severity') == severity])
            }
        
        # Calculate completion percentage
        completion_percentage = (auto_fixed / total_issues * 100) if total_issues > 0 else 100
        
        return {
            'total_issues': total_issues,
            'auto_fixed': auto_fixed,
            'manual_required': manual_required,
            'completion_percentage': round(completion_percentage, 1),
            'severity_breakdown': severity_stats,
            'fix_types': self._categorize_fixes(applied_fixes)
        }
    
    def _categorize_fixes(self, applied_fixes: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize applied fixes by type."""
        categories = {}
        for fix in applied_fixes:
            fix_type = fix.get('type', 'unknown')
            categories[fix_type] = categories.get(fix_type, 0) + 1
        return categories
    
    def _generate_next_steps(self, applied_fixes: List[Dict[str, Any]], 
                           manual_suggestions: List[Dict[str, Any]]) -> List[str]:
        """Generate recommended next steps."""
        steps = []
        
        if applied_fixes:
            steps.append(f"✅ {len(applied_fixes)} issues were automatically fixed")
        
        if manual_suggestions:
            high_priority = [s for s in manual_suggestions if s.get('priority') == 'high']
            if high_priority:
                steps.append(f"🔴 Address {len(high_priority)} high-priority issues manually")
            
            medium_priority = [s for s in manual_suggestions if s.get('priority') == 'medium']
            if medium_priority:
                steps.append(f"🟡 Consider fixing {len(medium_priority)} medium-priority issues")
        
        if not applied_fixes and not manual_suggestions:
            steps.append("✨ No issues found - code quality looks good!")
        
        steps.append("🧪 Run tests to ensure fixes don't break functionality")
        
        return steps
    
    def _calculate_quality_improvement(self, original_issues: List[CodeIssue], 
                                     applied_fixes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate quality improvement metrics."""
        original_errors = len([i for i in original_issues if i.severity == 'error'])
        original_warnings = len([i for i in original_issues if i.severity == 'warning'])
        
        fixed_errors = len([f for f in applied_fixes 
                           if any(i.severity == 'error' for i in original_issues 
                                 if i.rule_id == f.get('rule_id'))])
        fixed_warnings = len([f for f in applied_fixes 
                             if any(i.severity == 'warning' for i in original_issues 
                                   if i.rule_id == f.get('rule_id'))])
        
        # Calculate improvement score
        total_weight = original_errors * 3 + original_warnings * 1
        fixed_weight = fixed_errors * 3 + fixed_warnings * 1
        improvement_score = (fixed_weight / total_weight * 100) if total_weight > 0 else 0
        
        return {
            'original_errors': original_errors,
            'original_warnings': original_warnings,
            'fixed_errors': fixed_errors,
            'fixed_warnings': fixed_warnings,
            'improvement_score': round(improvement_score, 1),
            'remaining_errors': original_errors - fixed_errors,
            'remaining_warnings': original_warnings - fixed_warnings
        }
    
    def _generate_diff_preview(self, original: str, fixed: str) -> List[Dict[str, Any]]:
        """Generate a preview of changes between original and fixed content."""
        original_lines = original.split('\n')
        fixed_lines = fixed.split('\n')
        
        changes = []
        max_lines = max(len(original_lines), len(fixed_lines))
        
        for i in range(max_lines):
            original_line = original_lines[i] if i < len(original_lines) else ''
            fixed_line = fixed_lines[i] if i < len(fixed_lines) else ''
            
            if original_line != fixed_line:
                changes.append({
                    'line_number': i + 1,
                    'type': 'modified' if original_line and fixed_line else 
                           'added' if fixed_line else 'removed',
                    'original': original_line,
                    'fixed': fixed_line
                })
        
        return changes[:20]  # Limit preview to first 20 changes
    
    def _create_backup(self, file_path: str, content: str) -> bool:
        """Create a backup of the original file."""
        try:
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except:
            return False
    
    def _generate_directory_summary(self, fix_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for directory-wide fixes."""
        total_files = len(fix_results)
        modified_files = len([r for r in fix_results.values() if r.get('file_modified', False)])
        
        total_auto_fixes = sum(len(r.get('applied_fixes', [])) for r in fix_results.values())
        total_manual_suggestions = sum(len(r.get('manual_suggestions', [])) for r in fix_results.values())
        
        return {
            'files_analyzed': total_files,
            'files_modified': modified_files,
            'modification_rate': round(modified_files / total_files * 100, 1) if total_files > 0 else 0,
            'total_automated_fixes': total_auto_fixes,
            'total_manual_suggestions': total_manual_suggestions,
            'average_fixes_per_file': round(total_auto_fixes / total_files, 1) if total_files > 0 else 0
        }
