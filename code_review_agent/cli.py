#!/usr/bin/env python3
"""
Command Line Interface for the Code Review Agent
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, List

from .analyzers.file_analyzer import FileAnalyzer
from .fixers.fix_manager import FixManager
from .reporters.console_reporter import ConsoleReporter


def analyze_command(args):
    """Handle the analyze command."""
    analyzer = FileAnalyzer()
    
    if args.file:
        # Analyze single file
        issues = analyzer.analyze_file(args.file)
        
        if args.json:
            print(json.dumps([issue.to_dict() for issue in issues], indent=2))
        else:
            reporter = ConsoleReporter()
            print(reporter.generate_report(issues, {'file_path': args.file}))
    
    elif args.directory:
        # Analyze directory
        results = analyzer.analyze_directory(args.directory, args.patterns)
        
        if args.json:
            json_results = {}
            for file_path, issues in results.items():
                json_results[file_path] = [issue.to_dict() for issue in issues]
            print(json.dumps(json_results, indent=2))
        else:
            reporter = ConsoleReporter()
            total_issues = sum(len(issues) for issues in results.values())
            print(f"Analyzed {len(results)} files, found {total_issues} total issues\n")
            
            for file_path, issues in results.items():
                if issues:
                    print(f"\n📁 {file_path}")
                    print(reporter.generate_report(issues))


def fix_command(args):
    """Handle the fix command."""
    fix_manager = FixManager()
    
    if args.file:
        # Fix single file
        result = fix_manager.fix_file(args.file)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get('file_modified', False):
                print(f"✅ Fixed {args.file}")
                print(f"Applied {len(result.get('applied_fixes', []))} automated fixes")
                if result.get('manual_suggestions'):
                    print(f"💡 {len(result['manual_suggestions'])} manual suggestions available")
            else:
                print(f"ℹ️  No fixes needed for {args.file}")
    
    elif args.directory:
        # Fix directory
        result = fix_manager.fix_directory(args.directory, args.patterns)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"✅ Processed {result['files_processed']} files")
            print(f"📝 Modified {result['files_modified']} files")
            print(f"🔧 Applied {result['total_automated_fixes']} total fixes")


def standards_command(args):
    """Handle the standards command."""
    from .standards.project_standards import ProjectStandards
    
    standards = ProjectStandards()
    
    if args.category:
        category_standards = standards.get_standards_by_category(args.category)
        standards_data = [
            {
                'rule_id': std.rule_id,
                'description': std.description,
                'severity': std.severity,
                'auto_fixable': std.auto_fixable
            }
            for std in category_standards
        ]
    else:
        all_standards = standards.get_all_standards()
        standards_data = [
            {
                'rule_id': std.rule_id,
                'description': std.description,
                'severity': std.severity,
                'category': std.category,
                'auto_fixable': std.auto_fixable
            }
            for std in all_standards
        ]
    
    if args.json:
        print(json.dumps(standards_data, indent=2))
    else:
        print(f"📋 Code Review Standards ({len(standards_data)} rules)")
        print("=" * 50)
        
        for std in standards_data:
            icon = "🔧" if std['auto_fixable'] else "👁️"
            severity_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(std['severity'], "⚪")
            print(f"{icon} {severity_icon} {std['rule_id']}")
            print(f"   {std['description']}")
            if 'category' in std:
                print(f"   Category: {std['category']}")
            print()


def server_command(args):
    """Handle the server command."""
    from .server import run_server
    run_server(host=args.host, port=args.port, debug=args.debug)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TypeScript Playwright Cucumber Code Review Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ts-reviewer analyze --file src/components/Login.ts
  ts-reviewer analyze --directory src/ --patterns "*.ts" "*.spec.ts"
  ts-reviewer fix --file tests/login.spec.ts
  ts-reviewer fix --directory tests/ --patterns "*.spec.ts"
  ts-reviewer standards --category typescript
  ts-reviewer server --port 8080
        """
    )
    
    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze code files for quality issues')
    analyze_group = analyze_parser.add_mutually_exclusive_group(required=True)
    analyze_group.add_argument('--file', help='Analyze a single file')
    analyze_group.add_argument('--directory', help='Analyze all files in a directory')
    analyze_parser.add_argument('--patterns', nargs='+', default=['*.ts', '*.spec.ts', '*.feature'],
                               help='File patterns to include (default: *.ts *.spec.ts *.feature)')
    
    # Fix command
    fix_parser = subparsers.add_parser('fix', help='Apply automated fixes to code files')
    fix_group = fix_parser.add_mutually_exclusive_group(required=True)
    fix_group.add_argument('--file', help='Fix a single file')
    fix_group.add_argument('--directory', help='Fix all files in a directory')
    fix_parser.add_argument('--patterns', nargs='+', default=['*.ts', '*.spec.ts', '*.feature'],
                           help='File patterns to include (default: *.ts *.spec.ts *.feature)')
    
    # Standards command
    standards_parser = subparsers.add_parser('standards', help='Show available coding standards')
    standards_parser.add_argument('--category', help='Show standards for specific category')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start HTTP API server')
    server_parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    server_parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    server_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'analyze':
            analyze_command(args)
        elif args.command == 'fix':
            fix_command(args)
        elif args.command == 'standards':
            standards_command(args)
        elif args.command == 'server':
            server_command(args)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
