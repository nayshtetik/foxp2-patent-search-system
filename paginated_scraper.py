#!/usr/bin/env python3
"""
Paginated scraper to get all 3,665+ FOXP2 results from Google Patents
"""

import time
import re
from typing import List, Dict, Any
from urllib.parse import quote_plus

def scrape_all_google_patents(query: str, max_pages: int = 10) -> List[Dict[str, Any]]:
    """Scrape multiple pages to get more comprehensive results"""
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.action_chains import ActionChains
        
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
        
        try:
            search_url = f"https://patents.google.com/?q={quote_plus(query)}"
            print(f"🌐 Loading initial search: {search_url}")
            
            driver.get(search_url)
            time.sleep(8)
            
            # Wait for initial results
            try:
                WebDriverWait(driver, 20).until(
                    lambda d: d.find_elements(By.TAG_NAME, 'search-result-item')
                )
                print("✅ Initial search results loaded")
            except:
                print("⚠️ Timeout waiting for initial results")
            
            # First, check if there's a result count displayed
            try:
                # Look for result count indicators
                result_count_selectors = [
                    'result-nav',
                    '.search-header',
                    '[data-result-count]',
                    'span:contains("results")',
                    'div:contains("About")'
                ]
                
                total_results_text = ""
                for selector in result_count_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            for elem in elements:
                                text = elem.text
                                if 'result' in text.lower() or 'about' in text.lower():
                                    total_results_text = text
                                    break
                        if total_results_text:
                            break
                    except:
                        continue
                
                if total_results_text:
                    print(f"📊 Found results info: {total_results_text}")
                    # Extract number from text like "About 3,665 results"
                    numbers = re.findall(r'[\d,]+', total_results_text)
                    if numbers:
                        total_count = int(numbers[-1].replace(',', ''))
                        print(f"🎯 Total results available: {total_count:,}")
                
            except Exception as e:
                print(f"⚠️ Could not get total count: {e}")
            
            page_num = 1
            seen_patents = set()
            
            while page_num <= max_pages:
                print(f"\n📄 Processing page {page_num}...")
                
                # Extract results from current page
                search_items = driver.find_elements(By.TAG_NAME, 'search-result-item')
                print(f"📊 Found {len(search_items)} items on page {page_num}")
                
                page_results = 0
                for i, item in enumerate(search_items):
                    try:
                        text_content = item.text
                        
                        # Extract patent number
                        patent_patterns = [
                            r'\b([A-Z]{2}\d{7,10}[A-Z]?\d?)\b',
                            r'\b(US\d{7,10}[A-Z]\d?)\b',
                            r'\b(EP\d{7,10}[A-Z]\d?)\b',
                            r'\b(WO\d{4}/\d{6})\b'
                        ]
                        
                        patent_number = ''
                        for pattern in patent_patterns:
                            match = re.search(pattern, text_content)
                            if match:
                                patent_number = match.group(1)
                                break
                        
                        if patent_number and patent_number not in seen_patents:
                            seen_patents.add(patent_number)
                            
                            # Extract title
                            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                            title = ''
                            for line in lines:
                                if len(line) > 20 and line != patent_number and not line.isdigit():
                                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', line):
                                        title = line
                                        break
                            
                            if not title:
                                title = f"Patent {patent_number}"
                            
                            all_results.append({
                                'patent_number': patent_number,
                                'title': title[:200],
                                'abstract': '',
                                'inventors': [],
                                'assignees': [],
                                'publication_date': '',
                                'filing_date': '',
                                'url': f"https://patents.google.com/patent/{patent_number}",
                                'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                                'source': f'selenium_page_{page_num}',
                                'page': page_num
                            })
                            page_results += 1
                    
                    except Exception as e:
                        continue
                
                print(f"✅ Extracted {page_results} new patents from page {page_num}")
                print(f"📊 Total unique patents so far: {len(all_results)}")
                
                # Try to go to next page
                if page_num < max_pages:
                    print(f"🔄 Attempting to navigate to page {page_num + 1}...")
                    
                    # Look for next page button or pagination
                    next_found = False
                    
                    # Strategy 1: Look for "Next" button
                    try:
                        next_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')] | //a[contains(text(), 'Next')] | //*[@aria-label='Next page']")
                        for button in next_buttons:
                            if button.is_enabled() and button.is_displayed():
                                print("   🖱️ Found Next button, clicking...")
                                driver.execute_script("arguments[0].click();", button)
                                time.sleep(5)
                                next_found = True
                                break
                    except:
                        pass
                    
                    # Strategy 2: Look for pagination numbers
                    if not next_found:
                        try:
                            page_links = driver.find_elements(By.XPATH, f"//a[text()='{page_num + 1}'] | //button[text()='{page_num + 1}']")
                            for link in page_links:
                                if link.is_enabled() and link.is_displayed():
                                    print(f"   🖱️ Found page {page_num + 1} link, clicking...")
                                    driver.execute_script("arguments[0].click();", link)
                                    time.sleep(5)
                                    next_found = True
                                    break
                        except:
                            pass
                    
                    # Strategy 3: Scroll to load more results (infinite scroll)
                    if not next_found:
                        print("   📜 Trying scroll to load more results...")
                        last_height = driver.execute_script("return document.body.scrollHeight")
                        
                        # Scroll down
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(3)
                        
                        # Check if new content loaded
                        new_height = driver.execute_script("return document.body.scrollHeight")
                        if new_height > last_height:
                            print("   ✅ New content loaded via scrolling")
                            time.sleep(2)
                            next_found = True
                        else:
                            print("   ⚠️ No new content loaded")
                    
                    # Strategy 4: Try URL-based pagination
                    if not next_found:
                        try:
                            current_url = driver.current_url
                            if 'start=' in current_url:
                                # Update start parameter
                                start_value = page_num * 10  # Assuming 10 results per page
                                new_url = re.sub(r'start=\d+', f'start={start_value}', current_url)
                            else:
                                # Add start parameter
                                start_value = page_num * 10
                                separator = '&' if '?' in current_url else '?'
                                new_url = f"{current_url}{separator}start={start_value}"
                            
                            print(f"   🌐 Trying URL pagination: ...start={start_value}")
                            driver.get(new_url)
                            time.sleep(5)
                            next_found = True
                        except:
                            pass
                    
                    if not next_found:
                        print(f"   ⚠️ Could not find way to page {page_num + 1}, stopping pagination")
                        break
                
                page_num += 1
            
            print(f"\n🎯 Final Results Summary:")
            print(f"📊 Total unique patents extracted: {len(all_results)}")
            print(f"📄 Pages processed: {page_num - 1}")
            
            return all_results
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Paginated scraping error: {e}")
        return []

def test_paginated_scraper():
    """Test the paginated scraper"""
    print("🧪 Testing paginated scraper for comprehensive Google Patents results")
    print("=" * 70)
    
    query = "FOXP2"
    results = scrape_all_google_patents(query, max_pages=5)  # Try 5 pages
    
    print(f"\n📊 Comprehensive Results for '{query}':")
    print(f"Found {len(results)} total patents")
    
    if results:
        print(f"\n📄 Sample results:")
        for i, patent in enumerate(results[:10], 1):  # Show first 10
            print(f"{i:2d}. {patent['title'][:60]}...")
            print(f"     Patent: {patent['patent_number']} (Page {patent['page']})")
        
        if len(results) > 10:
            print(f"     ... and {len(results) - 10} more patents")
        
        # Show breakdown by page
        page_counts = {}
        for patent in results:
            page = patent.get('page', 1)
            page_counts[page] = page_counts.get(page, 0) + 1
        
        print(f"\n📊 Results by page:")
        for page in sorted(page_counts.keys()):
            print(f"   Page {page}: {page_counts[page]} patents")

if __name__ == "__main__":
    test_paginated_scraper()