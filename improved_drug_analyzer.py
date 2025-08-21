#!/usr/bin/env python3
"""
Improved drug discovery analyzer with better scoring and enhanced patent content extraction
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
from drug_discovery_analyzer import DrugDiscoveryPatentAnalyzer, DrugDiscoveryAnalysis

class ImprovedDrugDiscoveryAnalyzer(DrugDiscoveryPatentAnalyzer):
    """Enhanced analyzer with improved scoring and content extraction"""
    
    def __init__(self):
        super().__init__()
        
        # Enhanced keyword sets with more variations
        self.drug_discovery_keywords = {
            'therapeutic_targets': [
                'therapeutic target', 'drug target', 'target protein', 'target identification',
                'target validation', 'binding site', 'active site', 'receptor', 'enzyme',
                'protein complex', 'pathway', 'mechanism of action', 'molecular target',
                'protein interaction', 'binding affinity', 'target selectivity'
            ],
            'compounds_drugs': [
                'small molecule', 'compound', 'drug', 'pharmaceutical', 'inhibitor',
                'agonist', 'antagonist', 'modulator', 'ligand', 'chemical entity',
                'therapeutic compound', 'active ingredient', 'drug candidate',
                'lead compound', 'optimization', 'structure-activity relationship',
                'medicament', 'active compound', 'chemical compound', 'agent',
                'composition', 'formulation', 'substance'
            ],
            'biomarkers': [
                'biomarker', 'diagnostic marker', 'prognostic marker', 'predictive marker',
                'companion diagnostic', 'molecular marker', 'protein marker',
                'gene expression marker', 'therapeutic monitoring', 'indicator',
                'signature', 'profile', 'panel'
            ],
            'therapeutics': [
                'treatment', 'therapy', 'therapeutic', 'medicine', 'cure',
                'intervention', 'clinical trial', 'efficacy', 'safety',
                'dosage', 'administration', 'pharmaceutical composition',
                'medicinal', 'therapeutic method', 'medical treatment', 'remedy'
            ],
            'drug_development': [
                'drug development', 'drug discovery', 'preclinical', 'clinical development',
                'pharmacokinetics', 'pharmacodynamics', 'toxicity', 'ADMET',
                'formulation', 'delivery system', 'controlled release',
                'pharmaceutical development', 'drug design', 'lead optimization'
            ],
            'diseases': [
                'autism', 'speech disorder', 'language disorder', 'developmental disorder',
                'neurological disorder', 'neurodevelopmental', 'cognitive disorder',
                'psychiatric disorder', 'mental health', 'brain disorder',
                'neuropsychiatric', 'neurocognitive', 'behavioral disorder'
            ],
            'mechanisms': [
                'modulation', 'regulation', 'activation', 'inhibition', 'expression',
                'function', 'activity', 'signaling', 'cascade', 'network'
            ]
        }
        
        # Reduce exclusion patterns to be less restrictive
        self.exclusion_patterns = [
            'sequencing method only', 'pcr method only', 'detection method only',
            'bioinformatics tool', 'software algorithm', 'database system'
        ]
        
        # Add scoring weights
        self.category_weights = {
            'compounds_drugs': 3.0,      # Highest priority
            'therapeutics': 2.5,
            'therapeutic_targets': 2.0,
            'drug_development': 1.8,
            'biomarkers': 1.5,
            'diseases': 1.2,
            'mechanisms': 1.0
        }
    
    def analyze_drug_discovery_relevance(self, patent: Dict[str, Any]) -> DrugDiscoveryAnalysis:
        """Enhanced analysis with improved scoring"""
        
        # Combine title, abstract, and available text
        title = patent.get('title', '').lower()
        abstract = patent.get('abstract', '').lower() 
        raw_text = patent.get('raw_text', '').lower()
        
        # Weight different text sources
        text_sources = [
            (title, 3.0),      # Title is most important
            (abstract, 2.0),   # Abstract is very important
            (raw_text, 1.0)    # Raw text provides context
        ]
        
        # Calculate weighted scores by category
        category_scores = {}
        found_terms = {}
        total_weighted_score = 0
        
        for category, keywords in self.drug_discovery_keywords.items():
            score = 0
            terms = []
            
            for text, weight in text_sources:
                for keyword in keywords:
                    if keyword.lower() in text:
                        score += weight
                        if keyword not in terms:
                            terms.append(keyword)
            
            # Apply category weight
            weighted_score = score * self.category_weights.get(category, 1.0)
            category_scores[category] = weighted_score
            found_terms[category] = terms
            total_weighted_score += weighted_score
        
        # Check for exclusion patterns (reduced penalty)
        exclusion_penalty = 0
        full_text = f"{title} {abstract} {raw_text}"
        for pattern in self.exclusion_patterns:
            if pattern.lower() in full_text:
                exclusion_penalty += 5  # Reduced from 10
        
        # Calculate relevance score (0-100 scale)
        # Max possible score calculation
        max_possible = sum(
            len(keywords) * 3.0 * self.category_weights.get(category, 1.0)  # Assuming title matches
            for category, keywords in self.drug_discovery_keywords.items()
        )
        
        base_score = (total_weighted_score / max_possible) * 100 if max_possible > 0 else 0
        relevance_score = max(0, base_score - exclusion_penalty)
        
        # Determine primary category
        primary_category = "unknown"
        if category_scores:
            primary_category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence
        all_found_terms = []
        for terms_list in found_terms.values():
            all_found_terms.extend(terms_list)
        
        confidence = min(100, len(all_found_terms) * 8 + (30 if abstract else 0))
        
        # Enhanced reasoning
        reasoning = f"Analyzed title, abstract, and content. "
        reasoning += f"Weighted score: {total_weighted_score:.1f}. "
        reasoning += f"Found {len(all_found_terms)} drug discovery terms. "
        if exclusion_penalty > 0:
            reasoning += f"Applied {exclusion_penalty} point penalty. "
        reasoning += f"Primary focus: {primary_category}."
        
        return DrugDiscoveryAnalysis(
            relevance_score=relevance_score,
            category=primary_category,
            confidence=confidence,
            key_terms=all_found_terms[:10],  # Limit to top 10
            reasoning=reasoning
        )
    
    def extract_enhanced_patent_content(self, patent_number: str) -> Dict[str, Any]:
        """Extract detailed content from individual patent page"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from bs4 import BeautifulSoup
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                patent_url = f"https://patents.google.com/patent/{patent_number}"
                print(f"   🔍 Extracting content from: {patent_number}")
                
                driver.get(patent_url)
                time.sleep(3)
                
                # Wait for patent content to load
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "patent-text"))
                    )
                except:
                    pass  # Continue anyway
                
                # Get page source and parse with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Extract abstract
                abstract = ""
                abstract_selectors = [
                    'section[data-proto="ABSTRACT"]',
                    '.abstract',
                    '[data-proto="ABSTRACT"]'
                ]
                
                for selector in abstract_selectors:
                    abstract_elem = soup.select_one(selector)
                    if abstract_elem:
                        abstract = abstract_elem.get_text(strip=True)
                        break
                
                # Extract claims
                claims = ""
                claims_selectors = [
                    'section[data-proto="CLAIMS"]',
                    '.claims',
                    '[data-proto="CLAIMS"]'
                ]
                
                for selector in claims_selectors:
                    claims_elem = soup.select_one(selector)
                    if claims_elem:
                        claims_text = claims_elem.get_text(strip=True)
                        # Limit claims to first few for analysis
                        claims = claims_text[:1000] + "..." if len(claims_text) > 1000 else claims_text
                        break
                
                # Extract description
                description = ""
                desc_selectors = [
                    'section[data-proto="DESCRIPTION"]',
                    '.description',
                    '[data-proto="DESCRIPTION"]'
                ]
                
                for selector in desc_selectors:
                    desc_elem = soup.select_one(selector)
                    if desc_elem:
                        desc_text = desc_elem.get_text(strip=True)
                        # Limit description for analysis
                        description = desc_text[:2000] + "..." if len(desc_text) > 2000 else desc_text
                        break
                
                # Extract inventors and assignees
                inventors = []
                assignees = []
                
                inventor_elems = soup.select('[data-proto="INVENTOR"]')
                for elem in inventor_elems:
                    inventor_text = elem.get_text(strip=True)
                    if inventor_text:
                        inventors.append(inventor_text)
                
                assignee_elems = soup.select('[data-proto="ASSIGNEE"]')
                for elem in assignee_elems:
                    assignee_text = elem.get_text(strip=True)
                    if assignee_text:
                        assignees.append(assignee_text)
                
                return {
                    'enhanced_abstract': abstract,
                    'claims': claims,
                    'description': description,
                    'enhanced_inventors': inventors,
                    'enhanced_assignees': assignees,
                    'content_extraction_success': True
                }
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"   ⚠️ Failed to extract enhanced content for {patent_number}: {e}")
            return {'content_extraction_success': False}
    
    def analyze_patents_with_enhanced_content(self, patents: List[Dict[str, Any]], 
                                            min_relevance: float = 15.0,
                                            enhance_top_patents: bool = True) -> List[Dict[str, Any]]:
        """Analyze patents with option to enhance content for top candidates"""
        
        print(f"\n🔬 Enhanced analysis of {len(patents)} patents (min relevance: {min_relevance})...")
        
        # First pass: analyze with existing content
        analyzed_patents = []
        
        for i, patent in enumerate(patents):
            try:
                analysis = self.analyze_drug_discovery_relevance(patent)
                patent['drug_discovery_analysis'] = analysis
                
                if analysis.relevance_score >= min_relevance:
                    analyzed_patents.append(patent)
                
                if (i + 1) % 50 == 0:
                    print(f"   📊 Processed {i + 1}/{len(patents)} patents, found {len(analyzed_patents)} relevant")
                    
            except Exception as e:
                continue
        
        print(f"✅ First pass complete: {len(analyzed_patents)} potentially relevant patents")
        
        # Second pass: enhance content for promising patents
        if enhance_top_patents and analyzed_patents:
            print(f"\n🔍 Enhancing content for top {min(len(analyzed_patents), 20)} patents...")
            
            # Sort by relevance score and enhance top patents
            analyzed_patents.sort(key=lambda p: p['drug_discovery_analysis'].relevance_score, reverse=True)
            
            for i, patent in enumerate(analyzed_patents[:20]):  # Enhance top 20
                enhanced_content = self.extract_enhanced_patent_content(patent['patent_number'])
                patent.update(enhanced_content)
                
                # Re-analyze with enhanced content
                if enhanced_content.get('content_extraction_success'):
                    # Update patent with enhanced content for re-analysis
                    if enhanced_content.get('enhanced_abstract'):
                        patent['abstract'] = enhanced_content['enhanced_abstract']
                    
                    # Add claims and description to raw_text for analysis
                    enhanced_text = f"{patent.get('raw_text', '')} {enhanced_content.get('claims', '')} {enhanced_content.get('description', '')}"
                    patent['raw_text'] = enhanced_text
                    
                    # Re-analyze
                    new_analysis = self.analyze_drug_discovery_relevance(patent)
                    patent['drug_discovery_analysis'] = new_analysis
                    patent['enhanced_analysis'] = True
                    
                    print(f"   ✅ Enhanced {patent['patent_number']}: {new_analysis.relevance_score:.1f}")
                
                time.sleep(1)  # Rate limiting
        
        # Final filtering with updated scores
        final_patents = [p for p in analyzed_patents 
                        if p['drug_discovery_analysis'].relevance_score >= min_relevance]
        
        # Sort by final relevance score
        final_patents.sort(key=lambda p: p['drug_discovery_analysis'].relevance_score, reverse=True)
        
        print(f"🎯 Final result: {len(final_patents)} drug discovery relevant patents")
        return final_patents

