import requests
import os
import json
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfluenceScraper:
    def __init__(self, confluence_base_url):
        """Initialize the scraper with your Confluence base URL.
        
        Since you're using SSO on your local machine, we'll rely on your browser cookies.
        """
        self.confluence_base_url = confluence_base_url
        self.session = requests.Session()
        # The session will use your browser cookies for authentication
        
    def get_all_spaces(self):
        """Get all available Confluence spaces"""
        url = urljoin(self.confluence_base_url, "rest/api/space")
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()["results"]
        except Exception as e:
            logger.error(f"Failed to get spaces: {e}")
            return []
    
    def get_pages_in_space(self, space_key):
        """Get all pages in a specific space"""
        pages = []
        start = 0
        limit = 100
        
        while True:
            url = urljoin(self.confluence_base_url, 
                         f"rest/api/content?spaceKey={space_key}&limit={limit}&start={start}")
            try:
                response = self.session.get(url)
                response.raise_for_status()
                
                batch = response.json()["results"]
                if not batch:
                    break
                    
                pages.extend(batch)
                start += limit
                logger.info(f"Retrieved {len(pages)} pages from space {space_key}")
            except Exception as e:
                logger.error(f"Failed to get pages for space {space_key}: {e}")
                break
                
        return pages
    
    def get_page_content(self, page_id):
        """Get the content of a specific page"""
        url = urljoin(self.confluence_base_url, 
                     f"rest/api/content/{page_id}?expand=body.storage,version")
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get content for page {page_id}: {e}")
            return None
    
    def extract_text_from_html(self, html_content):
        """Extract clean text from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    
    def save_pages_to_disk(self, output_dir, space_keys=None):
        """Save all pages to disk for local processing"""
        os.makedirs(output_dir, exist_ok=True)
        
        if not space_keys:
            spaces = self.get_all_spaces()
            space_keys = [space["key"] for space in spaces]
        
        all_pages = []
        
        for space_key in space_keys:
            space_dir = os.path.join(output_dir, space_key)
            os.makedirs(space_dir, exist_ok=True)
            
            pages = self.get_pages_in_space(space_key)
            
            for page in pages:
                page_content = self.get_page_content(page["id"])
                if not page_content:
                    continue
                
                html_content = page_content["body"]["storage"]["value"]
                text_content = self.extract_text_from_html(html_content)
                
                metadata = {
                    "id": page["id"],
                    "title": page["title"],
                    "url": urljoin(self.confluence_base_url, f"pages/viewpage.action?pageId={page['id']}"),
                    "last_updated": page_content["version"]["when"],
                    "space_key": space_key
                }
                
                # Save the page content and metadata
                page_file = os.path.join(space_dir, f"{page['id']}.json")
                with open(page_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "metadata": metadata,
                        "content": text_content
                    }, f, ensure_ascii=False, indent=2)
                
                all_pages.append(metadata)
                logger.info(f"Saved page: {metadata['title']}")
        
        # Save an index of all pages
        index_file = os.path.join(output_dir, "index.json")
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(all_pages, f, ensure_ascii=False, indent=2)
        
        return all_pages