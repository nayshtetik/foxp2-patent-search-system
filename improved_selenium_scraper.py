#!/usr/bin/env python3
"""
Improved Selenium scraper for Google Patents with better result extraction
"""

import time
import re
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

def scrape_google_patents_improved(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Improved Selenium scraper for Google Patents"""
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        search_url = f"https://patents.google.com/?q={quote_plus(query)}"
        print(f"🌐 Loading: {search_url}")
        
        driver.get(search_url)
        
        # Wait for the page to load
        print("⏳ Waiting for page to load...")
        time.sleep(5)  # Increased wait time
        
        # Wait for search results or try to detect when loading is complete
        try:
            # Wait for various possible result containers
            WebDriverWait(driver, 15).until(
                lambda d: (
                    d.find_elements(By.TAG_NAME, 'search-result-item') or
                    d.find_elements(By.CSS_SELECTOR, '[data-result]') or
                    d.find_elements(By.XPATH, "//div[contains(@class, 'result')]") or
                    len(d.find_elements(By.XPATH, "//a[contains(@href, '/patent/')]")) > 0
                )
            )
            print("✅ Search results loaded")
        except:
            print("⚠️ Timeout waiting for results, continuing anyway...")
        
        # Additional wait to ensure all content is rendered
        time.sleep(2)
        
        results = []
        
        # Strategy 1: Look for search-result-item elements
        search_items = driver.find_elements(By.TAG_NAME, 'search-result-item')
        print(f"📊 Found {len(search_items)} search-result-item elements")
        
        for i, item in enumerate(search_items[:max_results]):
            try:
                # Try to extract data using Selenium methods
                patent_info = extract_from_selenium_element(item, driver)
                if patent_info:
                    results.append(patent_info)
                    print(f"✅ Extracted patent {i+1}: {patent_info['patent_number']}")
            except Exception as e:
                print(f"⚠️ Error extracting from item {i}: {e}")
                continue
        
        # Strategy 2: Parse the full HTML if we didn't get results
        if not results:
            print("🔄 Fallback to HTML parsing...")
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            results = parse_html_for_patents(soup, max_results)
        
        # Strategy 3: Direct JavaScript execution to get data
        if not results:
            print("🔄 Trying JavaScript data extraction...")
            results = extract_via_javascript(driver, max_results)
        
        print(f"🎯 Total results found: {len(results)}")
        return results
        
    except Exception as e:
        print(f"❌ Selenium error: {e}")
        return []
    
    finally:
        try:
            driver.quit()
        except:
            pass

def extract_from_selenium_element(element, driver) -> Optional[Dict[str, Any]]:
    """Extract patent data from a Selenium WebElement"""
    try:
        # Get the HTML content of this element
        html_content = element.get_attribute('innerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try to find patent number
        patent_number = ''
        
        # Look for links with /patent/ in href
        patent_links = soup.find_all('a', href=re.compile(r'/patent/'))
        if patent_links:
            href = patent_links[0].get('href', '')
            match = re.search(r'/patent/([^/?]+)', href)
            if match:
                patent_number = match.group(1)
        
        # Try to find patent number in text
        if not patent_number:
            text_content = element.text
            patent_match = re.search(r'\b([A-Z]{2}\d{7,10}[A-Z]?\d?)\b', text_content)
            if patent_match:
                patent_number = patent_match.group(1)
        
        # Look for title
        title = ''
        
        # Try to find clickable patent title
        try:
            title_elements = element.find_elements(By.XPATH, ".//a[contains(@href, '/patent/')]")
            if title_elements:
                title = title_elements[0].text.strip()
        except:
            pass
        
        # Fallback to finding any substantial text
        if not title:
            try:
                text_elements = element.find_elements(By.XPATH, ".//*[string-length(text()) > 20]")
                for elem in text_elements:
                    text = elem.text.strip()
                    if text and len(text) > 20 and not text.startswith('http'):
                        title = text
                        break
            except:
                pass
        
        # Look for abstract/description
        abstract = ''
        try:
            # Look for elements that might contain abstracts
            desc_elements = element.find_elements(By.XPATH, ".//*[string-length(text()) > 50]")
            for elem in desc_elements:
                text = elem.text.strip()
                if text and len(text) > 50 and text != title:
                    abstract = text
                    break
        except:
            pass
        
        if patent_number and title:
            return {
                'patent_number': patent_number,
                'title': title[:200],
                'abstract': abstract[:500] if abstract else '',
                'inventors': [],
                'assignees': [],
                'publication_date': '',
                'filing_date': '',
                'url': f"https://patents.google.com/patent/{patent_number}",
                'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                'source': 'selenium_improved'
            }
    
    except Exception as e:
        print(f"Element extraction error: {e}")
    
    return None

def parse_html_for_patents(soup, max_results: int) -> List[Dict[str, Any]]:
    """Parse HTML content for patent results"""
    results = []
    
    try:
        # Look for search result items
        result_elements = soup.find_all('search-result-item')
        print(f"📊 Found {len(result_elements)} search-result-item in HTML")
        
        for element in result_elements[:max_results]:
            # Extract patent information
            patent_info = extract_patent_from_html_element(element)
            if patent_info:
                results.append(patent_info)
        
        # If no search-result-item elements, look for patent links
        if not results:
            patent_links = soup.find_all('a', href=re.compile(r'/patent/'))
            print(f"📊 Found {len(patent_links)} patent links in HTML")
            
            seen_patents = set()
            for link in patent_links[:max_results]:
                href = link.get('href', '')
                match = re.search(r'/patent/([^/?]+)', href)
                if match:
                    patent_number = match.group(1)
                    if patent_number not in seen_patents:
                        seen_patents.add(patent_number)
                        
                        title = link.get_text(strip=True)
                        if not title or len(title) < 5:
                            # Look in parent elements for title
                            parent = link.parent
                            while parent and not title:
                                title = parent.get_text(strip=True)
                                if len(title) > 100:  # Too long, probably not just title
                                    title = title[:100] + "..."
                                    break
                                parent = parent.parent
                        
                        if not title:
                            title = f"Patent {patent_number}"
                        
                        results.append({
                            'patent_number': patent_number,
                            'title': title,
                            'abstract': '',
                            'inventors': [],
                            'assignees': [],
                            'publication_date': '',
                            'filing_date': '',
                            'url': f"https://patents.google.com{href}",
                            'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                            'source': 'html_parsing'
                        })
    
    except Exception as e:
        print(f"HTML parsing error: {e}")
    
    return results

def extract_patent_from_html_element(element) -> Optional[Dict[str, Any]]:
    """Extract patent info from BeautifulSoup element"""
    try:
        # Find patent links
        patent_links = element.find_all('a', href=re.compile(r'/patent/'))
        if not patent_links:
            return None
        
        href = patent_links[0].get('href', '')
        match = re.search(r'/patent/([^/?]+)', href)
        if not match:
            return None
        
        patent_number = match.group(1)
        
        # Get title from link text or nearby text
        title = patent_links[0].get_text(strip=True)
        if not title or len(title) < 5:
            # Look for title in the element content
            all_text = element.get_text(strip=True)
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            for line in lines:
                if len(line) > 10 and line != patent_number:
                    title = line
                    break
        
        if not title:
            title = f"Patent {patent_number}"
        
        # Look for abstract or description
        abstract = ''
        all_text = element.get_text(strip=True)
        if len(all_text) > len(title) + 50:
            # Try to extract description part
            abstract = all_text[len(title):].strip()
            if len(abstract) > 300:
                abstract = abstract[:300] + "..."
        
        return {
            'patent_number': patent_number,
            'title': title,
            'abstract': abstract,
            'inventors': [],
            'assignees': [],
            'publication_date': '',
            'filing_date': '',
            'url': f"https://patents.google.com{href}",
            'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
            'source': 'html_element'
        }
    
    except Exception as e:
        print(f"HTML element extraction error: {e}")
        return None

def extract_via_javascript(driver, max_results: int) -> List[Dict[str, Any]]:
    """Try to extract data via JavaScript execution"""
    try:
        from selenium.webdriver.common.by import By
        
        # Try to execute JavaScript to get search result data
        js_code = """
        // Try to find search results in various ways
        var results = [];
        
        // Method 1: Look for search-result-item elements
        var searchItems = document.getElementsByTagName('search-result-item');
        for (var i = 0; i < searchItems.length && i < arguments[0]; i++) {
            var item = searchItems[i];
            var links = item.querySelectorAll('a[href*="/patent/"]');
            if (links.length > 0) {
                var href = links[0].href;
                var match = href.match(/\/patent\/([^\/\?]+)/);
                if (match) {
                    results.push({
                        patent_number: match[1],
                        title: links[0].textContent.trim() || item.textContent.trim().substring(0, 100),
                        url: href,
                        source: 'javascript'
                    });
                }
            }
        }
        
        // Method 2: Look for any patent links if no search items found
        if (results.length === 0) {
            var patentLinks = document.querySelectorAll('a[href*="/patent/"]');
            var seen = {};
            for (var i = 0; i < patentLinks.length && results.length < arguments[0]; i++) {
                var link = patentLinks[i];
                var href = link.href;
                var match = href.match(/\/patent\/([^\/\?]+)/);
                if (match && !seen[match[1]]) {
                    seen[match[1]] = true;
                    results.push({
                        patent_number: match[1],
                        title: link.textContent.trim() || 'Patent ' + match[1],
                        url: href,
                        source: 'javascript_links'
                    });
                }
            }
        }
        
        return results;
        """
        
        js_results = driver.execute_script(js_code, max_results)
        
        results = []
        for js_result in js_results:
            results.append({
                'patent_number': js_result.get('patent_number', ''),
                'title': js_result.get('title', ''),
                'abstract': '',
                'inventors': [],
                'assignees': [],
                'publication_date': '',
                'filing_date': '',
                'url': js_result.get('url', ''),
                'pdf_link': f"https://patents.google.com/patent/{js_result.get('patent_number', '')}/pdf",
                'source': js_result.get('source', 'javascript')
            })
        
        print(f"📊 JavaScript extraction found {len(results)} results")
        return results
        
    except Exception as e:
        print(f"JavaScript extraction error: {e}")
        return []

def test_improved_scraper():
    """Test the improved scraper"""
    print("🧪 Testing improved Selenium scraper for Google Patents")
    print("=" * 60)
    
    query = "FOXP2"
    results = scrape_google_patents_improved(query, max_results=5)
    
    print(f"\n📊 Results for '{query}':")
    print(f"Found {len(results)} patents")
    
    for i, patent in enumerate(results, 1):
        print(f"\n{i}. {patent['title'][:80]}...")
        print(f"   Patent: {patent['patent_number']}")
        print(f"   URL: {patent['url']}")
        print(f"   Source: {patent['source']}")
        if patent['abstract']:
            print(f"   Abstract: {patent['abstract'][:100]}...")

if __name__ == "__main__":
    test_improved_scraper()