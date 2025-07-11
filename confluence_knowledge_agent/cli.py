"""
Command Line Interface for Confluence Knowledge Agent.

Provides management commands for the agent following ADK best practices.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from .server import run_server
from .data.validator import validate_data_structure, get_data_summary
from .tools.confluence_search import get_knowledge_base_stats
from .config.settings import get_agent_config, get_data_config, validate_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cmd_serve(args):
    """Start the server."""
    logger.info("Starting Confluence Knowledge Agent server...")
    run_server()


def cmd_validate(args):
    """Validate data structure."""
    data_config = get_data_config()
    data_dir = args.data_dir or data_config["data_dir"]
    
    logger.info(f"Validating data structure in: {data_dir}")
    
    is_valid, issues = validate_data_structure(data_dir)
    
    if is_valid:
        print("✅ Data structure is valid!")
    else:
        print("❌ Data structure validation failed:")
        for issue in issues:
            print(f"  • {issue}")
        sys.exit(1)


def cmd_stats(args):
    """Show knowledge base statistics."""
    try:
        stats = get_knowledge_base_stats()
        print(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        sys.exit(1)


def cmd_summary(args):
    """Show data directory summary."""
    data_config = get_data_config()
    data_dir = args.data_dir or data_config["data_dir"]
    
    summary = get_data_summary(data_dir)
    
    print(f"📊 Data Directory Summary: {data_dir}")
    print(f"  • Exists: {'✅' if summary['exists'] else '❌'}")
    print(f"  • Total Files: {summary['total_files']}")
    print(f"  • Total Size: {summary['total_size_bytes']:,} bytes")
    print(f"  • Spaces: {', '.join(summary['spaces']) if summary['spaces'] else 'None'}")
    print(f"  • Validation: {'✅' if summary['validation_status'] == 'valid' else '❌'}")
    
    if summary['validation_issues']:
        print("\n⚠️  Validation Issues:")
        for issue in summary['validation_issues']:
            print(f"  • {issue}")


def cmd_config(args):
    """Show configuration."""
    print("🔧 Agent Configuration:")
    agent_config = get_agent_config()
    for key, value in agent_config.items():
        if key == "instruction":
            print(f"  • {key}: [instruction text - {len(value)} characters]")
        else:
            print(f"  • {key}: {value}")
    
    print("\n📁 Data Configuration:")
    data_config = get_data_config()
    for key, value in data_config.items():
        print(f"  • {key}: {value}")
    
    print(f"\n✅ Configuration Valid: {'Yes' if validate_config() else 'No'}")


def cmd_test(args):
    """Run tests."""
    try:
        import pytest
        test_dir = Path(__file__).parent / "tests"
        exit_code = pytest.main([str(test_dir), "-v"])
        sys.exit(exit_code)
    except ImportError:
        logger.error("pytest not installed. Install with: pip install pytest")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Confluence Knowledge Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s serve                    # Start the server
  %(prog)s validate                 # Validate data structure
  %(prog)s stats                    # Show knowledge base stats
  %(prog)s summary                  # Show data directory summary
  %(prog)s config                   # Show configuration
  %(prog)s test                     # Run tests
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the server")
    serve_parser.set_defaults(func=cmd_serve)
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate data structure")
    validate_parser.add_argument("--data-dir", help="Data directory to validate")
    validate_parser.set_defaults(func=cmd_validate)
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show knowledge base statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show data directory summary")
    summary_parser.add_argument("--data-dir", help="Data directory to summarize")
    summary_parser.set_defaults(func=cmd_summary)
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")
    config_parser.set_defaults(func=cmd_config)
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.set_defaults(func=cmd_test)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
