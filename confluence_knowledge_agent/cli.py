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
# from .data.validator import validate_data_structure, get_data_summary  # Removed for production
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

    print(f"🔍 Checking data structure in: {data_dir}")

    from pathlib import Path
    data_path = Path(data_dir)

    if not data_path.exists():
        print("❌ Data directory does not exist. Run scrape command first.")
        sys.exit(1)

    index_file = data_path / "index.json"
    if not index_file.exists():
        print("❌ Index file missing. Run scrape command to generate data.")
        sys.exit(1)

    print("✅ Basic data structure is valid!")


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

    print(f"📊 Data Directory Summary: {data_dir}")

    try:
        from pathlib import Path
        data_path = Path(data_dir)

        if not data_path.exists():
            print("❌ Data directory does not exist. Run scrape command first.")
            return

        # Count files and directories
        json_files = list(data_path.glob("**/*.json"))
        spaces = [d.name for d in data_path.iterdir() if d.is_dir() and d.name != "vector_db"]

        print(f"  • Exists: ✅")
        print(f"  • Total JSON Files: {len(json_files)}")
        print(f"  • Total Spaces: {len(spaces)}")
        print(f"  • Spaces: {', '.join(spaces) if spaces else 'None'}")

        # Check for index file
        index_file = data_path / "index.json"
        print(f"  • Index file: {'✅' if index_file.exists() else '❌'}")

    except Exception as e:
        print(f"❌ Error reading data directory: {e}")


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
    print("🧪 Test functionality removed for production build.")
    print("✅ Use the scraper and serve commands for production usage.")


def cmd_scrape(args):
    """Scrape COM Insurance Confluence space."""
    from .data.scraper import ConfluenceCloudScraper

    print("🚀 COM Insurance Confluence Scraper")
    print("=" * 50)
    print(f"Space: {args.space_key}")
    print(f"Output: {args.output_dir}")
    print("-" * 50)

    try:
        scraper = ConfluenceCloudScraper()
        scraper.space_key = args.space_key

        # Test connection
        print("Testing connection to Confluence...")
        if not scraper.test_connection():
            print("\n❌ Connection failed. Please:")
            print("1. Open Chrome and log into https://COMinsurence.atlassian.net")
            print("2. Make sure you have access to the EQE space")
            print("3. Run this command again")
            return

        print("✅ Connection successful!")

        # Start scraping
        print(f"\nStarting to scrape space: {args.space_key}")
        result = scraper.scrape_space_to_files(args.output_dir, args.space_key)

        if result:
            print(f"\n🎉 Scraping completed!")
            print(f"✅ Successfully processed: {result['success']} pages")
            print(f"📁 Files saved to: {result['output_dir']}")
            print(f"📋 Index file: {result['index_file']}")

            if result['failed'] > 0:
                print(f"⚠️  Failed to process: {result['failed']} pages")

            print(f"\n🔄 Next steps:")
            print(f"1. Run 'python3 -m confluence_knowledge_agent.cli validate' to check data")
            print(f"2. Run 'python3 -m confluence_knowledge_agent.cli serve' to start the agent")
        else:
            print("❌ Scraping failed. Check the logs for details.")

    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Scraping failed")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Confluence Knowledge Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scrape                   # Scrape COM Insurance Confluence space
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

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape COM Insurance Confluence space")
    scrape_parser.add_argument("--output-dir", default="confluence_data", help="Output directory for scraped data")
    scrape_parser.add_argument("--space-key", default="EQE", help="Confluence space key to scrape")
    scrape_parser.set_defaults(func=cmd_scrape)
    
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
