#!/usr/bin/env python3
"""
Comprehensive scraper to get all 3,665+ FOXP2 results using discovered pagination
"""

import time
import re
from typing import List, Dict, Any
from urllib.parse import quote_plus

def scrape_comprehensive_google_patents(query: str, max_results: int = 500) -> List[Dict[str, Any]]:
    """Scrape comprehensive results using discovered pagination parameters"""
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        all_results = []
        seen_patents = set()
        
        try:
            base_url = f"https://patents.google.com/?q={quote_plus(query)}"
            
            # Use discovered parameters: num=100 for max results per page, page= for pagination
            results_per_page = 100
            max_pages = max_results // results_per_page + 1
            
            print(f"🌐 Starting comprehensive search for: {query}")
            print(f"📊 Target: {max_results} results across {max_pages} pages")
            print(f"📄 Using {results_per_page} results per page")
            
            for page_num in range(1, max_pages + 1):
                if len(all_results) >= max_results:
                    break
                
                # Construct URL with pagination
                search_url = f"{base_url}&num={results_per_page}&page={page_num}"
                
                print(f"\n📄 Page {page_num}: {search_url}")
                
                driver.get(search_url)
                time.sleep(5)  # Wait for page to load
                
                # Wait for search results
                try:
                    WebDriverWait(driver, 15).until(
                        lambda d: d.find_elements(By.TAG_NAME, 'search-result-item')
                    )
                except:
                    print(f"   ⚠️ Timeout waiting for page {page_num}")
                    continue
                
                # Extract results from current page
                search_items = driver.find_elements(By.TAG_NAME, 'search-result-item')
                print(f"   📊 Found {len(search_items)} items on page")
                
                page_results = 0
                for i, item in enumerate(search_items):
                    try:
                        text_content = item.text
                        
                        # Extract patent number
                        patent_patterns = [
                            r'\b([A-Z]{2}\d{7,10}[A-Z]?\d?)\b',
                            r'\b(US\d{7,10}[A-Z]\d?)\b',
                            r'\b(EP\d{7,10}[A-Z]\d?)\b',
                            r'\b(WO\d{4}/\d{6})\b',
                            r'\b(CN\d{9}[A-Z]?)\b',
                            r'\b(JP\d{7,10}[A-Z]?\d?)\b'
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
                                if (len(line) > 15 and 
                                    line != patent_number and 
                                    not line.isdigit() and
                                    not re.match(r'^\d{4}-\d{2}-\d{2}$', line) and
                                    not re.match(r'^[A-Z]{2,3}$', line)):  # Skip country codes
                                    title = line
                                    break
                            
                            if not title:
                                title = f"Patent {patent_number}"
                            
                            # Try to extract assignee/inventor info
                            assignee = ''
                            inventor = ''
                            for line in lines:
                                # Look for patterns that might indicate assignee
                                if any(word in line.lower() for word in ['inc', 'corp', 'ltd', 'company', 'university', 'foundation']):
                                    assignee = line
                                    break
                            
                            # Extract publication date if available
                            pub_date = ''
                            date_match = re.search(r'Published (\d{4}-\d{2}-\d{2})', text_content)
                            if date_match:
                                pub_date = date_match.group(1)
                            
                            result = {
                                'patent_number': patent_number,
                                'title': title[:200],
                                'abstract': '',
                                'inventors': [inventor] if inventor else [],
                                'assignees': [assignee] if assignee else [],
                                'publication_date': pub_date,
                                'filing_date': '',
                                'url': f"https://patents.google.com/patent/{patent_number}",
                                'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                                'source': f'comprehensive_page_{page_num}',
                                'page': page_num,
                                'item_index': i
                            }
                            
                            all_results.append(result)
                            page_results += 1
                            
                            if len(all_results) >= max_results:
                                break
                    
                    except Exception as e:
                        continue
                
                print(f"   ✅ Extracted {page_results} new patents")
                print(f"   📊 Total unique patents: {len(all_results)}")
                
                # Break if we didn't get any new results (end of available data)
                if page_results == 0:
                    print(f"   ⚠️ No new results on page {page_num}, stopping")
                    break
                
                # Small delay between pages
                time.sleep(1)
            
            print(f"\n🎯 COMPREHENSIVE SCRAPING COMPLETE:")
            print(f"📊 Total unique patents extracted: {len(all_results)}")
            print(f"📄 Pages processed: {page_num}")
            print(f"🎯 Coverage: {len(all_results)}/3,665 ({len(all_results)/3665*100:.1f}%)")
            
            return all_results
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Comprehensive scraping error: {e}")
        return []

def save_results_to_csv(results: List[Dict[str, Any]], filename: str = "foxp2_patents.csv"):
    """Save results to CSV file"""
    import csv
    
    if not results:
        print("No results to save")
        return
    
    filepath = f"patent_data/{filename}"
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['patent_number', 'title', 'publication_date', 'assignees', 'url', 'page', 'source']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow({
                'patent_number': result['patent_number'],
                'title': result['title'],
                'publication_date': result['publication_date'],
                'assignees': ', '.join(result['assignees']),
                'url': result['url'],
                'page': result['page'],
                'source': result['source']
            })
    
    print(f"💾 Saved {len(results)} results to {filepath}")

def test_comprehensive_scraper():
    """Test the comprehensive scraper"""
    print("🧪 Testing comprehensive scraper for all FOXP2 patents")
    print("=" * 70)
    
    query = "FOXP2"
    
    # Start with a reasonable number for testing
    results = scrape_comprehensive_google_patents(query, max_results=200)
    
    print(f"\n📊 Comprehensive Results for '{query}':")
    print(f"Found {len(results)} total patents")
    
    if results:
        # Show sample results
        print(f"\n📄 Sample results:")
        for i, patent in enumerate(results[:15], 1):
            print(f"{i:2d}. {patent['title'][:60]}...")
            print(f"     {patent['patent_number']} | Page {patent['page']} | {patent['publication_date']}")
        
        if len(results) > 15:
            print(f"     ... and {len(results) - 15} more patents")
        
        # Show statistics
        page_counts = {}
        countries = {}
        years = {}
        
        for patent in results:
            # Page statistics
            page = patent.get('page', 1)
            page_counts[page] = page_counts.get(page, 0) + 1
            
            # Country statistics
            patent_num = patent['patent_number']
            country = patent_num[:2] if len(patent_num) >= 2 else 'Unknown'
            countries[country] = countries.get(country, 0) + 1
            
            # Year statistics
            pub_date = patent['publication_date']
            if pub_date and len(pub_date) >= 4:
                year = pub_date[:4]
                years[year] = years.get(year, 0) + 1
        
        print(f"\n📊 Statistics:")
        print(f"   Pages: {min(page_counts.keys())} to {max(page_counts.keys())}")
        print(f"   Top countries: {sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]}")
        if years:
            print(f"   Publication years: {min(years.keys())} to {max(years.keys())}")
        
        # Save to CSV
        save_results_to_csv(results)

if __name__ == "__main__":
    test_comprehensive_scraper()