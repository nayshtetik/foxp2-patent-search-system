#!/usr/bin/env python3
"""
Selenium-based scraper for Google Patents that handles JavaScript rendering
"""

import time
import re
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

def setup_selenium_driver():
    """Setup Selenium WebDriver with Chrome"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        # Try to create driver (will fail if Chrome/ChromeDriver not installed)
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ Failed to setup Chrome WebDriver: {e}")
        print("💡 Please install Chrome and ChromeDriver:")
        print("   brew install --cask google-chrome")
        print("   brew install chromedriver")
        return None

def scrape_google_patents_selenium(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Scrape Google Patents using Selenium for JavaScript rendering"""
    
    driver = setup_selenium_driver()
    if not driver:
        return []
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        search_url = f"https://patents.google.com/?q={quote_plus(query)}"
        print(f"🌐 Loading: {search_url}")
        
        # Load the page
        driver.get(search_url)
        
        # Wait for the page to load and render
        print("⏳ Waiting for page to load...")
        time.sleep(3)
        
        # Wait for search results to appear
        try:
            # Wait for either search results or "no results" message
            WebDriverWait(driver, 10).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, 'search-result-item, .no-results, patent-result') or
                         len(d.find_elements(By.XPATH, "//a[contains(@href, '/patent/')]")) > 0
            )
        except:
            print("⚠️ Timeout waiting for search results")
        
        # Get the page source after JavaScript execution
        html_content = driver.page_source
        print(f"📄 Rendered HTML size: {len(html_content)} characters")
        
        # Save rendered HTML for debugging
        with open('patent_data/selenium_rendered.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("💾 Saved rendered HTML to patent_data/selenium_rendered.html")
        
        # Parse the rendered HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Strategy 1: Look for patent result elements
        result_selectors = [
            'search-result-item',
            'patent-result', 
            '.search-result',
            '[data-result]',
            'state-modifier'
        ]
        
        for selector in result_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ Found {len(elements)} elements with selector: {selector}")
                for element in elements[:max_results]:
                    patent_info = extract_patent_from_selenium_element(element)
                    if patent_info:
                        results.append(patent_info)
                break
        
        # Strategy 2: Look for patent links directly
        if not results:
            patent_links = soup.find_all('a', href=re.compile(r'/patent/'))
            print(f"📊 Found {len(patent_links)} patent links")
            
            seen_patents = set()
            for link in patent_links[:max_results]:
                href = link.get('href', '')
                patent_match = re.search(r'/patent/([^/?]+)', href)
                if patent_match:
                    patent_number = patent_match.group(1)
                    if patent_number not in seen_patents:
                        seen_patents.add(patent_number)
                        
                        # Get title from link text or nearby elements
                        title = link.get_text(strip=True)
                        if not title or len(title) < 10:
                            # Look for title in parent elements
                            parent = link.parent
                            if parent:
                                title = parent.get_text(strip=True)
                        
                        if not title:
                            title = f"Patent {patent_number}"
                        
                        patent_info = {
                            'patent_number': patent_number,
                            'title': title[:200],  # Limit title length
                            'abstract': '',
                            'inventors': [],
                            'assignees': [],
                            'publication_date': '',
                            'filing_date': '',
                            'url': f"https://patents.google.com{href}",
                            'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                            'source': 'selenium_scraping'
                        }
                        results.append(patent_info)
        
        # Strategy 3: Enhanced parsing with Selenium-specific methods
        if not results:
            print("🔍 Trying enhanced Selenium parsing...")
            results = parse_selenium_results_enhanced(driver, max_results)
        
        print(f"🎯 Total results found: {len(results)}")
        return results
        
    except Exception as e:
        print(f"❌ Selenium scraping error: {e}")
        return []
    
    finally:
        driver.quit()

def extract_patent_from_selenium_element(element) -> Optional[Dict[str, Any]]:
    """Extract patent information from a Selenium-rendered element"""
    try:
        # Look for patent number
        patent_number = ''
        
        # Try to find patent links
        patent_link = element.find('a', href=re.compile(r'/patent/([^/]+)'))
        if patent_link:
            href = patent_link.get('href', '')
            match = re.search(r'/patent/([^/]+)', href)
            if match:
                patent_number = match.group(1)
        
        # Look for title
        title = ''
        title_selectors = ['h3', 'h4', '.title', '.patent-title', 'a']
        for selector in title_selectors:
            title_elem = element.find(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                if title_text and len(title_text) > 5:
                    title = title_text
                    break
        
        # Look for abstract/description
        abstract = ''
        abstract_selectors = ['.abstract', '.description', '.snippet', 'p']
        for selector in abstract_selectors:
            abstract_elem = element.find(selector)
            if abstract_elem:
                abstract_text = abstract_elem.get_text(strip=True)
                if abstract_text and len(abstract_text) > 10:
                    abstract = abstract_text
                    break
        
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
                'source': 'selenium_element'
            }
    
    except Exception as e:
        print(f"Element extraction error: {e}")
    
    return None

def parse_selenium_results_enhanced(driver, max_results: int) -> List[Dict[str, Any]]:
    """Enhanced parsing using Selenium WebDriver methods"""
    try:
        from selenium.webdriver.common.by import By
        
        results = []
        
        # Try to find patent elements using various strategies
        xpath_selectors = [
            "//a[contains(@href, '/patent/')]",
            "//*[contains(@class, 'result')]",
            "//*[contains(@class, 'patent')]",
            "//*[contains(text(), 'US') and string-length(.) < 20]"  # Patent numbers
        ]
        
        for xpath in xpath_selectors:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                print(f"📊 XPath '{xpath}': {len(elements)} elements")
                
                if elements:
                    seen_patents = set()
                    for element in elements[:max_results * 2]:  # Get more to filter
                        try:
                            # Get element attributes
                            href = element.get_attribute('href')
                            text = element.text
                            
                            if href and '/patent/' in href:
                                patent_match = re.search(r'/patent/([^/?]+)', href)
                                if patent_match:
                                    patent_number = patent_match.group(1)
                                    if patent_number not in seen_patents and len(results) < max_results:
                                        seen_patents.add(patent_number)
                                        
                                        # Use element text as title, or get it from parent
                                        title = text.strip() if text else f"Patent {patent_number}"
                                        if len(title) < 10:
                                            try:
                                                parent_text = element.find_element(By.XPATH, "./..").text
                                                if parent_text and len(parent_text.strip()) > len(title):
                                                    title = parent_text.strip()
                                            except:
                                                pass
                                        
                                        results.append({
                                            'patent_number': patent_number,
                                            'title': title[:200],
                                            'abstract': '',
                                            'inventors': [],
                                            'assignees': [],
                                            'publication_date': '',
                                            'filing_date': '',
                                            'url': href,
                                            'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                                            'source': 'selenium_enhanced'
                                        })
                        except Exception as e:
                            continue
                    
                    if results:
                        break
            except Exception as e:
                print(f"XPath error: {e}")
                continue
        
        return results
        
    except Exception as e:
        print(f"Enhanced parsing error: {e}")
        return []

def test_selenium_scraper():
    """Test the Selenium scraper"""
    print("🧪 Testing Selenium scraper for Google Patents")
    print("=" * 50)
    
    query = "FOXP2"
    results = scrape_google_patents_selenium(query, max_results=5)
    
    print(f"\n📊 Results for '{query}':")
    print(f"Found {len(results)} patents")
    
    for i, patent in enumerate(results, 1):
        print(f"\n{i}. {patent['title'][:80]}...")
        print(f"   Patent: {patent['patent_number']}")
        print(f"   URL: {patent['url']}")
        print(f"   Source: {patent['source']}")

if __name__ == "__main__":
    test_selenium_scraper()