#!/usr/bin/env python3
"""
Direct collector for all 3,665 FOXP2 patents using the exact same approach that worked for 473 patents
"""

import time
import json
import csv
from pathlib import Path
from datetime import datetime
from improved_drug_analyzer import ImprovedDrugDiscoveryAnalyzer

def collect_and_analyze_all_3665():
    """Use the exact same approach that successfully collected 473 patents, but target all 3,665"""
    
    print("🧬 COLLECTING AND ANALYZING ALL 3,665 FOXP2 PATENTS")
    print("=" * 60)
    print("🎯 Using the EXACT approach that successfully collected 473 patents")
    print("⚡ Targeting all 3,665 patents across 37 pages")
    print("🔬 Will analyze each for drug discovery relevance")
    print()
    
    # Create analyzer instance (this contains the working collection method)
    analyzer = ImprovedDrugDiscoveryAnalyzer()
    
    start_time = time.time()
    
    print("📥 STEP 1: Collecting ALL FOXP2 patents...")
    print("🌐 Using gather_all_foxp2_patents with target 3665...")
    
    # This is the method that successfully collected 473 patents
    # Now we'll push it to get all 3,665
    all_patents = analyzer.gather_all_foxp2_patents(max_patents=3665)
    
    collection_time = time.time() - start_time
    
    if not all_patents:
        print("❌ Failed to collect patents")
        return
    
    print(f"✅ Collection complete: {len(all_patents)} patents in {collection_time/60:.1f} minutes")
    
    # Save the raw collection first
    results_dir = Path("patent_data/complete_3665")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save raw patents as JSON
    raw_json_file = results_dir / f"all_foxp2_patents_raw_{timestamp}.json"
    with open(raw_json_file, 'w', encoding='utf-8') as f:
        json.dump(all_patents, f, indent=2, ensure_ascii=False)
    
    # Save raw patents as CSV
    raw_csv_file = results_dir / f"all_foxp2_patents_raw_{timestamp}.csv"
    if all_patents:
        with open(raw_csv_file, 'w', newline='', encoding='utf-8') as f:
            all_keys = set()
            for patent in all_patents:
                all_keys.update(patent.keys())
            
            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(all_patents)
    
    print(f"💾 Raw patents saved:")
    print(f"   📄 JSON: {raw_json_file}")
    print(f"   📊 CSV: {raw_csv_file}")
    
    # Now analyze for drug discovery
    print(f"\n🔬 STEP 2: Drug discovery analysis...")
    print(f"🔬 Analyzing {len(all_patents)} patents for drug discovery relevance...")
    
    analysis_start = time.time()
    
    drug_patents = analyzer.analyze_patents_with_enhanced_content(
        all_patents, 
        min_relevance=3.0,  # Lower threshold to catch more candidates
        enhance_top_patents=True
    )
    
    analysis_time = time.time() - analysis_start
    total_time = time.time() - start_time
    
    # Generate final reports
    print(f"\n📊 STEP 3: Generating reports...")
    summary = analyzer.generate_summary_report(drug_patents)
    json_file, csv_file = analyzer.save_drug_discovery_results(
        drug_patents, 
        f"complete_3665_drug_discovery"
    )
    
    # Final summary
    print()
    print("🎯 COMPLETE 3,665 PATENT ANALYSIS RESULTS")
    print("=" * 50)
    print(f"📊 Total patents collected: {len(all_patents)}")
    print(f"🎯 Target was: 3,665 patents")
    print(f"📈 Collection success rate: {len(all_patents)/3665*100:.1f}%")
    print(f"🔬 Drug discovery relevant: {len(drug_patents)}")
    print(f"💊 Drug discovery rate: {len(drug_patents)/len(all_patents)*100:.1f}%")
    print(f"⏱️ Total time: {total_time/60:.1f} minutes")
    print(f"   Collection: {collection_time/60:.1f} min")
    print(f"   Analysis: {analysis_time/60:.1f} min")
    
    if drug_patents:
        print(f"\n🏆 TOP 10 DRUG DISCOVERY PATENTS:")
        for i, patent in enumerate(drug_patents[:10], 1):
            analysis = patent['drug_discovery_analysis']
            enhanced = "📈" if patent.get('enhanced_analysis') else ""
            print(f"{i:2d}. {patent['patent_number']} - Score: {analysis.relevance_score:.1f} {enhanced}")
            print(f"     {patent['title'][:70]}...")
    
    # Summary by categories
    if summary.get('category_distribution'):
        print(f"\n📋 Drug Discovery Categories:")
        for cat, count in list(summary['category_distribution'].items())[:5]:
            print(f"   {cat}: {count} patents")
    
    print(f"\n💾 Complete Results Saved:")
    print(f"   📄 All patents (raw): {raw_json_file}")
    print(f"   📊 All patents (CSV): {raw_csv_file}")  
    print(f"   🎯 Drug discovery: {json_file}")
    print(f"   📈 Top patents: {csv_file}")
    
    return all_patents, drug_patents

if __name__ == "__main__":
    all_patents, drug_patents = collect_and_analyze_all_3665()
    print("\n✅ Complete 3,665 patent analysis finished!")