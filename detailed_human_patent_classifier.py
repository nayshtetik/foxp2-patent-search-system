#!/usr/bin/env python3
"""
Detailed classification of 11 human therapeutic patents by:
- Molecule types
- Country of origin  
- Academic vs corporate affiliation
- Drug discovery stage
"""

import json
import csv
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class DetailedPatentClassification:
    patent_number: str
    title: str
    relevance_score: float
    
    # Molecule classification
    molecule_type: str
    molecule_subtype: str
    target_pathway: str
    
    # Geographic classification
    filing_country: str
    inventor_countries: List[str]
    assignee_country: str
    
    # Institutional classification
    institution_type: str  # academic, corporate, government, mixed
    primary_assignee: str
    assignee_classification: str
    
    # Drug discovery classification
    discovery_stage: str
    development_phase: str
    clinical_readiness: str
    regulatory_pathway: str
    
    # Additional metadata
    therapeutic_area: str
    mechanism_of_action: str
    abstract: str

class DetailedHumanPatentClassifier:
    """Detailed classifier for human therapeutic patents"""
    
    def __init__(self):
        self.results_dir = Path("patent_data/detailed_classification")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Molecule type classification
        self.molecule_types = {
            'small_molecule': {
                'keywords': [
                    'small molecule', 'compound', 'inhibitor', 'agonist', 'antagonist',
                    'ligand', 'drug', 'chemical', 'pharmaceutical compound',
                    'quinoxalinone', 'glutarimide', 'tricyclic', 'GSK-3 inhibitor',
                    'kinase inhibitor', 'modulator', 'synthetic compound'
                ],
                'subtypes': {
                    'kinase_inhibitor': ['kinase inhibitor', 'GSK-3', 'kinase'],
                    'receptor_modulator': ['receptor', 'agonist', 'antagonist', 'modulator'],
                    'enzyme_inhibitor': ['inhibitor', 'enzyme inhibitor'],
                    'synthetic_compound': ['synthetic', 'chemical compound']
                }
            },
            'biologics': {
                'keywords': [
                    'antibody', 'protein', 'peptide', 'enzyme', 'interferon',
                    'cytokine', 'immunoglobulin', 'therapeutic protein',
                    'recombinant protein', 'monoclonal antibody'
                ],
                'subtypes': {
                    'antibody': ['antibody', 'immunoglobulin', 'monoclonal'],
                    'protein_therapy': ['protein', 'enzyme', 'therapeutic protein'],
                    'cytokine': ['interferon', 'cytokine', 'interleukin']
                }
            },
            'nucleic_acid': {
                'keywords': [
                    'mRNA', 'RNA', 'DNA', 'oligonucleotide', 'nucleic acid',
                    'antisense', 'siRNA', 'microRNA', 'guide RNA', 'genetic'
                ],
                'subtypes': {
                    'mRNA': ['mRNA', 'messenger RNA'],
                    'therapeutic_RNA': ['RNA', 'siRNA', 'antisense'],
                    'oligonucleotide': ['oligonucleotide', 'nucleic acid']
                }
            },
            'cell_therapy': {
                'keywords': [
                    'cell therapy', 'cellular therapy', 'cell transplantation',
                    'stem cell', 'therapeutic cells', 'transplantation'
                ],
                'subtypes': {
                    'stem_cell': ['stem cell'],
                    'cell_transplant': ['cell transplantation', 'transplantation'],
                    'cellular_therapy': ['cellular therapy', 'cell therapy']
                }
            },
            'drug_delivery': {
                'keywords': [
                    'nanoparticle', 'lipid nanoparticle', 'formulation',
                    'pharmaceutical composition', 'delivery system',
                    'controlled release', 'sustained release'
                ],
                'subtypes': {
                    'nanoparticle': ['nanoparticle', 'lipid nanoparticle'],
                    'formulation': ['formulation', 'pharmaceutical composition'],
                    'delivery_system': ['delivery system', 'controlled release']
                }
            }
        }
        
        # Country mapping from patent prefixes
        self.country_codes = {
            'US': 'United States',
            'EP': 'European Patent Office',
            'WO': 'World Intellectual Property Organization',
            'CN': 'China',
            'JP': 'Japan',
            'CA': 'Canada',
            'AU': 'Australia',
            'HK': 'Hong Kong',
            'KR': 'South Korea',
            'DE': 'Germany',
            'FR': 'France',
            'GB': 'United Kingdom'
        }
        
        # Institution type keywords
        self.institution_keywords = {
            'academic': [
                'university', 'college', 'institute', 'research institute',
                'medical center', 'hospital', 'school of medicine',
                'national university', 'state university', 'tech university'
            ],
            'corporate': [
                'inc', 'ltd', 'corp', 'company', 'corporation', 'pharmaceuticals',
                'therapeutics', 'biotech', 'biotechnology', 'pharma',
                'ag', 'gmbh', 'sa', 'plc', 'co.'
            ],
            'government': [
                'national', 'ministry', 'department', 'government',
                'public health', 'nih', 'cdc', 'fda'
            ]
        }
        
        # Drug discovery stages
        self.discovery_stages = {
            'target_identification': [
                'target identification', 'target discovery', 'target validation',
                'identifying drug targets', 'target protein'
            ],
            'lead_discovery': [
                'lead discovery', 'compound screening', 'hit identification',
                'lead compound', 'drug discovery'
            ],
            'lead_optimization': [
                'lead optimization', 'structure-activity relationship',
                'medicinal chemistry', 'optimization', 'analog'
            ],
            'preclinical': [
                'preclinical', 'pharmaceutical composition', 'formulation',
                'therapeutic composition', 'drug composition'
            ],
            'clinical_development': [
                'clinical trial', 'phase I', 'phase II', 'phase III',
                'clinical study', 'human trial'
            ],
            'regulatory': [
                'approved', 'FDA approved', 'marketed', 'commercial',
                'regulatory approval'
            ]
        }
    
    def load_human_patents(self):
        """Load the 11 human therapeutic patents"""
        csv_file = Path("patent_data/human_therapeutics/human_therapeutic_patents_20250821_065621.csv")
        
        patents = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                patents.append(row)
        
        print(f"✅ Loaded {len(patents)} human therapeutic patents for detailed classification")
        return patents
    
    def classify_molecule_type(self, patent):
        """Classify molecule type and subtype"""
        text = f"{patent['title']} {patent['abstract']}".lower()
        
        molecule_scores = {}
        for mol_type, config in self.molecule_types.items():
            score = 0
            for keyword in config['keywords']:
                if keyword.lower() in text:
                    score += 1
            if score > 0:
                molecule_scores[mol_type] = score
        
        if molecule_scores:
            best_type = max(molecule_scores.items(), key=lambda x: x[1])[0]
            
            # Find subtype
            subtype = 'general'
            if best_type in self.molecule_types:
                subtypes = self.molecule_types[best_type].get('subtypes', {})
                for sub_name, sub_keywords in subtypes.items():
                    for keyword in sub_keywords:
                        if keyword.lower() in text:
                            subtype = sub_name
                            break
                    if subtype != 'general':
                        break
            
            return best_type, subtype
        else:
            return 'unclassified', 'unknown'
    
    def extract_geographic_info(self, patent):
        """Extract geographic information"""
        patent_number = patent['patent_number']
        
        # Extract filing country from patent number prefix
        filing_country = 'Unknown'
        for code, country in self.country_codes.items():
            if patent_number.startswith(code):
                filing_country = country
                break
        
        # Extract assignee country from assignee info (if available)
        assignee = patent.get('assignee', '')
        assignee_country = 'Unknown'
        
        # Look for country indicators in assignee
        country_indicators = {
            'Singapore': ['singapore'],
            'United States': ['usa', 'united states', 'america', 'inc', 'corp'],
            'China': ['china', 'chinese', 'beijing', 'shanghai'],
            'Japan': ['japan', 'japanese', 'tokyo', 'osaka'],
            'Germany': ['germany', 'german', 'gmbh', 'ag'],
            'United Kingdom': ['uk', 'united kingdom', 'britain', 'ltd'],
            'Switzerland': ['switzerland', 'swiss'],
            'France': ['france', 'french', 'sa'],
            'Canada': ['canada', 'canadian']
        }
        
        assignee_lower = assignee.lower()
        for country, indicators in country_indicators.items():
            for indicator in indicators:
                if indicator in assignee_lower:
                    assignee_country = country
                    break
            if assignee_country != 'Unknown':
                break
        
        return filing_country, [assignee_country], assignee_country
    
    def classify_institution_type(self, patent):
        """Classify institution type and assignee"""
        assignee = patent.get('assignee', '').lower()
        
        if not assignee or assignee == 'nan':
            return 'unknown', 'Unknown', 'unclassified'
        
        # Score different institution types
        scores = {'academic': 0, 'corporate': 0, 'government': 0}
        
        for inst_type, keywords in self.institution_keywords.items():
            for keyword in keywords:
                if keyword in assignee:
                    scores[inst_type] += 1
        
        # Determine primary type
        if scores['academic'] > scores['corporate'] and scores['academic'] > scores['government']:
            institution_type = 'academic'
        elif scores['corporate'] > scores['government']:
            institution_type = 'corporate'
        elif scores['government'] > 0:
            institution_type = 'government'
        else:
            institution_type = 'unknown'
        
        # Extract primary assignee name (first part before comma)
        primary_assignee = assignee.split(',')[0].strip().title()
        if len(primary_assignee) > 60:
            primary_assignee = primary_assignee[:60] + "..."
        
        # Detailed classification
        if 'university' in assignee:
            assignee_classification = 'University'
        elif 'therapeutics' in assignee or 'pharma' in assignee:
            assignee_classification = 'Pharmaceutical Company'
        elif 'biotech' in assignee:
            assignee_classification = 'Biotechnology Company'
        elif 'inc' in assignee or 'corp' in assignee:
            assignee_classification = 'Corporation'
        elif 'institute' in assignee:
            assignee_classification = 'Research Institute'
        else:
            assignee_classification = 'Other'
        
        return institution_type, primary_assignee, assignee_classification
    
    def classify_discovery_stage(self, patent):
        """Classify drug discovery and development stage"""
        text = f"{patent['title']} {patent['abstract']} {patent.get('development_stage', '')}".lower()
        
        # Score different stages
        stage_scores = {}
        for stage, keywords in self.discovery_stages.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 1
            if score > 0:
                stage_scores[stage] = score
        
        # Determine primary stage
        if stage_scores:
            discovery_stage = max(stage_scores.items(), key=lambda x: x[1])[0]
        else:
            discovery_stage = 'research'
        
        # Determine development phase
        if 'clinical trial' in text or 'phase' in text:
            development_phase = 'Clinical Development'
        elif 'preclinical' in text or 'pharmaceutical composition' in text:
            development_phase = 'Preclinical Development'
        elif 'optimization' in text or 'lead compound' in text:
            development_phase = 'Lead Optimization'
        elif 'discovery' in text or 'screening' in text:
            development_phase = 'Drug Discovery'
        else:
            development_phase = 'Basic Research'
        
        # Clinical readiness assessment
        clinical_indicators = ['clinical', 'trial', 'therapeutic', 'treatment', 'patient']
        clinical_score = sum(1 for indicator in clinical_indicators if indicator in text)
        
        if clinical_score >= 3:
            clinical_readiness = 'High'
        elif clinical_score >= 2:
            clinical_readiness = 'Medium'
        else:
            clinical_readiness = 'Low'
        
        # Regulatory pathway
        if 'drug' in text or 'pharmaceutical' in text:
            regulatory_pathway = 'Drug Approval (FDA/EMA)'
        elif 'biological' in text or 'protein' in text or 'antibody' in text:
            regulatory_pathway = 'Biologics License'
        elif 'device' in text or 'diagnostic' in text:
            regulatory_pathway = 'Medical Device'
        else:
            regulatory_pathway = 'To Be Determined'
        
        return discovery_stage, development_phase, clinical_readiness, regulatory_pathway
    
    def extract_mechanism_of_action(self, patent):
        """Extract mechanism of action"""
        text = f"{patent['title']} {patent['abstract']}".lower()
        
        # Common mechanisms
        mechanisms = {
            'Protein Degradation': ['crbn', 'degradation', 'protac', 'ubiquitin'],
            'Kinase Inhibition': ['kinase inhibitor', 'gsk-3', 'kinase'],
            'Receptor Modulation': ['receptor', 'agonist', 'antagonist', 'modulator'],
            'Gene Expression': ['mrna', 'rna', 'gene expression', 'transcription'],
            'Immune Modulation': ['immune', 'antibody', 'interferon', 'cytokine'],
            'Cell Therapy': ['cell therapy', 'transplantation', 'cellular'],
            'Drug Delivery': ['delivery', 'nanoparticle', 'formulation', 'composition'],
            'Target Identification': ['target', 'screening', 'identification']
        }
        
        for mechanism, keywords in mechanisms.items():
            for keyword in keywords:
                if keyword in text:
                    return mechanism
        
        return 'Unknown/Other'
    
    def create_detailed_classification(self, patents):
        """Create detailed classification for all patents"""
        
        print(f"\n🔬 DETAILED CLASSIFICATION OF 11 HUMAN THERAPEUTIC PATENTS")
        print("=" * 65)
        
        detailed_patents = []
        
        for patent in patents:
            # Molecule classification
            molecule_type, molecule_subtype = self.classify_molecule_type(patent)
            
            # Geographic classification
            filing_country, inventor_countries, assignee_country = self.extract_geographic_info(patent)
            
            # Institution classification
            institution_type, primary_assignee, assignee_classification = self.classify_institution_type(patent)
            
            # Discovery stage classification
            discovery_stage, development_phase, clinical_readiness, regulatory_pathway = self.classify_discovery_stage(patent)
            
            # Extract mechanism
            mechanism_of_action = self.extract_mechanism_of_action(patent)
            
            # Extract target pathway
            target_pathway = 'FOXP2-related'  # All patents are FOXP2-related
            
            classification = DetailedPatentClassification(
                patent_number=patent['patent_number'],
                title=patent['title'],
                relevance_score=float(patent['relevance_score']),
                
                molecule_type=molecule_type,
                molecule_subtype=molecule_subtype,
                target_pathway=target_pathway,
                
                filing_country=filing_country,
                inventor_countries=inventor_countries,
                assignee_country=assignee_country,
                
                institution_type=institution_type,
                primary_assignee=primary_assignee,
                assignee_classification=assignee_classification,
                
                discovery_stage=discovery_stage,
                development_phase=development_phase,
                clinical_readiness=clinical_readiness,
                regulatory_pathway=regulatory_pathway,
                
                therapeutic_area=patent['therapeutic_area'],
                mechanism_of_action=mechanism_of_action,
                abstract=patent.get('abstract', '')[:300] + "..." if len(patent.get('abstract', '')) > 300 else patent.get('abstract', '')
            )
            
            detailed_patents.append(classification)
        
        return detailed_patents
    
    def generate_detailed_report(self, detailed_patents):
        """Generate comprehensive detailed report"""
        
        print(f"\n📊 DETAILED PATENT CLASSIFICATION ANALYSIS")
        print("=" * 55)
        
        # Sort by relevance score
        detailed_patents.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Molecule type analysis
        molecule_counts = {}
        for patent in detailed_patents:
            mol_type = patent.molecule_type
            if mol_type not in molecule_counts:
                molecule_counts[mol_type] = 0
            molecule_counts[mol_type] += 1
        
        print(f"\n🧬 MOLECULE TYPE DISTRIBUTION:")
        for mol_type, count in sorted(molecule_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {mol_type.replace('_', ' ').title()}: {count} patents")
        
        # Geographic analysis
        country_counts = {}
        for patent in detailed_patents:
            country = patent.filing_country
            if country not in country_counts:
                country_counts[country] = 0
            country_counts[country] += 1
        
        print(f"\n🌍 GEOGRAPHIC DISTRIBUTION (Filing Country):")
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {country}: {count} patents")
        
        # Institution analysis
        institution_counts = {}
        for patent in detailed_patents:
            inst_type = patent.institution_type
            if inst_type not in institution_counts:
                institution_counts[inst_type] = 0
            institution_counts[inst_type] += 1
        
        print(f"\n🏢 INSTITUTIONAL DISTRIBUTION:")
        for inst_type, count in sorted(institution_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {inst_type.title()}: {count} patents")
        
        # Development stage analysis
        stage_counts = {}
        for patent in detailed_patents:
            stage = patent.development_phase
            if stage not in stage_counts:
                stage_counts[stage] = 0
            stage_counts[stage] += 1
        
        print(f"\n🔬 DEVELOPMENT STAGE DISTRIBUTION:")
        for stage, count in sorted(stage_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {stage}: {count} patents")
        
        # Detailed patent listing
        print(f"\n📄 DETAILED PATENT CLASSIFICATIONS:")
        print("=" * 50)
        
        for i, patent in enumerate(detailed_patents, 1):
            print(f"\n{i}. {patent.patent_number} (Score: {patent.relevance_score:.1f})")
            print(f"   Title: {patent.title[:60]}...")
            print(f"   🧬 Molecule: {patent.molecule_type.replace('_', ' ').title()} ({patent.molecule_subtype})")
            print(f"   🌍 Country: {patent.filing_country}")
            print(f"   🏢 Institution: {patent.institution_type.title()} - {patent.assignee_classification}")
            print(f"   🔬 Stage: {patent.development_phase}")
            print(f"   ⚡ Mechanism: {patent.mechanism_of_action}")
            print(f"   🎯 Clinical Readiness: {patent.clinical_readiness}")
            if patent.primary_assignee != 'Unknown':
                print(f"   🏷️ Assignee: {patent.primary_assignee}")
    
    def save_detailed_results(self, detailed_patents):
        """Save detailed classification results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert to dictionaries for export
        export_data = []
        for patent in detailed_patents:
            export_data.append({
                'patent_number': patent.patent_number,
                'title': patent.title,
                'relevance_score': patent.relevance_score,
                'molecule_type': patent.molecule_type,
                'molecule_subtype': patent.molecule_subtype,
                'target_pathway': patent.target_pathway,
                'filing_country': patent.filing_country,
                'assignee_country': patent.assignee_country,
                'institution_type': patent.institution_type,
                'primary_assignee': patent.primary_assignee,
                'assignee_classification': patent.assignee_classification,
                'discovery_stage': patent.discovery_stage,
                'development_phase': patent.development_phase,
                'clinical_readiness': patent.clinical_readiness,
                'regulatory_pathway': patent.regulatory_pathway,
                'therapeutic_area': patent.therapeutic_area,
                'mechanism_of_action': patent.mechanism_of_action,
                'abstract': patent.abstract
            })
        
        # Save as CSV
        csv_file = self.results_dir / f"detailed_human_patent_classification_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if export_data:
                writer = csv.DictWriter(f, fieldnames=export_data[0].keys())
                writer.writeheader()
                writer.writerows(export_data)
        
        # Save as JSON
        json_file = self.results_dir / f"detailed_human_patent_classification_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed Classification Results Saved:")
        print(f"   📊 CSV: {csv_file}")
        print(f"   📄 JSON: {json_file}")
        
        return csv_file, json_file

def main():
    """Main function"""
    classifier = DetailedHumanPatentClassifier()
    
    # Load human patents
    patents = classifier.load_human_patents()
    
    # Create detailed classification
    detailed_patents = classifier.create_detailed_classification(patents)
    
    # Generate report
    classifier.generate_detailed_report(detailed_patents)
    
    # Save results
    csv_file, json_file = classifier.save_detailed_results(detailed_patents)
    
    print(f"\n✅ DETAILED CLASSIFICATION COMPLETE!")
    print(f"📊 Classified {len(detailed_patents)} human therapeutic patents")

if __name__ == "__main__":
    main()