#!/usr/bin/env python3
"""
Debug the drug discovery analysis to see why no patents were found
"""

from drug_discovery_analyzer import DrugDiscoveryPatentAnalyzer
import json

def debug_patent_analysis():
    """Debug why no patents were classified as drug discovery relevant"""
    
    # Load the results from the previous run
    import glob
    json_files = glob.glob("patent_data/drug_discovery_analysis/foxp2_drug_discovery_*.json")
    
    if not json_files:
        print("❌ No analysis results found")
        return
    
    latest_file = max(json_files)
    
    with open(latest_file, 'r') as f:
        patents = json.load(f)
    
    print(f"🔍 Analyzing {len(patents)} patents from {latest_file}")
    
    analyzer = DrugDiscoveryPatentAnalyzer()
    
    # Look at first 10 patents and see what keywords they contain
    for i, patent in enumerate(patents[:10]):
        print(f"\n📄 Patent {i+1}: {patent['patent_number']}")
        print(f"   Title: {patent['title'][:80]}...")
        
        # Analyze this patent
        analysis = analyzer.analyze_drug_discovery_relevance(patent)
        print(f"   Score: {analysis.relevance_score:.1f}")
        print(f"   Category: {analysis.category}")
        print(f"   Key terms: {analysis.key_terms}")
        print(f"   Reasoning: {analysis.reasoning}")
        
        # Show raw text for manual inspection
        text_sample = patent.get('raw_text', '')[:200] + "..."
        print(f"   Raw text: {text_sample}")

def test_sample_patent_analysis():
    """Test analysis with manually created drug discovery patents"""
    
    analyzer = DrugDiscoveryPatentAnalyzer()
    
    # Test patents with known drug discovery content
    test_patents = [
        {
            'patent_number': 'TEST001',
            'title': 'Small molecule inhibitor targeting FOXP2 for autism treatment',
            'abstract': 'This invention relates to pharmaceutical compositions comprising small molecule compounds that selectively inhibit FOXP2 protein activity. The therapeutic compounds show efficacy in treating autism spectrum disorders in preclinical studies.',
            'raw_text': 'Small molecule inhibitor targeting FOXP2 for autism treatment pharmaceutical therapeutic compound drug development clinical trial'
        },
        {
            'patent_number': 'TEST002', 
            'title': 'FOXP2 biomarker for neurological disorder diagnosis',
            'abstract': 'Methods for using FOXP2 expression levels as a diagnostic biomarker for early detection of speech and language disorders.',
            'raw_text': 'FOXP2 biomarker neurological disorder diagnosis diagnostic marker speech language'
        },
        {
            'patent_number': 'TEST003',
            'title': 'Gene sequencing method for FOXP2 variants',
            'abstract': 'A PCR-based method for detecting genetic variants in the FOXP2 gene using novel primer sequences.',
            'raw_text': 'Gene sequencing method FOXP2 variants PCR detection primer sequences genetic testing'
        }
    ]
    
    print("🧪 Testing analysis with sample patents:")
    
    for patent in test_patents:
        print(f"\n📄 {patent['patent_number']}: {patent['title']}")
        
        analysis = analyzer.analyze_drug_discovery_relevance(patent)
        print(f"   Score: {analysis.relevance_score:.1f}")
        print(f"   Category: {analysis.category}")
        print(f"   Key terms: {analysis.key_terms}")
        print(f"   Reasoning: {analysis.reasoning}")

def check_keyword_coverage():
    """Check if our keywords are appropriate"""
    
    analyzer = DrugDiscoveryPatentAnalyzer()
    
    print("🔑 Current drug discovery keywords:")
    for category, keywords in analyzer.drug_discovery_keywords.items():
        print(f"\n{category.upper()}:")
        for keyword in keywords:
            print(f"   - {keyword}")
    
    print(f"\n❌ Exclusion patterns:")
    for pattern in analyzer.exclusion_patterns:
        print(f"   - {pattern}")

if __name__ == "__main__":
    print("🔍 DEBUGGING DRUG DISCOVERY ANALYSIS")
    print("=" * 50)
    
    check_keyword_coverage()
    test_sample_patent_analysis()
    debug_patent_analysis()