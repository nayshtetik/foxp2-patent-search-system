from typing import Dict, Any, List, Union, Optional, Tuple
import re
import requests
from dataclasses import dataclass
import time
import base64
from io import BytesIO
import hashlib

from .base_agent import BasePatentAgent, PatentData, PatentDataType, Task

@dataclass
class ChemicalStructure:
    smiles: Optional[str] = None
    inchi: Optional[str] = None
    mol_formula: Optional[str] = None
    mol_weight: Optional[float] = None
    structure_image: Optional[bytes] = None
    cas_number: Optional[str] = None
    iupac_name: Optional[str] = None
    common_names: List[str] = None
    
    def __post_init__(self):
        if self.common_names is None:
            self.common_names = []

@dataclass
class PatentDocument:
    patent_number: str
    title: str
    abstract: str
    claims: List[str]
    description: str
    inventors: List[str]
    assignees: List[str]
    publication_date: str
    filing_date: str
    priority_date: Optional[str]
    classification_codes: List[str]
    cited_patents: List[str]
    citing_patents: List[str]
    images: List[Dict[str, Any]]
    chemical_structures: List[ChemicalStructure]
    raw_text: str
    metadata: Dict[str, Any]

class PatentProcessingAgent(BasePatentAgent):
    def __init__(self, agent_id: str = "patent_processor_001"):
        super().__init__(
            agent_id=agent_id,
            name="Patent Processing Agent",
            description="Processes patent documents, extracts structured data, and identifies chemical structures"
        )
        self.chemistry_apis = {
            'pubchem': 'https://pubchem.ncbi.nlm.nih.gov/rest/pug',
            'chemspider': 'http://www.chemspider.com/Search.asmx',
            'rdkit_server': None  # Would be a custom RDKit server
        }
        
    def get_capabilities(self) -> List[str]:
        return [
            "pdf_text_extraction",
            "html_parsing", 
            "structured_data_extraction",
            "chemical_structure_recognition",
            "chemical_name_resolution",
            "smiles_generation",
            "molecular_formula_parsing",
            "image_processing",
            "patent_claims_parsing",
            "citation_extraction",
            "classification_code_parsing",
            "metadata_enrichment"
        ]
    
    def get_supported_input_types(self) -> List[PatentDataType]:
        return [PatentDataType.QUERY_RESULT]
    
    def get_output_type(self) -> PatentDataType:
        return PatentDataType.PATENT_DOCUMENT
    
    def process_task(self, task: Task) -> Union[PatentData, List[PatentData]]:
        if task.type == "process_patents":
            return self._process_patent_batch(task.input_data)
        elif task.type == "process_single_patent":
            return self._process_single_patent(task.input_data)
        elif task.type == "extract_chemicals":
            return self._extract_chemical_structures(task.input_data)
        elif task.type == "enrich_metadata":
            return self._enrich_patent_metadata(task.input_data)
        else:
            raise ValueError(f"Unsupported task type: {task.type}")
    
    def _process_patent_batch(self, query_results: List[PatentData]) -> List[PatentData]:
        """Process multiple patents from query results"""
        processed_patents = []
        
        for query_result in query_results:
            if query_result.type != PatentDataType.QUERY_RESULT:
                continue
                
            patents_list = query_result.content.get('patents', [])
            
            for patent_info in patents_list:
                try:
                    processed_patent = self._process_patent_info(patent_info)
                    processed_patents.append(processed_patent)
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"Error processing patent {patent_info.get('patent_number')}: {e}")
                    continue
        
        return processed_patents
    
    def _process_single_patent(self, patent_info: Dict[str, Any]) -> PatentData:
        """Process a single patent"""
        return self._process_patent_info(patent_info)
    
    def _process_patent_info(self, patent_info: Dict[str, Any]) -> PatentData:
        """Core patent processing logic"""
        patent_number = patent_info.get('patent_number', '')
        
        self.logger.info(f"Processing patent {patent_number}")
        
        # Fetch full patent document
        full_document = self._fetch_full_patent_document(patent_number, patent_info.get('source'))
        
        # Extract structured data
        structured_data = self._extract_structured_data(full_document)
        
        # Process chemical structures
        chemical_structures = self._identify_and_process_chemicals(structured_data)
        
        # Create patent document object
        patent_doc = PatentDocument(
            patent_number=patent_number,
            title=structured_data.get('title', ''),
            abstract=structured_data.get('abstract', ''),
            claims=structured_data.get('claims', []),
            description=structured_data.get('description', ''),
            inventors=structured_data.get('inventors', []),
            assignees=structured_data.get('assignees', []),
            publication_date=structured_data.get('publication_date', ''),
            filing_date=structured_data.get('filing_date', ''),
            priority_date=structured_data.get('priority_date'),
            classification_codes=structured_data.get('classification_codes', []),
            cited_patents=structured_data.get('cited_patents', []),
            citing_patents=structured_data.get('citing_patents', []),
            images=structured_data.get('images', []),
            chemical_structures=chemical_structures,
            raw_text=full_document.get('raw_text', ''),
            metadata=structured_data.get('metadata', {})
        )
        
        return PatentData(
            id=f"patent_doc_{patent_number}_{int(time.time())}",
            type=PatentDataType.PATENT_DOCUMENT,
            content={
                "patent_document": patent_doc.__dict__,
                "processing_stats": {
                    "chemicals_found": len(chemical_structures),
                    "claims_count": len(structured_data.get('claims', [])),
                    "images_count": len(structured_data.get('images', [])),
                    "text_length": len(full_document.get('raw_text', ''))
                }
            },
            metadata={
                "patent_number": patent_number,
                "processed_timestamp": time.time(),
                "source": patent_info.get('source', 'unknown')
            }
        )
    
    def _fetch_full_patent_document(self, patent_number: str, source: str) -> Dict[str, Any]:
        """Fetch complete patent document from various sources"""
        if source == 'google_patents':
            return self._fetch_from_google_patents(patent_number)
        elif source == 'espacenet':
            return self._fetch_from_espacenet(patent_number)
        else:
            return self._fetch_generic(patent_number)
    
    def _fetch_from_google_patents(self, patent_number: str) -> Dict[str, Any]:
        """Fetch patent from Google Patents (simulated)"""
        # In reality, would use Google Patents API or web scraping
        return {
            'raw_text': f"Full patent document for {patent_number}...",
            'html_content': f"<html>Patent {patent_number} content...</html>",
            'pdf_url': f"https://patents.google.com/patent/{patent_number}.pdf"
        }
    
    def _fetch_from_espacenet(self, patent_number: str) -> Dict[str, Any]:
        """Fetch patent from Espacenet (simulated)"""
        return {
            'raw_text': f"Espacenet patent document for {patent_number}...",
            'xml_content': f"<patent><number>{patent_number}</number></patent>",
            'pdf_url': f"https://worldwide.espacenet.com/patent/{patent_number}.pdf"
        }
    
    def _fetch_generic(self, patent_number: str) -> Dict[str, Any]:
        """Generic patent fetching"""
        return {
            'raw_text': f"Generic patent document for {patent_number}...",
            'content': f"Patent {patent_number} content..."
        }
    
    def _extract_structured_data(self, full_document: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from raw patent document"""
        raw_text = full_document.get('raw_text', '')
        
        # Use regex patterns to extract different sections
        title_pattern = r"Title:\s*(.+?)(?:\n|$)"
        abstract_pattern = r"Abstract[:\s]*(.+?)(?=Claims|Description|$)"
        claims_pattern = r"Claims[:\s]*(.+?)(?=Description|Background|$)"
        
        title_match = re.search(title_pattern, raw_text, re.IGNORECASE)
        abstract_match = re.search(abstract_pattern, raw_text, re.IGNORECASE | re.DOTALL)
        claims_match = re.search(claims_pattern, raw_text, re.IGNORECASE | re.DOTALL)
        
        # Extract claims as separate items
        claims = []
        if claims_match:
            claims_text = claims_match.group(1)
            # Split by claim numbers (1., 2., etc.)
            claim_items = re.split(r'\n\s*\d+\.\s*', claims_text)
            claims = [claim.strip() for claim in claim_items if claim.strip()]
        
        # Extract inventors and assignees
        inventors = self._extract_inventors(raw_text)
        assignees = self._extract_assignees(raw_text)
        
        # Extract classification codes
        classification_codes = self._extract_classification_codes(raw_text)
        
        # Extract cited patents
        cited_patents = self._extract_cited_patents(raw_text)
        
        return {
            'title': title_match.group(1).strip() if title_match else '',
            'abstract': abstract_match.group(1).strip() if abstract_match else '',
            'claims': claims,
            'description': raw_text,  # Full text for now
            'inventors': inventors,
            'assignees': assignees,
            'classification_codes': classification_codes,
            'cited_patents': cited_patents,
            'citing_patents': [],  # Would need reverse lookup
            'images': [],  # Would extract from PDF/HTML
            'metadata': {
                'extraction_method': 'regex_parsing',
                'document_length': len(raw_text)
            }
        }
    
    def _extract_inventors(self, text: str) -> List[str]:
        """Extract inventor names from patent text"""
        inventor_patterns = [
            r"Inventor[s]?[:\s]*(.+?)(?=Assignee|Abstract|$)",
            r"Invented by[:\s]*(.+?)(?=\n|$)"
        ]
        
        for pattern in inventor_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                inventors_text = match.group(1)
                # Split by common separators
                inventors = re.split(r'[,;]\s*', inventors_text.strip())
                return [inv.strip() for inv in inventors if inv.strip()]
        
        return []
    
    def _extract_assignees(self, text: str) -> List[str]:
        """Extract assignee/company names from patent text"""
        assignee_patterns = [
            r"Assignee[s]?[:\s]*(.+?)(?=Inventor|Abstract|$)",
            r"Assigned to[:\s]*(.+?)(?=\n|$)"
        ]
        
        for pattern in assignee_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                assignees_text = match.group(1)
                assignees = re.split(r'[,;]\s*', assignees_text.strip())
                return [ass.strip() for ass in assignees if ass.strip()]
        
        return []
    
    def _extract_classification_codes(self, text: str) -> List[str]:
        """Extract patent classification codes (CPC, IPC, etc.)"""
        # Common classification code patterns
        patterns = [
            r'[A-H]\d{2}[A-Z]\s*\d+/\d+',  # CPC/IPC format
            r'US\s*\d+[A-Z]*',  # US classification
            r'\d{3}/\d+\.?\d*'  # US format
        ]
        
        codes = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            codes.extend(matches)
        
        return list(set(codes))  # Remove duplicates
    
    def _extract_cited_patents(self, text: str) -> List[str]:
        """Extract cited patent references"""
        # Patent number patterns
        patterns = [
            r'US\s*\d{7,8}[A-Z]*\d*',
            r'EP\s*\d{7}[A-Z]*\d*',
            r'WO\s*\d{4}/\d{6}',
            r'\d{1,2}[,/]\d{3}[,/]\d{3}'
        ]
        
        cited_patents = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            cited_patents.extend(matches)
        
        return list(set(cited_patents))  # Remove duplicates
    
    def _identify_and_process_chemicals(self, structured_data: Dict[str, Any]) -> List[ChemicalStructure]:
        """Identify and process chemical structures in patent"""
        text_content = structured_data.get('description', '') + ' ' + structured_data.get('abstract', '')
        
        chemical_structures = []
        
        # Find chemical names, formulas, and identifiers
        chemical_mentions = self._find_chemical_mentions(text_content)
        
        for mention in chemical_mentions:
            try:
                chemical_structure = self._resolve_chemical_structure(mention)
                if chemical_structure:
                    chemical_structures.append(chemical_structure)
            except Exception as e:
                self.logger.warning(f"Could not resolve chemical structure for {mention}: {e}")
                continue
        
        return chemical_structures
    
    def _find_chemical_mentions(self, text: str) -> List[str]:
        """Find chemical names, formulas, and identifiers in text"""
        mentions = []
        
        # Molecular formulas (e.g., C6H12O6, H2SO4)
        formula_pattern = r'\b[A-Z][a-z]?(?:\d+[A-Z][a-z]?\d*)*\b'
        formulas = re.findall(formula_pattern, text)
        mentions.extend([f for f in formulas if self._looks_like_chemical_formula(f)])
        
        # CAS numbers (e.g., 50-00-0)
        cas_pattern = r'\b\d{2,7}-\d{2}-\d\b'
        cas_numbers = re.findall(cas_pattern, text)
        mentions.extend(cas_numbers)
        
        # Common chemical name patterns
        chemical_name_patterns = [
            r'\b\w+(?:yl|ine|ane|ene|yne|ide|ate|ite)\b',  # Common chemical suffixes
            r'\b(?:meth|eth|prop|but|pent|hex)yl\w*\b',    # Alkyl groups
            r'\b\w*(?:benzene|phenol|aniline|pyridine)\w*\b'  # Aromatic compounds
        ]
        
        for pattern in chemical_name_patterns:
            names = re.findall(pattern, text, re.IGNORECASE)
            mentions.extend(names)
        
        return list(set(mentions))  # Remove duplicates
    
    def _looks_like_chemical_formula(self, formula: str) -> bool:
        """Check if a string looks like a chemical formula"""
        # Must contain at least one element symbol and one number
        has_element = bool(re.search(r'[A-Z][a-z]?', formula))
        has_number = bool(re.search(r'\d', formula))
        reasonable_length = 2 <= len(formula) <= 30
        
        return has_element and has_number and reasonable_length
    
    def _resolve_chemical_structure(self, chemical_mention: str) -> Optional[ChemicalStructure]:
        """Resolve chemical structure from name/formula/identifier"""
        # Try different resolution methods
        
        # Method 1: Check if it's a CAS number
        if re.match(r'\d{2,7}-\d{2}-\d', chemical_mention):
            return self._resolve_by_cas_number(chemical_mention)
        
        # Method 2: Try as chemical name
        structure = self._resolve_by_name(chemical_mention)
        if structure:
            return structure
        
        # Method 3: Try as molecular formula
        if self._looks_like_chemical_formula(chemical_mention):
            return self._resolve_by_formula(chemical_mention)
        
        return None
    
    def _resolve_by_cas_number(self, cas_number: str) -> Optional[ChemicalStructure]:
        """Resolve structure by CAS number using PubChem"""
        try:
            # Simulated PubChem API call
            # In reality: requests.get(f"{self.chemistry_apis['pubchem']}/compound/name/{cas_number}/JSON")
            
            return ChemicalStructure(
                cas_number=cas_number,
                smiles="CCO",  # Placeholder
                mol_formula="C2H6O",  # Placeholder
                mol_weight=46.07,  # Placeholder
                iupac_name=f"compound_{cas_number}",
                common_names=[f"compound_{cas_number}"]
            )
        except Exception as e:
            self.logger.error(f"Error resolving CAS {cas_number}: {e}")
            return None
    
    def _resolve_by_name(self, chemical_name: str) -> Optional[ChemicalStructure]:
        """Resolve structure by chemical name"""
        try:
            # Simulated chemical name resolution
            return ChemicalStructure(
                iupac_name=chemical_name,
                common_names=[chemical_name],
                smiles="C",  # Placeholder
                mol_formula="CH4"  # Placeholder
            )
        except Exception as e:
            self.logger.error(f"Error resolving name {chemical_name}: {e}")
            return None
    
    def _resolve_by_formula(self, formula: str) -> Optional[ChemicalStructure]:
        """Resolve structure by molecular formula"""
        return ChemicalStructure(
            mol_formula=formula,
            smiles="C",  # Placeholder - would need structure generation
            common_names=[formula]
        )
    
    def _extract_chemical_structures(self, patent_data: PatentData) -> PatentData:
        """Extract only chemical structures from processed patent"""
        if patent_data.type != PatentDataType.PATENT_DOCUMENT:
            raise ValueError("Input must be a patent document")
        
        patent_doc_dict = patent_data.content.get('patent_document', {})
        chemical_structures = patent_doc_dict.get('chemical_structures', [])
        
        return PatentData(
            id=f"chemicals_{patent_data.id}",
            type=PatentDataType.CHEMICAL_STRUCTURE,
            content={
                "patent_number": patent_doc_dict.get('patent_number', ''),
                "chemical_structures": chemical_structures,
                "total_structures": len(chemical_structures)
            },
            metadata={
                "source_patent_id": patent_data.id,
                "extraction_timestamp": time.time()
            }
        )
    
    def _enrich_patent_metadata(self, patent_data: PatentData) -> PatentData:
        """Enrich patent with additional metadata"""
        # Add additional metadata like patent family, legal status, etc.
        enriched_content = patent_data.content.copy()
        enriched_metadata = patent_data.metadata.copy()
        
        # Simulated metadata enrichment
        enriched_metadata.update({
            "enriched_timestamp": time.time(),
            "patent_family_size": 5,  # Placeholder
            "legal_status": "Active",  # Placeholder
            "forward_citations": 12,  # Placeholder
            "backward_citations": 8   # Placeholder
        })
        
        return PatentData(
            id=f"enriched_{patent_data.id}",
            type=patent_data.type,
            content=enriched_content,
            metadata=enriched_metadata
        )