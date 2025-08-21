#!/usr/bin/env python3
"""
Final enhanced Selenium scraper for Google Patents with comprehensive extraction
"""

import time
import re
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

def scrape_google_patents_final(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Final comprehensive Selenium scraper for Google Patents"""
    
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
        
        # Wait longer for dynamic content to load
        print("⏳ Waiting for page to load...")
        time.sleep(8)
        
        # Wait for search results
        try:
            WebDriverWait(driver, 20).until(
                lambda d: d.find_elements(By.TAG_NAME, 'search-result-item')
            )
            print("✅ Search results detected")
        except:
            print("⚠️ No search-result-item found, continuing...")
        
        results = []
        
        # Debug: Let's see what we have
        search_items = driver.find_elements(By.TAG_NAME, 'search-result-item')
        print(f"📊 Found {len(search_items)} search-result-item elements")
        
        if search_items:
            for i, item in enumerate(search_items[:max_results]):
                print(f"\n🔍 Processing search item {i+1}...")
                
                # Get all the text content to debug
                text_content = item.text
                print(f"📄 Item text content: {text_content[:200]}...")
                
                # Get HTML content for parsing
                html_content = item.get_attribute('outerHTML')
                
                # Save sample HTML for debugging
                if i == 0:
                    with open('patent_data/search_item_sample.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print("💾 Saved sample search item HTML")
                
                # Try multiple extraction strategies
                patent_info = extract_comprehensive(item, text_content, html_content, driver)
                if patent_info:
                    results.append(patent_info)
                    print(f"✅ Extracted: {patent_info['patent_number']} - {patent_info['title'][:50]}...")
                else:
                    print(f"⚠️ Could not extract data from item {i+1}")
        
        # Alternative strategy: Try to click through to get more info
        if not results and search_items:
            print("🔄 Trying click-through strategy...")
            results = try_click_strategy(driver, search_items[:3])
        
        # Last resort: Extract from page source
        if not results:
            print("🔄 Last resort: page source analysis...")
            page_source = driver.page_source
            results = extract_from_page_source(page_source, query, max_results)
        
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

def extract_comprehensive(element, text_content: str, html_content: str, driver) -> Optional[Dict[str, Any]]:
    """Comprehensive extraction from search result element"""
    try:
        from selenium.webdriver.common.by import By
        
        # Strategy 1: Look for clickable elements that might be patent links
        clickable_elements = element.find_elements(By.XPATH, ".//*[@onclick or @href or @role='link']")
        print(f"   📊 Found {len(clickable_elements)} clickable elements")
        
        patent_number = ''
        title = ''
        url = ''
        
        # Strategy 2: Extract patent number from text using regex
        patent_patterns = [
            r'\b([A-Z]{2}\d{7,10}[A-Z]?\d?)\b',  # Standard patent format
            r'\b(US\d{7,10}[A-Z]\d?)\b',          # US patents
            r'\b(EP\d{7,10}[A-Z]\d?)\b',          # European patents
            r'\b(WO\d{4}/\d{6})\b'                # WIPO patents
        ]
        
        for pattern in patent_patterns:
            match = re.search(pattern, text_content)
            if match:
                patent_number = match.group(1)
                print(f"   ✅ Found patent number: {patent_number}")
                break
        
        # Strategy 3: Look for patent number in clickable elements
        if not patent_number:
            for elem in clickable_elements:
                try:
                    elem_text = elem.text
                    for pattern in patent_patterns:
                        match = re.search(pattern, elem_text)
                        if match:
                            patent_number = match.group(1)
                            title = elem_text.replace(patent_number, '').strip()
                            break
                    if patent_number:
                        break
                except:
                    continue
        
        # Strategy 4: Extract title from the text content
        if not title and text_content:
            # Split by lines and look for substantial text that could be title
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            for line in lines:
                if len(line) > 20 and line != patent_number and not line.isdigit():
                    # Skip lines that look like dates or short codes
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', line) and not re.match(r'^[A-Z]{1,5}\d+$', line):
                        title = line
                        break
        
        # Strategy 5: Try to get URL from href attributes in HTML
        href_matches = re.findall(r'href="([^"]*\/patent\/[^"]*)"', html_content)
        if href_matches:
            url = href_matches[0]
            if not url.startswith('http'):
                url = f"https://patents.google.com{url}"
            
            # Extract patent number from URL if we don't have it
            if not patent_number:
                url_match = re.search(r'/patent/([^/?]+)', url)
                if url_match:
                    patent_number = url_match.group(1)
        
        # Strategy 6: Use JavaScript to get additional data
        if patent_number and not title:
            try:
                js_code = f"""
                var items = document.getElementsByTagName('search-result-item');
                for (var i = 0; i < items.length; i++) {{
                    var item = items[i];
                    if (item.textContent.includes('{patent_number}')) {{
                        var links = item.querySelectorAll('a, span, div');
                        for (var j = 0; j < links.length; j++) {{
                            var text = links[j].textContent.trim();
                            if (text.length > 20 && !text.includes('{patent_number}')) {{
                                return text;
                            }}
                        }}
                    }}
                }}
                return '';
                """
                js_title = driver.execute_script(js_code)
                if js_title:
                    title = js_title[:200]  # Limit length
            except Exception as e:
                print(f"   ⚠️ JavaScript extraction failed: {e}")
        
        # Final validation and construction
        if patent_number:
            if not title:
                title = f"Patent {patent_number}"
            
            if not url:
                url = f"https://patents.google.com/patent/{patent_number}"
            
            return {
                'patent_number': patent_number,
                'title': title,
                'abstract': '',  # Will be filled later if needed
                'inventors': [],
                'assignees': [],
                'publication_date': '',
                'filing_date': '',
                'url': url,
                'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                'source': 'selenium_comprehensive'
            }
    
    except Exception as e:
        print(f"   ❌ Comprehensive extraction error: {e}")
    
    return None

def try_click_strategy(driver, search_items) -> List[Dict[str, Any]]:
    """Try clicking on search items to get more information"""
    results = []
    
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        
        original_window = driver.current_window_handle
        
        for i, item in enumerate(search_items):
            try:
                print(f"   🖱️ Trying to interact with item {i+1}...")
                
                # Try to find a clickable element
                clickable = None
                try:
                    clickable = item.find_element(By.XPATH, ".//a[@href]")
                except:
                    try:
                        clickable = item.find_element(By.XPATH, ".//*[@onclick]")
                    except:
                        try:
                            # Try clicking on the item itself
                            clickable = item
                        except:
                            continue
                
                if clickable:
                    # Get current URL before clicking
                    current_url = driver.current_url
                    
                    # Try to click
                    ActionChains(driver).move_to_element(clickable).click().perform()
                    time.sleep(2)
                    
                    # Check if we navigated to a patent page
                    new_url = driver.current_url
                    if new_url != current_url and '/patent/' in new_url:
                        print(f"   ✅ Navigated to patent page: {new_url}")
                        
                        # Extract patent info from the page
                        patent_match = re.search(r'/patent/([^/?]+)', new_url)
                        if patent_match:
                            patent_number = patent_match.group(1)
                            
                            # Try to get title from page
                            try:
                                title_element = driver.find_element(By.TAG_NAME, 'h1')
                                title = title_element.text.strip()
                            except:
                                title = f"Patent {patent_number}"
                            
                            results.append({
                                'patent_number': patent_number,
                                'title': title,
                                'abstract': '',
                                'inventors': [],
                                'assignees': [],
                                'publication_date': '',
                                'filing_date': '',
                                'url': new_url,
                                'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                                'source': 'click_strategy'
                            })
                        
                        # Go back to search results
                        driver.back()
                        time.sleep(2)
                
            except Exception as e:
                print(f"   ⚠️ Click strategy failed for item {i+1}: {e}")
                continue
    
    except Exception as e:
        print(f"Click strategy error: {e}")
    
    return results

def extract_from_page_source(page_source: str, query: str, max_results: int) -> List[Dict[str, Any]]:
    """Last resort: extract from full page source"""
    results = []
    
    try:
        # Look for patent numbers in the page source
        patent_pattern = r'\b([A-Z]{2}\d{7,10}[A-Z]?\d?)\b'
        patent_numbers = re.findall(patent_pattern, page_source)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_patents = []
        for patent in patent_numbers:
            if patent not in seen:
                seen.add(patent)
                unique_patents.append(patent)
        
        print(f"📊 Found {len(unique_patents)} unique patent numbers in page source")
        
        for patent_number in unique_patents[:max_results]:
            results.append({
                'patent_number': patent_number,
                'title': f'{query} related patent {patent_number}',
                'abstract': f'Patent found in search results for query: {query}',
                'inventors': [],
                'assignees': [],
                'publication_date': '',
                'filing_date': '',
                'url': f"https://patents.google.com/patent/{patent_number}",
                'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                'source': 'page_source_fallback'
            })
    
    except Exception as e:
        print(f"Page source extraction error: {e}")
    
    return results

def test_final_scraper():
    """Test the final scraper"""
    print("🧪 Testing final comprehensive Selenium scraper")
    print("=" * 60)
    
    query = "FOXP2"
    results = scrape_google_patents_final(query, max_results=5)
    
    print(f"\n📊 Final Results for '{query}':")
    print(f"Found {len(results)} patents")
    
    for i, patent in enumerate(results, 1):
        print(f"\n{i}. {patent['title']}")
        print(f"   Patent: {patent['patent_number']}")
        print(f"   URL: {patent['url']}")
        print(f"   Source: {patent['source']}")

if __name__ == "__main__":
    test_final_scraper()