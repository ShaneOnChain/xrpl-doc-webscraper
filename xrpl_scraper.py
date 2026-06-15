import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("xrpl_scraper")

class XRPLDocScraper:
    """
    Scraper for XRPL-py documentation that extracts content and saves it in a structured format
    for use with LLM/AI models.
    """
    
    def __init__(self, base_url="https://xrpl-py.readthedocs.io/en/stable/", output_dir="xrpl_docs"):
        """
        Initialize the scraper with base URL and output directory
        
        Args:
            base_url: The base URL of the documentation
            output_dir: Directory to save the extracted content
        """
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls = set()
        self.section_data = {}
        
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Create subdirectories for different sections
        self.sections = [
            "account", "ledger", "transaction", "wallet", 
            "clients", "models", "utils", "core", "asyncio"
        ]
        
        for section in self.sections:
            section_dir = os.path.join(output_dir, section)
            if not os.path.exists(section_dir):
                os.makedirs(section_dir)
    
    def get_page(self, url):
        """
        Fetch a page and return the BeautifulSoup object
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object of the page content
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def clean_text(self, text):
        """
        Clean text by removing extra whitespace and normalizing
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        # Replace multiple whitespace with a single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        return text.strip()
    
    def extract_method_details(self, soup, section):
        """
        Extract details about methods from the page
        
        Args:
            soup: BeautifulSoup object
            section: Section name
            
        Returns:
            List of method details
        """
        methods = []
        
        # Look for method sections
        method_sections = soup.select("dl.py.method, dl.py.function, dl.py.class")
        
        for method_section in method_sections:
            method_info = {}
            
            # Get name
            name_tag = method_section.select_one("dt")
            if name_tag:
                method_id = name_tag.get('id', '')
                method_info['id'] = method_id
                
                # Extract method name
                name_signature = name_tag.select_one("code.sig-name")
                if name_signature:
                    method_info['name'] = name_signature.get_text()
                else:
                    # Fallback
                    method_info['name'] = method_id.split('.')[-1] if method_id else "unknown"
                
                # Extract full signature
                signature = name_tag.select_one("span.sig-prename, span.sig-name, span.sig-paren")
                if signature:
                    method_info['signature'] = name_tag.get_text().strip()
                else:
                    method_info['signature'] = method_info['name']
            
            # Get description and parameters
            desc_tag = method_section.select_one("dd")
            if desc_tag:
                # Get main description
                description_parts = []
                for p in desc_tag.select("p"):
                    description_parts.append(self.clean_text(p.get_text()))
                
                method_info['description'] = "\n".join(description_parts)
                
                # Get parameters
                params = []
                param_list = desc_tag.select("dl.field-list dt.field-odd:contains('Parameters'), dl.field-list dt:contains('Parameters')")
                for param_header in param_list:
                    param_desc = param_header.find_next("dd")
                    if param_desc:
                        param_items = param_desc.select("li") or [param_desc]
                        for item in param_items:
                            param_text = self.clean_text(item.get_text())
                            if param_text:
                                params.append(param_text)
                
                method_info['parameters'] = params
                
                # Get return value
                returns = []
                return_headers = desc_tag.select("dl.field-list dt.field-even:contains('Returns'), dl.field-list dt:contains('Returns')")
                for return_header in return_headers:
                    return_desc = return_header.find_next("dd")
                    if return_desc:
                        return_text = self.clean_text(return_desc.get_text())
                        if return_text:
                            returns.append(return_text)
                
                method_info['returns'] = returns
                
                # Get examples if available
                examples = []
                example_headers = desc_tag.select("p:contains('Example'), strong:contains('Example')")
                for ex_header in example_headers:
                    # Look for code blocks after example headers
                    example_code = ex_header.find_next("pre")
                    if example_code:
                        examples.append(example_code.get_text())
                
                method_info['examples'] = examples
            
            methods.append(method_info)
        
        return methods
    
    def extract_class_details(self, soup, section):
        """
        Extract details about classes from the page
        
        Args:
            soup: BeautifulSoup object
            section: Section name
            
        Returns:
            List of class details
        """
        classes = []
        
        # Find class definitions
        class_sections = soup.select("dl.py.class")
        
        for class_section in class_sections:
            class_info = {}
            
            # Get name
            name_tag = class_section.select_one("dt")
            if name_tag:
                class_id = name_tag.get('id', '')
                class_info['id'] = class_id
                
                # Extract class name
                name_signature = name_tag.select_one("code.sig-name")
                if name_signature:
                    class_info['name'] = name_signature.get_text()
                else:
                    # Fallback
                    class_info['name'] = class_id.split('.')[-1] if class_id else "unknown"
                
                # Extract full signature
                class_info['signature'] = name_tag.get_text().strip()
            
            # Get description and methods
            desc_tag = class_section.select_one("dd")
            if desc_tag:
                # Get main description
                description_parts = []
                for p in desc_tag.select("p"):
                    description_parts.append(self.clean_text(p.get_text()))
                
                class_info['description'] = "\n".join(description_parts)
                
                # Get class methods
                methods = self.extract_method_details(desc_tag, section)
                class_info['methods'] = methods
                
                # Get attributes if any
                attributes = []
                attr_sections = desc_tag.select("dl.py.attribute")
                for attr_section in attr_sections:
                    attr_info = {}
                    attr_name_tag = attr_section.select_one("dt")
                    if attr_name_tag:
                        attr_info['name'] = attr_name_tag.get_text().strip()
                        attr_info['id'] = attr_name_tag.get('id', '')
                    
                    attr_desc_tag = attr_section.select_one("dd")
                    if attr_desc_tag:
                        attr_info['description'] = self.clean_text(attr_desc_tag.get_text())
                    
                    attributes.append(attr_info)
                
                class_info['attributes'] = attributes
            
            classes.append(class_info)
        
        return classes
    
    def extract_module_details(self, soup, url, section):
        """
        Extract module details from a page
        
        Args:
            soup: BeautifulSoup object
            url: URL of the page
            section: Section name
            
        Returns:
            Dictionary with module details
        """
        module_info = {
            'url': url,
            'section': section,
            'name': '',
            'description': '',
            'classes': [],
            'methods': [],
            'submodules': []
        }
        
        # Extract module name from title
        title_tag = soup.select_one("h1")
        if title_tag:
            module_info['name'] = self.clean_text(title_tag.get_text())
        
        # Extract module description
        desc_section = soup.select_one("section#module-contents")
        if desc_section:
            p_tags = desc_section.select("p")
            if p_tags:
                desc_text = [self.clean_text(p.get_text()) for p in p_tags]
                module_info['description'] = "\n".join(desc_text)
        
        # Extract classes
        module_info['classes'] = self.extract_class_details(soup, section)
        
        # Extract standalone methods (not part of a class)
        module_info['methods'] = self.extract_method_details(soup, section)
        
        # Look for submodule links
        module_section = soup.select_one("section#module-contents, div.toctree-wrapper")
        if module_section:
            submodule_links = module_section.select("a.reference.internal")
            for link in submodule_links:
                href = link.get('href', '')
                if href and not href.startswith('#') and 'xrpl' in href:
                    submodule_name = link.get_text().strip()
                    submodule_url = urljoin(url, href)
                    if submodule_url not in self.visited_urls and submodule_name:
                        module_info['submodules'].append({
                            'name': submodule_name,
                            'url': submodule_url
                        })
        
        return module_info
    
    def save_module_info(self, module_info):
        """
        Save module information to JSON files
        
        Args:
            module_info: Dictionary with module details
        """
        section = module_info.get('section', 'general')
        name = module_info.get('name', 'unknown').replace(' ', '_').lower()
        
        # Clean the name for file saving
        name = re.sub(r'[^\w\-_]', '', name)
        
        # Create the output file path
        output_file = os.path.join(self.output_dir, section, f"{name}.json")
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(module_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved module info to {output_file}")
    
    def scrape_url(self, url, section):
        """
        Scrape a URL and its submodules recursively
        
        Args:
            url: URL to scrape
            section: Section identifier
        """
        # Check if already visited
        if url in self.visited_urls:
            return
        
        logger.info(f"Scraping {url}")
        self.visited_urls.add(url)
        
        # Get the page
        soup = self.get_page(url)
        if not soup:
            logger.error(f"Failed to get page: {url}")
            return
        
        # Extract module details
        module_info = self.extract_module_details(soup, url, section)
        
        # Save info to file
        self.save_module_info(module_info)
        
        # Process submodules
        for submodule in module_info['submodules']:
            submodule_url = submodule['url']
            if submodule_url not in self.visited_urls:
                # Add a small delay to avoid overwhelming the server
                time.sleep(1)
                self.scrape_url(submodule_url, section)
    
    def scrape_main_sections(self):
        """
        Scrape the main documentation sections
        """
        section_urls = {
            "account": "source/xrpl.account.html",
            "ledger": "source/xrpl.ledger.html",
            "transaction": "source/xrpl.transaction.html",
            "wallet": "source/xrpl.wallet.html",
            "clients": "source/xrpl.clients.html",
            "models": "source/xrpl.models.html",
            "utils": "source/xrpl.utils.html",
            "core": "source/xrpl.core.html",
            "asyncio": "source/xrpl.asyncio.html"
        }
        
        for section, path in section_urls.items():
            url = urljoin(self.base_url, path)
            logger.info(f"Starting scrape of section: {section}")
            self.scrape_url(url, section)
    
    def create_index_file(self):
        """
        Create an index file that contains links to all scraped sections
        """
        index = {
            "base_url": self.base_url,
            "sections": {}
        }
        
        # For each section, list all files
        for section in self.sections:
            section_dir = os.path.join(self.output_dir, section)
            index["sections"][section] = []
            
            if os.path.exists(section_dir):
                for filename in os.listdir(section_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(section_dir, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                module_data = json.load(f)
                                
                                index["sections"][section].append({
                                    "name": module_data.get("name", ""),
                                    "url": module_data.get("url", ""),
                                    "file": filename,
                                    "classes": len(module_data.get("classes", [])),
                                    "methods": len(module_data.get("methods", []))
                                })
                        except json.JSONDecodeError:
                            logger.error(f"Error reading JSON file: {file_path}")
        
        # Save the index
        index_path = os.path.join(self.output_dir, "index.json")
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created index file at {index_path}")

def main():
    """
    Main function to run the scraper
    """
    scraper = XRPLDocScraper()
    scraper.scrape_main_sections()
    scraper.create_index_file()
    logger.info("Scraping completed!")

if __name__ == "__main__":
    main()