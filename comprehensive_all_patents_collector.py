#!/usr/bin/env python3
"""
Comprehensive collector to gather ALL 3,665 FOXP2 patents using multiple persistent strategies
"""

import time
import json
import csv
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus, urlencode
import re
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class ComprehensiveAllPatentsCollector:
    """Comprehensive collector using multiple persistent strategies to get ALL patents"""
    
    def __init__(self):
        self.results_dir = Path("patent_data/comprehensive_all")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Multiple user agents to rotate
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Session for requests
        self.session = requests.Session()
        
        # Chrome options for Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Collection settings
        self.base_delay = 3
        self.max_retries = 8
        self.timeout = 25
        
    def create_driver_with_rotation(self):
        """Create driver with rotated user agent"""
        user_agent = random.choice(self.user_agents)
        self.chrome_options.add_argument(f"--user-agent={user_agent}")
        
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(self.timeout)
        return driver
    
    def strategy_1_selenium_persistent(self, start_page=1, end_page=37):
        """Strategy 1: Persistent Selenium with exponential backoff"""
        print(f"🚀 STRATEGY 1: Persistent Selenium (Pages {start_page}-{end_page})")
        print("=" * 55)
        
        all_patents = []
        failed_pages = []
        
        for page_num in range(start_page, end_page + 1):
            print(f"\n📄 Page {page_num}/{end_page}")
            
            page_patents = None
            for attempt in range(self.max_retries):
                driver = None
                try:
                    print(f"   🔄 Attempt {attempt + 1}/{self.max_retries}")
                    
                    # Create fresh driver with rotation
                    driver = self.create_driver_with_rotation()
                    
                    # Navigate to page
                    url = f"https://patents.google.com/?q={quote_plus('FOXP2')}&num=100&page={page_num}"
                    print(f"   🌐 URL: {url}")
                    
                    driver.get(url)
                    
                    # Wait with custom conditions
                    wait_time = random.uniform(2, 5)
                    time.sleep(wait_time)
                    
                    # Wait for results to load
                    try:
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "search-result-item"))
                        )
                        
                        # Additional wait for full rendering
                        time.sleep(random.uniform(1, 3))
                        
                        # Extract patents
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        patent_items = soup.find_all('search-result-item')
                        
                        if patent_items:
                            page_patents = self.extract_patents_from_items(patent_items, page_num)
                            print(f"   ✅ Found {len(page_patents)} patents")
                            break
                        else:
                            print(f"   ⚠️ No patent items found")
                            
                    except Exception as e:
                        print(f"   ❌ Wait/extract failed: {e}")
                        
                except Exception as e:
                    print(f"   ❌ Driver error: {e}")
                    
                finally:
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                
                # Exponential backoff
                if attempt < self.max_retries - 1:
                    backoff_time = self.base_delay * (2 ** attempt) + random.uniform(1, 3)
                    print(f"   ⏳ Backoff: {backoff_time:.1f}s")
                    time.sleep(backoff_time)
            
            # Record results
            if page_patents:
                all_patents.extend(page_patents)
                print(f"📊 Progress: {len(all_patents)} total patents collected")
            else:
                failed_pages.append(page_num)
                print(f"❌ Failed: Page {page_num}")
            
            # Rate limiting between pages
            if page_num < end_page:
                page_delay = random.uniform(self.base_delay, self.base_delay * 2)
                time.sleep(page_delay)
        
        print(f"\n📊 Strategy 1 Results:")
        print(f"   ✅ Successful pages: {37 - len(failed_pages)}/37")
        print(f"   📄 Patents collected: {len(all_patents)}")
        print(f"   ❌ Failed pages: {failed_pages}")
        
        return all_patents, failed_pages
    
    def strategy_2_requests_scraping(self):
        """Strategy 2: Advanced requests-based scraping with session management"""
        print(f"\n🌐 STRATEGY 2: Advanced Requests Scraping")
        print("=" * 45)
        
        all_patents = []
        
        # Try different query variations
        query_variations = [
            "FOXP2",
            "forkhead box P2",
            "FOXP2 protein", 
            "FOXP2 gene",
            "speech language gene"
        ]
        
        for query_idx, query in enumerate(query_variations):
            print(f"\n🔍 Query {query_idx + 1}/{len(query_variations)}: {query}")
            
            # Rotate user agent
            self.session.headers.update({
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # Try multiple approaches for this query
            query_patents = []
            
            # Approach 1: Google Patents search results
            try:
                for page in range(1, 11):  # Try first 10 pages per query
                    url = f"https://patents.google.com/?q={quote_plus(query)}&num=100&page={page}"
                    
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        patents = self.extract_patents_from_html(response.text, page, query)
                        if patents:
                            query_patents.extend(patents)
                            print(f"   📄 Page {page}: +{len(patents)} patents")
                        else:
                            break  # No more results
                    
                    time.sleep(random.uniform(1, 3))
                    
            except Exception as e:
                print(f"   ❌ Requests approach failed: {e}")
            
            print(f"   📊 Query '{query}' results: {len(query_patents)} patents")
            all_patents.extend(query_patents)
            
            # Delay between queries
            time.sleep(random.uniform(2, 5))
        
        # Remove duplicates
        unique_patents = self.remove_duplicates(all_patents)
        
        print(f"\n📊 Strategy 2 Results:")
        print(f"   📄 Total patents: {len(all_patents)}")
        print(f"   📄 Unique patents: {len(unique_patents)}")
        
        return unique_patents
    
    def strategy_3_hybrid_approach(self, failed_pages_from_strategy1):
        """Strategy 3: Hybrid approach for failed pages"""
        print(f"\n🔄 STRATEGY 3: Hybrid Approach for Failed Pages")
        print("=" * 50)
        
        if not failed_pages_from_strategy1:
            print("   ✅ No failed pages to retry")
            return []
        
        print(f"   🎯 Retrying {len(failed_pages_from_strategy1)} failed pages")
        
        recovered_patents = []
        
        for page_num in failed_pages_from_strategy1:
            print(f"\n🔄 Recovering page {page_num}")
            
            # Try multiple methods for this page
            methods = [
                self.try_selenium_with_proxy_headers,
                self.try_requests_with_fake_browser,
                self.try_selenium_with_different_strategy
            ]
            
            for method_idx, method in enumerate(methods):
                try:
                    print(f"   📡 Method {method_idx + 1}/3")
                    page_patents = method(page_num)
                    
                    if page_patents:
                        recovered_patents.extend(page_patents)
                        print(f"   ✅ Recovered {len(page_patents)} patents from page {page_num}")
                        break
                    else:
                        print(f"   ⚠️ Method {method_idx + 1} found no patents")
                        
                except Exception as e:
                    print(f"   ❌ Method {method_idx + 1} failed: {e}")
                
                time.sleep(random.uniform(2, 4))
        
        print(f"\n📊 Strategy 3 Results:")
        print(f"   📄 Recovered patents: {len(recovered_patents)}")
        
        return recovered_patents
    
    def try_selenium_with_proxy_headers(self, page_num):
        """Try selenium with proxy-like headers"""
        driver = None
        try:
            driver = self.create_driver_with_rotation()
            
            # Set additional headers via JavaScript
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": random.choice(self.user_agents)
            })
            
            url = f"https://patents.google.com/?q={quote_plus('FOXP2')}&num=100&page={page_num}"
            driver.get(url)
            
            # Wait and extract
            time.sleep(random.uniform(3, 6))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            items = soup.find_all('search-result-item')
            
            return self.extract_patents_from_items(items, page_num) if items else []
            
        finally:
            if driver:
                driver.quit()
    
    def try_requests_with_fake_browser(self, page_num):
        """Try requests with extensive browser simulation"""
        try:
            # Extensive headers to mimic real browser
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            url = f"https://patents.google.com/?q={quote_plus('FOXP2')}&num=100&page={page_num}"
            
            response = self.session.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                return self.extract_patents_from_html(response.text, page_num, 'FOXP2')
            
        except Exception as e:
            pass
        
        return []
    
    def try_selenium_with_different_strategy(self, page_num):
        """Try selenium with completely different loading strategy"""
        driver = None
        try:
            # Different chrome options
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript")  # Try without JS
            
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)
            
            url = f"https://patents.google.com/?q={quote_plus('FOXP2')}&num=100&page={page_num}"
            driver.get(url)
            
            time.sleep(5)
            
            # Try to find any patent-related content
            page_source = driver.page_source
            return self.extract_patents_from_html(page_source, page_num, 'FOXP2')
            
        finally:
            if driver:
                driver.quit()
    
    def extract_patents_from_items(self, patent_items, page_num):
        """Extract patent data from BeautifulSoup items"""
        patents = []
        
        for item in patent_items:
            try:
                # Extract patent number
                patent_num_elem = item.select_one('.number')
                patent_number = patent_num_elem.get_text(strip=True) if patent_num_elem else f"UNKNOWN_P{page_num}_{len(patents)}"
                
                # Extract title
                title_elem = item.select_one('.result-title')
                title = title_elem.get_text(strip=True) if title_elem else "No title"
                
                # Extract snippet/abstract
                snippet_elem = item.select_one('.snippet')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                # Extract assignee
                assignee_elem = item.select_one('.assignee')
                assignee = assignee_elem.get_text(strip=True) if assignee_elem else ""
                
                # Extract publication date
                date_elem = item.select_one('.filing-date, .publication-date')
                pub_date = date_elem.get_text(strip=True) if date_elem else ""
                
                # Extract inventors
                inventor_elems = item.select('.inventor')
                inventors = [inv.get_text(strip=True) for inv in inventor_elems]
                
                patent_data = {
                    'patent_number': patent_number,
                    'title': title,
                    'abstract': snippet,
                    'assignee': assignee,
                    'publication_date': pub_date,
                    'inventors': inventors,
                    'raw_text': f"{title} {snippet}",
                    'page_collected': page_num,
                    'collection_timestamp': datetime.now().isoformat(),
                    'source': 'comprehensive_collector'
                }
                
                patents.append(patent_data)
                
            except Exception as e:
                continue
        
        return patents
    
    def extract_patents_from_html(self, html_content, page_num, query):
        """Extract patent data from raw HTML"""
        patents = []
        
        try:
            # Look for patent numbers using multiple patterns
            patent_patterns = [
                r'[A-Z]{2}\d{7,12}[A-Z]\d?',  # General format
                r'US\d{7,10}[A-Z]\d?',        # US patents
                r'EP\d{7,10}[A-Z]\d?',        # EP patents
                r'WO\d{4}/\d{6}[A-Z]\d?',     # WO patents
                r'CN\d{9,12}[A-Z]?',          # CN patents
                r'JP\d{10,13}[A-Z]?',         # JP patents
            ]
            
            all_patent_nums = []
            for pattern in patent_patterns:
                matches = re.findall(pattern, html_content)
                all_patent_nums.extend(matches)
            
            # Look for titles near patent numbers
            title_patterns = [
                r'<[^>]*title[^>]*>([^<]+)</[^>]*>',
                r'title="([^"]+)"',
                r'<h\d[^>]*>([^<]+)</h\d>',
            ]
            
            titles = []
            for pattern in title_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                titles.extend(matches)
            
            # Create patent entries
            unique_patents = list(set(all_patent_nums))
            
            for i, patent_num in enumerate(unique_patents[:100]):  # Limit per page
                title = titles[i] if i < len(titles) else f"Patent {patent_num}"
                
                patent_data = {
                    'patent_number': patent_num,
                    'title': title.strip(),
                    'abstract': "",
                    'assignee': "",
                    'publication_date': "",
                    'inventors': [],
                    'raw_text': f"{patent_num} {title}",
                    'page_collected': page_num,
                    'collection_timestamp': datetime.now().isoformat(),
                    'source': f'html_extraction_{query}'
                }
                patents.append(patent_data)
                
        except Exception as e:
            pass
        
        return patents
    
    def remove_duplicates(self, patents):
        """Remove duplicate patents based on patent number"""
        seen = set()
        unique_patents = []
        
        for patent in patents:
            patent_num = patent.get('patent_number', '')
            if patent_num and patent_num not in seen:
                seen.add(patent_num)
                unique_patents.append(patent)
        
        return unique_patents
    
    def run_comprehensive_collection(self):
        """Run all strategies to collect ALL patents"""
        
        print("🌟 COMPREHENSIVE ALL-PATENTS COLLECTION")
        print("=" * 60)
        print("🎯 Mission: Collect ALL 3,665 FOXP2 patents")
        print("🚀 Using: Multiple persistent strategies")
        print("⏱️ Estimated time: 45-90 minutes")
        print()
        
        start_time = time.time()
        all_patents = []
        
        # Strategy 1: Persistent Selenium
        strategy1_patents, failed_pages = self.strategy_1_selenium_persistent()
        all_patents.extend(strategy1_patents)
        
        # Strategy 2: Advanced requests scraping
        strategy2_patents = self.strategy_2_requests_scraping()
        all_patents.extend(strategy2_patents)
        
        # Strategy 3: Hybrid recovery for failed pages
        strategy3_patents = self.strategy_3_hybrid_approach(failed_pages)
        all_patents.extend(strategy3_patents)
        
        # Remove duplicates from all strategies
        unique_patents = self.remove_duplicates(all_patents)
        
        total_time = time.time() - start_time
        
        # Final summary
        print(f"\n🎯 COMPREHENSIVE COLLECTION COMPLETE")
        print("=" * 50)
        print(f"📊 Strategy 1 (Selenium): {len(strategy1_patents)} patents")
        print(f"📊 Strategy 2 (Requests): {len(strategy2_patents)} patents")
        print(f"📊 Strategy 3 (Recovery): {len(strategy3_patents)} patents")
        print(f"📊 Total collected: {len(all_patents)} patents")
        print(f"📊 Unique patents: {len(unique_patents)} patents")
        print(f"🎯 Target: 3,665 patents")
        print(f"📈 Success rate: {len(unique_patents)/3665*100:.1f}%")
        print(f"⏱️ Total time: {total_time/60:.1f} minutes")
        
        return unique_patents
    
    def save_comprehensive_results(self, patents):
        """Save comprehensive collection results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = self.results_dir / f"comprehensive_all_foxp2_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_file = self.results_dir / f"comprehensive_all_foxp2_{timestamp}.csv"
        if patents:
            all_keys = set()
            for patent in patents:
                all_keys.update(patent.keys())
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(patents)
        
        print(f"\n💾 Comprehensive Results Saved:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📊 CSV: {csv_file}")
        
        return json_file, csv_file
    
    def analyze_comprehensive_results(self, patents):
        """Analyze comprehensive results for drug discovery"""
        if not patents:
            print("❌ No patents to analyze")
            return []
        
        print(f"\n🔬 COMPREHENSIVE DRUG DISCOVERY ANALYSIS")
        print("=" * 50)
        
        try:
            from improved_drug_analyzer import ImprovedDrugDiscoveryAnalyzer
            
            analyzer = ImprovedDrugDiscoveryAnalyzer()
            
            # Analyze all patents
            drug_patents = analyzer.analyze_patents_with_enhanced_content(
                patents, 
                min_relevance=3.0,
                enhance_top_patents=True
            )
            
            # Generate summary
            summary = analyzer.generate_summary_report(drug_patents)
            json_file, csv_file = analyzer.save_drug_discovery_results(
                drug_patents, 
                "comprehensive_all_drug_discovery"
            )
            
            print(f"\n🎯 COMPREHENSIVE DRUG DISCOVERY RESULTS:")
            print(f"   📊 Total patents: {len(patents)}")
            print(f"   🎯 Drug discovery relevant: {len(drug_patents)}")
            print(f"   📈 Success rate: {len(drug_patents)/len(patents)*100:.1f}%")
            
            return drug_patents
            
        except ImportError:
            print("⚠️ Drug discovery analyzer not available")
            return patents

def main():
    """Main comprehensive collection function"""
    collector = ComprehensiveAllPatentsCollector()
    
    # Run comprehensive collection
    patents = collector.run_comprehensive_collection()
    
    if patents:
        # Save results
        json_file, csv_file = collector.save_comprehensive_results(patents)
        
        # Analyze for drug discovery
        drug_patents = collector.analyze_comprehensive_results(patents)
        
        print(f"\n✅ COMPREHENSIVE COLLECTION MISSION COMPLETE!")
        print(f"🌟 Successfully collected {len(patents)} patents")
        print(f"💊 Found {len(drug_patents)} drug discovery relevant patents")
        print(f"📁 Results saved and ready for analysis")
        
    else:
        print("❌ Comprehensive collection failed")

if __name__ == "__main__":
    main()