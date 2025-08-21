#!/usr/bin/env python3
"""
Automatic multi-batch collector - runs multiple collection strategies in sequence
to maximize patent gathering toward 3,665 target
"""

import time
import json
import csv
from pathlib import Path
from datetime import datetime
from improved_drug_analyzer import ImprovedDrugDiscoveryAnalyzer

class AutoMultiBatchCollector:
    """Automatically run multiple collection strategies to maximize patent gathering"""
    
    def __init__(self):
        self.results_dir = Path("patent_data/auto_multi_batch")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.analyzer = ImprovedDrugDiscoveryAnalyzer()
        
        # Different collection strategies to try
        self.strategies = [
            {"max_patents": 300, "description": "Standard collection (300 patents)"},
            {"max_patents": 500, "description": "Extended collection (500 patents)"},
            {"max_patents": 800, "description": "Large batch collection (800 patents)"},
            {"max_patents": 1000, "description": "Maximum collection (1000 patents)"},
            {"max_patents": 1200, "description": "Aggressive collection (1200 patents)"},
        ]
    
    def load_all_existing_patents(self):
        """Load all existing patents from all directories"""
        all_existing = []
        
        search_dirs = [
            "patent_data/final_drug_discovery",
            "patent_data/complete_3665", 
            "patent_data/persistent_batches",
            "patent_data/drug_discovery_analysis",
            "patent_data/auto_multi_batch",
            "patent_data/alternative_sources",
            "patent_data/wipo_collection"
        ]
        
        print("🔍 Loading ALL existing patents from all sources...")
        
        for search_dir in search_dirs:
            dir_path = Path(search_dir)
            if dir_path.exists():
                json_files = list(dir_path.glob("*.json"))
                for json_file in json_files:
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, list) and data:
                                all_existing.extend(data)
                                print(f"   📄 {json_file.name}: +{len(data)} patents")
                    except Exception as e:
                        continue
        
        # Remove duplicates
        seen = set()
        unique_existing = []
        for patent in all_existing:
            patent_num = patent.get('patent_number', '')
            if patent_num and patent_num not in seen and not patent_num.startswith('PLACEHOLDER'):
                seen.add(patent_num)
                unique_existing.append(patent)
        
        print(f"✅ Total loaded: {len(all_existing)} raw patents")
        print(f"✅ Unique patents: {len(unique_existing)} (after deduplication)")
        return unique_existing
    
    def try_strategy(self, strategy, existing_count):
        """Try a specific collection strategy"""
        max_patents = strategy["max_patents"]
        description = strategy["description"]
        
        print(f"\n🚀 Strategy: {description}")
        print(f"🎯 Target: {max_patents} patents")
        
        try:
            # Use the analyzer's collection method with this target
            new_patents = self.analyzer.gather_all_foxp2_patents(max_patents=max_patents)
            
            if new_patents:
                print(f"   ✅ Collected: {len(new_patents)} patents")
                return new_patents
            else:
                print(f"   ❌ No patents collected")
                return []
                
        except Exception as e:
            print(f"   ❌ Strategy failed: {e}")
            return []
    
    def run_multiple_strategies(self, max_runtime_minutes=30):
        """Run multiple strategies within time limit"""
        
        print("🌟 AUTO MULTI-BATCH COLLECTION")
        print("=" * 45)
        print(f"🎯 Mission: Collect as many patents as possible toward 3,665")
        print(f"⏱️ Time limit: {max_runtime_minutes} minutes")
        print(f"🚀 Strategies: {len(self.strategies)} different approaches")
        print()
        
        start_time = time.time()
        all_collected = []
        
        # Load existing patents
        existing_patents = self.load_all_existing_patents()
        all_patents = existing_patents.copy()
        
        # Try each strategy
        for strategy_idx, strategy in enumerate(self.strategies, 1):
            # Check time limit
            elapsed = (time.time() - start_time) / 60
            if elapsed > max_runtime_minutes:
                print(f"⏰ Time limit reached ({elapsed:.1f} min)")
                break
            
            print(f"\n📡 Strategy {strategy_idx}/{len(self.strategies)}")
            print(f"   Current total: {len(all_patents)} patents")
            
            # Try this strategy
            strategy_patents = self.try_strategy(strategy, len(all_patents))
            
            if strategy_patents:
                # Add to collection
                all_collected.extend(strategy_patents)
                
                # Remove duplicates from combined set
                seen = set()
                temp_all = all_patents + strategy_patents
                unique_all = []
                
                for patent in temp_all:
                    patent_num = patent.get('patent_number', '')
                    if patent_num and patent_num not in seen and not patent_num.startswith('PLACEHOLDER'):
                        seen.add(patent_num)
                        unique_all.append(patent)
                
                prev_count = len(all_patents)
                all_patents = unique_all
                new_unique = len(all_patents) - prev_count
                
                print(f"   📊 New unique patents: {new_unique}")
                print(f"   📊 Total now: {len(all_patents)}")
                
                # Save intermediate results
                self.save_intermediate_results(all_patents, strategy_idx)
                
            else:
                print(f"   ⚠️ Strategy {strategy_idx} yielded no new patents")
            
            # Rate limiting between strategies
            time.sleep(5)
        
        total_time = time.time() - start_time
        
        # Final results
        print(f"\n🎯 AUTO MULTI-BATCH COMPLETE")
        print("=" * 40)
        print(f"📊 Starting patents: {len(existing_patents)}")
        print(f"📊 Strategies attempted: {strategy_idx}")
        print(f"📊 Total collected: {len(all_collected)}")
        print(f"📊 Final unique total: {len(all_patents)}")
        print(f"🎯 Target: 3,665 patents")
        print(f"📈 Progress: {len(all_patents)/3665*100:.1f}%")
        print(f"⏱️ Total time: {total_time/60:.1f} minutes")
        
        # Calculate remaining
        remaining = 3665 - len(all_patents)
        if remaining > 0:
            print(f"\n📋 Remaining work:")
            print(f"   Still needed: {remaining} patents")
            print(f"   Current rate: {len(all_patents)/total_time*60:.1f} patents/min")
            est_time = remaining / (len(all_patents)/total_time) / 60
            print(f"   Estimated time to completion: {est_time:.1f} minutes")
        else:
            print(f"\n🎉 TARGET ACHIEVED!")
        
        return all_patents
    
    def save_intermediate_results(self, patents, strategy_num):
        """Save intermediate results after each strategy"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save current state
        intermediate_file = self.results_dir / f"strategy_{strategy_num}_{timestamp}.json"
        with open(intermediate_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Saved: {intermediate_file.name}")
    
    def save_final_results(self, patents):
        """Save final comprehensive results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = self.results_dir / f"auto_multi_batch_final_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_file = self.results_dir / f"auto_multi_batch_final_{timestamp}.csv"
        if patents:
            all_keys = set()
            for patent in patents:
                all_keys.update(patent.keys())
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(patents)
        
        print(f"\n💾 Final Results Saved:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📊 CSV: {csv_file}")
        
        return json_file, csv_file
    
    def comprehensive_drug_discovery_analysis(self, patents):
        """Run comprehensive drug discovery analysis on final collection"""
        if not patents:
            return []
        
        print(f"\n🔬 COMPREHENSIVE DRUG DISCOVERY ANALYSIS")
        print("=" * 50)
        
        try:
            # Full analysis with enhancement
            drug_patents = self.analyzer.analyze_patents_with_enhanced_content(
                patents, 
                min_relevance=3.0,
                enhance_top_patents=True
            )
            
            # Generate comprehensive summary
            summary = self.analyzer.generate_summary_report(drug_patents)
            json_file, csv_file = self.analyzer.save_drug_discovery_results(
                drug_patents, 
                "auto_multi_batch_drug_discovery"
            )
            
            print(f"\n🎯 FINAL DRUG DISCOVERY RESULTS:")
            print(f"   📊 Total patents analyzed: {len(patents)}")
            print(f"   🎯 Drug discovery relevant: {len(drug_patents)}")
            print(f"   📈 Success rate: {len(drug_patents)/len(patents)*100:.1f}%")
            
            if drug_patents:
                print(f"\n🏆 TOP 10 DRUG DISCOVERY PATENTS:")
                for i, patent in enumerate(drug_patents[:10], 1):
                    analysis = patent.get('drug_discovery_analysis')
                    if analysis:
                        enhanced = "📈" if patent.get('enhanced_analysis') else ""
                        print(f"{i:2d}. {patent['patent_number']} - Score: {analysis.relevance_score:.1f} {enhanced}")
                        print(f"     {patent['title'][:60]}...")
            
            return drug_patents
            
        except Exception as e:
            print(f"❌ Drug discovery analysis failed: {e}")
            return []

def main():
    """Main function"""
    collector = AutoMultiBatchCollector()
    
    # Run multiple strategies
    all_patents = collector.run_multiple_strategies(max_runtime_minutes=45)
    
    # Save final results
    json_file, csv_file = collector.save_final_results(all_patents)
    
    # Run comprehensive drug discovery analysis
    drug_patents = collector.comprehensive_drug_discovery_analysis(all_patents)
    
    print(f"\n✅ AUTO MULTI-BATCH MISSION COMPLETE!")
    print(f"🌟 Final collection: {len(all_patents)} total patents")
    print(f"💊 Drug discovery relevant: {len(drug_patents)} patents")
    print(f"📁 All results saved and analyzed")

if __name__ == "__main__":
    main()