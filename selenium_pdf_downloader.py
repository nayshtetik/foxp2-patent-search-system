#!/usr/bin/env python3
"""
Selenium-Based PDF Downloader for Preclinical Small Molecule Patents
================================================================

Uses Selenium WebDriver to download PDF files from Google Patents
for preclinical stage small molecule patents.
"""

import os
import time
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests

class SeleniumPDFDownloader:
    def __init__(self):
        self.data_dir = Path("patent_data")
        self.pdf_dir = self.data_dir / "downloaded_pdfs" / "preclinical_small_molecules"
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Selenium Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        # Set download preferences
        prefs = {
            "download.default_directory": str(self.pdf_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        self.chrome_options.add_experimental_option("prefs", prefs)
        
        self.driver = None
        
    def start_driver(self):
        """Initialize the Chrome WebDriver"""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            print("✅ Chrome WebDriver started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start Chrome WebDriver: {e}")
            return False
    
    def stop_driver(self):
        """Stop the Chrome WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("🛑 Chrome WebDriver stopped")
    
    def load_preclinical_small_molecules(self):
        """Load preclinical small molecule patents"""
        classification_file = self.data_dir / "detailed_classification" / "detailed_human_patent_classification_20250821_070448.csv"
        
        if not classification_file.exists():
            raise FileNotFoundError(f"Classification file not found: {classification_file}")
            
        df = pd.read_csv(classification_file)
        
        # Filter for small molecules in preclinical development
        filtered = df[
            (df['molecule_type'] == 'small_molecule') & 
            (df['development_phase'] == 'Preclinical Development')
        ].copy()
        
        print(f"📊 Found {len(filtered)} preclinical small molecule patents:")
        for _, row in filtered.iterrows():
            print(f"  • {row['patent_number']}: {row['title'][:60]}...")
            
        return filtered
    
    def download_patent_pdf_selenium(self, patent_number, title):
        """Download PDF using Selenium navigation"""
        try:
            # Navigate to patent page
            patent_url = f"https://patents.google.com/patent/{patent_number}"
            print(f"📥 Accessing: {patent_url}")
            
            self.driver.get(patent_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for PDF download link
            try:
                # Try to find PDF link by various methods
                pdf_links = []
                
                # Method 1: Look for direct PDF links
                pdf_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                pdf_links.extend([elem.get_attribute('href') for elem in pdf_elements])
                
                # Method 2: Look for download buttons/links
                download_elements = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'PDF') or contains(text(), 'Download')]")
                pdf_links.extend([elem.get_attribute('href') for elem in download_elements])
                
                # Method 3: Try direct PDF URL construction
                direct_pdf_url = f"https://patents.google.com/patent/{patent_number}/pdf"
                pdf_links.append(direct_pdf_url)
                
                print(f"🔍 Found {len(pdf_links)} potential PDF links")
                
                # Try each PDF link
                for pdf_url in pdf_links:
                    if pdf_url and self.download_pdf_direct(pdf_url, patent_number, title):
                        return True
                        
                # If no direct download worked, try navigating to PDF view
                try:
                    self.driver.get(f"https://patents.google.com/patent/{patent_number}/pdf")
                    time.sleep(3)
                    
                    # Check if we got a PDF
                    current_url = self.driver.current_url
                    if 'pdf' in current_url.lower():
                        print(f"✅ PDF view loaded for {patent_number}")
                        return self.save_pdf_from_browser(patent_number, title)
                    
                except Exception as e:
                    print(f"⚠️  PDF navigation failed: {e}")
                
                return False
                
            except Exception as e:
                print(f"❌ Error finding PDF links: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Selenium download failed for {patent_number}: {e}")
            return False
    
    def download_pdf_direct(self, pdf_url, patent_number, title):
        """Try direct PDF download with requests"""
        try:
            print(f"🔗 Trying direct download: {pdf_url}")
            
            response = requests.get(pdf_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type:
                    # Save the PDF
                    safe_title = "".join(c for c in title[:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    filename = f"{patent_number}_{safe_title}.pdf"
                    filepath = self.pdf_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    file_size = filepath.stat().st_size
                    print(f"✅ Downloaded: {filename} ({file_size:,} bytes)")
                    return True
                else:
                    print(f"⚠️  Response not a PDF: {content_type}")
            else:
                print(f"⚠️  HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Direct download failed: {e}")
            
        return False
    
    def save_pdf_from_browser(self, patent_number, title):
        """Save PDF from browser if it's displaying a PDF"""
        try:
            # This is a placeholder - browser PDF saving is complex
            # For now, we'll try to get the content from the page source
            page_source = self.driver.page_source
            
            if 'pdf' in page_source.lower():
                print(f"📄 PDF content detected in browser for {patent_number}")
                # This would require more complex implementation
                # to extract actual PDF data from browser
                return False
            
        except Exception as e:
            print(f"❌ Browser PDF save failed: {e}")
            
        return False
    
    def download_all_pdfs(self):
        """Download all preclinical small molecule patent PDFs"""
        print("🔬 Selenium PDF Downloader for Preclinical Small Molecules")
        print("=" * 65)
        
        # Load patents
        patents = self.load_preclinical_small_molecules()
        
        if len(patents) == 0:
            print("❌ No preclinical small molecule patents found!")
            return
            
        # Start Selenium driver
        if not self.start_driver():
            print("❌ Cannot start WebDriver - aborting download")
            return
            
        print(f"\n📁 Download directory: {self.pdf_dir}")
        print(f"🎯 Downloading {len(patents)} patent PDFs...\n")
        
        successful_downloads = 0
        failed_downloads = []
        
        try:
            for idx, row in patents.iterrows():
                patent_number = row['patent_number']
                title = row['title']
                
                print(f"\n[{idx + 1}/{len(patents)}] Processing {patent_number}")
                print(f"    Title: {title[:80]}...")
                
                if self.download_patent_pdf_selenium(patent_number, title):
                    successful_downloads += 1
                else:
                    failed_downloads.append(patent_number)
                    
                # Be respectful to the server
                time.sleep(2)
                
        finally:
            self.stop_driver()
        
        # Summary
        print("\n" + "=" * 65)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 65)
        print(f"✅ Successful downloads: {successful_downloads}")
        print(f"❌ Failed downloads: {len(failed_downloads)}")
        print(f"📁 Download directory: {self.pdf_dir}")
        
        if failed_downloads:
            print(f"\n❌ Failed patents: {', '.join(failed_downloads)}")
            
        # Create detailed summary
        summary_file = self.pdf_dir / "selenium_download_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Selenium PDF Download Summary - Preclinical Small Molecules\n")
            f.write(f"=" * 65 + "\n")
            f.write(f"Download timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total patents processed: {len(patents)}\n")
            f.write(f"Successful downloads: {successful_downloads}\n")
            f.write(f"Failed downloads: {len(failed_downloads)}\n\n")
            
            f.write("Target Patents (Preclinical Small Molecules):\n")
            f.write("-" * 50 + "\n")
            for _, row in patents.iterrows():
                f.write(f"{row['patent_number']}: {row['title']}\n")
                f.write(f"  Score: {row['relevance_score']:.2f}\n")
                f.write(f"  Subtype: {row['molecule_subtype']}\n")
                f.write(f"  URL: https://patents.google.com/patent/{row['patent_number']}\n\n")
                
        print(f"📄 Summary saved to: {summary_file}")

def main():
    downloader = SeleniumPDFDownloader()
    downloader.download_all_pdfs()

if __name__ == "__main__":
    main()