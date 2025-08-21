#!/usr/bin/env python3
"""
Simple but reliable collector for all 3,665 FOXP2 patents
Using the proven approach from our successful 473-patent collection
"""

import time
import json
import csv
from pathlib import Path
from datetime import datetime
from comprehensive_scraper import scrape_comprehensive_google_patents

def collect_all_3665_patents():
    """Collect all 3,665 patents using our proven scraper"""
    
    print("🧬 COLLECTING ALL 3,665 FOXP2 PATENTS")
    print("=" * 50)
    print("🎯 Using proven scraper that successfully collected 473 patents")
    print("⚡ Now targeting all 37 pages for complete dataset")
    print()
    
    # Use our proven scraper with increased page count
    start_time = time.time()
    
    print("🚀 Starting collection with comprehensive scraper...")
    all_patents = scrape_comprehensive_google_patents(
        query="FOXP2",
        max_results=3665  # Target all 3,665 patents
    )
    
    total_time = time.time() - start_time
    
    print()
    print("✅ COLLECTION COMPLETE")
    print("=" * 30)
    print(f"📊 Total patents collected: {len(all_patents)}")
    print(f"🎯 Target was: 3,665 patents")
    print(f"📈 Success rate: {len(all_patents)/3665*100:.1f}%")
    print(f"⏱️ Total time: {total_time/60:.1f} minutes")
    
    # Save results
    results_dir = Path("patent_data/complete_3665")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save as JSON
    json_file = results_dir / f"all_foxp2_patents_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_patents, f, indent=2, ensure_ascii=False)
    
    # Save as CSV
    csv_file = results_dir / f"all_foxp2_patents_{timestamp}.csv"
    if all_patents:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            # Get all possible keys
            all_keys = set()
            for patent in all_patents:
                all_keys.update(patent.keys())
            
            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(all_patents)
    
    print(f"💾 Results saved:")
    print(f"   📄 JSON: {json_file}")
    print(f"   📊 CSV: {csv_file}")
    
    return all_patents, json_file, csv_file

def analyze_all_for_drug_discovery(patents):
    """Run drug discovery analysis on the complete dataset"""
    if not patents:
        print("❌ No patents to analyze")
        return
    
    print()
    print("🔬 DRUG DISCOVERY ANALYSIS")
    print("=" * 30)
    print(f"📊 Analyzing {len(patents)} patents for drug discovery relevance...")
    
    from improved_drug_analyzer import ImprovedDrugDiscoveryAnalyzer
    
    analyzer = ImprovedDrugDiscoveryAnalyzer()
    
    # Analyze all patents
    drug_patents = analyzer.analyze_patents_with_enhanced_content(
        patents, 
        min_relevance=3.0,  # Lower threshold for comprehensive analysis
        enhance_top_patents=True
    )
    
    # Generate reports
    summary = analyzer.generate_summary_report(drug_patents)
    json_file, csv_file = analyzer.save_drug_discovery_results(
        drug_patents, 
        "complete_3665_drug_discovery"
    )
    
    print()
    print("🎯 FINAL DRUG DISCOVERY RESULTS")
    print("=" * 40)
    print(f"📊 Total patents analyzed: {len(patents)}")
    print(f"🎯 Drug discovery relevant: {len(drug_patents)}")
    print(f"📈 Success rate: {len(drug_patents)/len(patents)*100:.1f}%")
    
    if drug_patents:
        print(f"\n🏆 TOP 10 DRUG DISCOVERY PATENTS:")
        for i, patent in enumerate(drug_patents[:10], 1):
            analysis = patent['drug_discovery_analysis']
            print(f"{i:2d}. {patent['patent_number']} - Score: {analysis.relevance_score:.1f}")
            print(f"     {patent['title'][:70]}...")
    
    return drug_patents

if __name__ == "__main__":
    # Step 1: Collect all 3,665 patents
    all_patents, json_file, csv_file = collect_all_3665_patents()
    
    # Step 2: Analyze for drug discovery
    if all_patents:
        drug_patents = analyze_all_for_drug_discovery(all_patents)
        print("\n✅ Complete analysis finished!")
    else:
        print("\n❌ Collection failed - no patents to analyze")