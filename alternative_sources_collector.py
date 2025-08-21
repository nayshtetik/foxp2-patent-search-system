#!/usr/bin/env python3
"""
Alternative patent sources collector - try USPTO, Lens.org, and other public databases
"""

import time
import json
import csv
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus, urlencode
import re

class AlternativePatentCollector:
    """Collect patents from alternative public sources"""
    
    def __init__(self):
        self.results_dir = Path("patent_data/alternative_sources")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.delay = 2
    
    def try_uspto_api(self, query="FOXP2", start=0, rows=100):
        """Try USPTO PatentsView API"""
        try:
            print(f"   🇺🇸 USPTO API: start={start}, rows={rows}")
            
            # USPTO PatentsView API
            uspto_url = "https://api.patentsview.org/patents/query"
            
            # Search in patent title and abstract
            search_query = {
                "_or": [
                    {"patent_title": query},
                    {"patent_abstract": query}
                ]
            }
            
            payload = {
                "q": search_query,
                "f": [
                    "patent_number",
                    "patent_title", 
                    "patent_abstract",
                    "patent_date",
                    "assignee_organization",
                    "inventor_last_name",
                    "inventor_first_name"
                ],
                "o": {"page": start//rows + 1, "per_page": min(rows, 1000)},
                "s": [{"patent_date": "desc"}]
            }
            
            response = self.session.post(uspto_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('count', 0) > 0:
                    patents = data.get('patents', [])
                    print(f"   ✅ USPTO API: Found {len(patents)} patents")
                    return self.process_uspto_patents(patents)
                else:
                    print(f"   ⚠️ USPTO API: No patents found")
            else:
                print(f"   ❌ USPTO API: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ USPTO API failed: {e}")
            
        return []
    
    def process_uspto_patents(self, uspto_patents):
        """Process USPTO API response"""
        patents = []
        
        for patent_data in uspto_patents:
            try:
                # Extract inventors
                inventors = []
                if patent_data.get('inventors'):
                    for inventor in patent_data['inventors']:
                        name = f"{inventor.get('inventor_first_name', '')} {inventor.get('inventor_last_name', '')}".strip()
                        if name:
                            inventors.append(name)
                
                # Extract assignees
                assignees = []
                if patent_data.get('assignees'):
                    for assignee in patent_data['assignees']:
                        org = assignee.get('assignee_organization', '')
                        if org:
                            assignees.append(org)
                
                patent = {
                    'patent_number': patent_data.get('patent_number', ''),
                    'title': patent_data.get('patent_title', ''),
                    'abstract': patent_data.get('patent_abstract', ''),
                    'assignee': ', '.join(assignees),
                    'publication_date': patent_data.get('patent_date', ''),
                    'inventors': inventors,
                    'raw_text': f"{patent_data.get('patent_title', '')} {patent_data.get('patent_abstract', '')}",
                    'collection_timestamp': datetime.now().isoformat(),
                    'source': 'uspto_api'
                }
                patents.append(patent)
                
            except Exception as e:
                print(f"   ⚠️ Failed to process USPTO patent: {e}")
                continue
        
        return patents
    
    def try_lens_org_api(self, query="FOXP2", offset=0, size=100):
        """Try Lens.org patent search API"""
        try:
            print(f"   🔍 Lens.org API: offset={offset}, size={size}")
            
            # Lens.org patent search (public endpoint)
            lens_url = "https://www.lens.org/lens/search/patent/structured"
            
            # Simple query structure
            params = {
                'q': query,
                'n': size,
                's': offset,
                'l': 'en'
            }
            
            # Add specific headers for Lens.org
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Patent Research Tool 1.0',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(lens_url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print(f"   ✅ Lens.org: HTTP 200, checking data...")
                
                # Try to extract patent info from response
                patents = self.extract_from_lens_response(response.text)
                print(f"   📊 Lens.org: Extracted {len(patents)} patents")
                return patents
            else:
                print(f"   ❌ Lens.org: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Lens.org failed: {e}")
            
        return []
    
    def extract_from_lens_response(self, response_text):
        """Extract patent data from Lens.org response"""
        patents = []
        
        try:
            # Look for patent numbers in the response
            patent_patterns = [
                r'[A-Z]{2}[\d]{6,12}[A-Z]?\d?',  # General pattern
                r'US[\d]{7,10}[A-Z]?\d?',        # US patents
                r'EP[\d]{7,10}[A-Z]?\d?',        # EP patents
                r'WO[\d]{4}[\d]{6}[A-Z]?\d?',    # WO patents
            ]
            
            found_patents = []
            for pattern in patent_patterns:
                matches = re.findall(pattern, response_text)
                found_patents.extend(matches)
            
            # Remove duplicates while preserving order
            unique_patents = []
            seen = set()
            for patent in found_patents:
                if patent not in seen:
                    seen.add(patent)
                    unique_patents.append(patent)
            
            # Create patent entries
            for patent_num in unique_patents[:100]:  # Limit to 100
                patent = {
                    'patent_number': patent_num,
                    'title': f"Patent {patent_num}",  # Basic title
                    'abstract': "",
                    'assignee': "",
                    'publication_date': "",
                    'inventors': [],
                    'raw_text': patent_num,
                    'collection_timestamp': datetime.now().isoformat(),
                    'source': 'lens_org'
                }
                patents.append(patent)
                
        except Exception as e:
            print(f"   ❌ Lens extraction failed: {e}")
        
        return patents
    
    def try_pubmed_patents(self, query="FOXP2"):
        """Try to find patents referenced in PubMed literature"""
        try:
            print(f"   📚 PubMed patent references...")
            
            # NCBI E-utilities API
            pubmed_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            
            params = {
                'db': 'pubmed',
                'term': f'{query} AND patent',
                'retmax': 200,
                'format': 'json'
            }
            
            response = self.session.get(pubmed_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                pmids = data.get('esearchresult', {}).get('idlist', [])
                
                if pmids:
                    print(f"   ✅ PubMed: Found {len(pmids)} articles mentioning patents")
                    return self.extract_patents_from_pubmed(pmids[:20])  # Limit to first 20
                else:
                    print(f"   ⚠️ PubMed: No articles found")
            else:
                print(f"   ❌ PubMed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ PubMed failed: {e}")
            
        return []
    
    def extract_patents_from_pubmed(self, pmids):
        """Extract patent references from PubMed articles"""
        patents = []
        
        try:
            # Fetch abstracts for the PMIDs
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            
            params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'rettype': 'abstract',
                'retmode': 'text'
            }
            
            response = self.session.get(fetch_url, params=params, timeout=30)
            
            if response.status_code == 200:
                text = response.text
                
                # Look for patent numbers in the abstracts
                patent_patterns = [
                    r'US[\s]?[\d]{7,10}[A-Z]?\d?',
                    r'EP[\s]?[\d]{7,10}[A-Z]?\d?', 
                    r'WO[\s]?[\d]{4}[\d]{6}[A-Z]?\d?',
                    r'Patent[\s]+No\.?[\s]*[\d,]+',
                ]
                
                found_patents = []
                for pattern in patent_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    found_patents.extend(matches)
                
                # Clean and create patent entries
                for patent_ref in found_patents[:50]:
                    clean_ref = re.sub(r'[^\w]', '', patent_ref)
                    if len(clean_ref) > 5:  # Valid patent number
                        patent = {
                            'patent_number': clean_ref,
                            'title': f"Patent {clean_ref} (from literature)",
                            'abstract': "",
                            'assignee': "",
                            'publication_date': "",
                            'inventors': [],
                            'raw_text': patent_ref,
                            'collection_timestamp': datetime.now().isoformat(),
                            'source': 'pubmed_refs'
                        }
                        patents.append(patent)
                
        except Exception as e:
            print(f"   ❌ PubMed extraction failed: {e}")
        
        return patents
    
    def try_crossref_patents(self, query="FOXP2"):
        """Try Crossref API for patent references"""
        try:
            print(f"   📖 Crossref patent references...")
            
            crossref_url = "https://api.crossref.org/works"
            
            params = {
                'query': f'{query} patent',
                'rows': 100,
                'filter': 'type:patent'
            }
            
            response = self.session.get(crossref_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                works = data.get('message', {}).get('items', [])
                
                patents = []
                for work in works:
                    if work.get('type') == 'patent':
                        patent = {
                            'patent_number': work.get('DOI', '').replace('10.', ''),
                            'title': ' '.join(work.get('title', [])),
                            'abstract': work.get('abstract', ''),
                            'assignee': '',
                            'publication_date': '',
                            'inventors': [],
                            'raw_text': ' '.join(work.get('title', [])),
                            'collection_timestamp': datetime.now().isoformat(),
                            'source': 'crossref'
                        }
                        patents.append(patent)
                
                print(f"   ✅ Crossref: Found {len(patents)} patents")
                return patents
            else:
                print(f"   ❌ Crossref: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Crossref failed: {e}")
            
        return []
    
    def collect_from_alternative_sources(self, target_patents=3665):
        """Collect patents from all alternative sources"""
        
        print("🔄 ALTERNATIVE PATENT SOURCES COLLECTION")
        print("=" * 50)
        print("🎯 Target: 3,665 FOXP2 patents")
        print("🔍 Sources: USPTO, Lens.org, PubMed, Crossref")
        print()
        
        all_patents = []
        start_time = time.time()
        
        # Method 1: USPTO PatentsView API
        print("🇺🇸 Method 1: USPTO PatentsView API")
        print("-" * 35)
        
        uspto_patents = []
        for start in range(0, min(2000, target_patents), 100):
            if len(uspto_patents) >= 1000:  # Limit USPTO to 1000
                break
                
            batch_patents = self.try_uspto_api(start=start, rows=100)
            if batch_patents:
                uspto_patents.extend(batch_patents)
                print(f"   📊 USPTO batch {start//100 + 1}: +{len(batch_patents)} (total: {len(uspto_patents)})")
            else:
                print(f"   ⚠️ USPTO batch {start//100 + 1}: No patents")
                break  # Stop if no more results
            
            time.sleep(self.delay)
        
        print(f"📊 USPTO Results: {len(uspto_patents)} patents")
        all_patents.extend(uspto_patents)
        
        # Method 2: Lens.org
        print(f"\n🔍 Method 2: Lens.org")
        print("-" * 25)
        
        lens_patents = []
        for offset in range(0, min(1000, target_patents), 100):
            batch_patents = self.try_lens_org_api(offset=offset, size=100)
            if batch_patents:
                lens_patents.extend(batch_patents)
                print(f"   📊 Lens batch {offset//100 + 1}: +{len(batch_patents)} (total: {len(lens_patents)})")
            else:
                print(f"   ⚠️ Lens batch {offset//100 + 1}: No patents")
                break
            
            time.sleep(self.delay)
        
        print(f"📊 Lens.org Results: {len(lens_patents)} patents")
        all_patents.extend(lens_patents)
        
        # Method 3: PubMed patent references
        print(f"\n📚 Method 3: PubMed Patent References")
        print("-" * 40)
        
        pubmed_patents = self.try_pubmed_patents()
        print(f"📊 PubMed Results: {len(pubmed_patents)} patents")
        all_patents.extend(pubmed_patents)
        
        # Method 4: Crossref
        print(f"\n📖 Method 4: Crossref")
        print("-" * 20)
        
        crossref_patents = self.try_crossref_patents()
        print(f"📊 Crossref Results: {len(crossref_patents)} patents")
        all_patents.extend(crossref_patents)
        
        # Remove duplicates
        print(f"\n🔗 COMBINING ALL SOURCES")
        print("-" * 25)
        
        seen = set()
        unique_patents = []
        
        for patent in all_patents:
            patent_num = patent.get('patent_number', '')
            if patent_num and patent_num not in seen:
                seen.add(patent_num)
                unique_patents.append(patent)
        
        total_time = time.time() - start_time
        
        print(f"📊 Final Results:")
        print(f"   USPTO: {len(uspto_patents)}")
        print(f"   Lens.org: {len(lens_patents)}")
        print(f"   PubMed: {len(pubmed_patents)}")
        print(f"   Crossref: {len(crossref_patents)}")
        print(f"   Combined: {len(all_patents)}")
        print(f"   Unique: {len(unique_patents)}")
        print(f"   Target: {target_patents}")
        print(f"   Success Rate: {len(unique_patents)/target_patents*100:.1f}%")
        print(f"   Time: {total_time/60:.1f} minutes")
        
        return unique_patents
    
    def save_alternative_results(self, patents):
        """Save alternative sources results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = self.results_dir / f"alternative_foxp2_patents_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_file = self.results_dir / f"alternative_foxp2_patents_{timestamp}.csv"
        if patents:
            all_keys = set()
            for patent in patents:
                all_keys.update(patent.keys())
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(patents)
        
        print(f"\n💾 Alternative Sources Results Saved:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📊 CSV: {csv_file}")
        
        return json_file, csv_file

def main():
    """Main alternative sources collection function"""
    collector = AlternativePatentCollector()
    
    # Collect from alternative sources
    patents = collector.collect_from_alternative_sources(target_patents=3665)
    
    if patents:
        # Save results
        json_file, csv_file = collector.save_alternative_results(patents)
        
        print(f"\n✅ ALTERNATIVE SOURCES COLLECTION COMPLETE!")
        print(f"🔍 Collected {len(patents)} patents from alternative sources")
        print(f"📊 Ready for drug discovery analysis")
        
        return patents
    else:
        print("❌ No patents collected from alternative sources")
        return []

if __name__ == "__main__":
    main()