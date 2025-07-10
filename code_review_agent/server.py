#!/usr/bin/env python3
"""
HTTP API Server for VS Code Integration
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    from flask import Flask, request, jsonify, cors
    from flask_cors import CORS
except ImportError:
    print("Flask is required for the server. Install with: pip install flask flask-cors")
    exit(1)

from .analyzers.file_analyzer import FileAnalyzer
from .fixers.fix_manager import FixManager
from .standards.project_standards import ProjectStandards


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for VS Code extension


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'ts-playwright-cucumber-reviewer',
        'version': '1.0.0'
    })


@app.route('/analyze', methods=['POST'])
def analyze_code():
    """
    Analyze code content or file.
    
    Request body:
    {
        "content": "code content",
        "file_path": "path/to/file.ts",
        "file_type": "typescript|playwright|cucumber"  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        content = data.get('content')
        file_path = data.get('file_path', 'unknown.ts')
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        # Analyze the content
        analyzer = FileAnalyzer()
        issues = analyzer.analyze_file(file_path, content)
        
        # Convert issues to JSON-serializable format
        issues_data = [issue.to_dict() for issue in issues]
        
        # Get summary
        summary = analyzer.get_analysis_summary()
        
        return jsonify({
            'file_path': file_path,
            'issues': issues_data,
            'summary': summary,
            'total_issues': len(issues),
            'auto_fixable_count': len([i for i in issues if i.auto_fixable])
        })
    
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/fix', methods=['POST'])
def fix_code():
    """
    Apply one-click fix to code content.
    
    Request body:
    {
        "content": "code content",
        "file_path": "path/to/file.ts"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        content = data.get('content')
        file_path = data.get('file_path', 'unknown.ts')
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        # First analyze to get issues
        analyzer = FileAnalyzer()
        issues = analyzer.analyze_file(file_path, content)
        
        # Apply fixes
        fix_manager = FixManager()
        fix_result = fix_manager.one_click_fix(content, file_path, issues)
        
        return jsonify({
            'original_content': content,
            'fixed_content': fix_result['fixed_content'],
            'content_changed': fix_result['content_changed'],
            'applied_fixes': fix_result['applied_fixes'],
            'manual_suggestions': fix_result['manual_suggestions'],
            'fix_statistics': fix_result['fix_statistics'],
            'next_steps': fix_result['next_steps']
        })
    
    except Exception as e:
        logger.error(f"Error fixing code: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/standards', methods=['GET'])
def get_standards():
    """
    Get coding standards information.
    
    Query parameters:
    - category: Filter by category (typescript, playwright, cucumber)
    - auto_fixable: Filter by auto-fixable (true/false)
    """
    try:
        category = request.args.get('category')
        auto_fixable = request.args.get('auto_fixable')
        
        standards = ProjectStandards()
        
        if category:
            standards_list = standards.get_standards_by_category(category)
        else:
            standards_list = standards.get_all_standards()
        
        if auto_fixable is not None:
            auto_fixable_bool = auto_fixable.lower() == 'true'
            standards_list = [s for s in standards_list if s.auto_fixable == auto_fixable_bool]
        
        standards_data = [
            {
                'rule_id': std.rule_id,
                'description': std.description,
                'severity': std.severity,
                'category': std.category,
                'auto_fixable': std.auto_fixable,
                'examples': std.examples
            }
            for std in standards_list
        ]
        
        return jsonify({
            'standards': standards_data,
            'total_count': len(standards_data),
            'categories': list(standards.get_rule_categories())
        })
    
    except Exception as e:
        logger.error(f"Error getting standards: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/analyze-file', methods=['POST'])
def analyze_file():
    """
    Analyze a file by path.
    
    Request body:
    {
        "file_path": "absolute/path/to/file.ts"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({'error': 'No file_path provided'}), 400
        
        if not Path(file_path).exists():
            return jsonify({'error': f'File not found: {file_path}'}), 404
        
        # Analyze the file
        analyzer = FileAnalyzer()
        issues = analyzer.analyze_file(file_path)
        
        # Convert issues to JSON-serializable format
        issues_data = [issue.to_dict() for issue in issues]
        
        return jsonify({
            'file_path': file_path,
            'issues': issues_data,
            'total_issues': len(issues),
            'auto_fixable_count': len([i for i in issues if i.auto_fixable])
        })
    
    except Exception as e:
        logger.error(f"Error analyzing file: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat_interface():
    """
    Chat interface for VS Code Copilot integration.
    
    Request body:
    {
        "message": "user message",
        "context": {
            "file_path": "current file path",
            "content": "current file content",
            "selection": "selected text"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        message = data.get('message', '')
        context = data.get('context', {})
        
        # Process the chat message
        response = process_chat_message(message, context)
        
        return jsonify({
            'response': response,
            'suggestions': generate_suggestions(context)
        })
    
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({'error': str(e)}), 500


def process_chat_message(message: str, context: Dict[str, Any]) -> str:
    """Process a chat message and return a response."""
    message_lower = message.lower()
    
    if 'analyze' in message_lower or 'review' in message_lower:
        return handle_analyze_request(context)
    elif 'fix' in message_lower:
        return handle_fix_request(context)
    elif 'standards' in message_lower or 'rules' in message_lower:
        return handle_standards_request(context)
    else:
        return "I can help you analyze code, apply fixes, or explain coding standards. What would you like me to do?"


def handle_analyze_request(context: Dict[str, Any]) -> str:
    """Handle code analysis request."""
    content = context.get('content')
    file_path = context.get('file_path', 'unknown.ts')
    
    if not content:
        return "Please provide code content to analyze."
    
    try:
        analyzer = FileAnalyzer()
        issues = analyzer.analyze_file(file_path, content)
        
        if not issues:
            return "✅ Great! No code quality issues found."
        
        error_count = len([i for i in issues if i.severity == 'error'])
        warning_count = len([i for i in issues if i.severity == 'warning'])
        auto_fixable = len([i for i in issues if i.auto_fixable])
        
        response = f"Found {len(issues)} issues:\n"
        response += f"• {error_count} errors\n"
        response += f"• {warning_count} warnings\n"
        response += f"• {auto_fixable} auto-fixable\n\n"
        
        # Show top 3 issues
        for i, issue in enumerate(issues[:3], 1):
            response += f"{i}. Line {issue.line_number}: {issue.description}\n"
        
        if len(issues) > 3:
            response += f"... and {len(issues) - 3} more issues.\n"
        
        if auto_fixable > 0:
            response += f"\n💡 I can automatically fix {auto_fixable} of these issues. Would you like me to apply the fixes?"
        
        return response
    
    except Exception as e:
        return f"Error analyzing code: {str(e)}"


def handle_fix_request(context: Dict[str, Any]) -> str:
    """Handle code fix request."""
    content = context.get('content')
    file_path = context.get('file_path', 'unknown.ts')
    
    if not content:
        return "Please provide code content to fix."
    
    try:
        # Analyze first
        analyzer = FileAnalyzer()
        issues = analyzer.analyze_file(file_path, content)
        
        # Apply fixes
        fix_manager = FixManager()
        fix_result = fix_manager.one_click_fix(content, file_path, issues)
        
        if not fix_result['content_changed']:
            return "No automated fixes available for this code."
        
        applied_count = len(fix_result['applied_fixes'])
        manual_count = len(fix_result['manual_suggestions'])
        
        response = f"✅ Applied {applied_count} automated fixes!\n\n"
        
        if manual_count > 0:
            response += f"💡 {manual_count} issues require manual attention:\n"
            for suggestion in fix_result['manual_suggestions'][:3]:
                response += f"• {suggestion['title']}\n"
        
        return response
    
    except Exception as e:
        return f"Error fixing code: {str(e)}"


def handle_standards_request(context: Dict[str, Any]) -> str:
    """Handle coding standards request."""
    file_path = context.get('file_path', '')
    
    try:
        standards = ProjectStandards()
        
        # Determine file type
        if '.spec.ts' in file_path or '.test.ts' in file_path:
            category_standards = standards.get_standards_by_category('playwright')
            category_name = "Playwright"
        elif file_path.endswith('.feature'):
            category_standards = standards.get_standards_by_category('cucumber')
            category_name = "Cucumber"
        elif file_path.endswith(('.ts', '.js')):
            category_standards = standards.get_standards_by_category('typescript')
            category_name = "TypeScript"
        else:
            category_standards = standards.get_all_standards()
            category_name = "All"
        
        response = f"📋 {category_name} Coding Standards ({len(category_standards)} rules):\n\n"
        
        # Group by severity
        errors = [s for s in category_standards if s.severity == 'error']
        warnings = [s for s in category_standards if s.severity == 'warning']
        
        if errors:
            response += f"🔴 Critical Rules ({len(errors)}):\n"
            for rule in errors[:3]:
                response += f"• {rule.rule_id}: {rule.description}\n"
        
        if warnings:
            response += f"\n🟡 Warning Rules ({len(warnings)}):\n"
            for rule in warnings[:3]:
                response += f"• {rule.rule_id}: {rule.description}\n"
        
        auto_fixable = len([s for s in category_standards if s.auto_fixable])
        response += f"\n🔧 {auto_fixable} rules are auto-fixable"
        
        return response
    
    except Exception as e:
        return f"Error getting standards: {str(e)}"


def generate_suggestions(context: Dict[str, Any]) -> List[str]:
    """Generate helpful suggestions based on context."""
    suggestions = [
        "Analyze this code for quality issues",
        "Apply automated fixes to this file",
        "Show coding standards for this file type",
        "Explain a specific rule or issue"
    ]
    
    file_path = context.get('file_path', '')
    
    if '.spec.ts' in file_path or '.test.ts' in file_path:
        suggestions.extend([
            "Check for Playwright best practices",
            "Review test structure and naming",
            "Validate locator usage"
        ])
    elif file_path.endswith('.feature'):
        suggestions.extend([
            "Review Gherkin syntax",
            "Check scenario structure",
            "Validate step definitions"
        ])
    
    return suggestions


def run_server(host: str = 'localhost', port: int = 8000, debug: bool = False):
    """Run the HTTP server."""
    logger.info(f"Starting Code Review Agent server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


def main():
    """Main server entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Code Review Agent HTTP Server")
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8000, help='Server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    run_server(args.host, args.port, args.debug)


if __name__ == '__main__':
    main()
