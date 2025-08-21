#!/usr/bin/env python3
"""
Final comprehensive drug discovery pipeline for all 3,665 FOXP2 patents
"""

import time
import json
from pathlib import Path
from datetime import datetime
from improved_drug_analyzer import ImprovedDrugDiscoveryAnalyzer
from typing import List, Dict, Any

class FinalDrugDiscoveryPipeline:
    """Complete pipeline for analyzing all FOXP2 patents for drug discovery relevance"""
    
    def __init__(self):
        self.analyzer = ImprovedDrugDiscoveryAnalyzer()
        self.results_dir = Path("patent_data/final_drug_discovery")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Drug discovery categories for classification
        self.drug_discovery_stages = {
            'target_identification': [
                'target identification', 'target discovery', 'target protein',
                'molecular target', 'therapeutic target', 'drug target'
            ],
            'lead_discovery': [
                'lead compound', 'small molecule', 'compound screening',
                'drug candidate', 'chemical entity', 'active compound'
            ],
            'lead_optimization': [
                'lead optimization', 'structure-activity relationship', 'SAR',
                'optimization', 'medicinal chemistry', 'drug design'
            ],
            'preclinical_development': [
                'preclinical', 'toxicity', 'pharmacokinetics', 'pharmacodynamics',
                'ADMET', 'safety', 'efficacy'
            ],
            'biomarkers': [
                'biomarker', 'diagnostic marker', 'companion diagnostic',
                'predictive marker', 'prognostic marker'
            ],
            'therapeutics': [
                'therapeutic', 'treatment', 'therapy', 'pharmaceutical composition',
                'medicament', 'drug formulation', 'clinical trial'
            ],
            'mechanisms': [
                'mechanism of action', 'pathway', 'signaling', 'modulation',
                'regulation', 'inhibition', 'activation'
            ]
        }
    
    def run_comprehensive_analysis(self, target_patents: int = 1000, 
                                 min_relevance: float = 5.0) -> Dict[str, Any]:
        """Run complete analysis pipeline"""
        
        print("🧬 FINAL FOXP2 DRUG DISCOVERY PIPELINE")
        print("=" * 60)
        print(f"🎯 Target: {target_patents} patents (working toward all 3,665)")
        print(f"📊 Minimum relevance threshold: {min_relevance}")
        
        start_time = datetime.now()
        
        # Step 1: Comprehensive patent collection
        print(f"\n📥 STEP 1: Collecting FOXP2 patents...")
        all_patents = self.collect_patents_with_progress(target_patents)
        
        if not all_patents:
            print("❌ Failed to collect patents")
            return {}
        
        # Step 2: Drug discovery analysis
        print(f"\n🔬 STEP 2: Drug discovery relevance analysis...")
        drug_relevant_patents = self.analyze_all_patents(all_patents, min_relevance)
        
        # Step 3: Enhanced content extraction for relevant patents
        print(f"\n🔍 STEP 3: Enhanced content extraction...")
        enhanced_patents = self.enhance_relevant_patents(drug_relevant_patents)
        
        # Step 4: Drug discovery stage classification
        print(f"\n📋 STEP 4: Drug discovery stage classification...")
        classified_patents = self.classify_drug_discovery_stages(enhanced_patents)
        
        # Step 5: Generate comprehensive report
        print(f"\n📊 STEP 5: Generating comprehensive report...")
        analysis_results = self.generate_comprehensive_report(
            all_patents, classified_patents, start_time
        )
        
        # Step 6: Export results
        print(f"\n💾 STEP 6: Exporting results...")
        self.export_comprehensive_results(analysis_results)
        
        return analysis_results
    
    def collect_patents_with_progress(self, target_patents: int) -> List[Dict[str, Any]]:
        """Collect patents with detailed progress tracking"""
        
        all_patents = []
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from urllib.parse import quote_plus
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            driver = webdriver.Chrome(options=chrome_options)
            seen_patents = set()
            
            try:
                base_url = f"https://patents.google.com/?q={quote_plus('FOXP2')}"
                results_per_page = 100
                max_pages = (target_patents // results_per_page) + 1
                
                print(f"🌐 Starting collection: {target_patents} patents across {max_pages} pages")
                
                for page_num in range(1, max_pages + 1):
                    if len(all_patents) >= target_patents:
                        break
                    
                    search_url = f"{base_url}&num={results_per_page}&page={page_num}"
                    
                    print(f"📄 Page {page_num:2d}/{max_pages}: ", end="", flush=True)
                    
                    driver.get(search_url)
                    time.sleep(3)
                    
                    try:
                        WebDriverWait(driver, 15).until(
                            lambda d: d.find_elements(By.TAG_NAME, 'search-result-item')
                        )
                    except:
                        print("⚠️  Timeout")
                        continue
                    
                    search_items = driver.find_elements(By.TAG_NAME, 'search-result-item')
                    page_results = 0
                    
                    for item in search_items:
                        try:
                            patent_data = self.analyzer._extract_enhanced_patent_data(item, page_num, 0)
                            if patent_data and patent_data['patent_number'] not in seen_patents:
                                seen_patents.add(patent_data['patent_number'])
                                all_patents.append(patent_data)
                                page_results += 1
                                
                                if len(all_patents) >= target_patents:
                                    break
                        except:
                            continue
                    
                    print(f"+{page_results} = {len(all_patents)} total")
                    
                    if page_results == 0:
                        print("   No new results, stopping")
                        break
                    
                    # Save checkpoint every 10 pages
                    if page_num % 10 == 0:
                        self.save_checkpoint(all_patents, page_num)
                    
                    time.sleep(1)
                
                print(f"✅ Collection complete: {len(all_patents)} patents")
                return all_patents
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"❌ Collection error: {e}")
            return []
    
    def analyze_all_patents(self, patents: List[Dict[str, Any]], 
                           min_relevance: float) -> List[Dict[str, Any]]:
        """Analyze all patents for drug discovery relevance"""
        
        relevant_patents = []
        
        print(f"🔬 Analyzing {len(patents)} patents (threshold: {min_relevance})...")
        
        for i, patent in enumerate(patents):
            try:
                analysis = self.analyzer.analyze_drug_discovery_relevance(patent)
                patent['drug_discovery_analysis'] = analysis
                
                if analysis.relevance_score >= min_relevance:
                    relevant_patents.append(patent)
                
                # Progress indicator
                if (i + 1) % 50 == 0:
                    progress = (i + 1) / len(patents) * 100
                    print(f"   📊 {progress:.1f}% - Found {len(relevant_patents)} relevant patents")
                    
            except Exception as e:
                continue
        
        print(f"✅ Analysis complete: {len(relevant_patents)} relevant patents found")
        return relevant_patents
    
    def enhance_relevant_patents(self, patents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract enhanced content for relevant patents"""
        
        if not patents:
            return patents
        
        print(f"🔍 Enhancing content for {len(patents)} relevant patents...")
        
        # Sort by relevance score and enhance top patents
        patents.sort(key=lambda p: p['drug_discovery_analysis'].relevance_score, reverse=True)
        
        enhanced_count = 0
        for i, patent in enumerate(patents):
            try:
                print(f"   📄 {i+1:2d}/{len(patents)}: {patent['patent_number']} ", end="", flush=True)
                
                enhanced_content = self.analyzer.extract_enhanced_patent_content(patent['patent_number'])
                patent.update(enhanced_content)
                
                if enhanced_content.get('content_extraction_success'):
                    # Re-analyze with enhanced content
                    if enhanced_content.get('enhanced_abstract'):
                        patent['abstract'] = enhanced_content['enhanced_abstract']
                    
                    enhanced_text = f"{patent.get('raw_text', '')} {enhanced_content.get('claims', '')} {enhanced_content.get('description', '')}"
                    patent['raw_text'] = enhanced_text
                    
                    # Re-analyze with enhanced content
                    new_analysis = self.analyzer.analyze_drug_discovery_relevance(patent)
                    patent['drug_discovery_analysis'] = new_analysis
                    patent['enhanced_analysis'] = True
                    enhanced_count += 1
                    
                    print(f"✅ Score: {new_analysis.relevance_score:.1f}")
                else:
                    print("⚠️  No enhanced content")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
        
        print(f"✅ Enhanced {enhanced_count}/{len(patents)} patents")
        return patents
    
    def classify_drug_discovery_stages(self, patents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify patents by drug discovery stage"""
        
        print(f"📋 Classifying {len(patents)} patents by drug discovery stage...")
        
        for patent in patents:
            # Get all text for classification
            all_text = f"{patent.get('title', '')} {patent.get('abstract', '')} {patent.get('claims', '')} {patent.get('description', '')}".lower()
            
            # Score each stage
            stage_scores = {}
            for stage, keywords in self.drug_discovery_stages.items():
                score = sum(1 for keyword in keywords if keyword.lower() in all_text)
                stage_scores[stage] = score
            
            # Determine primary and secondary stages
            sorted_stages = sorted(stage_scores.items(), key=lambda x: x[1], reverse=True)
            
            primary_stage = sorted_stages[0][0] if sorted_stages[0][1] > 0 else 'unclassified'
            secondary_stage = sorted_stages[1][0] if len(sorted_stages) > 1 and sorted_stages[1][1] > 0 else None
            
            patent['drug_discovery_stage'] = {
                'primary': primary_stage,
                'secondary': secondary_stage,
                'stage_scores': stage_scores
            }
        
        print("✅ Stage classification complete")
        return patents
    
    def generate_comprehensive_report(self, all_patents: List[Dict[str, Any]], 
                                    drug_patents: List[Dict[str, Any]], 
                                    start_time: datetime) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Basic statistics
        stats = {
            'collection_stats': {
                'total_patents_collected': len(all_patents),
                'drug_discovery_relevant': len(drug_patents),
                'success_rate_percent': len(drug_patents) / len(all_patents) * 100 if all_patents else 0,
                'processing_time_seconds': processing_time,
                'collection_timestamp': start_time.isoformat()
            }
        }
        
        if not drug_patents:
            return stats
        
        # Category analysis
        categories = {}
        stages = {}
        scores = []
        assignees = {}
        years = {}
        
        for patent in drug_patents:
            analysis = patent.get('drug_discovery_analysis')
            if analysis:
                categories[analysis.category] = categories.get(analysis.category, 0) + 1
                scores.append(analysis.relevance_score)
            
            stage_info = patent.get('drug_discovery_stage', {})
            primary_stage = stage_info.get('primary', 'unclassified')
            stages[primary_stage] = stages.get(primary_stage, 0) + 1
            
            # Assignee analysis
            for assignee in patent.get('enhanced_assignees', patent.get('assignees', [])):
                if assignee:
                    assignees[assignee] = assignees.get(assignee, 0) + 1
            
            # Year analysis
            pub_date = patent.get('publication_date', '')
            if pub_date and len(pub_date) >= 4:
                year = pub_date[:4]
                years[year] = years.get(year, 0) + 1
        
        # Top performers
        top_patents = sorted(drug_patents, 
                           key=lambda p: p['drug_discovery_analysis'].relevance_score, 
                           reverse=True)[:20]
        
        stats.update({
            'relevance_analysis': {
                'average_score': sum(scores) / len(scores) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'high_relevance_count': len([s for s in scores if s > 20]),
                'very_high_relevance_count': len([s for s in scores if s > 50])
            },
            'category_distribution': dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
            'stage_distribution': dict(sorted(stages.items(), key=lambda x: x[1], reverse=True)),
            'top_assignees': dict(sorted(assignees.items(), key=lambda x: x[1], reverse=True)[:10]),
            'publication_years': dict(sorted(years.items(), reverse=True)),
            'top_patents': [
                {
                    'patent_number': p['patent_number'],
                    'title': p['title'][:100],
                    'relevance_score': p['drug_discovery_analysis'].relevance_score,
                    'category': p['drug_discovery_analysis'].category,
                    'stage': p.get('drug_discovery_stage', {}).get('primary', 'unknown'),
                    'enhanced': p.get('enhanced_analysis', False)
                }
                for p in top_patents
            ]
        })
        
        return stats
    
    def export_comprehensive_results(self, analysis_results: Dict[str, Any]):
        """Export comprehensive results in multiple formats"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Summary JSON report
        summary_file = self.results_dir / f"foxp2_drug_discovery_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print(f"📄 Summary report: {summary_file}")
        
        # 2. Top patents CSV
        if 'top_patents' in analysis_results:
            csv_file = self.results_dir / f"foxp2_top_drug_patents_{timestamp}.csv"
            import csv
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['patent_number', 'title', 'relevance_score', 'category', 'stage', 'enhanced'])
                writer.writeheader()
                writer.writerows(analysis_results['top_patents'])
            
            print(f"📊 Top patents CSV: {csv_file}")
        
        # 3. Statistics summary
        stats_file = self.results_dir / f"foxp2_statistics_{timestamp}.txt"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("FOXP2 DRUG DISCOVERY ANALYSIS SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            
            collection_stats = analysis_results.get('collection_stats', {})
            f.write(f"Total Patents Analyzed: {collection_stats.get('total_patents_collected', 0)}\n")
            f.write(f"Drug Discovery Relevant: {collection_stats.get('drug_discovery_relevant', 0)}\n")
            f.write(f"Success Rate: {collection_stats.get('success_rate_percent', 0):.1f}%\n")
            f.write(f"Processing Time: {collection_stats.get('processing_time_seconds', 0):.1f} seconds\n\n")
            
            if 'category_distribution' in analysis_results:
                f.write("CATEGORY DISTRIBUTION:\n")
                for cat, count in analysis_results['category_distribution'].items():
                    f.write(f"  {cat}: {count} patents\n")
                f.write("\n")
            
            if 'stage_distribution' in analysis_results:
                f.write("DRUG DISCOVERY STAGE DISTRIBUTION:\n")
                for stage, count in analysis_results['stage_distribution'].items():
                    f.write(f"  {stage}: {count} patents\n")
        
        print(f"📈 Statistics report: {stats_file}")
    
    def save_checkpoint(self, patents: List[Dict[str, Any]], page_num: int):
        """Save progress checkpoint"""
        checkpoint_file = self.results_dir / f"checkpoint_page_{page_num}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, default=str)

def main():
    """Main function to run the complete pipeline"""
    
    pipeline = FinalDrugDiscoveryPipeline()
    
    # Run comprehensive analysis
    # Start with a manageable number, then scale up
    results = pipeline.run_comprehensive_analysis(
        target_patents=300,  # Can be increased to 3665 for full analysis
        min_relevance=5.0    # Lower threshold to capture more patents
    )
    
    # Display key results
    if results:
        collection_stats = results.get('collection_stats', {})
        print(f"\n🎯 FINAL RESULTS SUMMARY:")
        print("=" * 40)
        print(f"📊 Total patents: {collection_stats.get('total_patents_collected', 0)}")
        print(f"🎯 Drug discovery relevant: {collection_stats.get('drug_discovery_relevant', 0)}")
        print(f"📈 Success rate: {collection_stats.get('success_rate_percent', 0):.1f}%")
        
        if 'top_patents' in results and results['top_patents']:
            print(f"\n🏆 TOP 5 DRUG DISCOVERY PATENTS:")
            for i, patent in enumerate(results['top_patents'][:5], 1):
                enhanced = "📈" if patent['enhanced'] else ""
                print(f"{i}. {patent['patent_number']} - Score: {patent['relevance_score']:.1f} {enhanced}")
                print(f"   {patent['title']}")
                print(f"   Category: {patent['category']} | Stage: {patent['stage']}")

if __name__ == "__main__":
    main()