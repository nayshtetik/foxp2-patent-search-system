#!/usr/bin/env python3
"""
Filter FOXP2 patents for human applications and sort by therapeutic areas
"""

import json
import csv
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class TherapeuticClassification:
    patent_number: str
    title: str
    relevance_score: float
    therapeutic_area: str
    human_relevance: str
    specific_indication: str
    development_stage: str
    abstract: str
    assignee: str

class HumanTherapeuticFilter:
    """Filter and classify patents for human therapeutic applications"""
    
    def __init__(self):
        self.results_dir = Path("patent_data/human_therapeutics")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Therapeutic area keywords
        self.therapeutic_areas = {
            'neurology_psychiatry': {
                'keywords': [
                    'autism', 'speech disorder', 'language disorder', 'developmental disorder',
                    'neurodevelopmental', 'cognitive disorder', 'psychiatric disorder',
                    'mental health', 'brain disorder', 'neuropsychiatric', 'neurocognitive',
                    'behavioral disorder', 'intellectual disability', 'learning disability',
                    'communication disorder', 'social behavior', 'repetitive behavior',
                    'anxiety', 'depression', 'schizophrenia', 'bipolar', 'ADHD',
                    'neurological', 'neural', 'brain', 'cerebral', 'cognitive'
                ],
                'display_name': 'Neurology & Psychiatry'
            },
            'oncology': {
                'keywords': [
                    'cancer', 'tumor', 'carcinoma', 'oncology', 'malignant', 'neoplasm',
                    'metastasis', 'chemotherapy', 'radiotherapy', 'immunotherapy',
                    'anti-cancer', 'anticancer', 'cytotoxic', 'apoptosis', 'cell death',
                    'adenoid cystic carcinoma', 'breast cancer', 'lung cancer',
                    'prostate cancer', 'colorectal cancer', 'melanoma', 'leukemia',
                    'lymphoma', 'sarcoma', 'glioma', 'hepatocellular'
                ],
                'display_name': 'Oncology'
            },
            'immunology': {
                'keywords': [
                    'immune', 'immunotherapy', 'autoimmune', 'inflammation',
                    'inflammatory', 'cytokine', 'interferon', 'interleukin',
                    'antibody', 'immunoglobulin', 'T cell', 'B cell', 'lymphocyte',
                    'macrophage', 'dendritic cell', 'NK cell', 'regulatory T',
                    'immune response', 'immune system', 'immunomodulation',
                    'transplantation', 'graft rejection', 'allergy', 'asthma'
                ],
                'display_name': 'Immunology & Inflammation'
            },
            'gene_therapy': {
                'keywords': [
                    'gene therapy', 'gene editing', 'CRISPR', 'genome editing',
                    'genetic modification', 'transfection', 'transduction',
                    'viral vector', 'adenovirus', 'lentivirus', 'retrovirus',
                    'AAV', 'adeno-associated virus', 'nucleic acid delivery',
                    'oligonucleotide', 'antisense', 'siRNA', 'miRNA', 'guide RNA',
                    'cas9', 'cas12', 'prime editing', 'base editing'
                ],
                'display_name': 'Gene Therapy & Editing'
            },
            'regenerative_medicine': {
                'keywords': [
                    'stem cell', 'cell therapy', 'regenerative medicine',
                    'tissue engineering', 'cell transplantation', 'cellular therapy',
                    'mesenchymal stem', 'embryonic stem', 'induced pluripotent',
                    'iPSC', 'organoid', 'tissue repair', 'wound healing',
                    'neural regeneration', 'cardiac repair', 'bone regeneration'
                ],
                'display_name': 'Regenerative Medicine & Cell Therapy'
            },
            'drug_delivery': {
                'keywords': [
                    'drug delivery', 'nanoparticle', 'liposome', 'lipid nanoparticle',
                    'microparticle', 'controlled release', 'sustained release',
                    'targeted delivery', 'pharmaceutical composition', 'formulation',
                    'bioavailability', 'pharmacokinetics', 'encapsulation',
                    'polymer', 'hydrogel', 'micelle', 'vesicle', 'carrier'
                ],
                'display_name': 'Drug Delivery & Formulation'
            },
            'diagnostics': {
                'keywords': [
                    'biomarker', 'diagnostic', 'detection', 'screening', 'assay',
                    'companion diagnostic', 'molecular diagnostic', 'genetic testing',
                    'prognostic', 'predictive marker', 'therapeutic monitoring',
                    'imaging', 'contrast agent', 'probe', 'biosensor',
                    'point of care', 'liquid biopsy', 'circulating tumor'
                ],
                'display_name': 'Diagnostics & Biomarkers'
            },
            'rare_diseases': {
                'keywords': [
                    'rare disease', 'orphan drug', 'genetic disorder', 'inherited disorder',
                    'monogenic', 'syndromic', 'congenital', 'hereditary',
                    'familial', 'genetic syndrome', 'metabolic disorder',
                    'lysosomal storage', 'mitochondrial', 'muscular dystrophy'
                ],
                'display_name': 'Rare Diseases & Genetic Disorders'
            }
        }
        
        # Human relevance indicators
        self.human_indicators = {
            'high_human': [
                'human', 'patient', 'clinical', 'therapeutic', 'treatment',
                'therapy', 'medicine', 'pharmaceutical', 'drug', 'medicament',
                'clinical trial', 'human subject', 'individual', 'person'
            ],
            'exclude_animal': [
                'veterinary', 'animal', 'canine', 'feline', 'bovine', 'porcine',
                'murine', 'rodent', 'mouse', 'rat', 'pig', 'cow', 'dog', 'cat',
                'pet', 'livestock', 'non-human'
            ]
        }
        
        # Development stage indicators
        self.development_stages = {
            'preclinical': ['preclinical', 'in vitro', 'cell culture', 'animal model'],
            'clinical': ['clinical trial', 'phase I', 'phase II', 'phase III', 'clinical study'],
            'approved': ['FDA approved', 'approved', 'marketed', 'commercial'],
            'research': ['research', 'discovery', 'experimental', 'investigational']
        }
    
    def load_drug_discovery_patents(self):
        """Load the drug discovery relevant patents"""
        # Try to load from the most recent analysis
        possible_files = [
            "patent_data/final_drug_discovery/foxp2_drug_discovery_summary_20250821_053437.json",
            "patent_data/auto_multi_batch/strategy_4_20250821_065229.json",
            "patent_data/final_drug_discovery/foxp2_top_drug_patents_20250821_053437.csv"
        ]
        
        patents = []
        
        # Try CSV first (has the analyzed patents)
        csv_file = Path("patent_data/final_drug_discovery/foxp2_top_drug_patents_20250821_053437.csv")
        if csv_file.exists():
            print(f"📄 Loading from CSV: {csv_file}")
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    patents.append({
                        'patent_number': row['patent_number'],
                        'title': row['title'],
                        'relevance_score': float(row['relevance_score']),
                        'category': row['category'],
                        'stage': row['stage'],
                        'enhanced': row['enhanced'] == 'True',
                        'abstract': '',  # Will need to get from full dataset
                        'assignee': ''   # Will need to get from full dataset
                    })
        
        print(f"✅ Loaded {len(patents)} drug discovery patents")
        return patents
    
    def enhance_patent_data(self, patents):
        """Enhance patents with abstract and assignee data from full dataset"""
        # Load full dataset to get abstracts
        full_data_files = [
            "patent_data/auto_multi_batch/strategy_4_20250821_065229.json",
            "patent_data/persistent_batches/cumulative_all_patents_20250821_064749.json"
        ]
        
        full_patents = {}
        
        for file_path in full_data_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for patent in data:
                            patent_num = patent.get('patent_number', '')
                            if patent_num:
                                full_patents[patent_num] = patent
                        print(f"   📄 {Path(file_path).name}: +{len(data)} patents")
            except Exception as e:
                continue
        
        # Enhance the drug discovery patents
        enhanced_patents = []
        for patent in patents:
            patent_num = patent['patent_number']
            if patent_num in full_patents:
                full_data = full_patents[patent_num]
                patent['abstract'] = full_data.get('abstract', '')
                patent['assignee'] = full_data.get('assignee', '')
            enhanced_patents.append(patent)
        
        print(f"✅ Enhanced {len(enhanced_patents)} patents with full data")
        return enhanced_patents
    
    def classify_human_relevance(self, patent):
        """Classify patent for human relevance"""
        text_to_analyze = f"{patent['title']} {patent['abstract']}".lower()
        
        # Check for animal-specific exclusions
        for exclude_term in self.human_indicators['exclude_animal']:
            if exclude_term in text_to_analyze:
                return 'animal_specific'
        
        # Check for human indicators
        human_score = 0
        for human_term in self.human_indicators['high_human']:
            if human_term in text_to_analyze:
                human_score += 1
        
        if human_score >= 2:
            return 'high_human'
        elif human_score >= 1:
            return 'likely_human'
        else:
            return 'unclear'
    
    def classify_therapeutic_area(self, patent):
        """Classify patent by therapeutic area"""
        text_to_analyze = f"{patent['title']} {patent['abstract']}".lower()
        
        area_scores = {}
        
        for area, config in self.therapeutic_areas.items():
            score = 0
            matched_keywords = []
            
            for keyword in config['keywords']:
                if keyword.lower() in text_to_analyze:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                area_scores[area] = {
                    'score': score,
                    'keywords': matched_keywords
                }
        
        if area_scores:
            # Return the area with highest score
            best_area = max(area_scores.items(), key=lambda x: x[1]['score'])
            return best_area[0], best_area[1]['keywords']
        else:
            return 'general_therapeutics', []
    
    def extract_specific_indication(self, patent, therapeutic_area):
        """Extract specific indication from patent"""
        text = f"{patent['title']} {patent['abstract']}".lower()
        
        # Common indication patterns
        indication_patterns = [
            r'treating\s+([^,\.]+)',
            r'treatment\s+of\s+([^,\.]+)',
            r'therapy\s+for\s+([^,\.]+)',
            r'therapeutic\s+treatment\s+of\s+([^,\.]+)',
            r'for\s+the\s+treatment\s+of\s+([^,\.]+)',
            r'use\s+in\s+treating\s+([^,\.]+)'
        ]
        
        indications = []
        for pattern in indication_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            indications.extend(matches)
        
        if indications:
            # Return the first meaningful indication
            return indications[0].strip()[:100]  # Limit length
        
        # Fallback to therapeutic area-specific extraction
        if therapeutic_area == 'oncology':
            cancer_types = re.findall(r'(\w+\s+cancer|\w+\s+carcinoma|\w+\s+tumor)', text)
            if cancer_types:
                return cancer_types[0]
        
        elif therapeutic_area == 'neurology_psychiatry':
            neuro_conditions = re.findall(r'(autism|speech disorder|language disorder|cognitive disorder)', text)
            if neuro_conditions:
                return neuro_conditions[0]
        
        return 'unspecified'
    
    def classify_development_stage(self, patent):
        """Classify development stage"""
        text = f"{patent['title']} {patent['abstract']} {patent.get('stage', '')}".lower()
        
        for stage, keywords in self.development_stages.items():
            for keyword in keywords:
                if keyword in text:
                    return stage
        
        # Default based on patent type
        if 'composition' in text or 'formulation' in text:
            return 'preclinical'
        elif 'method' in text:
            return 'research'
        else:
            return 'research'
    
    def filter_and_classify_human_therapeutics(self, patents):
        """Filter for human applications and classify by therapeutic areas"""
        
        print(f"\n🔬 FILTERING FOR HUMAN THERAPEUTIC APPLICATIONS")
        print("=" * 55)
        
        human_therapeutics = []
        classifications = {
            'high_human': 0,
            'likely_human': 0,
            'animal_specific': 0,
            'unclear': 0
        }
        
        for patent in patents:
            # Classify human relevance
            human_relevance = self.classify_human_relevance(patent)
            classifications[human_relevance] += 1
            
            # Only include human-relevant patents
            if human_relevance in ['high_human', 'likely_human']:
                # Classify therapeutic area
                therapeutic_area, keywords = self.classify_therapeutic_area(patent)
                
                # Extract specific indication
                specific_indication = self.extract_specific_indication(patent, therapeutic_area)
                
                # Classify development stage
                development_stage = self.classify_development_stage(patent)
                
                classification = TherapeuticClassification(
                    patent_number=patent['patent_number'],
                    title=patent['title'],
                    relevance_score=patent['relevance_score'],
                    therapeutic_area=therapeutic_area,
                    human_relevance=human_relevance,
                    specific_indication=specific_indication,
                    development_stage=development_stage,
                    abstract=patent.get('abstract', ''),
                    assignee=patent.get('assignee', '')
                )
                
                human_therapeutics.append(classification)
        
        print(f"📊 Human relevance classification:")
        for category, count in classifications.items():
            print(f"   {category}: {count} patents")
        
        print(f"\n✅ Selected {len(human_therapeutics)} human therapeutic patents")
        return human_therapeutics
    
    def sort_by_therapeutic_areas(self, human_therapeutics):
        """Sort and group patents by therapeutic areas"""
        
        # Group by therapeutic area
        therapeutic_groups = {}
        
        for patent in human_therapeutics:
            area = patent.therapeutic_area
            if area not in therapeutic_groups:
                therapeutic_groups[area] = []
            therapeutic_groups[area].append(patent)
        
        # Sort each group by relevance score
        for area in therapeutic_groups:
            therapeutic_groups[area].sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Sort areas by number of patents (largest first)
        sorted_areas = sorted(therapeutic_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        return sorted_areas
    
    def generate_therapeutic_report(self, sorted_therapeutic_areas):
        """Generate comprehensive therapeutic areas report"""
        
        print(f"\n🎯 HUMAN THERAPEUTIC APPLICATIONS BY AREA")
        print("=" * 55)
        
        total_human_patents = sum(len(patents) for _, patents in sorted_therapeutic_areas)
        
        for area_name, patents in sorted_therapeutic_areas:
            display_name = self.therapeutic_areas.get(area_name, {}).get('display_name', area_name.title())
            
            print(f"\n🏥 {display_name} ({len(patents)} patents)")
            print("-" * 50)
            
            # Show top 5 patents in this area
            for i, patent in enumerate(patents[:5], 1):
                print(f"{i}. {patent.patent_number} - Score: {patent.relevance_score:.1f}")
                print(f"   Title: {patent.title[:70]}...")
                print(f"   Indication: {patent.specific_indication}")
                print(f"   Stage: {patent.development_stage}")
                if patent.assignee:
                    print(f"   Assignee: {patent.assignee[:50]}...")
                print()
            
            if len(patents) > 5:
                print(f"   ... and {len(patents) - 5} more patents in this area")
                print()
        
        # Summary statistics
        print(f"\n📊 THERAPEUTIC AREAS SUMMARY")
        print("=" * 35)
        print(f"Total human therapeutic patents: {total_human_patents}")
        print(f"Therapeutic areas covered: {len(sorted_therapeutic_areas)}")
        
        # Top therapeutic areas
        print(f"\nTop therapeutic areas by patent count:")
        for area_name, patents in sorted_therapeutic_areas[:5]:
            display_name = self.therapeutic_areas.get(area_name, {}).get('display_name', area_name.title())
            print(f"  {display_name}: {len(patents)} patents")
    
    def save_therapeutic_results(self, sorted_therapeutic_areas):
        """Save results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Flatten all patents for CSV export
        all_human_patents = []
        for area_name, patents in sorted_therapeutic_areas:
            display_name = self.therapeutic_areas.get(area_name, {}).get('display_name', area_name.title())
            for patent in patents:
                all_human_patents.append({
                    'patent_number': patent.patent_number,
                    'title': patent.title,
                    'relevance_score': patent.relevance_score,
                    'therapeutic_area': display_name,
                    'therapeutic_area_code': area_name,
                    'human_relevance': patent.human_relevance,
                    'specific_indication': patent.specific_indication,
                    'development_stage': patent.development_stage,
                    'abstract': patent.abstract[:500] + "..." if len(patent.abstract) > 500 else patent.abstract,
                    'assignee': patent.assignee
                })
        
        # Save as CSV
        csv_file = self.results_dir / f"human_therapeutic_patents_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if all_human_patents:
                writer = csv.DictWriter(f, fieldnames=all_human_patents[0].keys())
                writer.writeheader()
                writer.writerows(all_human_patents)
        
        # Save detailed JSON by therapeutic area
        json_file = self.results_dir / f"therapeutic_areas_detailed_{timestamp}.json"
        detailed_data = {}
        
        for area_name, patents in sorted_therapeutic_areas:
            display_name = self.therapeutic_areas.get(area_name, {}).get('display_name', area_name.title())
            detailed_data[display_name] = [
                {
                    'patent_number': p.patent_number,
                    'title': p.title,
                    'relevance_score': p.relevance_score,
                    'human_relevance': p.human_relevance,
                    'specific_indication': p.specific_indication,
                    'development_stage': p.development_stage,
                    'abstract': p.abstract,
                    'assignee': p.assignee
                }
                for p in patents
            ]
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Human Therapeutic Results Saved:")
        print(f"   📊 CSV: {csv_file}")
        print(f"   📄 JSON: {json_file}")
        print(f"   📈 Total patents: {len(all_human_patents)}")
        
        return csv_file, json_file

def main():
    """Main function"""
    filter_analyzer = HumanTherapeuticFilter()
    
    # Load drug discovery patents
    patents = filter_analyzer.load_drug_discovery_patents()
    
    # Enhance with full data
    enhanced_patents = filter_analyzer.enhance_patent_data(patents)
    
    # Filter for human therapeutics
    human_therapeutics = filter_analyzer.filter_and_classify_human_therapeutics(enhanced_patents)
    
    # Sort by therapeutic areas
    sorted_areas = filter_analyzer.sort_by_therapeutic_areas(human_therapeutics)
    
    # Generate report
    filter_analyzer.generate_therapeutic_report(sorted_areas)
    
    # Save results
    csv_file, json_file = filter_analyzer.save_therapeutic_results(sorted_areas)
    
    print(f"\n✅ HUMAN THERAPEUTIC ANALYSIS COMPLETE!")

if __name__ == "__main__":
    main()