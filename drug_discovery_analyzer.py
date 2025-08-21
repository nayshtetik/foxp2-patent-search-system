#!/usr/bin/env python3
"""
Comprehensive FOXP2 Patent Drug Discovery Analyzer
Gathers all 3,665 patents and filters for drug discovery relevance
"""

import time
import re
import json
import csv
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from pathlib import Path
from datetime import datetime
import concurrent.futures
from dataclasses import dataclass

@dataclass
class DrugDiscoveryAnalysis:
    """Results of drug discovery relevance analysis"""
    relevance_score: float  # 0-100
    category: str  # e.g., "Target", "Compound", "Biomarker", "Therapeutic"
    confidence: float  # 0-100
    key_terms: List[str]
    reasoning: str

class DrugDiscoveryPatentAnalyzer:
    """Comprehensive analyzer for FOXP2 patents with drug discovery focus"""
    
    def __init__(self):
        self.results_dir = Path("patent_data/drug_discovery_analysis")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Drug discovery keywords and patterns
        self.drug_discovery_keywords = {
            'therapeutic_targets': [
                'therapeutic target', 'drug target', 'target protein', 'target identification',
                'target validation', 'binding site', 'active site', 'receptor', 'enzyme',
                'protein complex', 'pathway', 'mechanism of action'
            ],
            'compounds_drugs': [
                'small molecule', 'compound', 'drug', 'pharmaceutical', 'inhibitor',
                'agonist', 'antagonist', 'modulator', 'ligand', 'chemical entity',
                'therapeutic compound', 'active ingredient', 'drug candidate',
                'lead compound', 'optimization', 'structure-activity relationship'
            ],
            'biomarkers': [
                'biomarker', 'diagnostic marker', 'prognostic marker', 'predictive marker',
                'companion diagnostic', 'molecular marker', 'protein marker',
                'gene expression marker', 'therapeutic monitoring'
            ],
            'therapeutics': [
                'treatment', 'therapy', 'therapeutic', 'medicine', 'cure',
                'intervention', 'clinical trial', 'efficacy', 'safety',
                'dosage', 'administration', 'pharmaceutical composition'
            ],
            'drug_development': [
                'drug development', 'drug discovery', 'preclinical', 'clinical development',
                'pharmacokinetics', 'pharmacodynamics', 'toxicity', 'ADMET',
                'formulation', 'delivery system', 'controlled release'
            ],
            'diseases': [
                'autism', 'speech disorder', 'language disorder', 'developmental disorder',
                'neurological disorder', 'neurodevelopmental', 'cognitive disorder',
                'psychiatric disorder', 'mental health', 'brain disorder'
            ]
        }
        
        # Exclusion patterns (patents likely NOT drug discovery)
        self.exclusion_patterns = [
            'diagnostic kit', 'sequencing method', 'pcr method', 'detection method',
            'genetic testing', 'screening method', 'research tool', 'laboratory method',
            'bioinformatics', 'software', 'algorithm', 'database', 'computer system'
        ]
    
    def gather_all_foxp2_patents(self, max_patents: int = 3665) -> List[Dict[str, Any]]:
        """Gather all FOXP2 patents with enhanced data extraction"""
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
            all_patents = []
            seen_patents = set()
            
            try:
                base_url = f"https://patents.google.com/?q={quote_plus('FOXP2')}"
                results_per_page = 100  # Maximum allowed by Google Patents
                max_pages = (max_patents // results_per_page) + 1
                
                print(f"🧬 Starting comprehensive FOXP2 patent collection")
                print(f"🎯 Target: {max_patents} patents across {max_pages} pages")
                print(f"📊 Using {results_per_page} results per page")
                
                for page_num in range(1, max_pages + 1):
                    if len(all_patents) >= max_patents:
                        break
                    
                    search_url = f"{base_url}&num={results_per_page}&page={page_num}"
                    print(f"\n📄 Page {page_num}/{max_pages}: {search_url}")
                    
                    driver.get(search_url)
                    time.sleep(3)
                    
                    # Wait for results
                    try:
                        WebDriverWait(driver, 15).until(
                            lambda d: d.find_elements(By.TAG_NAME, 'search-result-item')
                        )
                    except:
                        print(f"   ⚠️ Timeout on page {page_num}")
                        continue
                    
                    search_items = driver.find_elements(By.TAG_NAME, 'search-result-item')
                    print(f"   📊 Found {len(search_items)} items on page")
                    
                    page_results = 0
                    for i, item in enumerate(search_items):
                        try:
                            patent_data = self._extract_enhanced_patent_data(item, page_num, i)
                            if patent_data and patent_data['patent_number'] not in seen_patents:
                                seen_patents.add(patent_data['patent_number'])
                                all_patents.append(patent_data)
                                page_results += 1
                                
                                if len(all_patents) >= max_patents:
                                    break
                        except Exception as e:
                            continue
                    
                    print(f"   ✅ Extracted {page_results} patents (Total: {len(all_patents)})")
                    
                    if page_results == 0:
                        print(f"   ⚠️ No new results, stopping at page {page_num}")
                        break
                    
                    # Progress save every 10 pages
                    if page_num % 10 == 0:
                        self._save_patents_checkpoint(all_patents, page_num)
                    
                    time.sleep(1)  # Rate limiting
                
                print(f"\n🎯 Collection complete: {len(all_patents)} patents gathered")
                return all_patents
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"❌ Error gathering patents: {e}")
            return []
    
    def _extract_enhanced_patent_data(self, item, page_num: int, item_index: int) -> Optional[Dict[str, Any]]:
        """Extract enhanced patent data including abstract and detailed metadata"""
        try:
            text_content = item.text
            
            # Extract patent number
            patent_patterns = [
                r'\b([A-Z]{2}\d{7,10}[A-Z]?\d?)\b',
                r'\b(WO\d{4}/\d{6})\b',
                r'\b(US\d{7,10}[A-Z]\d?)\b'
            ]
            
            patent_number = ''
            for pattern in patent_patterns:
                match = re.search(pattern, text_content)
                if match:
                    patent_number = match.group(1)
                    break
            
            if not patent_number:
                return None
            
            # Extract title
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            title = ''
            for line in lines:
                if (len(line) > 15 and 
                    line != patent_number and 
                    not line.isdigit() and
                    not re.match(r'^\d{4}-\d{2}-\d{2}$', line) and
                    not re.match(r'^[A-Z]{2,5}$', line)):
                    title = line
                    break
            
            # Extract metadata
            pub_date = ''
            filing_date = ''
            assignees = []
            inventors = []
            
            # Look for dates
            pub_match = re.search(r'Published (\d{4}-\d{2}-\d{2})', text_content)
            if pub_match:
                pub_date = pub_match.group(1)
            
            filed_match = re.search(r'Filed (\d{4}-\d{2}-\d{2})', text_content)
            if filed_match:
                filing_date = filed_match.group(1)
            
            # Look for assignees/companies
            for line in lines:
                if any(indicator in line.lower() for indicator in ['inc', 'corp', 'ltd', 'company', 'university', 'foundation', 'institute']):
                    assignees.append(line)
                    break
            
            # Basic abstract extraction (from visible text)
            abstract = ''
            long_lines = [line for line in lines if len(line) > 50]
            if long_lines:
                for line in long_lines:
                    if not any(skip in line.lower() for skip in ['patent', 'filed', 'published', 'priority']):
                        abstract = line[:500]  # Limit length
                        break
            
            return {
                'patent_number': patent_number,
                'title': title[:200] if title else f"Patent {patent_number}",
                'abstract': abstract,
                'inventors': inventors,
                'assignees': assignees,
                'publication_date': pub_date,
                'filing_date': filing_date,
                'url': f"https://patents.google.com/patent/{patent_number}",
                'pdf_link': f"https://patents.google.com/patent/{patent_number}/pdf",
                'page': page_num,
                'item_index': item_index,
                'raw_text': text_content,
                'collection_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return None
    
    def analyze_drug_discovery_relevance(self, patent: Dict[str, Any]) -> DrugDiscoveryAnalysis:
        """Analyze a patent for drug discovery relevance using keyword analysis and AI"""
        text_to_analyze = f"{patent.get('title', '')} {patent.get('abstract', '')}".lower()
        
        # Calculate relevance scores by category
        category_scores = {}
        found_terms = {}
        
        for category, keywords in self.drug_discovery_keywords.items():
            score = 0
            terms = []
            for keyword in keywords:
                if keyword.lower() in text_to_analyze:
                    score += 1
                    terms.append(keyword)
            
            category_scores[category] = score
            found_terms[category] = terms
        
        # Check for exclusion patterns
        exclusion_penalty = 0
        for pattern in self.exclusion_patterns:
            if pattern.lower() in text_to_analyze:
                exclusion_penalty += 10
        
        # Calculate overall relevance score
        total_keywords_found = sum(category_scores.values())
        max_possible_score = sum(len(keywords) for keywords in self.drug_discovery_keywords.values())
        
        base_score = (total_keywords_found / max_possible_score) * 100
        relevance_score = max(0, base_score - exclusion_penalty)
        
        # Determine primary category
        primary_category = max(category_scores.items(), key=lambda x: x[1])[0] if total_keywords_found > 0 else "unknown"
        
        # Determine confidence based on number of matches and abstract quality
        confidence = min(100, (total_keywords_found * 10) + (50 if patent.get('abstract') else 0))
        
        # Create reasoning
        all_found_terms = []
        for terms_list in found_terms.values():
            all_found_terms.extend(terms_list)
        
        reasoning = f"Found {total_keywords_found} drug discovery keywords. "
        if all_found_terms:
            reasoning += f"Key terms: {', '.join(all_found_terms[:5])}. "
        if exclusion_penalty > 0:
            reasoning += f"Penalty applied for research/diagnostic patterns. "
        reasoning += f"Primary category: {primary_category}."
        
        return DrugDiscoveryAnalysis(
            relevance_score=relevance_score,
            category=primary_category,
            confidence=confidence,
            key_terms=all_found_terms,
            reasoning=reasoning
        )
    
    def analyze_with_openai(self, patent: Dict[str, Any]) -> Optional[DrugDiscoveryAnalysis]:
        """Enhanced analysis using OpenAI API for better accuracy"""
        try:
            import openai
            import os
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return None
            
            client = openai.OpenAI(api_key=api_key)
            
            prompt = f"""
            Analyze this patent for drug discovery relevance:
            
            Title: {patent.get('title', '')}
            Abstract: {patent.get('abstract', '')}
            Patent Number: {patent.get('patent_number', '')}
            
            Please analyze this patent and provide:
            1. Drug discovery relevance score (0-100)
            2. Primary category (Target/Compound/Biomarker/Therapeutic/Other)
            3. Confidence level (0-100)
            4. Key terms that indicate drug discovery relevance
            5. Brief reasoning
            
            Focus on: therapeutic targets, drug compounds, biomarkers, treatments, pharmaceutical compositions, and clinical applications.
            
            Respond in JSON format:
            {{
                "relevance_score": <0-100>,
                "category": "<category>",
                "confidence": <0-100>,
                "key_terms": ["term1", "term2"],
                "reasoning": "<brief explanation>"
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return DrugDiscoveryAnalysis(
                relevance_score=float(result.get('relevance_score', 0)),
                category=result.get('category', 'unknown'),
                confidence=float(result.get('confidence', 0)),
                key_terms=result.get('key_terms', []),
                reasoning=result.get('reasoning', '')
            )
            
        except Exception as e:
            print(f"⚠️ OpenAI analysis failed: {e}")
            return None
    
    def filter_drug_discovery_patents(self, patents: List[Dict[str, Any]], 
                                     min_relevance: float = 30.0) -> List[Dict[str, Any]]:
        """Filter patents for drug discovery relevance"""
        print(f"\n🔬 Analyzing {len(patents)} patents for drug discovery relevance...")
        
        drug_discovery_patents = []
        
        # Analyze patents in parallel for speed
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_patent = {
                executor.submit(self._analyze_single_patent, patent): patent 
                for patent in patents
            }
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_patent)):
                patent = future_to_patent[future]
                try:
                    analysis = future.result()
                    if analysis and analysis.relevance_score >= min_relevance:
                        patent['drug_discovery_analysis'] = analysis
                        drug_discovery_patents.append(patent)
                        
                        if len(drug_discovery_patents) % 10 == 0:
                            print(f"   ✅ Found {len(drug_discovery_patents)} relevant patents so far...")
                
                except Exception as e:
                    continue
                
                if (i + 1) % 100 == 0:
                    print(f"   📊 Processed {i + 1}/{len(patents)} patents")
        
        print(f"🎯 Found {len(drug_discovery_patents)} drug discovery relevant patents")
        return drug_discovery_patents
    
    def _analyze_single_patent(self, patent: Dict[str, Any]) -> Optional[DrugDiscoveryAnalysis]:
        """Analyze a single patent with fallback methods"""
        # Try OpenAI analysis first
        ai_analysis = self.analyze_with_openai(patent)
        if ai_analysis:
            return ai_analysis
        
        # Fallback to keyword analysis
        return self.analyze_drug_discovery_relevance(patent)
    
    def _save_patents_checkpoint(self, patents: List[Dict[str, Any]], page_num: int):
        """Save progress checkpoint"""
        checkpoint_file = self.results_dir / f"checkpoint_page_{page_num}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, default=str)
        print(f"   💾 Saved checkpoint: {len(patents)} patents")
    
    def save_drug_discovery_results(self, patents: List[Dict[str, Any]], filename: str = "foxp2_drug_discovery"):
        """Save filtered drug discovery patents with analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON
        json_file = self.results_dir / f"{filename}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, default=str)
        
        # Save CSV summary
        csv_file = self.results_dir / f"{filename}_summary_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Patent Number', 'Title', 'Relevance Score', 'Category', 
                'Confidence', 'Key Terms', 'Publication Date', 'Assignees', 'URL'
            ])
            
            for patent in patents:
                analysis = patent.get('drug_discovery_analysis')
                writer.writerow([
                    patent.get('patent_number', ''),
                    patent.get('title', '')[:100],
                    analysis.relevance_score if analysis else 0,
                    analysis.category if analysis else '',
                    analysis.confidence if analysis else 0,
                    ', '.join(analysis.key_terms[:5]) if analysis else '',
                    patent.get('publication_date', ''),
                    ', '.join(patent.get('assignees', []))[:100],
                    patent.get('url', '')
                ])
        
        print(f"💾 Saved results to:")
        print(f"   📄 Detailed: {json_file}")
        print(f"   📊 Summary: {csv_file}")
        
        return json_file, csv_file
    
    def generate_summary_report(self, patents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics and insights"""
        if not patents:
            return {}
        
        # Category distribution
        categories = {}
        relevance_scores = []
        key_terms_count = {}
        assignees_count = {}
        years = {}
        
        for patent in patents:
            analysis = patent.get('drug_discovery_analysis')
            if analysis:
                # Categories
                cat = analysis.category
                categories[cat] = categories.get(cat, 0) + 1
                relevance_scores.append(analysis.relevance_score)
                
                # Key terms
                for term in analysis.key_terms:
                    key_terms_count[term] = key_terms_count.get(term, 0) + 1
            
            # Assignees
            for assignee in patent.get('assignees', []):
                assignees_count[assignee] = assignees_count.get(assignee, 0) + 1
            
            # Years
            pub_date = patent.get('publication_date', '')
            if pub_date and len(pub_date) >= 4:
                year = pub_date[:4]
                years[year] = years.get(year, 0) + 1
        
        summary = {
            'total_patents': len(patents),
            'average_relevance_score': sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0,
            'category_distribution': dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
            'top_key_terms': dict(sorted(key_terms_count.items(), key=lambda x: x[1], reverse=True)[:20]),
            'top_assignees': dict(sorted(assignees_count.items(), key=lambda x: x[1], reverse=True)[:10]),
            'publication_years': dict(sorted(years.items(), key=lambda x: x[0], reverse=True)),
            'high_relevance_count': len([p for p in patents if p.get('drug_discovery_analysis') and p['drug_discovery_analysis'].relevance_score > 70])
        }
        
        return summary

def run_comprehensive_analysis(max_patents: int = 500, min_relevance: float = 30.0):
    """Run the complete drug discovery analysis pipeline"""
    analyzer = DrugDiscoveryPatentAnalyzer()
    
    print("🧬 FOXP2 Drug Discovery Patent Analysis Pipeline")
    print("=" * 60)
    
    # Step 1: Gather all patents
    print("\n📥 Step 1: Gathering FOXP2 patents...")
    all_patents = analyzer.gather_all_foxp2_patents(max_patents)
    
    if not all_patents:
        print("❌ Failed to gather patents")
        return
    
    # Step 2: Filter for drug discovery relevance
    print(f"\n🔬 Step 2: Analyzing for drug discovery relevance (min score: {min_relevance})...")
    drug_patents = analyzer.filter_drug_discovery_patents(all_patents, min_relevance)
    
    # Step 3: Generate reports
    print(f"\n📊 Step 3: Generating analysis report...")
    summary = analyzer.generate_summary_report(drug_patents)
    
    # Step 4: Save results
    json_file, csv_file = analyzer.save_drug_discovery_results(drug_patents)
    
    # Step 5: Display summary
    print(f"\n🎯 ANALYSIS COMPLETE")
    print("=" * 40)
    print(f"📊 Total patents analyzed: {len(all_patents)}")
    print(f"🎯 Drug discovery relevant: {len(drug_patents)}")
    print(f"📈 Success rate: {len(drug_patents)/len(all_patents)*100:.1f}%")
    print(f"⭐ High relevance (>70): {summary.get('high_relevance_count', 0)}")
    
    if summary.get('category_distribution'):
        print(f"\n📋 Top categories:")
        for cat, count in list(summary['category_distribution'].items())[:5]:
            print(f"   {cat}: {count} patents")
    
    if summary.get('top_key_terms'):
        print(f"\n🔑 Top terms:")
        for term, count in list(summary['top_key_terms'].items())[:10]:
            print(f"   {term}: {count} occurrences")
    
    return drug_patents, summary

if __name__ == "__main__":
    # Start with a test run
    drug_patents, summary = run_comprehensive_analysis(max_patents=200, min_relevance=25.0)