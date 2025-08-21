#!/usr/bin/env python3
"""
Robust collector specifically designed to gather all 3,665 FOXP2 patents
"""

import time
import json
import csv
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging

class Complete3665Collector:
    """Robust collector for all 3,665 FOXP2 patents"""
    
    def __init__(self):
        self.results_dir = Path("patent_data/complete_3665")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
        # Rate limiting
        self.delay_between_pages = 2
        self.delay_between_retries = 5
        self.max_retries = 3
        
    def create_driver(self):
        """Create a new Chrome driver instance"""
        return webdriver.Chrome(options=self.chrome_options)
    
    def extract_patents_from_page(self, driver, page_num):
        """Extract patent data from a single page"""
        patents = []
        
        try:
            # Wait for results to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "search-result-item"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            patent_items = soup.find_all('search-result-item')
            
            for item in patent_items:
                try:
                    # Extract patent number
                    patent_num_elem = item.select_one('.number')
                    patent_number = patent_num_elem.get_text(strip=True) if patent_num_elem else "Unknown"
                    
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
                        'collection_timestamp': datetime.now().isoformat()
                    }
                    
                    patents.append(patent_data)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract patent from item: {e}")
                    continue
            
            return patents
            
        except Exception as e:
            self.logger.error(f"Failed to extract patents from page {page_num}: {e}")
            return []
    
    def collect_page_with_retries(self, page_num):
        """Collect a single page with retry logic"""
        url = f"https://patents.google.com/search?q=FOXP2&num=100&page={page_num}"
        
        for attempt in range(self.max_retries):
            driver = None
            try:
                self.logger.info(f"📄 Page {page_num}/37 (attempt {attempt + 1})...")
                
                driver = self.create_driver()
                driver.get(url)
                
                # Wait and extract
                patents = self.extract_patents_from_page(driver, page_num)
                
                if patents:
                    self.logger.info(f"✅ Page {page_num}: +{len(patents)} patents")
                    return patents
                else:
                    self.logger.warning(f"⚠️ Page {page_num}: No patents found (attempt {attempt + 1})")
                    
            except Exception as e:
                self.logger.error(f"❌ Page {page_num} attempt {attempt + 1} failed: {e}")
                
            finally:
                if driver:
                    driver.quit()
                    
            if attempt < self.max_retries - 1:
                self.logger.info(f"⏳ Waiting {self.delay_between_retries}s before retry...")
                time.sleep(self.delay_between_retries)
        
        self.logger.error(f"❌ Failed to collect page {page_num} after {self.max_retries} attempts")
        return []
    
    def collect_all_patents(self):
        """Collect all 3,665 patents across 37 pages"""
        all_patents = []
        failed_pages = []
        
        print("🧬 COLLECTING ALL 3,665 FOXP2 PATENTS")
        print("=" * 50)
        print("🎯 Target: 37 pages × ~100 patents = 3,665 total")
        print("⏱️ Estimated time: 15-20 minutes")
        print()
        
        start_time = time.time()
        
        for page_num in range(1, 38):  # Pages 1-37
            patents = self.collect_page_with_retries(page_num)
            
            if patents:
                all_patents.extend(patents)
                print(f"📊 Progress: {len(all_patents)} patents collected from {page_num} pages")
            else:
                failed_pages.append(page_num)
                print(f"❌ Failed: Page {page_num}")
            
            # Rate limiting between pages
            if page_num < 37:
                time.sleep(self.delay_between_pages)
            
            # Progress checkpoint every 5 pages
            if page_num % 5 == 0:
                elapsed = time.time() - start_time
                print(f"⏱️ Checkpoint: {page_num}/37 pages, {len(all_patents)} patents, {elapsed/60:.1f} min elapsed")
        
        total_time = time.time() - start_time
        
        print()
        print("✅ COLLECTION COMPLETE")
        print("=" * 30)
        print(f"📊 Total patents collected: {len(all_patents)}")
        print(f"✅ Successful pages: {37 - len(failed_pages)}/37")
        print(f"❌ Failed pages: {failed_pages}")
        print(f"⏱️ Total time: {total_time/60:.1f} minutes")
        
        return all_patents, failed_pages
    
    def save_results(self, patents):
        """Save collected patents to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = self.results_dir / f"all_foxp2_patents_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_file = self.results_dir / f"all_foxp2_patents_{timestamp}.csv"
        if patents:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=patents[0].keys())
                writer.writeheader()
                writer.writerows(patents)
        
        print(f"💾 Results saved:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📊 CSV: {csv_file}")
        
        return json_file, csv_file

def main():
    """Main collection function"""
    collector = Complete3665Collector()
    
    # Collect all patents
    patents, failed_pages = collector.collect_all_patents()
    
    if patents:
        # Save results
        json_file, csv_file = collector.save_results(patents)
        
        # Summary statistics
        print()
        print("📈 COLLECTION SUMMARY")
        print("=" * 25)
        print(f"Total patents: {len(patents)}")
        print(f"Success rate: {len(patents)/3665*100:.1f}%")
        print(f"Average per page: {len(patents)/37:.1f}")
        
        if failed_pages:
            print(f"Failed pages: {failed_pages}")
            print("💡 You can re-run specific pages if needed")
    else:
        print("❌ No patents collected")

if __name__ == "__main__":
    main()