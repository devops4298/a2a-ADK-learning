"""
Main Code Review Agent using Google's Agent Development Kit.
"""
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from google.adk.agents import Agent
from .analyzers.file_analyzer import FileAnalyzer
from .linters.linter_manager import LinterManager
from .fixers.fix_manager import FixManager
from .standards.project_standards import ProjectStandards


def analyze_code_file(file_path: str, content: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a single code file for quality issues.
    
    Args:
        file_path: Path to the file to analyze
        content: Optional file content (if not provided, will read from file)
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        analyzer = FileAnalyzer()
        issues = analyzer.analyze_file(file_path, content)
        
        # Get analysis summary
        summary = analyzer.get_analysis_summary()
        
        # Group issues by category and severity
        issues_by_severity = {}
        issues_by_category = {}
        
        for issue in issues:
            # Group by severity
            severity = issue.severity
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append({
                'rule_id': issue.rule_id,
                'description': issue.description,
                'line_number': issue.line_number,
                'column': issue.column,
                'category': issue.category,
                'auto_fixable': issue.auto_fixable,
                'suggested_fix': issue.suggested_fix
            })
            
            # Group by category
            category = issue.category
            if category not in issues_by_category:
                issues_by_category[category] = []
            issues_by_category[category].append({
                'rule_id': issue.rule_id,
                'description': issue.description,
                'line_number': issue.line_number,
                'severity': issue.severity
            })
        
        return {
            'file_path': file_path,
            'total_issues': len(issues),
            'issues_by_severity': issues_by_severity,
            'issues_by_category': issues_by_category,
            'summary': summary,
            'auto_fixable_count': len([i for i in issues if i.auto_fixable]),
            'compliance_score': max(0, 100 - len(issues) * 2)  # Simple scoring
        }
        
    except Exception as e:
        return {
            'file_path': file_path,
            'error': str(e),
            'total_issues': 0,
            'issues_by_severity': {},
            'issues_by_category': {},
            'summary': {'error': str(e)}
        }


def analyze_directory(directory_path: str, file_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Analyze all relevant files in a directory.
    
    Args:
        directory_path: Path to directory to analyze
        file_patterns: File patterns to include (default: common patterns)
        
    Returns:
        Dictionary containing analysis results for all files
    """
    try:
        analyzer = FileAnalyzer()
        results = analyzer.analyze_directory(directory_path, file_patterns)
        
        # Aggregate results
        total_issues = 0
        total_files = 0
        files_with_issues = 0
        all_issues_by_severity = {'error': 0, 'warning': 0, 'info': 0}
        all_issues_by_category = {}
        
        file_results = {}
        
        for file_path, issues in results.items():
            if file_path == 'error':
                continue
                
            total_files += 1
            file_issue_count = len(issues)
            total_issues += file_issue_count
            
            if file_issue_count > 0:
                files_with_issues += 1
            
            # Count by severity and category
            for issue in issues:
                severity = issue.severity
                category = issue.category
                
                all_issues_by_severity[severity] = all_issues_by_severity.get(severity, 0) + 1
                all_issues_by_category[category] = all_issues_by_category.get(category, 0) + 1
            
            # Store file results
            file_results[file_path] = {
                'issue_count': file_issue_count,
                'issues': [issue.to_dict() for issue in issues],
                'auto_fixable': len([i for i in issues if i.auto_fixable])
            }
        
        # Calculate overall compliance score
        compliance_score = max(0, 100 - (total_issues / max(total_files, 1)) * 10)
        
        return {
            'directory': directory_path,
            'total_files_analyzed': total_files,
            'files_with_issues': files_with_issues,
            'total_issues': total_issues,
            'issues_by_severity': all_issues_by_severity,
            'issues_by_category': all_issues_by_category,
            'compliance_score': round(compliance_score, 2),
            'file_results': file_results,
            'summary': {
                'status': 'good' if compliance_score > 80 else 'needs_improvement',
                'message': f'Analyzed {total_files} files, found {total_issues} issues'
            }
        }
        
    except Exception as e:
        return {
            'directory': directory_path,
            'error': str(e),
            'total_files_analyzed': 0,
            'total_issues': 0
        }


def one_click_fix(file_path: str, content: Optional[str] = None) -> Dict[str, Any]:
    """
    Apply one-click fix to a file - automatically fix what can be fixed and suggest manual fixes.
    
    Args:
        file_path: Path to the file to fix
        content: Optional file content (if not provided, will read from file)
        
    Returns:
        Dictionary containing fix results
    """
    try:
        # First analyze the file
        analyzer = FileAnalyzer()
        if content is None:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        issues = analyzer.analyze_file(file_path, content)
        
        # Apply fixes
        fix_manager = FixManager()
        fix_result = fix_manager.one_click_fix(content, file_path, issues)
        
        return {
            'file_path': file_path,
            'original_issues': len(issues),
            'content_changed': fix_result['content_changed'],
            'fixed_content': fix_result['fixed_content'],
            'applied_fixes': fix_result['applied_fixes'],
            'manual_suggestions': fix_result['manual_suggestions'],
            'fix_statistics': fix_result['fix_statistics'],
            'next_steps': fix_result['next_steps'],
            'quality_improvement': fix_result['quality_improvement']
        }
        
    except Exception as e:
        return {
            'file_path': file_path,
            'error': str(e),
            'content_changed': False
        }


def get_coding_standards() -> Dict[str, Any]:
    """
    Get all coding standards defined for the project.
    
    Returns:
        Dictionary containing all coding standards
    """
    try:
        standards = ProjectStandards()
        
        return {
            'typescript_standards': len(standards.typescript_standards.get_all_standards()),
            'playwright_standards': len(standards.playwright_standards.get_all_standards()),
            'cucumber_standards': len(standards.cucumber_standards.get_all_standards()),
            'total_standards': len(standards.get_all_standards()),
            'categories': list(standards.get_rule_categories()),
            'auto_fixable_count': len(standards.get_auto_fixable_standards()),
            'standards_by_category': {
                category: len(standards.get_standards_by_category(category))
                for category in standards.get_rule_categories()
            }
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'total_standards': 0
        }


def get_linter_status() -> Dict[str, Any]:
    """
    Get status of all available linting tools.
    
    Returns:
        Dictionary containing linter status information
    """
    try:
        linter_manager = LinterManager()
        return linter_manager.get_linter_status()
        
    except Exception as e:
        return {
            'error': str(e),
            'linters': {}
        }


# Create the main agent
root_agent = Agent(
    name="code_review_agent",
    model="gemini-2.0-flash",
    description=(
        "AI-powered code review assistant for TypeScript, Playwright, and Cucumber projects. "
        "Analyzes code quality, applies automated fixes, and provides manual suggestions."
    ),
    instruction=(
        "You are an expert code review assistant specializing in TypeScript, Playwright automation, "
        "and Cucumber BDD projects. You can analyze code files, identify quality issues, apply "
        "automated fixes, and provide detailed suggestions for manual improvements. "
        "Always provide specific, actionable feedback with line numbers and examples."
    ),
    tools=[
        analyze_code_file,
        analyze_directory, 
        one_click_fix,
        get_coding_standards,
        get_linter_status
    ],
)
