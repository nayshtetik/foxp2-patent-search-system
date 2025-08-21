#!/usr/bin/env python3
"""
WIPO patent collector to get all 3,665 FOXP2 patents using WIPO Global Database
"""

import time
import json
import csv
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus, urlencode
import re

class WIPOPatentCollector:
    """Collect patents using WIPO Global Brand Database and patent search"""
    
    def __init__(self):
        self.results_dir = Path("patent_data/wipo_collection")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # WIPO API endpoints
        self.wipo_search_base = "https://patentscope.wipo.int/search/rest/v1"
        self.wipo_web_base = "https://patentscope.wipo.int/search/en/search.jsf"
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        self.delay = 2  # Delay between requests to be respectful
    
    def search_wipo_api(self, query="FOXP2", start=0, num_results=100):
        """Search WIPO using their REST API"""
        try:
            print(f"   🌐 WIPO API search: start={start}, num={num_results}")
            
            # WIPO PatentScope REST API search
            search_url = f"{self.wipo_search_base}/search"
            
            params = {
                'q': query,
                'start': start,
                'num': num_results,
                'format': 'json'
            }
            
            response = self.session.get(search_url, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ WIPO API: {response.status_code}, data type: {type(data)}")
                    return data
                except json.JSONDecodeError:
                    print(f"   ⚠️ WIPO API: JSON decode failed, trying XML")
                    return self.parse_xml_response(response.text)
            else:
                print(f"   ❌ WIPO API: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ WIPO API failed: {e}")
            
        return None
    
    def parse_xml_response(self, xml_content):
        """Parse XML response from WIPO"""
        try:
            root = ET.fromstring(xml_content)
            patents = []
            
            # Look for patent entries in XML
            for item in root.findall('.//item'):
                patent_data = {}
                
                # Extract basic fields
                for field in ['title', 'description', 'id', 'link']:
                    element = item.find(field)
                    if element is not None:
                        patent_data[field] = element.text
                
                if patent_data:
                    patents.append(patent_data)
            
            return {'patents': patents, 'total': len(patents)}
            
        except ET.ParseError as e:
            print(f"   ❌ XML parsing failed: {e}")
            return None
    
    def search_wipo_web(self, query="FOXP2", page=1):
        """Search WIPO using web interface"""
        try:
            print(f"   🌐 WIPO Web search: page={page}")
            
            # WIPO web search parameters
            params = {
                'query': query,
                'office': 'all',
                'sortOption': 'Relevance',
                'page': page,
                'maxRec': 100
            }
            
            response = self.session.get(self.wipo_web_base, params=params, timeout=15)
            
            if response.status_code == 200:
                patents = self.extract_patents_from_html(response.text, page)
                print(f"   ✅ WIPO Web: Found {len(patents)} patents")
                return patents
            else:
                print(f"   ❌ WIPO Web: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ WIPO Web failed: {e}")
            
        return []
    
    def extract_patents_from_html(self, html_content, page):
        """Extract patent data from WIPO HTML"""
        patents = []
        
        try:
            # Look for patent numbers and titles using regex
            patent_patterns = [
                r'WO/?(\d{4})/(\d{6})',  # WO/2023/123456
                r'PCT/[A-Z]{2}\d{4}/\d{6}',  # PCT/US2023/123456
                r'[A-Z]{2}\d{7,10}[A-Z]\d?',  # Standard format
            ]
            
            all_patent_nums = []
            for pattern in patent_patterns:
                matches = re.findall(pattern, html_content)
                if isinstance(matches[0], tuple) if matches else False:
                    # Handle tuple matches (WO pattern)
                    all_patent_nums.extend([f"WO{m[0]}{m[1]}" for m in matches])
                else:
                    all_patent_nums.extend(matches)
            
            # Look for titles near patent numbers
            title_patterns = [
                r'<title[^>]*>([^<]+)</title>',
                r'<h[1-6][^>]*>([^<]+)</h[1-6]>',
                r'title="([^"]+)"'
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
                    'abstract': "",  # Will be filled later if needed
                    'assignee': "",
                    'publication_date': "",
                    'inventors': [],
                    'raw_text': f"{patent_num} {title}",
                    'page_collected': page,
                    'collection_timestamp': datetime.now().isoformat(),
                    'source': 'wipo_web'
                }
                patents.append(patent_data)
            
        except Exception as e:
            print(f"   ❌ HTML extraction failed: {e}")
        
        return patents
    
    def try_espacenet_api(self, query="FOXP2"):
        """Try European Patent Office Espacenet API"""
        try:
            print(f"   🌐 Trying Espacenet API...")
            
            # EPO Open Patent Services API
            espacenet_url = "https://ops.epo.org/3.2/rest-services/published-data/search"
            
            params = {
                'q': f'txt="{query}"',
                'Range': '1-100'
            }
            
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'Patent Research Tool'
            }
            
            response = self.session.get(espacenet_url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Espacenet: Found data")
                return self.process_espacenet_data(data)
            else:
                print(f"   ❌ Espacenet: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Espacenet failed: {e}")
            
        return []
    
    def process_espacenet_data(self, data):
        """Process Espacenet API response"""
        patents = []
        
        try:
            # Navigate Espacenet JSON structure
            if 'ops:world-patent-data' in data:
                search_result = data['ops:world-patent-data'].get('ops:biblio-search', {})
                results = search_result.get('ops:search-result', {}).get('ops:publication-reference', [])
                
                for result in results:
                    patent_data = self.extract_from_espacenet_result(result)
                    if patent_data:
                        patents.append(patent_data)
            
        except Exception as e:
            print(f"   ❌ Espacenet processing failed: {e}")
        
        return patents
    
    def extract_from_espacenet_result(self, result):
        """Extract patent data from single Espacenet result"""
        try:
            # Extract document ID
            doc_id = result.get('document-id', {})
            patent_number = f"{doc_id.get('country', '')}{doc_id.get('doc-number', '')}{doc_id.get('kind', '')}"
            
            # Extract basic info
            patent_data = {
                'patent_number': patent_number,
                'title': f"Patent {patent_number}",
                'abstract': "",
                'assignee': "",
                'publication_date': doc_id.get('date', ""),
                'inventors': [],
                'raw_text': patent_number,
                'collection_timestamp': datetime.now().isoformat(),
                'source': 'espacenet'
            }
            
            return patent_data
            
        except Exception as e:
            return None
    
    def collect_from_multiple_sources(self, target_patents=3665):
        """Collect patents from multiple WIPO and international sources"""
        
        print("🌍 WIPO & INTERNATIONAL PATENT COLLECTION")
        print("=" * 50)
        print("🎯 Target: 3,665 FOXP2 patents")
        print("🔍 Sources: WIPO API, WIPO Web, Espacenet")
        print()
        
        all_patents = []
        start_time = time.time()
        
        # Method 1: WIPO API search
        print("📡 Method 1: WIPO PatentScope API")
        print("-" * 35)
        
        for start in range(0, min(1000, target_patents), 100):  # Try first 1000 via API
            if len(all_patents) >= target_patents:
                break
                
            print(f"   📄 API batch: {start//100 + 1}/10")
            api_data = self.search_wipo_api(start=start, num_results=100)
            
            if api_data and 'patents' in api_data:
                batch_patents = api_data['patents']
                all_patents.extend(batch_patents)
                print(f"   ✅ Added {len(batch_patents)} patents (total: {len(all_patents)})")
            else:
                print(f"   ⚠️ No data from API batch")
            
            time.sleep(self.delay)
        
        print(f"\n📊 WIPO API Results: {len(all_patents)} patents")
        
        # Method 2: WIPO Web Search
        print("\n🌐 Method 2: WIPO Web Interface")
        print("-" * 35)
        
        web_patents = []
        for page in range(1, min(21, (target_patents//100) + 1)):  # Try 20 pages max
            print(f"   📄 Web page: {page}/20")
            page_patents = self.search_wipo_web(page=page)
            
            if page_patents:
                web_patents.extend(page_patents)
                print(f"   ✅ Added {len(page_patents)} patents (web total: {len(web_patents)})")
            else:
                print(f"   ⚠️ No patents from web page {page}")
                
            time.sleep(self.delay)
        
        print(f"\n📊 WIPO Web Results: {len(web_patents)} patents")
        
        # Method 3: Espacenet API
        print("\n🇪🇺 Method 3: Espacenet API")
        print("-" * 30)
        
        espacenet_patents = self.try_espacenet_api()
        print(f"📊 Espacenet Results: {len(espacenet_patents)} patents")
        
        # Combine all sources
        print(f"\n🔗 COMBINING ALL SOURCES")
        print("-" * 25)
        
        combined_patents = all_patents + web_patents + espacenet_patents
        
        # Remove duplicates based on patent number
        seen = set()
        unique_patents = []
        
        for patent in combined_patents:
            patent_num = patent.get('patent_number', '')
            if patent_num and patent_num not in seen:
                seen.add(patent_num)
                unique_patents.append(patent)
        
        total_time = time.time() - start_time
        
        print(f"📊 Final Results:")
        print(f"   WIPO API: {len(all_patents)}")
        print(f"   WIPO Web: {len(web_patents)}")
        print(f"   Espacenet: {len(espacenet_patents)}")
        print(f"   Combined: {len(combined_patents)}")
        print(f"   Unique: {len(unique_patents)}")
        print(f"   Target: {target_patents}")
        print(f"   Success Rate: {len(unique_patents)/target_patents*100:.1f}%")
        print(f"   Time: {total_time/60:.1f} minutes")
        
        return unique_patents
    
    def save_wipo_results(self, patents):
        """Save WIPO collection results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = self.results_dir / f"wipo_foxp2_patents_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_file = self.results_dir / f"wipo_foxp2_patents_{timestamp}.csv"
        if patents:
            all_keys = set()
            for patent in patents:
                all_keys.update(patent.keys())
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(patents)
        
        print(f"\n💾 WIPO Results Saved:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📊 CSV: {csv_file}")
        
        return json_file, csv_file
    
    def analyze_wipo_patents_for_drug_discovery(self, patents):
        """Analyze WIPO patents for drug discovery relevance"""
        if not patents:
            print("❌ No patents to analyze")
            return []
        
        print(f"\n🔬 DRUG DISCOVERY ANALYSIS OF WIPO PATENTS")
        print("=" * 50)
        print(f"📊 Analyzing {len(patents)} WIPO patents...")
        
        try:
            from improved_drug_analyzer import ImprovedDrugDiscoveryAnalyzer
            
            analyzer = ImprovedDrugDiscoveryAnalyzer()
            
            # Analyze patents for drug discovery relevance
            drug_patents = analyzer.analyze_patents_with_enhanced_content(
                patents, 
                min_relevance=3.0,
                enhance_top_patents=False  # Skip enhancement for now due to different source
            )
            
            # Generate summary
            summary = analyzer.generate_summary_report(drug_patents)
            
            print(f"\n🎯 WIPO DRUG DISCOVERY RESULTS:")
            print(f"   📊 Total analyzed: {len(patents)}")
            print(f"   🎯 Drug discovery relevant: {len(drug_patents)}")
            print(f"   📈 Success rate: {len(drug_patents)/len(patents)*100:.1f}%")
            
            if drug_patents:
                print(f"\n🏆 TOP 10 WIPO DRUG DISCOVERY PATENTS:")
                for i, patent in enumerate(drug_patents[:10], 1):
                    analysis = patent['drug_discovery_analysis']
                    print(f"{i:2d}. {patent['patent_number']} - Score: {analysis.relevance_score:.1f}")
                    print(f"     {patent['title'][:70]}...")
            
            return drug_patents
            
        except ImportError:
            print("⚠️ Drug discovery analyzer not available")
            return patents

def main():
    """Main WIPO collection function"""
    collector = WIPOPatentCollector()
    
    # Collect from WIPO and international sources
    patents = collector.collect_from_multiple_sources(target_patents=3665)
    
    if patents:
        # Save results
        json_file, csv_file = collector.save_wipo_results(patents)
        
        # Analyze for drug discovery
        drug_patents = collector.analyze_wipo_patents_for_drug_discovery(patents)
        
        print(f"\n✅ WIPO COLLECTION COMPLETE!")
        print(f"🌍 Collected {len(patents)} patents from international sources")
        print(f"💊 Found {len(drug_patents)} drug discovery relevant patents")
        
    else:
        print("❌ No patents collected from WIPO sources")

if __name__ == "__main__":
    main()