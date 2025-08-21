#!/usr/bin/env python3
"""
Analyze Google Patents pagination to understand how to get all 3,665 results
"""

import time
import re
from urllib.parse import quote_plus

def analyze_google_patents_pagination(query: str):
    """Analyze how Google Patents implements pagination"""
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            search_url = f"https://patents.google.com/?q={quote_plus(query)}"
            print(f"🔍 Analyzing: {search_url}")
            
            driver.get(search_url)
            time.sleep(8)
            
            # Get page source for analysis
            page_source = driver.page_source
            
            print(f"\n📊 ANALYZING PAGINATION STRUCTURE:")
            print("=" * 50)
            
            # Look for pagination-related elements
            pagination_selectors = [
                'result-nav',
                '.pagination',
                '.paging',
                '.page-nav',
                '[data-page]',
                'button[aria-label*="page"]',
                'a[aria-label*="page"]',
                'button:contains("Next")',
                'a:contains("Next")'
            ]
            
            for selector in pagination_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        for i, elem in enumerate(elements[:3]):
                            print(f"   {i+1}. Text: {elem.text[:100]}")
                            print(f"      HTML: {elem.get_attribute('outerHTML')[:200]}...")
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
            
            # Look for result count information
            print(f"\n📈 RESULT COUNT ANALYSIS:")
            print("=" * 50)
            
            # Check various ways Google might show result counts
            count_patterns = [
                r'About ([\d,]+) result',
                r'([\d,]+) results found',
                r'Showing [\d,]+ of ([\d,]+)',
                r'(\d{1,3}(?:,\d{3})*) patents',
                r'of ([\d,]+) total'
            ]
            
            for pattern in count_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                if matches:
                    for match in matches:
                        count = int(match.replace(',', ''))
                        print(f"✅ Found count via pattern '{pattern}': {count:,}")
            
            # Look for JavaScript data that might contain pagination info
            print(f"\n🔧 JAVASCRIPT DATA ANALYSIS:")
            print("=" * 50)
            
            js_patterns = [
                r'window\.__data__\s*=\s*({.*?});',
                r'AF_initDataCallback\((.*?)\);',
                r'"totalResults":\s*(\d+)',
                r'"numResults":\s*(\d+)',
                r'"resultCount":\s*(\d+)'
            ]
            
            for pattern in js_patterns:
                matches = re.findall(pattern, page_source, re.DOTALL)
                print(f"📊 Pattern '{pattern}': {len(matches)} matches")
                if matches and len(matches) <= 3:
                    for i, match in enumerate(matches[:2]):
                        preview = str(match)[:200] + "..." if len(str(match)) > 200 else str(match)
                        print(f"   {i+1}. {preview}")
            
            # Try different URL patterns for pagination
            print(f"\n🌐 URL PATTERN TESTING:")
            print("=" * 50)
            
            base_url = driver.current_url
            print(f"Base URL: {base_url}")
            
            # Test different pagination URL patterns
            url_patterns = [
                f"{base_url}&start=10",
                f"{base_url}&page=2",
                f"{base_url}&offset=10",
                f"{base_url}&num=100",  # Try more results per page
                f"{base_url}&start=10&num=50"
            ]
            
            for test_url in url_patterns:
                try:
                    print(f"\n🧪 Testing URL: {test_url}")
                    driver.get(test_url)
                    time.sleep(3)
                    
                    # Check if we got different results
                    search_items = driver.find_elements(By.TAG_NAME, 'search-result-item')
                    print(f"   📊 Found {len(search_items)} search items")
                    
                    if search_items:
                        # Get first patent number to see if it's different
                        first_item_text = search_items[0].text
                        patent_match = re.search(r'\b([A-Z]{2}\d{7,10}[A-Z]?\d?)\b', first_item_text)
                        if patent_match:
                            print(f"   🔍 First patent: {patent_match.group(1)}")
                    
                    # Check URL after navigation
                    final_url = driver.current_url
                    if final_url != test_url:
                        print(f"   🔄 URL changed to: {final_url}")
                    
                except Exception as e:
                    print(f"   ❌ Error testing URL: {e}")
            
            # Try to find the actual pagination mechanism by inspecting network requests
            print(f"\n🌐 NETWORK REQUEST ANALYSIS:")
            print("=" * 50)
            
            # Execute JavaScript to see if there are AJAX endpoints
            try:
                js_code = """
                // Look for any pagination-related functions or data
                var paginationInfo = {};
                
                // Check for common pagination variables
                if (typeof window.__data__ !== 'undefined') {
                    paginationInfo.windowData = 'Found window.__data__';
                }
                
                // Look for pagination functions
                var scripts = document.getElementsByTagName('script');
                var paginationFunctions = [];
                for (var i = 0; i < scripts.length; i++) {
                    var script = scripts[i];
                    if (script.innerHTML.includes('nextPage') || 
                        script.innerHTML.includes('loadMore') ||
                        script.innerHTML.includes('pagination')) {
                        paginationFunctions.push('Found pagination-related script');
                    }
                }
                paginationInfo.paginationFunctions = paginationFunctions;
                
                // Check for result count in DOM
                var allText = document.body.textContent || document.body.innerText;
                var countMatch = allText.match(/About ([\\d,]+) result/i);
                if (countMatch) {
                    paginationInfo.resultCount = countMatch[1];
                }
                
                return paginationInfo;
                """
                
                js_result = driver.execute_script(js_code)
                print(f"📊 JavaScript analysis result: {js_result}")
                
            except Exception as e:
                print(f"❌ JavaScript analysis error: {e}")
            
            # Check if there are any hidden elements or parameters
            print(f"\n🔍 HIDDEN ELEMENTS ANALYSIS:")
            print("=" * 50)
            
            hidden_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="hidden"]')
            print(f"📊 Found {len(hidden_inputs)} hidden input elements")
            
            for i, hidden in enumerate(hidden_inputs[:5]):
                name = hidden.get_attribute('name')
                value = hidden.get_attribute('value')
                print(f"   {i+1}. {name}: {value}")
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")

if __name__ == "__main__":
    analyze_google_patents_pagination("FOXP2")