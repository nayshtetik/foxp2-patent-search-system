#!/usr/bin/env python3
"""
FOXP2 Preclinical Small Molecule Patent PDF Downloader
====================================================

Downloads PDF files for all preclinical stage small molecule patents
from the human therapeutic FOXP2 patent dataset.
"""

import os
import csv
import time
import requests
from urllib.parse import urljoin
import pandas as pd
from pathlib import Path

class PreclinicalSmallMoleculePDFDownloader:
    def __init__(self):
        self.data_dir = Path("patent_data")
        self.pdf_dir = self.data_dir / "downloaded_pdfs" / "preclinical_small_molecules"
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def load_detailed_classifications(self):
        """Load the detailed classification data"""
        classification_file = self.data_dir / "detailed_classification" / "detailed_human_patent_classification_20250821_070448.csv"
        
        if not classification_file.exists():
            raise FileNotFoundError(f"Classification file not found: {classification_file}")
            
        df = pd.read_csv(classification_file)
        return df
    
    def filter_preclinical_small_molecules(self, df):
        """Filter for preclinical stage small molecules"""
        # Filter for small molecules in preclinical development
        filtered = df[
            (df['molecule_type'] == 'small_molecule') & 
            (df['development_phase'] == 'Preclinical Development')
        ].copy()
        
        print(f"📊 Found {len(filtered)} preclinical small molecule patents:")
        for _, row in filtered.iterrows():
            print(f"  • {row['patent_number']}: {row['title'][:60]}...")
            
        return filtered
    
    def get_pdf_url(self, patent_number):
        """Generate PDF URL for a patent number"""
        return f"https://patents.google.com/patent/{patent_number}/pdf"
    
    def download_pdf(self, patent_number, title, max_retries=3):
        """Download PDF for a single patent"""
        pdf_url = self.get_pdf_url(patent_number)
        
        # Clean filename
        safe_title = "".join(c for c in title[:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{patent_number}_{safe_title}.pdf"
        filepath = self.pdf_dir / filename
        
        if filepath.exists():
            print(f"✅ Already exists: {filename}")
            return True
            
        print(f"📥 Downloading: {patent_number}")
        print(f"    URL: {pdf_url}")
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(pdf_url, timeout=30)
                response.raise_for_status()
                
                # Check if it's actually a PDF
                if response.headers.get('content-type', '').lower().startswith('application/pdf'):
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    file_size = filepath.stat().st_size
                    print(f"✅ Downloaded: {filename} ({file_size:,} bytes)")
                    return True
                else:
                    print(f"⚠️  Not a PDF response for {patent_number}")
                    return False
                    
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed for {patent_number}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        return False
    
    def download_all_pdfs(self):
        """Download all preclinical small molecule patent PDFs"""
        print("🔬 FOXP2 Preclinical Small Molecule Patent PDF Downloader")
        print("=" * 60)
        
        # Load and filter data
        df = self.load_detailed_classifications()
        preclinical_small_molecules = self.filter_preclinical_small_molecules(df)
        
        if len(preclinical_small_molecules) == 0:
            print("❌ No preclinical small molecule patents found!")
            return
            
        print(f"\n📁 Download directory: {self.pdf_dir}")
        print(f"🎯 Downloading {len(preclinical_small_molecules)} patent PDFs...\n")
        
        # Download each PDF
        successful_downloads = 0
        failed_downloads = []
        
        for idx, row in preclinical_small_molecules.iterrows():
            patent_number = row['patent_number']
            title = row['title']
            
            print(f"\n[{idx + 1}/{len(preclinical_small_molecules)}] Processing {patent_number}")
            
            if self.download_pdf(patent_number, title):
                successful_downloads += 1
            else:
                failed_downloads.append(patent_number)
                
            # Be respectful to the server
            time.sleep(1)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"✅ Successful downloads: {successful_downloads}")
        print(f"❌ Failed downloads: {len(failed_downloads)}")
        print(f"📁 Download directory: {self.pdf_dir}")
        
        if failed_downloads:
            print(f"\n❌ Failed patents: {', '.join(failed_downloads)}")
            
        # Create download summary
        summary_file = self.pdf_dir / "download_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"FOXP2 Preclinical Small Molecule Patent PDF Download Summary\n")
            f.write(f"=" * 60 + "\n")
            f.write(f"Download timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total patents processed: {len(preclinical_small_molecules)}\n")
            f.write(f"Successful downloads: {successful_downloads}\n")
            f.write(f"Failed downloads: {len(failed_downloads)}\n\n")
            
            f.write("Preclinical Small Molecule Patents:\n")
            f.write("-" * 40 + "\n")
            for _, row in preclinical_small_molecules.iterrows():
                f.write(f"{row['patent_number']}: {row['title']}\n")
                f.write(f"  Relevance Score: {row['relevance_score']:.2f}\n")
                f.write(f"  Molecule Subtype: {row['molecule_subtype']}\n\n")
                
            if failed_downloads:
                f.write(f"\nFailed Downloads:\n")
                f.write("-" * 20 + "\n")
                for patent in failed_downloads:
                    f.write(f"{patent}\n")
        
        print(f"📄 Summary saved to: {summary_file}")
        print(f"\n🎉 Download complete! Check {self.pdf_dir} for PDF files.")

def main():
    downloader = PreclinicalSmallMoleculePDFDownloader()
    downloader.download_all_pdfs()

if __name__ == "__main__":
    main()