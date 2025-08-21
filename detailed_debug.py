#!/usr/bin/env python3
"""
Detailed debugging to understand why patents aren't scoring high enough
"""

from improved_drug_analyzer import ImprovedDrugDiscoveryAnalyzer
import json
import glob

def analyze_sample_patents():
    """Analyze actual patents to see scoring details"""
    
    analyzer = ImprovedDrugDiscoveryAnalyzer()
    
    # Load recent results
    json_files = glob.glob("patent_data/drug_discovery_analysis/improved_foxp2_drug_discovery_*.json")
    if not json_files:
        print("❌ No results found")
        return
    
    latest_file = max(json_files)
    with open(latest_file, 'r') as f:
        patents = json.load(f)
    
    print(f"🔍 Analyzing {len(patents)} patents from recent run")
    
    # Analyze first 5 patents in detail
    for i, patent in enumerate(patents[:5]):
        print(f"\n{'='*60}")
        print(f"📄 PATENT {i+1}: {patent['patent_number']}")
        print(f"Title: {patent['title']}")
        print(f"Abstract: {patent.get('abstract', 'None')[:200]}...")
        
        # Show raw text sample
        raw_text = patent.get('raw_text', '')
        print(f"Raw text sample: {raw_text[:300]}...")
        
        # Analyze this patent step by step
        analysis = analyzer.analyze_drug_discovery_relevance(patent)
        
        print(f"\n🔬 ANALYSIS RESULTS:")
        print(f"   Relevance Score: {analysis.relevance_score:.2f}")
        print(f"   Category: {analysis.category}")
        print(f"   Confidence: {analysis.confidence:.1f}")
        print(f"   Key Terms Found: {analysis.key_terms}")
        print(f"   Reasoning: {analysis.reasoning}")
        
        # Manual keyword checking
        print(f"\n🔑 MANUAL KEYWORD CHECK:")
        text_to_check = f"{patent.get('title', '')} {patent.get('abstract', '')} {patent.get('raw_text', '')}".lower()
        
        keyword_hits = []
        for category, keywords in analyzer.drug_discovery_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_to_check:
                    keyword_hits.append(f"{keyword} ({category})")
        
        if keyword_hits:
            print(f"   Found keywords: {', '.join(keyword_hits[:10])}")
        else:
            print(f"   No keywords found in text")
            
        # Check for common drug-related terms manually
        drug_terms = ['drug', 'compound', 'therapeutic', 'treatment', 'medicine', 'therapy', 'pharmaceutical', 'inhibitor', 'target']
        found_drug_terms = [term for term in drug_terms if term in text_to_check]
        if found_drug_terms:
            print(f"   Basic drug terms found: {found_drug_terms}")

def test_scoring_mechanism():
    """Test the scoring mechanism with controlled examples"""
    
    analyzer = ImprovedDrugDiscoveryAnalyzer()
    
    # Test patents with different levels of drug discovery content
    test_cases = [
        {
            'patent_number': 'HIGH_DRUG',
            'title': 'Pharmaceutical composition comprising small molecule drug targeting FOXP2 for therapeutic treatment of autism',
            'abstract': 'This invention relates to pharmaceutical compositions and therapeutic methods for treating autism spectrum disorders using novel small molecule compounds that specifically inhibit FOXP2 protein activity. The drug candidates showed efficacy in preclinical studies.',
            'raw_text': 'pharmaceutical composition small molecule drug therapeutic treatment autism inhibitor compound efficacy preclinical clinical trial'
        },
        {
            'patent_number': 'MEDIUM_DRUG',
            'title': 'FOXP2 biomarker for neurological disorder diagnosis and treatment monitoring',
            'abstract': 'Methods for using FOXP2 expression as a biomarker for diagnosis and therapeutic monitoring of speech disorders.',
            'raw_text': 'biomarker diagnosis therapeutic monitoring speech disorders neurological treatment'
        },
        {
            'patent_number': 'LOW_DRUG',
            'title': 'FOXP2 gene expression in developmental studies',
            'abstract': 'Research methods for studying FOXP2 gene expression during development.',
            'raw_text': 'gene expression developmental studies research methods laboratory'
        }
    ]
    
    print(f"\n🧪 TESTING SCORING MECHANISM:")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n📄 {test_case['patent_number']}")
        print(f"Title: {test_case['title']}")
        
        analysis = analyzer.analyze_drug_discovery_relevance(test_case)
        
        print(f"Score: {analysis.relevance_score:.2f}")
        print(f"Category: {analysis.category}")
        print(f"Key Terms: {analysis.key_terms}")
        print(f"Reasoning: {analysis.reasoning}")

def check_real_foxp2_patents_manually():
    """Manually check some real FOXP2 patents that should be drug-related"""
    
    # Some patent numbers we found that might be drug-related based on titles
    potentially_drug_related = [
        "US11679148B2",  # "Methods and compositions for treating cancers"
        "AU2009329380A1", # "Use of FOXP2 as a marker for abnormal lymphocytes and as a target for therapy"
        "US9044492B2",   # "Method for modulating the efficiency of double-strand break-induced mutagenesis"
        "US11352647B2",  # "Crispr enzymes and systems"
        "EP2751269B1"    # "Methods and compounds useful in conditions related to repeat expansion"
    ]
    
    print(f"\n🎯 CHECKING POTENTIALLY DRUG-RELATED PATENTS:")
    print("=" * 50)
    
    # Create mock patents with these titles to test scoring
    test_patents = [
        {
            'patent_number': 'US11679148B2',
            'title': 'Methods and compositions for treating cancers',
            'abstract': 'Therapeutic compositions and methods for treating cancer using pharmaceutical compounds.',
            'raw_text': 'methods compositions treating cancers therapeutic pharmaceutical compounds treatment'
        },
        {
            'patent_number': 'AU2009329380A1', 
            'title': 'Use of FOXP2 as a marker for abnormal lymphocytes and as a target for therapy',
            'abstract': 'FOXP2 protein as therapeutic target and biomarker for treatment of lymphocyte disorders.',
            'raw_text': 'FOXP2 marker therapeutic target therapy treatment lymphocytes biomarker pharmaceutical'
        }
    ]
    
    analyzer = ImprovedDrugDiscoveryAnalyzer()
    
    for patent in test_patents:
        print(f"\n📄 {patent['patent_number']}")
        print(f"Title: {patent['title']}")
        
        analysis = analyzer.analyze_drug_discovery_relevance(patent)
        
        print(f"Score: {analysis.relevance_score:.2f}")
        print(f"Category: {analysis.category}")
        print(f"Key Terms: {analysis.key_terms}")

if __name__ == "__main__":
    print("🔍 DETAILED DRUG DISCOVERY ANALYSIS DEBUG")
    print("=" * 60)
    
    test_scoring_mechanism()
    check_real_foxp2_patents_manually()
    analyze_sample_patents()