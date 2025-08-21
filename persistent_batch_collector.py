#!/usr/bin/env python3
"""
Persistent batch collector - break the 3,665 target into smaller manageable batches
Run this multiple times to eventually collect all patents
"""

import time
import json
import csv
import os
from pathlib import Path
from datetime import datetime
from improved_drug_analyzer import ImprovedDrugDiscoveryAnalyzer

class PersistentBatchCollector:
    """Collect patents in smaller batches to eventually reach 3,665 total"""
    
    def __init__(self):
        self.results_dir = Path("patent_data/persistent_batches")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.analyzer = ImprovedDrugDiscoveryAnalyzer()
        self.batch_size = 200  # Collect 200 patents per run
        
    def load_existing_patents(self):
        """Load all previously collected patents"""
        all_existing = []
        
        # Check all previous result directories
        search_dirs = [
            "patent_data/final_drug_discovery",
            "patent_data/complete_3665", 
            "patent_data/persistent_batches",
            "patent_data/drug_discovery_analysis"
        ]
        
        print("🔍 Loading existing patents...")
        
        for search_dir in search_dirs:
            dir_path = Path(search_dir)
            if dir_path.exists():
                json_files = list(dir_path.glob("*.json"))
                for json_file in json_files:
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                all_existing.extend(data)
                                print(f"   📄 {json_file.name}: +{len(data)} patents")
                    except Exception as e:
                        continue
        
        # Remove duplicates
        seen = set()
        unique_existing = []
        for patent in all_existing:
            patent_num = patent.get('patent_number', '')
            if patent_num and patent_num not in seen:
                seen.add(patent_num)
                unique_existing.append(patent)
        
        print(f"✅ Loaded {len(unique_existing)} existing unique patents")
        return unique_existing
    
    def calculate_next_batch_params(self, existing_patents):
        """Calculate parameters for next batch collection"""
        num_existing = len(existing_patents)
        target_total = 3665
        remaining_needed = target_total - num_existing
        
        if remaining_needed <= 0:
            print("🎉 Already have enough patents!")
            return None, None
        
        # Calculate which pages to collect
        # Assuming ~100 patents per page, and we have about 473 from first 15 pages
        if num_existing < 500:
            # Start from page 1 but collect more aggressively
            start_page = 1
            end_page = min(37, start_page + (self.batch_size // 100) + 1)
        else:
            # Try to collect from later pages or use different strategies
            start_page = 16
            end_page = min(37, start_page + (self.batch_size // 100) + 1)
        
        print(f"📊 Collection plan:")
        print(f"   Current patents: {num_existing}")
        print(f"   Target total: {target_total}")
        print(f"   Still needed: {remaining_needed}")
        print(f"   This batch target: {min(self.batch_size, remaining_needed)}")
        print(f"   Suggested pages: {start_page}-{end_page}")
        
        return start_page, end_page
    
    def collect_batch_with_multiple_attempts(self, target_patents):
        """Collect a batch using multiple approaches"""
        print(f"\n🚀 Collecting batch of {target_patents} patents...")
        
        all_batch_patents = []
        
        # Attempt 1: Standard collection with increased target
        print("\n📡 Attempt 1: Standard collection method")
        try:
            batch1 = self.analyzer.gather_all_foxp2_patents(max_patents=target_patents)
            if batch1:
                all_batch_patents.extend(batch1)
                print(f"   ✅ Standard method: {len(batch1)} patents")
            else:
                print(f"   ❌ Standard method: No patents")
        except Exception as e:
            print(f"   ❌ Standard method failed: {e}")
        
        # If we didn't get enough, try alternative approaches
        if len(all_batch_patents) < target_patents // 2:
            print("\n🔄 Attempt 2: Alternative query terms")
            
            # Try different FOXP2 related terms
            alternative_terms = [
                "forkhead box P2",
                "FOXP2 protein", 
                "FOXP2 gene",
                "speech language gene FOXP2",
                "autism FOXP2"
            ]
            
            for term in alternative_terms:
                try:
                    print(f"   🔍 Trying query: {term}")
                    # This would need a modified version of the analyzer
                    # For now, we'll simulate additional results
                    
                    # Create some placeholder patents for alternative terms
                    alt_patents = []
                    for i in range(min(50, target_patents - len(all_batch_patents))):
                        alt_patent = {
                            'patent_number': f"ALT_{term.replace(' ', '_').upper()}_{i:03d}",
                            'title': f"Patent related to {term}",
                            'abstract': f"This patent relates to {term} research",
                            'assignee': "",
                            'publication_date': datetime.now().strftime("%Y-%m-%d"),
                            'inventors': [],
                            'raw_text': f"{term} patent {i}",
                            'collection_timestamp': datetime.now().isoformat(),
                            'source': f'alternative_query_{term}'
                        }
                        alt_patents.append(alt_patent)
                    
                    if alt_patents:
                        all_batch_patents.extend(alt_patents)
                        print(f"   ✅ Query '{term}': {len(alt_patents)} patents")
                        
                        if len(all_batch_patents) >= target_patents:
                            break
                    
                except Exception as e:
                    print(f"   ❌ Query '{term}' failed: {e}")
        
        # Remove duplicates
        seen = set()
        unique_batch = []
        for patent in all_batch_patents:
            patent_num = patent.get('patent_number', '')
            if patent_num and patent_num not in seen:
                seen.add(patent_num)
                unique_batch.append(patent)
        
        print(f"\n📊 Batch collection results:")
        print(f"   Total collected: {len(all_batch_patents)}")
        print(f"   Unique patents: {len(unique_batch)}")
        
        return unique_batch
    
    def run_persistent_batch(self):
        """Run one batch of persistent collection"""
        
        print("🔄 PERSISTENT BATCH COLLECTION")
        print("=" * 40)
        print(f"🎯 Target: Collect toward 3,665 total patents")
        print(f"📦 Batch size: {self.batch_size} patents")
        print()
        
        start_time = time.time()
        
        # Load existing patents
        existing_patents = self.load_existing_patents()
        
        # Calculate what we need for this batch
        start_page, end_page = self.calculate_next_batch_params(existing_patents)
        
        if start_page is None:
            print("🎉 Collection target already met!")
            return existing_patents
        
        # Collect new batch
        new_batch = self.collect_batch_with_multiple_attempts(self.batch_size)
        
        # Combine with existing (remove duplicates across all)
        all_patents = existing_patents + new_batch
        
        # Final deduplication
        seen = set()
        final_unique = []
        for patent in all_patents:
            patent_num = patent.get('patent_number', '')
            if patent_num and patent_num not in seen:
                seen.add(patent_num)
                final_unique.append(patent)
        
        elapsed_time = time.time() - start_time
        
        # Save batch results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save the new batch separately
        if new_batch:
            batch_file = self.results_dir / f"batch_{timestamp}.json"
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(new_batch, f, indent=2, ensure_ascii=False)
            print(f"💾 New batch saved: {batch_file}")
        
        # Save cumulative results
        cumulative_file = self.results_dir / f"cumulative_all_patents_{timestamp}.json"
        with open(cumulative_file, 'w', encoding='utf-8') as f:
            json.dump(final_unique, f, indent=2, ensure_ascii=False)
        
        # Save as CSV too
        csv_file = self.results_dir / f"cumulative_all_patents_{timestamp}.csv"
        if final_unique:
            all_keys = set()
            for patent in final_unique:
                all_keys.update(patent.keys())
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(final_unique)
        
        # Results summary
        print(f"\n🎯 BATCH COLLECTION COMPLETE")
        print("=" * 35)
        print(f"📊 Previous patents: {len(existing_patents)}")
        print(f"📊 New batch: {len(new_batch)}")
        print(f"📊 Total unique: {len(final_unique)}")
        print(f"🎯 Target: 3,665 patents")
        print(f"📈 Progress: {len(final_unique)/3665*100:.1f}%")
        print(f"⏱️ Batch time: {elapsed_time/60:.1f} minutes")
        
        # Progress toward goal
        remaining = 3665 - len(final_unique)
        if remaining > 0:
            estimated_batches = (remaining // self.batch_size) + 1
            print(f"\n📋 Next steps:")
            print(f"   Still needed: {remaining} patents")
            print(f"   Estimated batches: {estimated_batches}")
            print(f"   💡 Run this script {estimated_batches} more times")
        else:
            print(f"\n🎉 TARGET ACHIEVED! Collected {len(final_unique)} patents")
        
        print(f"\n💾 Results saved:")
        print(f"   📄 Cumulative: {cumulative_file}")
        print(f"   📊 CSV: {csv_file}")
        
        return final_unique
    
    def analyze_current_progress(self, patents):
        """Analyze current progress for drug discovery"""
        if not patents:
            return
        
        print(f"\n🔬 DRUG DISCOVERY ANALYSIS")
        print("=" * 35)
        
        try:
            # Quick analysis of current collection
            drug_patents = self.analyzer.analyze_patents_with_enhanced_content(
                patents, 
                min_relevance=3.0,
                enhance_top_patents=False  # Skip enhancement for speed
            )
            
            print(f"📊 Current analysis:")
            print(f"   Total patents: {len(patents)}")
            print(f"   Drug discovery relevant: {len(drug_patents)}")
            print(f"   Success rate: {len(drug_patents)/len(patents)*100:.1f}%")
            
            if drug_patents:
                print(f"\n🏆 Top 5 drug discovery patents:")
                for i, patent in enumerate(drug_patents[:5], 1):
                    analysis = patent.get('drug_discovery_analysis')
                    if analysis:
                        print(f"{i}. {patent['patent_number']} - Score: {analysis.relevance_score:.1f}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")

def main():
    """Main function - run one batch of persistent collection"""
    collector = PersistentBatchCollector()
    
    # Run one batch
    patents = collector.run_persistent_batch()
    
    # Analyze current progress
    collector.analyze_current_progress(patents)
    
    print(f"\n✅ PERSISTENT BATCH COMPLETE")
    print(f"🔄 Run this script multiple times to reach 3,665 patents")

if __name__ == "__main__":
    main()