def run_improved_analysis(max_patents: int = 300, min_relevance: float = 15.0):
    """Run improved drug discovery analysis"""
    
    analyzer = ImprovedDrugDiscoveryAnalyzer()
    
    print("🧬 IMPROVED FOXP2 Drug Discovery Analysis")
    print("=" * 50)
    
    # Step 1: Gather patents
    print(f"\n📥 Gathering up to {max_patents} FOXP2 patents...")
    all_patents = analyzer.gather_all_foxp2_patents(max_patents)
    
    if not all_patents:
        print("❌ Failed to gather patents")
        return
    
    # Step 2: Analyze with enhanced scoring
    print(f"\n🔬 Analyzing with improved scoring (threshold: {min_relevance})...")
    drug_patents = analyzer.analyze_patents_with_enhanced_content(
        all_patents, 
        min_relevance=min_relevance,
        enhance_top_patents=True
    )
    
    # Step 3: Generate detailed report
    summary = analyzer.generate_summary_report(drug_patents)
    
    # Step 4: Save results
    json_file, csv_file = analyzer.save_drug_discovery_results(drug_patents, "improved_foxp2_drug_discovery")
    
    # Step 5: Display detailed results
    print(f"\n🎯 IMPROVED ANALYSIS RESULTS")
    print("=" * 40)
    print(f"📊 Total patents analyzed: {len(all_patents)}")
    print(f"🎯 Drug discovery relevant: {len(drug_patents)}")
    print(f"📈 Success rate: {len(drug_patents)/len(all_patents)*100:.1f}%")
    print(f"⭐ High relevance (>50): {len([p for p in drug_patents if p['drug_discovery_analysis'].relevance_score > 50])}")
    
    if drug_patents:
        print(f"\n🏆 TOP 10 DRUG DISCOVERY PATENTS:")
        for i, patent in enumerate(drug_patents[:10], 1):
            analysis = patent['drug_discovery_analysis']
            enhanced = "📈" if patent.get('enhanced_analysis') else ""
            print(f"{i:2d}. {patent['patent_number']} - Score: {analysis.relevance_score:.1f} {enhanced}")
            print(f"     {patent['title'][:70]}...")
            print(f"     Category: {analysis.category} | Terms: {', '.join(analysis.key_terms[:3])}")
    
    if summary.get('category_distribution'):
        print(f"\n📋 Categories:")
        for cat, count in list(summary['category_distribution'].items())[:5]:
            print(f"   {cat}: {count} patents")
    
    return drug_patents, summary

if __name__ == "__main__":
    # Run improved analysis
    drug_patents, summary = run_improved_analysis(max_patents=200, min_relevance=12.0)