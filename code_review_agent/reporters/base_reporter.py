"""
Base reporter class for generating code review reports.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..analyzers.base_analyzer import CodeIssue


class BaseReporter(ABC):
    """Base class for all report generators."""
    
    def __init__(self, name: str):
        self.name = name
        self.timestamp = datetime.now()
    
    @abstractmethod
    def generate_report(self, issues: List[CodeIssue], 
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate a report from the list of issues."""
        pass
    
    def calculate_compliance_score(self, issues: List[CodeIssue], 
                                 total_lines: int = 1000) -> float:
        """
        Calculate compliance score based on issues found.
        
        Args:
            issues: List of code issues
            total_lines: Total lines of code analyzed
            
        Returns:
            Compliance score from 0-100
        """
        if not issues:
            return 100.0
        
        # Weight issues by severity
        error_weight = 10
        warning_weight = 5
        info_weight = 1
        
        total_weight = 0
        for issue in issues:
            if issue.severity == 'error':
                total_weight += error_weight
            elif issue.severity == 'warning':
                total_weight += warning_weight
            else:
                total_weight += info_weight
        
        # Calculate score (max penalty is 50% of total lines)
        max_penalty = total_lines * 0.5
        penalty = min(total_weight, max_penalty)
        score = max(0, 100 - (penalty / total_lines * 100))
        
        return round(score, 2)
    
    def group_issues_by_severity(self, issues: List[CodeIssue]) -> Dict[str, List[CodeIssue]]:
        """Group issues by severity level."""
        groups = {'error': [], 'warning': [], 'info': []}
        
        for issue in issues:
            severity = issue.severity.lower()
            if severity in groups:
                groups[severity].append(issue)
            else:
                groups['info'].append(issue)  # Default to info
        
        return groups
    
    def group_issues_by_file(self, issues: List[CodeIssue]) -> Dict[str, List[CodeIssue]]:
        """Group issues by file path."""
        groups = {}
        
        for issue in issues:
            file_path = issue.file_path or 'unknown'
            if file_path not in groups:
                groups[file_path] = []
            groups[file_path].append(issue)
        
        return groups
    
    def group_issues_by_category(self, issues: List[CodeIssue]) -> Dict[str, List[CodeIssue]]:
        """Group issues by category."""
        groups = {}
        
        for issue in issues:
            category = issue.category or 'general'
            if category not in groups:
                groups[category] = []
            groups[category].append(issue)
        
        return groups
    
    def get_issue_statistics(self, issues: List[CodeIssue]) -> Dict[str, Any]:
        """Get comprehensive statistics about issues."""
        if not issues:
            return {
                'total': 0,
                'by_severity': {'error': 0, 'warning': 0, 'info': 0},
                'by_category': {},
                'auto_fixable': 0,
                'files_affected': 0
            }
        
        severity_groups = self.group_issues_by_severity(issues)
        category_groups = self.group_issues_by_category(issues)
        file_groups = self.group_issues_by_file(issues)
        
        auto_fixable = len([i for i in issues if i.auto_fixable])
        
        return {
            'total': len(issues),
            'by_severity': {
                'error': len(severity_groups['error']),
                'warning': len(severity_groups['warning']),
                'info': len(severity_groups['info'])
            },
            'by_category': {cat: len(issues) for cat, issues in category_groups.items()},
            'auto_fixable': auto_fixable,
            'files_affected': len(file_groups),
            'most_problematic_files': self._get_most_problematic_files(file_groups),
            'most_common_rules': self._get_most_common_rules(issues)
        }
    
    def _get_most_problematic_files(self, file_groups: Dict[str, List[CodeIssue]]) -> List[Dict[str, Any]]:
        """Get files with the most issues."""
        file_stats = []
        
        for file_path, file_issues in file_groups.items():
            errors = len([i for i in file_issues if i.severity == 'error'])
            warnings = len([i for i in file_issues if i.severity == 'warning'])
            
            file_stats.append({
                'file': file_path,
                'total_issues': len(file_issues),
                'errors': errors,
                'warnings': warnings,
                'score': errors * 3 + warnings  # Weight errors more heavily
            })
        
        # Sort by score (descending) and return top 10
        file_stats.sort(key=lambda x: x['score'], reverse=True)
        return file_stats[:10]
    
    def _get_most_common_rules(self, issues: List[CodeIssue]) -> List[Dict[str, Any]]:
        """Get most frequently violated rules."""
        rule_counts = {}
        
        for issue in issues:
            rule_id = issue.rule_id
            if rule_id not in rule_counts:
                rule_counts[rule_id] = {
                    'rule_id': rule_id,
                    'count': 0,
                    'severity': issue.severity,
                    'category': issue.category,
                    'auto_fixable': issue.auto_fixable
                }
            rule_counts[rule_id]['count'] += 1
        
        # Sort by count (descending) and return top 10
        sorted_rules = sorted(rule_counts.values(), key=lambda x: x['count'], reverse=True)
        return sorted_rules[:10]
    
    def format_timestamp(self, timestamp: Optional[datetime] = None) -> str:
        """Format timestamp for display."""
        if timestamp is None:
            timestamp = self.timestamp
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_severity_color(self, severity: str) -> str:
        """Get color code for severity level."""
        colors = {
            'error': '#dc3545',    # Red
            'warning': '#ffc107',  # Yellow
            'info': '#17a2b8'      # Blue
        }
        return colors.get(severity.lower(), '#6c757d')  # Gray default
    
    def get_severity_icon(self, severity: str) -> str:
        """Get icon for severity level."""
        icons = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        return icons.get(severity.lower(), '•')
    
    def truncate_text(self, text: str, max_length: int = 100) -> str:
        """Truncate text to specified length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + '...'
    
    def format_file_path(self, file_path: str, max_length: int = 50) -> str:
        """Format file path for display."""
        if not file_path or len(file_path) <= max_length:
            return file_path or 'unknown'
        
        # Show beginning and end of path
        if '/' in file_path:
            parts = file_path.split('/')
            if len(parts) > 2:
                return f"{parts[0]}/.../{parts[-1]}"
        
        return self.truncate_text(file_path, max_length)
    
    def generate_summary(self, issues: List[CodeIssue], 
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a summary of the analysis results."""
        stats = self.get_issue_statistics(issues)
        
        # Calculate compliance score
        total_lines = metadata.get('total_lines', 1000) if metadata else 1000
        compliance_score = self.calculate_compliance_score(issues, total_lines)
        
        # Determine overall status
        error_count = stats['by_severity']['error']
        warning_count = stats['by_severity']['warning']
        
        if error_count == 0 and warning_count == 0:
            status = 'excellent'
            status_message = 'No issues found - excellent code quality!'
        elif error_count == 0 and warning_count <= 5:
            status = 'good'
            status_message = 'Good code quality with minor warnings'
        elif error_count <= 2 and warning_count <= 10:
            status = 'fair'
            status_message = 'Fair code quality - some issues need attention'
        else:
            status = 'needs_improvement'
            status_message = 'Code quality needs improvement'
        
        return {
            'timestamp': self.format_timestamp(),
            'total_issues': stats['total'],
            'compliance_score': compliance_score,
            'status': status,
            'status_message': status_message,
            'statistics': stats,
            'recommendations': self._generate_recommendations(stats),
            'metadata': metadata or {}
        }

    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on statistics."""
        recommendations = []

        error_count = stats['by_severity']['error']
        warning_count = stats['by_severity']['warning']
        auto_fixable = stats['auto_fixable']

        if error_count > 0:
            recommendations.append(f"🔴 Fix {error_count} critical error(s) immediately")

        if auto_fixable > 0:
            recommendations.append(f"🔧 Run auto-fix to resolve {auto_fixable} issue(s) automatically")

        if warning_count > 10:
            recommendations.append("⚠️ Consider addressing warnings to improve code quality")

        if stats['files_affected'] > 5:
            recommendations.append("📁 Focus on most problematic files first")

        if not recommendations:
            recommendations.append("✨ Great job! Code quality looks excellent")

        return recommendations
