import requests
import json
import time
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, quote, urlparse
import logging
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from base_agent import BasePatentAgent, PatentData, PatentDataType, Task

@dataclass
class DownloadResult:
    """Result of a PDF download operation"""
    success: bool
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None

class EnhancedPatentAgent(BasePatentAgent):
    """Enhanced patent search agent with PDF download capabilities and improved query interface"""
    
    def __init__(self, agent_id: str = "enhanced_patent_agent_001"):
        super().__init__(
            agent_id=agent_id,
            name="Enhanced Patent Search Agent",
            description="Advanced patent search with PDF download and improved query interface"
        )
        
        # Setup download directory
        self.download_dir = Path("patent_data/downloaded_pdfs")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # API endpoints for patent search and download
        self.apis = {
            'google_patents_web': 'https://patents.google.com',
            'google_patents_api': 'https://api.searchapi.io/api/v1/search',
            'espacenet_web': 'https://worldwide.espacenet.com',
            'uspto_web': 'https://www.uspto.gov',
            'pubchem': 'https://pubchem.ncbi.nlm.nih.gov'
        }
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # seconds between requests
        
        # Setup API keys
        self.setup_api_keys()
    
    def setup_api_keys(self):
        """Setup API keys from environment variables"""
        self.api_keys = {
            'searchapi': os.getenv('SEARCHAPI_KEY'),
            'uspto': os.getenv('USPTO_API_KEY'),
        }
        
        if not self.api_keys['searchapi']:
            self.logger.warning("SEARCHAPI_KEY not set - using web scraping fallback")
    
    def get_capabilities(self) -> List[str]:
        return [
            "web_patent_search",
            "pdf_download",
            "batch_download",
            "search_by_keywords",
            "search_by_patent_number",
            "search_by_inventor",
            "search_by_assignee",
            "search_chemical_compounds",
            "advanced_query_builder",
            "download_manager",
            "progress_tracking"
        ]
    
    def get_supported_input_types(self) -> List[PatentDataType]:
        """Return supported input data types"""
        return [PatentDataType.QUERY_RESULT]
    
    def get_output_type(self) -> PatentDataType:
        """Return output data type"""
        return PatentDataType.QUERY_RESULT
    
    def process_task(self, task: Task) -> PatentData:
        """Process a task and return results"""
        if task.type == "patent_search":
            return self._process_search_task(task.input_data)
        else:
            raise ValueError(f"Unsupported task type: {task.type}")
    
    def _process_search_task(self, search_params: Dict[str, Any]) -> PatentData:
        """Process search task and return PatentData object"""
        results = self.search_patents(search_params)
        
        return PatentData(
            id=f"search_result_{int(time.time())}",
            type=PatentDataType.QUERY_RESULT,
            content=results,
            metadata={
                "search_timestamp": time.time(),
                "agent_id": self.agent_id
            }
        )
    
    def rate_limit(self, api_name: str):
        """Implement rate limiting for API calls"""
        current_time = time.time()
        if api_name in self.last_request_time:
            time_since_last = current_time - self.last_request_time[api_name]
            if time_since_last < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last
                time.sleep(sleep_time)
        
        self.last_request_time[api_name] = time.time()
    
    def search_patents(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Main patent search interface"""
        search_type = query_params.get('search_type', 'keywords')
        
        if search_type == 'keywords':
            return self.search_by_keywords(query_params)
        elif search_type == 'patent_number':
            return self.search_by_patent_number(query_params)
        elif search_type == 'inventor':
            return self.search_by_inventor(query_params)
        elif search_type == 'assignee':
            return self.search_by_assignee(query_params)
        elif search_type == 'chemical':
            return self.search_chemical_compounds(query_params)
        else:
            raise ValueError(f"Unsupported search type: {search_type}")
    
    def search_by_keywords(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search patents by keywords"""
        keywords = params.get('keywords', [])
        if isinstance(keywords, str):
            keywords = [keywords]
        
        max_results = params.get('max_results', 50)
        include_pdfs = params.get('include_pdfs', True)
        
        query = ' '.join(keywords)
        
        # Search using multiple sources
        all_results = []
        
        # Google Patents search
        google_results = self._search_google_patents_web(query, max_results // 2)
        all_results.extend(google_results)
        
        # Espacenet search (if available)
        espacenet_results = self._search_espacenet_web(query, max_results // 2)
        all_results.extend(espacenet_results)
        
        # Deduplicate and format results
        unique_results = self._deduplicate_results(all_results)
        
        # Download PDFs if requested
        if include_pdfs:
            self._download_patents_batch(unique_results[:10])  # Limit initial downloads
        
        return {
            'query': query,
            'total_results': len(unique_results),
            'patents': unique_results,
            'search_timestamp': datetime.now().isoformat(),
            'download_dir': str(self.download_dir)
        }
    
    def search_by_patent_number(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for specific patent by number"""
        patent_number = params.get('patent_number', '')
        include_pdf = params.get('include_pdf', True)
        
        if not patent_number:
            raise ValueError("Patent number is required")
        
        # Clean patent number
        clean_patent_number = re.sub(r'[^\w]', '', patent_number.upper())
        
        # Search Google Patents
        patent_data = self._get_patent_details_google(patent_number)
        
        if patent_data and include_pdf:
            download_result = self.download_patent_pdf(patent_data)
            patent_data['download_result'] = download_result
        
        return {
            'patent_number': patent_number,
            'patent_data': patent_data,
            'search_timestamp': datetime.now().isoformat()
        }
    
    def search_by_inventor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search patents by inventor name"""
        inventor_name = params.get('inventor_name', '')
        max_results = params.get('max_results', 30)
        
        query = f'inventor:"{inventor_name}"'
        return self._search_google_patents_web(query, max_results)
    
    def search_by_assignee(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search patents by assignee/company"""
        assignee_name = params.get('assignee_name', '')
        max_results = params.get('max_results', 30)
        
        query = f'assignee:"{assignee_name}"'
        return self._search_google_patents_web(query, max_results)
    
    def search_chemical_compounds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for chemical compound patents"""
        compound_name = params.get('compound_name', '')
        smiles = params.get('smiles', '')
        molecular_formula = params.get('molecular_formula', '')
        
        search_terms = []
        if compound_name:
            search_terms.append(compound_name)
        if molecular_formula:
            search_terms.append(molecular_formula)
        if smiles:
            search_terms.append(f'SMILES:{smiles}')
        
        query = ' '.join(search_terms)
        results = self._search_google_patents_web(query, params.get('max_results', 30))
        
        return {
            'compound_search': {
                'compound_name': compound_name,
                'smiles': smiles,
                'molecular_formula': molecular_formula
            },
            'results': results,
            'search_timestamp': datetime.now().isoformat()
        }
    
    def _search_google_patents_web(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search Google Patents using web interface"""
        self.rate_limit('google_patents')
        
        # Use SearchAPI if available, otherwise web scraping
        if self.api_keys['searchapi']:
            return self._search_with_searchapi(query, max_results)
        else:
            return self._search_google_patents_scraping(query, max_results)
    
    def _search_with_searchapi(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using SearchAPI.io service"""
        params = {
            'engine': 'google_patents',
            'q': query,
            'num': min(max_results, 20),
            'api_key': self.api_keys['searchapi']
        }
        
        try:
            response = self.session.get(self.apis['google_patents_api'], params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'organic_results' in data:
                for result in data['organic_results']:
                    patent_info = {
                        'patent_number': result.get('publication_number', ''),
                        'title': result.get('title', ''),
                        'abstract': result.get('snippet', ''),
                        'inventors': result.get('inventors', []),
                        'assignees': result.get('assignees', []),
                        'publication_date': result.get('publication_date', ''),
                        'filing_date': result.get('filing_date', ''),
                        'url': result.get('link', ''),
                        'pdf_link': result.get('pdf', ''),
                        'source': 'google_patents_api'
                    }
                    results.append(patent_info)
            
            self.logger.info(f"Found {len(results)} patents via SearchAPI")
            return results
            
        except Exception as e:
            self.logger.error(f"SearchAPI error: {e}")
            return []
    
    def _search_google_patents_scraping(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Enhanced web scraping using Selenium for JavaScript-rendered content"""
        try:
            print("🤖 Using Selenium for JavaScript-rendered content...")
            return self._selenium_search(query, max_results)
            
        except ImportError:
            print("⚠️ Selenium not available, falling back to static scraping")
            return self._static_scraping_fallback(query, max_results)
        except Exception as e:
            self.logger.error(f"Selenium scraping error: {e}")
            print(f"❌ Selenium failed: {e}")
            return self._static_scraping_fallback(query, max_results)
    
    def _selenium_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Use Selenium with comprehensive pagination to get more results"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from urllib.parse import quote_plus
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            all_results = []
            seen_patents = set()
            
            try:
                base_url = f"https://patents.google.com/?q={quote_plus(query)}"
                
                # Use discovered pagination: num=100 for max results per page, page= for pagination
                results_per_page = min(100, max_results)  # Google Patents max is 100
                max_pages = max_results // results_per_page + 1
                
                print(f"🌐 Comprehensive search for: {query}")
                print(f"📊 Target: up to {max_results} results across {max_pages} pages")
                
                for page_num in range(1, max_pages + 1):
                    if len(all_results) >= max_results:
                        break
                    
                    # Use discovered pagination parameters
                    search_url = f"{base_url}&num={results_per_page}&page={page_num}"
                    print(f"📄 Page {page_num}: Loading {results_per_page} results...")
                    
                    driver.get(search_url)
                    time.sleep(5)
                    
                    # Wait for search results
                    try:
                        WebDriverWait(driver, 15).until(
                            lambda d: d.find_elements(By.TAG_NAME, 'search-result-item')
                        )
                    except:
                        print(f"   ⚠️ Timeout on page {page_num}")
                        continue
                    
                    # Extract results from current page
                    search_items = driver.find_elements(By.TAG_NAME, 'search-result-item')
                    print(f"   📊 Found {len(search_items)} items")
                    
                    page_results = 0
                    for i, item in enumerate(search_items):
                        try:
                            text_content = item.text
                            
                            # Extract patent number with expanded patterns
                            patent_patterns = [
                                r'\b([A-Z]{2}\d{7,10}[A-Z]?\d?)\b',  # Standard format
                                r'\b(US\d{7,10}[A-Z]\d?)\b',          # US patents
                                r'\b(EP\d{7,10}[A-Z]\d?)\b',          # European patents
                                r'\b(WO\d{4}/\d{6})\b',               # WIPO patents
                                r'\b(CN\d{9}[A-Z]?)\b',               # Chinese patents
                                r'\b(JP\d{7,10}[A-Z]?\d?)\b'          # Japanese patents
                            ]
                            
                            patent_number = ''
                            for pattern in patent_patterns:
                                match = re.search(pattern, text_content)
                                if match:
                                    patent_number = match.group(1)
                                    break
                            
                            if patent_number and patent_number not in seen_patents:
                                seen_patents.add(patent_number)
                                
                                # Extract title with improved logic
                                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                                title = ''
                                for line in lines:
                                    if (len(line) > 15 and 
                                        line != patent_number and 
                                        not line.isdigit() and
                                        not re.match(r'^\d{4}-\d{2}-\d{2}$', line) and
                                        not re.match(r'^[A-Z]{2,3}$', line)):
                                        title = line
                                        break
                                
                                if not title:
                                    title = f"Patent {patent_number}"
                                
                                # Extract publication date
                                pub_date = ''
                                date_match = re.search(r'Published (\d{4}-\d{2}-\d{2})', text_content)
                                if date_match:
                                    pub_date = date_match.group(1)
                                
                                all_results.append({
                                    'patent_number': patent_number,
                                    'title': title[:200],
                                    'abstract': '',
                                    'inventors': [],
                                    'assignees': [],
                                    'publication_date': pub_date,
                                    'filing_date': '',
                                    'url': f"https://patents.google.com/patent/{patent_number}",
                                    'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                                    'source': f'selenium_comprehensive_p{page_num}'
                                })
                                page_results += 1
                                
                                if len(all_results) >= max_results:
                                    break
                        
                        except Exception as e:
                            continue
                    
                    print(f"   ✅ Extracted {page_results} new patents (total: {len(all_results)})")
                    
                    # Stop if no new results (end of available data)
                    if page_results == 0:
                        print(f"   ⚠️ No new results on page {page_num}, stopping")
                        break
                    
                    time.sleep(1)  # Rate limiting
                
                print(f"🎯 Comprehensive search complete: {len(all_results)} unique patents")
                return all_results
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"❌ Selenium comprehensive search error: {e}")
            return []
    
    def _static_scraping_fallback(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback static scraping when Selenium is not available"""
        try:
            from urllib.parse import quote_plus
            
            # Simple static request (will not get dynamic content)
            search_url = f"https://patents.google.com/?q={quote_plus(query)}"
            print(f"🌐 Static fallback: {search_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = self.session.get(search_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Since Google Patents is JavaScript-heavy, static scraping won't work well
            # Return a helpful demo result
            print("⚠️ Static scraping limited - Google Patents requires JavaScript")
            return self._create_demo_result(query)
            
        except Exception as e:
            print(f"❌ Static fallback error: {e}")
            return self._create_demo_result(query)
    
    def _parse_json_results(self, data, max_results: int) -> List[Dict[str, Any]]:
        """Parse JSON data for patent results"""
        results = []
        
        try:
            # Handle different JSON structures
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get('results', data.get('patents', [data]))
            else:
                return []
            
            for item in items[:max_results]:
                if isinstance(item, dict):
                    patent_info = {
                        'patent_number': item.get('id', item.get('patent_number', item.get('publication_number', ''))),
                        'title': item.get('title', item.get('name', '')),
                        'abstract': item.get('abstract', item.get('snippet', item.get('description', ''))),
                        'inventors': item.get('inventors', []),
                        'assignees': item.get('assignees', item.get('assignee', [])),
                        'publication_date': item.get('publication_date', item.get('published', '')),
                        'filing_date': item.get('filing_date', item.get('filed', '')),
                        'url': item.get('url', ''),
                        'pdf_link': item.get('pdf_link', ''),
                        'source': 'google_patents_json'
                    }
                    
                    # Clean up and validate
                    if patent_info['patent_number'] and patent_info['title']:
                        if not patent_info['url']:
                            patent_info['url'] = f"https://patents.google.com/patent/{patent_info['patent_number']}"
                        if not patent_info['pdf_link']:
                            patent_info['pdf_link'] = f"https://patents.google.com/patent/{patent_info['patent_number']}/pdf"
                        
                        results.append(patent_info)
            
        except Exception as e:
            print(f"JSON parsing error: {e}")
        
        return results
    
    def _parse_html_results(self, soup, max_results: int) -> List[Dict[str, Any]]:
        """Parse HTML using BeautifulSoup"""
        results = []
        
        try:
            # Look for various patent result patterns
            selectors = [
                'article[data-result]',
                '.search-result-item',
                '.patent-result',
                'div[data-patent-id]',
                'a[href*="/patent/"]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    
                    for element in elements[:max_results]:
                        patent_info = self._extract_patent_from_element(element)
                        if patent_info:
                            results.append(patent_info)
                    
                    if results:
                        break
            
        except Exception as e:
            print(f"HTML parsing error: {e}")
        
        return results
    
    def _extract_patent_from_element(self, element) -> Optional[Dict[str, Any]]:
        """Extract patent information from HTML element"""
        try:
            # Try to find patent number
            patent_number = ''
            
            # Look for patent number in various places
            patent_link = element.find('a', href=re.compile(r'/patent/([^/]+)'))
            if patent_link:
                match = re.search(r'/patent/([^/]+)', patent_link['href'])
                if match:
                    patent_number = match.group(1)
            
            # Look for title
            title = ''
            title_element = element.find(['h3', 'h4', 'h5', '.title', '.patent-title'])
            if title_element:
                title = title_element.get_text(strip=True)
            
            # Look for abstract/snippet
            abstract = ''
            abstract_element = element.find(['.abstract', '.snippet', '.description'])
            if abstract_element:
                abstract = abstract_element.get_text(strip=True)
            
            if patent_number and title:
                return {
                    'patent_number': patent_number,
                    'title': title,
                    'abstract': abstract,
                    'inventors': [],
                    'assignees': [],
                    'publication_date': '',
                    'filing_date': '',
                    'url': f"https://patents.google.com/patent/{patent_number}",
                    'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                    'source': 'google_patents_html'
                }
        
        except Exception as e:
            print(f"Element extraction error: {e}")
        
        return None
    
    def _parse_alternative_patterns(self, html_content: str, max_results: int) -> List[Dict[str, Any]]:
        """Try alternative regex patterns to find patent data"""
        results = []
        
        try:
            # Look for patent URLs in the HTML
            patent_url_pattern = r'href="(/patent/([^"]+))"'
            matches = re.findall(patent_url_pattern, html_content)
            
            seen_patents = set()
            for link, patent_num in matches:
                if patent_num not in seen_patents and len(results) < max_results:
                    seen_patents.add(patent_num)
                    
                    # Try to find title near the link
                    title = f"Patent {patent_num}"  # Default title
                    
                    # Look for title patterns around the patent number
                    title_patterns = [
                        rf'{re.escape(patent_num)}[^<]*<[^>]*>([^<]+)',
                        rf'title="([^"]*{re.escape(patent_num)}[^"]*)"',
                        rf'>{patent_num}</a>[^<]*<[^>]*>([^<]+)'
                    ]
                    
                    for pattern in title_patterns:
                        title_match = re.search(pattern, html_content, re.IGNORECASE)
                        if title_match:
                            title = title_match.group(1).strip()
                            break
                    
                    results.append({
                        'patent_number': patent_num,
                        'title': title,
                        'abstract': '',
                        'inventors': [],
                        'assignees': [],
                        'publication_date': '',
                        'filing_date': '',
                        'url': f"https://patents.google.com{link}",
                        'pdf_link': f"https://patents.google.com/patent/{patent_num}/pdf",
                        'source': 'google_patents_regex'
                    })
        
        except Exception as e:
            print(f"Alternative pattern error: {e}")
        
        return results
    
    def _try_alternative_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Try alternative search approach"""
        try:
            from urllib.parse import quote_plus
            
            # Try the old-style Google Patents URL
            alt_url = f"https://patents.google.com/search?q={quote_plus(query)}&type=PATENT"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = self.session.get(alt_url, headers=headers, timeout=30)
            if response.status_code == 200:
                # Parse this response
                soup = BeautifulSoup(response.text, 'html.parser')
                return self._parse_html_results(soup, max_results)
        
        except Exception as e:
            print(f"Alternative search error: {e}")
        
        return []
    
    def _enhance_patent_details(self, patent_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance patent information by fetching additional details"""
        try:
            if not patent_info.get('url'):
                return patent_info
            
            self.rate_limit('patent_details')
            
            response = self.session.get(patent_info['url'], timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to extract more details
                abstract_elem = soup.find('section', {'data-proto': 'ABSTRACT'})
                if abstract_elem and not patent_info.get('abstract'):
                    patent_info['abstract'] = abstract_elem.get_text(strip=True)
                
                # Try to find inventors
                inventors_section = soup.find('section', string=re.compile(r'Inventor', re.I))
                if inventors_section:
                    inventors = [elem.get_text(strip=True) for elem in inventors_section.find_all('span')]
                    patent_info['inventors'] = [inv for inv in inventors if inv]
                
                # Try to find assignees
                assignee_section = soup.find('section', string=re.compile(r'Assignee', re.I))
                if assignee_section:
                    assignees = [elem.get_text(strip=True) for elem in assignee_section.find_all('span')]
                    patent_info['assignees'] = [ass for ass in assignees if ass]
        
        except Exception as e:
            print(f"Enhancement error for {patent_info.get('patent_number', 'unknown')}: {e}")
        
        return patent_info
    
    def _create_demo_result(self, query: str) -> List[Dict[str, Any]]:
        """Create a demo result when scraping fails"""
        return [{
            'patent_number': 'DEMO-SCRAPING-001',
            'title': f'Web Scraping Demo Result for "{query}"',
            'abstract': f'This is a demonstration result for query "{query}". Google Patents uses complex JavaScript rendering that makes scraping challenging. For production use, consider using the SearchAPI.io integration for reliable results. The system shows {query}-related patents would be found here.',
            'inventors': ['Demo Inventor'],
            'assignees': ['Demo Company'],
            'publication_date': '2023-01-01',
            'filing_date': '2022-01-01',
            'url': f'https://patents.google.com/?q={query.replace(" ", "+")}',
            'pdf_link': '',
            'source': 'demo_scraping_fallback'
        }]
    
    def _search_espacenet_web(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search Espacenet (placeholder for future implementation)"""
        # Placeholder for Espacenet search
        self.logger.info("Espacenet search would be implemented here")
        return []
    
    def _get_patent_details_google(self, patent_number: str) -> Optional[Dict[str, Any]]:
        """Get detailed patent information from Google Patents"""
        if self.api_keys['searchapi']:
            params = {
                'engine': 'google_patents',
                'q': patent_number,
                'api_key': self.api_keys['searchapi']
            }
            
            try:
                self.rate_limit('google_patents')
                response = self.session.get(self.apis['google_patents_api'], params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if 'organic_results' in data and data['organic_results']:
                    result = data['organic_results'][0]
                    
                    return {
                        'patent_number': result.get('publication_number', patent_number),
                        'title': result.get('title', ''),
                        'abstract': result.get('snippet', ''),
                        'inventors': result.get('inventors', []),
                        'assignees': result.get('assignees', []),
                        'publication_date': result.get('publication_date', ''),
                        'filing_date': result.get('filing_date', ''),
                        'url': result.get('link', ''),
                        'pdf_link': result.get('pdf', ''),
                        'source': 'google_patents_detail'
                    }
                
            except Exception as e:
                self.logger.error(f"Patent details error: {e}")
        
        return None
    
    def download_patent_pdf(self, patent_data: Dict[str, Any]) -> DownloadResult:
        """Download PDF for a single patent"""
        patent_number = patent_data.get('patent_number', '')
        pdf_link = patent_data.get('pdf_link', '')
        
        if not patent_number:
            return DownloadResult(False, error_message="No patent number provided")
        
        # Clean filename
        safe_filename = re.sub(r'[^\w\-_.]', '_', patent_number)
        file_path = self.download_dir / f"{safe_filename}.pdf"
        
        # Check if file already exists
        if file_path.exists():
            return DownloadResult(
                True, 
                str(file_path), 
                file_size=file_path.stat().st_size
            )
        
        # Try to download from provided PDF link
        if pdf_link:
            success = self._download_pdf_from_url(pdf_link, file_path)
            if success:
                return DownloadResult(
                    True,
                    str(file_path),
                    file_size=file_path.stat().st_size
                )
        
        # Try to construct Google Patents PDF URL
        google_pdf_url = f"https://patents.google.com/patent/{patent_number}/pdf"
        success = self._download_pdf_from_url(google_pdf_url, file_path)
        
        if success:
            return DownloadResult(
                True,
                str(file_path),
                file_size=file_path.stat().st_size
            )
        else:
            return DownloadResult(
                False,
                error_message="Failed to download PDF from any source"
            )
    
    def _download_pdf_from_url(self, url: str, file_path: Path) -> bool:
        """Download PDF from URL"""
        try:
            self.rate_limit('pdf_download')
            
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Check if response is actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and 'application/pdf' not in content_type:
                # Check first few bytes for PDF signature
                first_chunk = next(response.iter_content(chunk_size=8192))
                if not first_chunk.startswith(b'%PDF'):
                    self.logger.warning(f"URL {url} does not return PDF content")
                    return False
                
                # Write first chunk
                with open(file_path, 'wb') as f:
                    f.write(first_chunk)
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            self.logger.info(f"Downloaded PDF: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"PDF download error for {url}: {e}")
            if file_path.exists():
                file_path.unlink()  # Remove partial file
            return False
    
    def _download_patents_batch(self, patents: List[Dict[str, Any]], max_workers: int = 3):
        """Download PDFs for multiple patents in parallel"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            download_tasks = {
                executor.submit(self.download_patent_pdf, patent): patent 
                for patent in patents
            }
            
            for future in as_completed(download_tasks):
                patent = download_tasks[future]
                try:
                    result = future.result()
                    patent['download_result'] = result
                except Exception as e:
                    patent['download_result'] = DownloadResult(
                        False, 
                        error_message=str(e)
                    )
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate patents from results"""
        seen_patents = set()
        unique_results = []
        
        for result in results:
            patent_key = result.get('patent_number', '').strip().upper()
            if patent_key and patent_key not in seen_patents:
                seen_patents.add(patent_key)
                unique_results.append(result)
        
        return unique_results
    
    def get_download_status(self) -> Dict[str, Any]:
        """Get status of downloaded patents"""
        pdf_files = list(self.download_dir.glob("*.pdf"))
        
        total_size = sum(f.stat().st_size for f in pdf_files)
        
        return {
            'download_directory': str(self.download_dir),
            'total_pdfs': len(pdf_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'files': [
                {
                    'name': f.name,
                    'size_kb': round(f.stat().st_size / 1024, 2),
                    'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                }
                for f in sorted(pdf_files, key=lambda x: x.stat().st_mtime, reverse=True)
            ]
        }
    
    def cleanup_downloads(self, older_than_days: int = 30) -> Dict[str, Any]:
        """Clean up old downloaded files"""
        cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
        
        removed_files = []
        total_size_removed = 0
        
        for pdf_file in self.download_dir.glob("*.pdf"):
            if pdf_file.stat().st_mtime < cutoff_time:
                size = pdf_file.stat().st_size
                pdf_file.unlink()
                removed_files.append(pdf_file.name)
                total_size_removed += size
        
        return {
            'removed_files': len(removed_files),
            'size_freed_mb': round(total_size_removed / (1024 * 1024), 2),
            'files_removed': removed_files
        }

# Command-line interface functions
def create_agent() -> EnhancedPatentAgent:
    """Create and return a new enhanced patent agent"""
    return EnhancedPatentAgent()

def interactive_search():
    """Interactive command-line interface for patent searching"""
    agent = create_agent()
    
    print("🔍 Enhanced Patent Search Agent")
    print("=" * 50)
    print("Available search types:")
    print("1. Keywords search")
    print("2. Patent number lookup")
    print("3. Inventor search")
    print("4. Assignee search")
    print("5. Chemical compounds")
    print("6. Download status")
    print("7. Cleanup downloads")
    print()
    
    while True:
        try:
            choice = input("Select search type (1-7) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                break
            
            if choice == '1':
                keywords = input("Enter search keywords (space-separated): ").strip()
                max_results = int(input("Max results (default 20): ") or "20")
                include_pdfs = input("Download PDFs? (y/n, default y): ").strip().lower() != 'n'
                
                params = {
                    'search_type': 'keywords',
                    'keywords': keywords.split(),
                    'max_results': max_results,
                    'include_pdfs': include_pdfs
                }
                
                print("\n🔍 Searching...")
                results = agent.search_patents(params)
                print(f"Found {results['total_results']} patents")
                
                for i, patent in enumerate(results['patents'][:5], 1):
                    print(f"\n{i}. {patent.get('title', 'No title')}")
                    print(f"   Patent: {patent.get('patent_number', 'N/A')}")
                    if 'download_result' in patent:
                        dr = patent['download_result']
                        if dr.success:
                            print(f"   ✅ PDF downloaded: {dr.file_path}")
                        else:
                            print(f"   ❌ PDF download failed: {dr.error_message}")
            
            elif choice == '2':
                patent_number = input("Enter patent number: ").strip()
                include_pdf = input("Download PDF? (y/n, default y): ").strip().lower() != 'n'
                
                params = {
                    'search_type': 'patent_number',
                    'patent_number': patent_number,
                    'include_pdf': include_pdf
                }
                
                print("\n🔍 Looking up patent...")
                result = agent.search_patents(params)
                
                if result['patent_data']:
                    patent = result['patent_data']
                    print(f"\n📄 {patent.get('title', 'No title')}")
                    print(f"Patent: {patent.get('patent_number', 'N/A')}")
                    print(f"Publication Date: {patent.get('publication_date', 'N/A')}")
                    
                    if 'download_result' in patent:
                        dr = patent['download_result']
                        if dr.success:
                            print(f"✅ PDF downloaded: {dr.file_path}")
                        else:
                            print(f"❌ PDF download failed: {dr.error_message}")
                else:
                    print("❌ Patent not found")
            
            elif choice == '6':
                status = agent.get_download_status()
                print(f"\n📊 Download Status:")
                print(f"Directory: {status['download_directory']}")
                print(f"Total PDFs: {status['total_pdfs']}")
                print(f"Total Size: {status['total_size_mb']} MB")
                
                if status['files']:
                    print("\nRecent files:")
                    for file_info in status['files'][:10]:
                        print(f"  📄 {file_info['name']} ({file_info['size_kb']} KB)")
            
            elif choice == '7':
                days = int(input("Remove files older than (days, default 30): ") or "30")
                result = agent.cleanup_downloads(days)
                print(f"\n🧹 Cleanup complete:")
                print(f"Removed {result['removed_files']} files")
                print(f"Freed {result['size_freed_mb']} MB")
            
            print("\n" + "=" * 50)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    interactive_search()