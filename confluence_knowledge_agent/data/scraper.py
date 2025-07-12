import requests
import os
import json
import sqlite3
import time
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
from pathlib import Path
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfluenceCloudScraper:
    def __init__(self, confluence_base_url: str = "https://COMinsurence.atlassian.net"):
        """Initialize the scraper for COM Insurance Confluence Cloud.

        Uses Chrome browser cookies for authentication.
        """
        self.confluence_base_url = confluence_base_url
        self.space_key = "EQE"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        # Load Chrome cookies
        self._load_chrome_cookies()

    def _load_chrome_cookies(self):
        """Load cookies from Chrome browser for Confluence authentication."""
        try:
            # Chrome cookies database path on macOS
            chrome_cookies_path = Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"

            if not chrome_cookies_path.exists():
                logger.warning("Chrome cookies database not found. Please ensure Chrome is installed and you're logged into Confluence.")
                return

            # Copy the cookies database to avoid locking issues
            import tempfile
            import shutil
            temp_cookies = tempfile.NamedTemporaryFile(delete=False)
            shutil.copy2(chrome_cookies_path, temp_cookies.name)

            # Connect to Chrome cookies database
            conn = sqlite3.connect(temp_cookies.name)
            cursor = conn.cursor()

            # Query cookies for Confluence domain
            cursor.execute("""
                SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly
                FROM cookies
                WHERE host_key LIKE '%atlassian.net%' OR host_key LIKE '%COMinsurence.atlassian.net%'
            """)

            cookies_loaded = 0
            for row in cursor.fetchall():
                name, value, host_key, path, expires_utc, is_secure, is_httponly = row

                # Convert Chrome timestamp to Unix timestamp
                if expires_utc > 0:
                    # Chrome uses microseconds since 1601-01-01, convert to Unix timestamp
                    expires = (expires_utc / 1000000) - 11644473600
                else:
                    expires = None

                # Add cookie to session
                self.session.cookies.set(
                    name=name,
                    value=value,
                    domain=host_key,
                    path=path,
                    secure=bool(is_secure),
                    expires=expires
                )
                cookies_loaded += 1

            conn.close()
            os.unlink(temp_cookies.name)  # Clean up temp file

            logger.info(f"Loaded {cookies_loaded} cookies from Chrome for Confluence authentication")

        except Exception as e:
            logger.error(f"Failed to load Chrome cookies: {e}")
            logger.info("You may need to manually log into Confluence in Chrome first")

    def get_space_pages(self, space_key: str = None) -> List[Dict[str, Any]]:
        """Get all pages from the EQE space."""
        if space_key is None:
            space_key = self.space_key

        all_pages = []
        start = 0
        limit = 50

        while True:
            url = f"{self.confluence_base_url}/wiki/rest/api/content"
            params = {
                'spaceKey': space_key,
                'type': 'page',
                'status': 'current',
                'expand': 'body.storage,metadata.labels,space,version,ancestors',
                'start': start,
                'limit': limit
            }

            try:
                logger.info(f"Fetching pages {start}-{start+limit} from space {space_key}")
                response = self.session.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                pages = data.get('results', [])

                if not pages:
                    break

                all_pages.extend(pages)

                # Check if there are more pages
                if len(pages) < limit:
                    break

                start += limit
                time.sleep(0.5)  # Be respectful to the API

            except Exception as e:
                logger.error(f"Failed to get pages from space {space_key}: {e}")
                break

        logger.info(f"Found {len(all_pages)} pages in space {space_key}")
        return all_pages

    def parse_page_content(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and clean page content from Confluence API response."""
        try:
            page_id = page_data['id']
            title = page_data['title']

            # Get the storage format content
            body_storage = page_data.get('body', {}).get('storage', {})
            raw_content = body_storage.get('value', '')

            # Parse HTML content with BeautifulSoup
            soup = BeautifulSoup(raw_content, 'html.parser')

            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'meta', 'link']):
                element.decompose()

            # Extract text content
            text_content = soup.get_text(separator='\n', strip=True)

            # Clean up the text
            lines = text_content.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('//') and len(line) > 2:
                    cleaned_lines.append(line)

            content = '\n'.join(cleaned_lines)

            # Extract metadata
            space_info = page_data.get('space', {})
            version_info = page_data.get('version', {})
            labels = [label['name'] for label in page_data.get('metadata', {}).get('labels', {}).get('results', [])]

            # Build page URL
            page_url = f"{self.confluence_base_url}/wiki/spaces/{space_info.get('key', '')}/pages/{page_id}"

            # Get author information
            author = version_info.get('by', {}).get('displayName', 'Unknown')
            last_updated = version_info.get('when', '')

            return {
                'id': page_id,
                'title': title,
                'content': content,
                'url': page_url,
                'space_key': space_info.get('key', ''),
                'space_name': space_info.get('name', ''),
                'author': author,
                'last_updated': last_updated,
                'labels': labels,
                'version': version_info.get('number', 1)
            }

        except Exception as e:
            logger.error(f"Failed to parse page content: {e}")
            return None

    def scrape_space_to_files(self, output_dir: str = "confluence_data", space_key: str = None):
        """Scrape the entire EQE space and save to files."""
        if space_key is None:
            space_key = self.space_key

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Create space directory
        space_dir = output_path / space_key
        space_dir.mkdir(exist_ok=True)

        logger.info(f"Starting to scrape Confluence space: {space_key}")
        logger.info(f"Output directory: {output_path}")

        # Get all pages from the space
        pages = self.get_space_pages(space_key)

        if not pages:
            logger.error("No pages found. Please check your authentication and space access.")
            return

        # Process each page
        processed_pages = []
        failed_pages = []

        for i, page_data in enumerate(pages, 1):
            try:
                logger.info(f"Processing page {i}/{len(pages)}: {page_data['title']}")

                # Parse page content
                parsed_page = self.parse_page_content(page_data)

                if parsed_page:
                    # Save page to file
                    page_filename = f"{parsed_page['id']}.json"
                    page_file_path = space_dir / page_filename

                    with open(page_file_path, 'w', encoding='utf-8') as f:
                        json.dump(parsed_page, f, indent=2, ensure_ascii=False)

                    processed_pages.append({
                        'id': parsed_page['id'],
                        'space_key': space_key,
                        'title': parsed_page['title'],
                        'url': parsed_page['url'],
                        'last_updated': parsed_page['last_updated']
                    })

                    logger.info(f"✅ Saved: {parsed_page['title']}")
                else:
                    failed_pages.append(page_data['title'])
                    logger.error(f"❌ Failed to process: {page_data['title']}")

                # Small delay to be respectful
                time.sleep(0.2)

            except Exception as e:
                failed_pages.append(page_data.get('title', 'Unknown'))
                logger.error(f"❌ Error processing page: {e}")

        # Create index file
        index_file_path = output_path / "index.json"
        with open(index_file_path, 'w', encoding='utf-8') as f:
            json.dump(processed_pages, f, indent=2, ensure_ascii=False)

        # Summary
        logger.info(f"\n🎉 Scraping completed!")
        logger.info(f"✅ Successfully processed: {len(processed_pages)} pages")
        logger.info(f"❌ Failed to process: {len(failed_pages)} pages")
        logger.info(f"📁 Files saved to: {output_path}")
        logger.info(f"📋 Index file: {index_file_path}")

        if failed_pages:
            logger.warning(f"Failed pages: {', '.join(failed_pages)}")

        return {
            'success': len(processed_pages),
            'failed': len(failed_pages),
            'output_dir': str(output_path),
            'index_file': str(index_file_path)
        }

    def test_connection(self) -> bool:
        """Test if we can connect to Confluence with current authentication."""
        try:
            url = f"{self.confluence_base_url}/wiki/rest/api/space/{self.space_key}"
            response = self.session.get(url)

            if response.status_code == 200:
                space_info = response.json()
                logger.info(f"✅ Successfully connected to space: {space_info.get('name', 'Unknown')}")
                return True
            elif response.status_code == 401:
                logger.error("❌ Authentication failed. Please log into Confluence in Chrome first.")
                return False
            elif response.status_code == 403:
                logger.error("❌ Access denied. You may not have permission to access this space.")
                return False
            else:
                logger.error(f"❌ Connection failed with status code: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False


def main():
    """Main function to scrape COM Insurance Confluence space."""
    print("🚀 COM Insurance Confluence Scraper")
    print("=" * 50)

    # Initialize scraper
    scraper = ConfluenceCloudScraper()

    # Test connection first
    print("Testing connection to Confluence...")
    if not scraper.test_connection():
        print("\n❌ Connection failed. Please:")
        print("1. Open Chrome and log into https://COMinsurence.atlassian.net")
        print("2. Make sure you have access to the EQE space")
        print("3. Run this script again")
        return

    print("✅ Connection successful!")

    # Start scraping
    print(f"\nStarting to scrape space: {scraper.space_key}")
    result = scraper.scrape_space_to_files()

    if result:
        print(f"\n🎉 Scraping completed successfully!")
        print(f"📊 Pages processed: {result['success']}")
        print(f"📁 Output directory: {result['output_dir']}")
        print(f"📋 Index file: {result['index_file']}")

        if result['failed'] > 0:
            print(f"⚠️  Failed pages: {result['failed']}")
    else:
        print("❌ Scraping failed. Check the logs above for details.")


if __name__ == "__main__":
    main()