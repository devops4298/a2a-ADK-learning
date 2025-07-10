"""
Main file analyzer that coordinates all specific analyzers.
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from .typescript_analyzer import TypeScriptAnalyzer
from .playwright_analyzer import PlaywrightAnalyzer
from .cucumber_analyzer import CucumberAnalyzer
from .base_analyzer import CodeIssue


class FileAnalyzer:
    """Main analyzer that coordinates all specific analyzers based on file type."""
    
    def __init__(self):
        self.typescript_analyzer = TypeScriptAnalyzer()
        self.playwright_analyzer = PlaywrightAnalyzer()
        self.cucumber_analyzer = CucumberAnalyzer()
        self.all_issues: List[CodeIssue] = []
    
    def analyze_file(self, file_path: str, content: Optional[str] = None) -> List[CodeIssue]:
        """
        Analyze a file and return all issues found.
        
        Args:
            file_path: Path to the file to analyze
            content: File content (if None, will read from file_path)
            
        Returns:
            List of CodeIssue objects
        """
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return [CodeIssue(
                    rule_id='file-read-error',
                    description=f'Could not read file: {str(e)}',
                    severity='error',
                    line_number=1,
                    file_path=file_path,
                    category='system'
                )]
        
        issues = []
        file_extension = Path(file_path).suffix.lower()
        
        # Determine which analyzers to run based on file type and content
        analyzers_to_run = self._get_analyzers_for_file(file_path, content)
        
        for analyzer in analyzers_to_run:
            analyzer_issues = analyzer.analyze_file(file_path, content)
            issues.extend(analyzer_issues)
        
        self.all_issues = issues
        return issues
    
    def analyze_directory(self, directory_path: str, 
                         file_patterns: Optional[List[str]] = None) -> Dict[str, List[CodeIssue]]:
        """
        Analyze all relevant files in a directory.
        
        Args:
            directory_path: Path to directory to analyze
            file_patterns: List of file patterns to include (default: common test file patterns)
            
        Returns:
            Dictionary mapping file paths to their issues
        """
        if file_patterns is None:
            file_patterns = [
                '*.ts', '*.js', '*.spec.ts', '*.test.ts', 
                '*.feature', '*steps.ts', '*step.ts'
            ]
        
        results = {}
        directory = Path(directory_path)
        
        if not directory.exists():
            return {'error': [CodeIssue(
                rule_id='directory-not-found',
                description=f'Directory not found: {directory_path}',
                severity='error',
                line_number=1,
                category='system'
            )]}
        
        # Find all matching files
        matching_files = []
        for pattern in file_patterns:
            matching_files.extend(directory.rglob(pattern))
        
        # Analyze each file
        for file_path in matching_files:
            if file_path.is_file():
                try:
                    issues = self.analyze_file(str(file_path))
                    if issues:  # Only include files with issues
                        results[str(file_path)] = issues
                except Exception as e:
                    results[str(file_path)] = [CodeIssue(
                        rule_id='analysis-error',
                        description=f'Analysis failed: {str(e)}',
                        severity='error',
                        line_number=1,
                        file_path=str(file_path),
                        category='system'
                    )]
        
        return results
    
    def _get_analyzers_for_file(self, file_path: str, content: str) -> List:
        """Determine which analyzers should run for a given file."""
        analyzers = []
        file_extension = Path(file_path).suffix.lower()
        file_name = Path(file_path).name.lower()
        
        # TypeScript files
        if file_extension in ['.ts', '.js']:
            analyzers.append(self.typescript_analyzer)
        
        # Playwright test files
        if (file_extension in ['.ts', '.js'] and 
            ('.spec.' in file_name or '.test.' in file_name or 
             'playwright' in content.lower() or 'page.' in content)):
            analyzers.append(self.playwright_analyzer)
        
        # Cucumber files
        if file_extension == '.feature':
            analyzers.append(self.cucumber_analyzer)
        elif ('step' in file_name and file_extension in ['.ts', '.js']):
            analyzers.append(self.cucumber_analyzer)
        
        return analyzers
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all analysis results."""
        if not self.all_issues:
            return {
                'total_files_analyzed': 0,
                'total_issues': 0,
                'summary': 'No issues found or no files analyzed'
            }
        
        # Group issues by severity
        severity_counts = {
            'error': len([i for i in self.all_issues if i.severity == 'error']),
            'warning': len([i for i in self.all_issues if i.severity == 'warning']),
            'info': len([i for i in self.all_issues if i.severity == 'info'])
        }
        
        # Group issues by category
        category_counts = {}
        for issue in self.all_issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        # Group issues by file
        file_counts = {}
        for issue in self.all_issues:
            file_counts[issue.file_path] = file_counts.get(issue.file_path, 0) + 1
        
        # Calculate compliance score (0-100)
        total_lines_analyzed = sum(self._count_lines_in_file(fp) for fp in file_counts.keys())
        compliance_score = max(0, 100 - (len(self.all_issues) * 100 / max(total_lines_analyzed, 1)))
        
        return {
            'total_files_analyzed': len(file_counts),
            'total_issues': len(self.all_issues),
            'severity_breakdown': severity_counts,
            'category_breakdown': category_counts,
            'files_with_issues': len(file_counts),
            'auto_fixable_issues': len([i for i in self.all_issues if i.auto_fixable]),
            'compliance_score': round(compliance_score, 2),
            'most_problematic_files': sorted(file_counts.items(), 
                                           key=lambda x: x[1], reverse=True)[:5],
            'most_common_categories': sorted(category_counts.items(), 
                                           key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _count_lines_in_file(self, file_path: str) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 1  # Default to 1 to avoid division by zero
    
    def get_issues_by_severity(self, severity: str) -> List[CodeIssue]:
        """Get all issues with a specific severity level."""
        return [issue for issue in self.all_issues if issue.severity == severity]
    
    def get_issues_by_category(self, category: str) -> List[CodeIssue]:
        """Get all issues in a specific category."""
        return [issue for issue in self.all_issues if issue.category == category]
    
    def get_auto_fixable_issues(self) -> List[CodeIssue]:
        """Get all issues that can be automatically fixed."""
        return [issue for issue in self.all_issues if issue.auto_fixable]
    
    def get_issues_by_file(self, file_path: str) -> List[CodeIssue]:
        """Get all issues for a specific file."""
        return [issue for issue in self.all_issues if issue.file_path == file_path]
    
    def export_results(self, format_type: str = 'json') -> str:
        """Export analysis results in specified format."""
        if format_type == 'json':
            import json
            return json.dumps([issue.to_dict() for issue in self.all_issues], indent=2)
        elif format_type == 'csv':
            import csv
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                'file_path', 'rule_id', 'description', 'severity', 
                'line_number', 'category', 'auto_fixable'
            ])
            writer.writeheader()
            for issue in self.all_issues:
                writer.writerow(issue.to_dict())
            return output.getvalue()
        else:
            # Plain text format
            result = []
            for issue in self.all_issues:
                result.append(
                    f"{issue.file_path}:{issue.line_number} "
                    f"[{issue.severity.upper()}] {issue.description} "
                    f"({issue.rule_id})"
                )
            return '\n'.join(result)
