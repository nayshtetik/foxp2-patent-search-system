#!/usr/bin/env python3
"""
Resume collection from page 16 to complete all 3,665 FOXP2 patents
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
from urllib.parse import quote_plus

class ResumePatentCollector:
    """Resume collection from page 16 to complete the dataset"""
    
    def __init__(self):
        self.results_dir = Path("patent_data/complete_3665")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Chrome options optimized for stability
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        # Rate limiting settings
        self.delay_between_pages = 3  # Increased delay
        self.max_retries = 5          # More retries
        self.timeout = 20             # Longer timeout
    
    def extract_patents_from_page(self, driver, page_num):
        """Extract patent data from current page"""
        patents = []
        
        try:
            # Wait for search results to load
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "search-result-item"))
            )
            
            # Additional wait for full loading
            time.sleep(2)
            
            # Get page source and parse
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            patent_items = soup.find_all('search-result-item')
            
            print(f"   📄 Found {len(patent_items)} patent items on page")
            
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
                    print(f"   ⚠️ Failed to extract patent: {e}")
                    continue
            
            return patents
            
        except Exception as e:
            print(f"   ❌ Failed to extract patents from page {page_num}: {e}")
            return []
    
    def collect_page_with_retries(self, page_num):
        """Collect a single page with enhanced retry logic"""
        base_url = f"https://patents.google.com/?q={quote_plus('FOXP2')}"
        url = f"{base_url}&num=100&page={page_num}"
        
        for attempt in range(self.max_retries):
            driver = None
            try:
                print(f"📄 Page {page_num}/37 (attempt {attempt + 1})...")
                print(f"   🌐 URL: {url}")
                
                # Create fresh driver for each attempt
                driver = webdriver.Chrome(options=self.chrome_options)
                driver.set_page_load_timeout(self.timeout)
                
                # Navigate to page
                driver.get(url)
                
                # Extract patents
                patents = self.extract_patents_from_page(driver, page_num)
                
                if patents:
                    print(f"   ✅ Page {page_num}: Successfully collected {len(patents)} patents")
                    return patents
                else:
                    print(f"   ⚠️ Page {page_num}: No patents found (attempt {attempt + 1})")
                    
            except Exception as e:
                print(f"   ❌ Page {page_num} attempt {attempt + 1} failed: {e}")
                
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                    
            # Wait before retry
            if attempt < self.max_retries - 1:
                wait_time = self.delay_between_pages * (attempt + 1)  # Exponential backoff
                print(f"   ⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        
        print(f"   ❌ Failed to collect page {page_num} after {self.max_retries} attempts")
        return []
    
    def resume_collection_from_page16(self):
        """Resume collection from page 16 through 37"""
        
        print("🔄 RESUMING FOXP2 PATENT COLLECTION FROM PAGE 16")
        print("=" * 55)
        print("🎯 Target: Pages 16-37 (remaining ~2,200 patents)")
        print("⏱️ Estimated time: 30-45 minutes")
        print("🛡️ Enhanced retry logic and rate limiting")
        print()
        
        all_patents = []
        failed_pages = []
        start_time = time.time()
        
        # Resume from page 16 through 37
        for page_num in range(16, 38):
            patents = self.collect_page_with_retries(page_num)
            
            if patents:
                all_patents.extend(patents)
                print(f"📊 Progress: {len(all_patents)} patents collected from pages 16-{page_num}")
            else:
                failed_pages.append(page_num)
                print(f"❌ Failed: Page {page_num}")
            
            # Rate limiting between successful pages
            if page_num < 37 and patents:
                time.sleep(self.delay_between_pages)
            
            # Progress checkpoint every 5 pages
            if (page_num - 15) % 5 == 0:
                elapsed = time.time() - start_time
                remaining_pages = 37 - page_num
                print(f"⏱️ Checkpoint: {page_num}/37 pages, {len(all_patents)} new patents, {elapsed/60:.1f} min elapsed")
                print(f"   📈 Estimated {remaining_pages * (elapsed/(page_num-15))/60:.1f} minutes remaining")
        
        total_time = time.time() - start_time
        
        print()
        print("✅ RESUME COLLECTION COMPLETE")
        print("=" * 35)
        print(f"📊 New patents collected: {len(all_patents)}")
        print(f"✅ Successful pages: {22 - len(failed_pages)}/22 (pages 16-37)")
        print(f"❌ Failed pages: {failed_pages}")
        print(f"⏱️ Total time: {total_time/60:.1f} minutes")
        
        return all_patents, failed_pages
    
    def combine_with_existing_data(self, new_patents):
        """Combine new patents with existing 473 patents"""
        
        print("\n🔗 COMBINING WITH EXISTING DATA")
        print("=" * 35)
        
        # Load existing patents from previous successful run
        existing_files = list(Path("patent_data/final_drug_discovery").glob("*.json"))
        existing_patents = []
        
        if existing_files:
            # Load the most recent existing data
            latest_file = max(existing_files, key=lambda f: f.stat().st_mtime)
            print(f"📄 Loading existing data from: {latest_file.name}")
            
            try:
                with open(latest_file, 'r') as f:
                    existing_data = json.load(f)
                    
                # Extract raw patent data (before drug discovery analysis)
                if isinstance(existing_data, list) and existing_data:
                    existing_patents = existing_data
                    print(f"✅ Loaded {len(existing_patents)} existing patents")
            except Exception as e:
                print(f"⚠️ Could not load existing data: {e}")
        
        # Combine datasets
        all_patents = existing_patents + new_patents
        
        # Remove duplicates based on patent_number
        seen = set()
        unique_patents = []
        for patent in all_patents:
            patent_num = patent.get('patent_number', '')
            if patent_num and patent_num not in seen:
                seen.add(patent_num)
                unique_patents.append(patent)
        
        print(f"📊 Combined dataset: {len(unique_patents)} unique patents")
        print(f"   📥 Existing: {len(existing_patents)}")
        print(f"   📥 New: {len(new_patents)}")
        print(f"   🔄 Duplicates removed: {len(all_patents) - len(unique_patents)}")
        
        return unique_patents
    
    def save_complete_dataset(self, patents):
        """Save the complete combined dataset"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save complete dataset as JSON
        json_file = self.results_dir / f"complete_foxp2_dataset_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, ensure_ascii=False)
        
        # Save complete dataset as CSV
        csv_file = self.results_dir / f"complete_foxp2_dataset_{timestamp}.csv"
        if patents:
            all_keys = set()
            for patent in patents:
                all_keys.update(patent.keys())
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(patents)
        
        print(f"\n💾 Complete dataset saved:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📊 CSV: {csv_file}")
        
        return json_file, csv_file

def main():
    """Main function to resume collection from page 16"""
    collector = ResumePatentCollector()
    
    # Resume collection from page 16
    new_patents, failed_pages = collector.resume_collection_from_page16()
    
    # Combine with existing data
    complete_dataset = collector.combine_with_existing_data(new_patents)
    
    # Save complete dataset
    json_file, csv_file = collector.save_complete_dataset(complete_dataset)
    
    # Final summary
    print(f"\n🎯 FINAL COMPLETE DATASET SUMMARY")
    print("=" * 40)
    print(f"📊 Total patents collected: {len(complete_dataset)}")
    print(f"🎯 Target was: 3,665 patents")
    print(f"📈 Completion rate: {len(complete_dataset)/3665*100:.1f}%")
    
    if failed_pages:
        print(f"❌ Failed pages in this run: {failed_pages}")
        print(f"💡 These pages can be retried individually if needed")
    
    print(f"\n✅ Ready for complete drug discovery analysis on {len(complete_dataset)} patents!")

if __name__ == "__main__":
    main()