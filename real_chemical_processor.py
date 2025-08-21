import requests
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import time

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors, Crippen
    from rdkit.Chem.Draw import rdMolDraw2D
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("RDKit not available - chemical structure processing will be limited")

from base_agent import BasePatentAgent, PatentData, PatentDataType, Task

@dataclass
class RealChemicalStructure:
    compound_name: str
    smiles: Optional[str] = None
    inchi: Optional[str] = None
    inchi_key: Optional[str] = None
    molecular_formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    cas_number: Optional[str] = None
    iupac_name: Optional[str] = None
    synonyms: List[str] = None
    structure_image_svg: Optional[str] = None
    pubchem_cid: Optional[int] = None
    chemspider_id: Optional[str] = None
    
    # Drug-likeness properties
    lipinski_compliant: Optional[bool] = None
    logp: Optional[float] = None
    polar_surface_area: Optional[float] = None
    rotatable_bonds: Optional[int] = None
    hbd_count: Optional[int] = None  # Hydrogen bond donors
    hba_count: Optional[int] = None  # Hydrogen bond acceptors
    
    # Source information
    source_database: str = "unknown"
    confidence_score: float = 0.0
    
    def __post_init__(self):
        if self.synonyms is None:
            self.synonyms = []

class RealChemicalProcessor(BasePatentAgent):
    """Real chemical structure processing using actual chemical databases and RDKit"""
    
    def __init__(self, agent_id: str = "real_chemical_processor_001"):
        super().__init__(
            agent_id=agent_id,
            name="Real Chemical Processor",
            description="Processes real chemical structures using PubChem, ChemSpider, and RDKit"
        )
        
        # Chemical database APIs
        self.apis = {
            'pubchem': 'https://pubchem.ncbi.nlm.nih.gov/rest/pug',
            'chemspider': 'https://www.chemspider.com/Search.asmx',  # Requires API key
            'opsin': 'https://opsin.ch.cam.ac.uk/opsin',  # Chemical name to structure
            'cir': 'https://cactus.nci.nih.gov/chemical/structure'  # NCI Chemical Identifier Resolver
        }
        
        self.setup_rdkit()
    
    def setup_rdkit(self):
        """Setup RDKit if available"""
        if RDKIT_AVAILABLE:
            self.logger.info("RDKit available - full chemical processing enabled")
        else:
            self.logger.warning("RDKit not available - limited chemical processing")
    
    def get_capabilities(self) -> List[str]:
        capabilities = [
            "chemical_name_resolution",
            "structure_lookup",
            "property_calculation",
            "drug_likeness_assessment",
            "chemical_database_search",
            "structure_image_generation"
        ]
        
        if RDKIT_AVAILABLE:
            capabilities.extend([
                "smiles_validation",
                "molecular_descriptor_calculation",
                "substructure_search",
                "similarity_search",
                "structure_standardization"
            ])
        
        return capabilities
    
    def get_supported_input_types(self) -> List[PatentDataType]:
        return [PatentDataType.PATENT_DOCUMENT, PatentDataType.QUERY_RESULT]
    
    def get_output_type(self) -> PatentDataType:
        return PatentDataType.CHEMICAL_STRUCTURE
    
    def process_task(self, task: Task) -> PatentData:
        if task.type == "extract_chemicals":
            return self._extract_chemicals_from_patent(task.input_data)
        elif task.type == "resolve_chemical":
            return self._resolve_chemical_structure(task.input_data)
        elif task.type == "analyze_drug_likeness":
            return self._analyze_drug_likeness(task.input_data)
        else:
            raise ValueError(f"Unsupported task type: {task.type}")
    
    def _extract_chemicals_from_patent(self, patent_data: Union[PatentData, List[PatentData]]) -> PatentData:
        """Extract and process real chemical structures from patent data"""
        
        # Extract patent text
        if isinstance(patent_data, list):
            patent_data = patent_data[0]
        
        if patent_data.type == PatentDataType.QUERY_RESULT:
            patents_list = patent_data.content.get('patents', [])
            if not patents_list:
                raise ValueError("No patents found in query results")
            patent_info = patents_list[0]
            text_content = patent_info.get('title', '') + ' ' + patent_info.get('abstract', '')
            patent_number = patent_info.get('patent_number', '')
        else:
            patent_doc = patent_data.content.get('patent_document', {})
            text_content = patent_doc.get('title', '') + ' ' + patent_doc.get('abstract', '') + ' ' + patent_doc.get('description', '')
            patent_number = patent_doc.get('patent_number', '')
        
        self.logger.info(f"Extracting chemicals from patent {patent_number}")
        
        # Find chemical mentions in text
        chemical_mentions = self._find_chemical_mentions(text_content)
        
        # Process each chemical mention
        chemical_structures = []
        for mention in chemical_mentions:
            try:
                structure = self._process_chemical_mention(mention)
                if structure:
                    chemical_structures.append(structure)
            except Exception as e:
                self.logger.warning(f"Could not process chemical mention '{mention}': {e}")
                continue
        
        return PatentData(
            id=f"chemicals_extracted_{patent_number}_{int(time.time())}",
            type=PatentDataType.CHEMICAL_STRUCTURE,
            content={
                "patent_number": patent_number,
                "chemical_structures": [struct.__dict__ for struct in chemical_structures],
                "total_structures_found": len(chemical_structures),
                "chemical_mentions": chemical_mentions,
                "extraction_method": "real_database_lookup"
            },
            metadata={
                "extraction_timestamp": time.time(),
                "rdkit_available": RDKIT_AVAILABLE,
                "databases_used": ["pubchem", "cir", "opsin"]
            }
        )
    
    def _find_chemical_mentions(self, text: str) -> List[str]:
        """Find chemical names, formulas, and identifiers in text using improved patterns"""
        mentions = set()
        
        # Molecular formulas (improved pattern)
        formula_pattern = r'\b[A-Z][a-z]?(?:\d+[A-Z][a-z]?\d*)*\b'
        formulas = re.findall(formula_pattern, text)
        for formula in formulas:
            if self._looks_like_chemical_formula(formula):
                mentions.add(formula)
        
        # CAS numbers
        cas_pattern = r'\b\d{2,7}-\d{2}-\d\b'
        cas_numbers = re.findall(cas_pattern, text)
        mentions.update(cas_numbers)
        
        # Common pharmaceutical/chemical terms
        pharma_patterns = [
            r'\b\w*(?:yl|ine|ane|ene|yne|ide|ate|ite|ol|al)\b',  # Chemical suffixes
            r'\b(?:meth|eth|prop|but|pent|hex|hept|oct)yl\w*\b',  # Alkyl groups
            r'\b\w*(?:benzene|phenol|aniline|pyridine|indole|furan|thiophene)\w*\b',  # Aromatics
            r'\b\w*(?:amide|ester|ether|ketone|aldehyde|acid)\b',  # Functional groups
        ]
        
        for pattern in pharma_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) > 3 and len(match) < 50:  # Reasonable length
                    mentions.add(match)
        
        # NIB-specific compounds (for FOXP2 search)
        nib_pattern = r'\bNIB-?\d+\w*\b'
        nib_compounds = re.findall(nib_pattern, text, re.IGNORECASE)
        mentions.update(nib_compounds)
        
        # FOXP2-related terms
        foxp2_compounds = [
            "FOXP2 modulator", "FOXP2 inhibitor", "FOXP2 activator",
            "forkhead modulator", "transcription factor modulator"
        ]
        
        for term in foxp2_compounds:
            if term.lower() in text.lower():
                mentions.add(term)
        
        return list(mentions)
    
    def _looks_like_chemical_formula(self, formula: str) -> bool:
        """Enhanced chemical formula detection"""
        # Must contain at least one element symbol and one number
        has_element = bool(re.search(r'[A-Z][a-z]?', formula))
        has_number = bool(re.search(r'\d', formula))
        reasonable_length = 2 <= len(formula) <= 30
        
        # Common non-chemical terms to exclude
        exclude_terms = {'AND', 'THE', 'FOR', 'NOT', 'BUT', 'CAN', 'MAY', 'DNA', 'RNA', 'PCR', 'HIV', 'FDA', 'NIH'}
        if formula.upper() in exclude_terms:
            return False
        
        return has_element and has_number and reasonable_length
    
    def _process_chemical_mention(self, mention: str) -> Optional[RealChemicalStructure]:
        """Process a chemical mention using real databases"""
        
        # Try different resolution methods in order of reliability
        
        # 1. Try PubChem first (most comprehensive)
        structure = self._resolve_via_pubchem(mention)
        if structure:
            return structure
        
        # 2. Try Chemical Identifier Resolver (NCI)
        structure = self._resolve_via_cir(mention)
        if structure:
            return structure
        
        # 3. Try OPSIN for chemical names
        structure = self._resolve_via_opsin(mention)
        if structure:
            return structure
        
        # 4. If it looks like a molecular formula, create basic structure
        if self._looks_like_chemical_formula(mention):
            return RealChemicalStructure(
                compound_name=mention,
                molecular_formula=mention,
                source_database="formula_extraction",
                confidence_score=0.3
            )
        
        return None
    
    def _resolve_via_pubchem(self, identifier: str) -> Optional[RealChemicalStructure]:
        """Resolve chemical structure via PubChem API"""
        try:
            # First, search for the compound
            search_url = f"{self.apis['pubchem']}/compound/name/{requests.utils.quote(identifier)}/JSON"
            
            response = requests.get(search_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if 'PC_Compounds' in data:
                    compound = data['PC_Compounds'][0]
                    
                    # Extract properties
                    props = compound.get('props', [])
                    structure = RealChemicalStructure(
                        compound_name=identifier,
                        source_database="pubchem",
                        confidence_score=0.9
                    )
                    
                    # Parse compound properties
                    for prop in props:
                        urn = prop.get('urn', {})
                        label = urn.get('label', '')
                        
                        if label == 'Molecular Formula':
                            structure.molecular_formula = prop.get('value', {}).get('sval', '')
                        elif label == 'Molecular Weight':
                            structure.molecular_weight = prop.get('value', {}).get('fval', 0.0)
                        elif label == 'SMILES' and prop.get('value', {}).get('sval'):
                            structure.smiles = prop.get('value', {}).get('sval', '')
                        elif label == 'InChI':
                            structure.inchi = prop.get('value', {}).get('sval', '')
                        elif label == 'InChI Key':
                            structure.inchi_key = prop.get('value', {}).get('sval', '')
                    
                    # Get CID for additional data
                    if 'id' in compound and 'id' in compound['id']:
                        cid = compound['id']['id']
                        structure.pubchem_cid = cid
                        
                        # Get additional properties and synonyms
                        self._enrich_from_pubchem_cid(structure, cid)
                    
                    # Calculate drug-likeness if SMILES available
                    if structure.smiles and RDKIT_AVAILABLE:
                        self._calculate_drug_properties(structure)
                    
                    return structure
            
        except Exception as e:
            self.logger.warning(f"PubChem resolution failed for '{identifier}': {e}")
        
        return None
    
    def _resolve_via_cir(self, identifier: str) -> Optional[RealChemicalStructure]:
        """Resolve via NCI Chemical Identifier Resolver"""
        try:
            # Get SMILES
            smiles_url = f"{self.apis['cir']}/{requests.utils.quote(identifier)}/smiles"
            response = requests.get(smiles_url, timeout=10)
            
            if response.status_code == 200 and response.text.strip():
                smiles = response.text.strip()
                
                if smiles and smiles != 'Chemical not found':
                    structure = RealChemicalStructure(
                        compound_name=identifier,
                        smiles=smiles,
                        source_database="cir",
                        confidence_score=0.7
                    )
                    
                    # Try to get additional properties
                    try:
                        # Molecular formula
                        formula_url = f"{self.apis['cir']}/{requests.utils.quote(identifier)}/formula"
                        formula_response = requests.get(formula_url, timeout=5)
                        if formula_response.status_code == 200:
                            structure.molecular_formula = formula_response.text.strip()
                        
                        # Molecular weight
                        mw_url = f"{self.apis['cir']}/{requests.utils.quote(identifier)}/mw"
                        mw_response = requests.get(mw_url, timeout=5)
                        if mw_response.status_code == 200:
                            try:
                                structure.molecular_weight = float(mw_response.text.strip())
                            except ValueError:
                                pass
                    
                    except Exception:
                        pass  # Additional properties are optional
                    
                    # Calculate drug properties if possible
                    if RDKIT_AVAILABLE:
                        self._calculate_drug_properties(structure)
                    
                    return structure
        
        except Exception as e:
            self.logger.warning(f"CIR resolution failed for '{identifier}': {e}")
        
        return None
    
    def _resolve_via_opsin(self, chemical_name: str) -> Optional[RealChemicalStructure]:
        """Resolve chemical name to structure using OPSIN"""
        try:
            # OPSIN converts chemical names to structures
            opsin_url = f"{self.apis['opsin']}/{requests.utils.quote(chemical_name)}.smi"
            
            response = requests.get(opsin_url, timeout=10)
            if response.status_code == 200 and response.text.strip():
                smiles = response.text.strip()
                
                if smiles and not smiles.startswith('Could not parse'):
                    structure = RealChemicalStructure(
                        compound_name=chemical_name,
                        smiles=smiles,
                        source_database="opsin",
                        confidence_score=0.6
                    )
                    
                    # Calculate properties from SMILES
                    if RDKIT_AVAILABLE:
                        self._calculate_drug_properties(structure)
                        self._calculate_molecular_properties(structure)
                    
                    return structure
        
        except Exception as e:
            self.logger.warning(f"OPSIN resolution failed for '{chemical_name}': {e}")
        
        return None
    
    def _enrich_from_pubchem_cid(self, structure: RealChemicalStructure, cid: int):
        """Enrich structure data using PubChem CID"""
        try:
            # Get synonyms
            synonyms_url = f"{self.apis['pubchem']}/compound/cid/{cid}/synonyms/JSON"
            response = requests.get(synonyms_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'InformationList' in data and data['InformationList']:
                    synonyms = data['InformationList'][0].get('Synonym', [])
                    structure.synonyms = synonyms[:10]  # Limit to first 10
        
        except Exception as e:
            self.logger.warning(f"Failed to get synonyms for CID {cid}: {e}")
    
    def _calculate_drug_properties(self, structure: RealChemicalStructure):
        """Calculate drug-likeness properties using RDKit"""
        if not RDKIT_AVAILABLE or not structure.smiles:
            return
        
        try:
            mol = Chem.MolFromSmiles(structure.smiles)
            if mol is None:
                return
            
            # Calculate Lipinski properties
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)
            tpsa = Descriptors.TPSA(mol)
            rotatable_bonds = Descriptors.NumRotatableBonds(mol)
            
            structure.molecular_weight = mw
            structure.logp = logp
            structure.hbd_count = hbd
            structure.hba_count = hba
            structure.polar_surface_area = tpsa
            structure.rotatable_bonds = rotatable_bonds
            
            # Lipinski Rule of Five compliance
            lipinski_violations = 0
            if mw > 500: lipinski_violations += 1
            if logp > 5: lipinski_violations += 1
            if hbd > 5: lipinski_violations += 1
            if hba > 10: lipinski_violations += 1
            
            structure.lipinski_compliant = lipinski_violations <= 1
            
        except Exception as e:
            self.logger.warning(f"Drug property calculation failed: {e}")
    
    def _calculate_molecular_properties(self, structure: RealChemicalStructure):
        """Calculate basic molecular properties from SMILES"""
        if not RDKIT_AVAILABLE or not structure.smiles:
            return
        
        try:
            mol = Chem.MolFromSmiles(structure.smiles)
            if mol is None:
                return
            
            # Basic molecular properties
            if not structure.molecular_weight:
                structure.molecular_weight = Descriptors.MolWt(mol)
            
            if not structure.molecular_formula:
                structure.molecular_formula = rdMolDescriptors.CalcMolFormula(mol)
            
        except Exception as e:
            self.logger.warning(f"Molecular property calculation failed: {e}")
    
    def _generate_structure_image(self, structure: RealChemicalStructure) -> Optional[str]:
        """Generate SVG image of chemical structure"""
        if not RDKIT_AVAILABLE or not structure.smiles:
            return None
        
        try:
            mol = Chem.MolFromSmiles(structure.smiles)
            if mol is None:
                return None
            
            drawer = rdMolDraw2D.MolDraw2DSVG(300, 300)
            drawer.DrawMolecule(mol)
            drawer.FinishDrawing()
            
            return drawer.GetDrawingText()
            
        except Exception as e:
            self.logger.warning(f"Structure image generation failed: {e}")
            return None
    
    def _analyze_drug_likeness(self, chemical_data: PatentData) -> PatentData:
        """Analyze drug-likeness of extracted chemicals"""
        
        chemical_structures = chemical_data.content.get('chemical_structures', [])
        
        drug_analysis = {
            "total_compounds": len(chemical_structures),
            "lipinski_compliant": 0,
            "drug_like_compounds": [],
            "non_drug_like_compounds": [],
            "analysis_summary": {}
        }
        
        for struct_dict in chemical_structures:
            struct = RealChemicalStructure(**struct_dict)
            
            if struct.lipinski_compliant is True:
                drug_analysis["lipinski_compliant"] += 1
                drug_analysis["drug_like_compounds"].append({
                    "name": struct.compound_name,
                    "smiles": struct.smiles,
                    "molecular_weight": struct.molecular_weight,
                    "logp": struct.logp,
                    "reason": "Lipinski Rule of Five compliant"
                })
            elif struct.lipinski_compliant is False:
                drug_analysis["non_drug_like_compounds"].append({
                    "name": struct.compound_name,
                    "smiles": struct.smiles,
                    "molecular_weight": struct.molecular_weight,
                    "logp": struct.logp,
                    "reason": "Lipinski Rule of Five violations"
                })
        
        # Summary statistics
        if drug_analysis["total_compounds"] > 0:
            drug_analysis["analysis_summary"] = {
                "percentage_drug_like": (drug_analysis["lipinski_compliant"] / drug_analysis["total_compounds"]) * 100,
                "average_molecular_weight": sum(s.get("molecular_weight", 0) for s in [RealChemicalStructure(**d) for d in chemical_structures] if s.molecular_weight) / len([s for s in chemical_structures if RealChemicalStructure(**s).molecular_weight]),
                "rdkit_processing_enabled": RDKIT_AVAILABLE
            }
        
        return PatentData(
            id=f"drug_analysis_{int(time.time())}",
            type=PatentDataType.ANALYSIS_REPORT,
            content={
                "analysis_type": "drug_likeness",
                "patent_number": chemical_data.content.get("patent_number", ""),
                "drug_analysis": drug_analysis
            },
            metadata={
                "analysis_timestamp": time.time(),
                "rdkit_available": RDKIT_AVAILABLE
            }
        )
    
    # Convenience methods
    def process_foxp2_chemicals(self, patent_data: PatentData) -> PatentData:
        """Specialized processing for FOXP2-related chemicals"""
        
        # Extract chemicals with focus on FOXP2/NIB compounds
        chemicals_data = self._extract_chemicals_from_patent(patent_data)
        
        # Filter for FOXP2-relevant compounds
        all_structures = chemicals_data.content.get('chemical_structures', [])
        foxp2_relevant = []
        
        for struct_dict in all_structures:
            struct = RealChemicalStructure(**struct_dict)
            
            # Check if compound is relevant to FOXP2
            name_lower = struct.compound_name.lower()
            if any(term in name_lower for term in ['foxp2', 'nib', 'indole', 'forkhead', 'benzamide']):
                foxp2_relevant.append(struct_dict)
        
        # Update the chemicals data with FOXP2 focus
        chemicals_data.content.update({
            "foxp2_relevant_structures": foxp2_relevant,
            "total_foxp2_relevant": len(foxp2_relevant),
            "analysis_focus": "foxp2_therapeutics"
        })
        
        return chemicals_data