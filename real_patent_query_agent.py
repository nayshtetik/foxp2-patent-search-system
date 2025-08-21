import requests
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, quote
import logging

from base_agent import BasePatentAgent, PatentData, PatentDataType, Task

class RealPatentQueryAgent(BasePatentAgent):
    """Real patent search agent using actual APIs"""
    
    def __init__(self, agent_id: str = "real_patent_query_001"):
        super().__init__(
            agent_id=agent_id,
            name="Real Patent Query Agent",
            description="Searches real patent databases using actual APIs"
        )
        
        # Real API endpoints
        self.apis = {
            'google_patents': 'https://api.searchapi.io/api/v1/search',
            'espacenet': 'https://ops.epo.org/3.2/rest-services',
            'uspto_ptab': 'https://developer.uspto.gov/api/v2/ptab',
            'pubchem_patents': 'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view',
            'surechembl': 'https://www.surechembl.org/api/1.0'
        }
        
        # API keys (to be set via environment variables)
        self.api_keys = {
            'searchapi': None,  # Set via SEARCHAPI_KEY env var
            'uspto': None,      # Set via USPTO_API_KEY env var
        }
        
        self.setup_api_keys()
    
    def setup_api_keys(self):
        """Setup API keys from environment variables"""
        import os
        self.api_keys['searchapi'] = os.getenv('SEARCHAPI_KEY')
        self.api_keys['uspto'] = os.getenv('USPTO_API_KEY')
        
        if not self.api_keys['searchapi']:
            self.logger.warning("SEARCHAPI_KEY not set - Google Patents searches will be limited")
        if not self.api_keys['uspto']:
            self.logger.warning("USPTO_API_KEY not set - USPTO searches will be limited")
    
    def get_capabilities(self) -> List[str]:
        return [
            "real_keyword_search",
            "chemical_compound_search",
            "patent_number_lookup",
            "inventor_search",
            "assignee_search",
            "classification_search",
            "multi_database_search",
            "patent_family_search",
            "legal_status_check"
        ]
    
    def get_supported_input_types(self) -> List[PatentDataType]:
        return []
    
    def get_output_type(self) -> PatentDataType:
        return PatentDataType.QUERY_RESULT
    
    def process_task(self, task: Task) -> PatentData:
        if task.type == "real_search_patents":
            return self._real_search_patents(task.input_data)
        elif task.type == "chemical_search":
            return self._chemical_compound_search(task.input_data)
        elif task.type == "patent_lookup":
            return self._patent_number_lookup(task.input_data)
        else:
            raise ValueError(f"Unsupported task type: {task.type}")
    
    def _real_search_patents(self, search_params: Dict[str, Any]) -> PatentData:
        """Real patent search using actual APIs"""
        keywords = search_params.get('keywords', [])
        max_results = search_params.get('max_results', 50)
        
        all_results = []
        
        # Search Google Patents via SearchAPI
        if self.api_keys['searchapi']:
            try:
                google_results = self._search_google_patents_real(keywords, max_results // 2)
                all_results.extend(google_results)
            except Exception as e:
                self.logger.error(f"Google Patents search failed: {e}")
        
        # Search USPTO PTAB database
        try:
            uspto_results = self._search_uspto_ptab(keywords, max_results // 2)
            all_results.extend(uspto_results)
        except Exception as e:
            self.logger.error(f"USPTO search failed: {e}")
        
        # Search Espacenet (free access)
        try:
            espacenet_results = self._search_espacenet_free(keywords, max_results // 3)
            all_results.extend(espacenet_results)
        except Exception as e:
            self.logger.error(f"Espacenet search failed: {e}")
        
        # Deduplicate results
        unique_results = self._deduplicate_results(all_results)
        
        return PatentData(
            id=f"real_query_result_{int(time.time())}",
            type=PatentDataType.QUERY_RESULT,
            content={
                "query_parameters": search_params,
                "total_results": len(unique_results),
                "patents": unique_results,
                "sources_used": ["google_patents", "uspto_ptab", "espacenet"]
            },
            metadata={
                "search_timestamp": time.time(),
                "query_type": "real_search",
                "api_status": {
                    "searchapi_available": bool(self.api_keys['searchapi']),
                    "uspto_available": bool(self.api_keys['uspto'])
                }
            }
        )
    
    def _search_google_patents_real(self, keywords: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search Google Patents using SearchAPI.io"""
        if not self.api_keys['searchapi']:
            self.logger.warning("SearchAPI key not available")
            return []
        
        query = " ".join(keywords)
        
        params = {
            'engine': 'google_patents',
            'q': query,
            'num': min(max_results, 20),  # API limit
            'api_key': self.api_keys['searchapi']
        }
        
        try:
            response = requests.get(self.apis['google_patents'], params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'organic_results' in data:
                for result in data['organic_results']:
                    patent_info = {
                        "patent_number": result.get('publication_number', ''),
                        "title": result.get('title', ''),
                        "abstract": result.get('snippet', ''),
                        "inventors": result.get('inventors', []),
                        "assignees": result.get('assignees', []),
                        "publication_date": result.get('publication_date', ''),
                        "filing_date": result.get('filing_date', ''),
                        "source": "google_patents_real",
                        "url": result.get('link', ''),
                        "pdf_link": result.get('pdf', ''),
                        "priority_date": result.get('priority_date', ''),
                        "legal_status": result.get('legal_status', '')
                    }
                    results.append(patent_info)
            
            self.logger.info(f"Found {len(results)} patents from Google Patents")
            return results
            
        except Exception as e:
            self.logger.error(f"Google Patents search error: {e}")
            return []
    
    def _search_uspto_ptab(self, keywords: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search USPTO PTAB database"""
        query = " AND ".join(keywords)
        
        # USPTO PTAB API endpoint
        url = f"{self.apis['uspto_ptab']}/trials"
        
        params = {
            'q': query,
            'limit': min(max_results, 25),
            'format': 'json'
        }
        
        if self.api_keys['uspto']:
            params['api_key'] = self.api_keys['uspto']
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'results' in data:
                for result in data['results']:
                    patent_info = {
                        "patent_number": result.get('patent_number', ''),
                        "title": result.get('patent_title', ''),
                        "abstract": result.get('patent_abstract', ''),
                        "inventors": [],
                        "assignees": [result.get('patent_owner', '')],
                        "publication_date": result.get('institution_date', ''),
                        "filing_date": result.get('filing_date', ''),
                        "source": "uspto_ptab",
                        "url": result.get('url', ''),
                        "trial_number": result.get('trial_number', ''),
                        "proceeding_type": result.get('proceeding_type_category', '')
                    }
                    results.append(patent_info)
            
            self.logger.info(f"Found {len(results)} patents from USPTO PTAB")
            return results
            
        except Exception as e:
            self.logger.error(f"USPTO PTAB search error: {e}")
            return []
    
    def _search_espacenet_free(self, keywords: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search Espacenet using free access (limited)"""
        # Note: This uses web scraping approach since Espacenet API requires registration
        # In production, you should register for proper API access
        
        query = "+".join(keywords)
        
        # Using a simplified approach - in production use proper Espacenet OPS API
        try:
            # Placeholder for real Espacenet search
            # Would need to implement proper OPS API calls or web scraping
            self.logger.info("Espacenet search would be implemented here with proper API access")
            return []
            
        except Exception as e:
            self.logger.error(f"Espacenet search error: {e}")
            return []
    
    def _chemical_compound_search(self, search_params: Dict[str, Any]) -> PatentData:
        """Search for patents containing specific chemical compounds"""
        compound_name = search_params.get('compound_name', '')
        smiles = search_params.get('smiles', '')
        molecular_formula = search_params.get('molecular_formula', '')
        
        results = []
        
        # Search SureChEMBL for chemical patents
        if compound_name or smiles:
            surechembl_results = self._search_surechembl(compound_name, smiles)
            results.extend(surechembl_results)
        
        # Search PubChem Patents
        if compound_name:
            pubchem_results = self._search_pubchem_patents(compound_name)
            results.extend(pubchem_results)
        
        unique_results = self._deduplicate_results(results)
        
        return PatentData(
            id=f"chemical_search_{int(time.time())}",
            type=PatentDataType.QUERY_RESULT,
            content={
                "query_parameters": search_params,
                "total_results": len(unique_results),
                "patents": unique_results,
                "search_type": "chemical_compounds"
            },
            metadata={
                "search_timestamp": time.time(),
                "query_type": "chemical_search"
            }
        )
    
    def _search_surechembl(self, compound_name: str, smiles: str) -> List[Dict[str, Any]]:
        """Search SureChEMBL database for chemical patents"""
        try:
            base_url = "https://www.surechembl.org/api/1.0/compounds"
            
            # Search by compound name
            if compound_name:
                params = {'q': compound_name}
                response = requests.get(f"{base_url}/search", params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for compound in data.get('compounds', []):
                        # Get patents for this compound
                        compound_id = compound.get('compound_id')
                        if compound_id:
                            patent_response = requests.get(
                                f"{base_url}/{compound_id}/patents", 
                                timeout=30
                            )
                            
                            if patent_response.status_code == 200:
                                patent_data = patent_response.json()
                                
                                for patent in patent_data.get('patents', []):
                                    patent_info = {
                                        "patent_number": patent.get('patent_id', ''),
                                        "title": patent.get('title', ''),
                                        "abstract": patent.get('abstract', ''),
                                        "publication_date": patent.get('publication_date', ''),
                                        "source": "surechembl",
                                        "compound_info": {
                                            "compound_id": compound_id,
                                            "smiles": compound.get('smiles', ''),
                                            "molecular_formula": compound.get('molecular_formula', '')
                                        }
                                    }
                                    results.append(patent_info)
                    
                    self.logger.info(f"Found {len(results)} patents from SureChEMBL")
                    return results
            
            return []
            
        except Exception as e:
            self.logger.error(f"SureChEMBL search error: {e}")
            return []
    
    def _search_pubchem_patents(self, compound_name: str) -> List[Dict[str, Any]]:
        """Search PubChem patent database"""
        try:
            # Search for compound in PubChem first
            search_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/cids/JSON"
            response = requests.get(search_url.format(quote(compound_name)), timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                cids = data.get('IdentifierList', {}).get('CID', [])
                
                results = []
                for cid in cids[:5]:  # Limit to first 5 CIDs
                    # Get patent information for this compound
                    patent_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
                    patent_response = requests.get(patent_url, timeout=30)
                    
                    if patent_response.status_code == 200:
                        patent_data = patent_response.json()
                        
                        # Extract patent information from PubChem data
                        # (This would need detailed parsing of PubChem's complex JSON structure)
                        # Simplified example:
                        patent_info = {
                            "compound_cid": cid,
                            "compound_name": compound_name,
                            "source": "pubchem_patents",
                            "title": f"Compound {compound_name} patent references",
                            "pubchem_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
                        }
                        results.append(patent_info)
                
                self.logger.info(f"Found {len(results)} compound references from PubChem")
                return results
            
            return []
            
        except Exception as e:
            self.logger.error(f"PubChem search error: {e}")
            return []
    
    def _patent_number_lookup(self, search_params: Dict[str, Any]) -> PatentData:
        """Look up specific patent by number"""
        patent_number = search_params.get('patent_number', '')
        
        patent_details = None
        
        # Try different APIs for patent lookup
        if self.api_keys['searchapi']:
            patent_details = self._lookup_google_patents(patent_number)
        
        if not patent_details:
            patent_details = self._lookup_espacenet(patent_number)
        
        if patent_details:
            results = [patent_details]
        else:
            results = []
        
        return PatentData(
            id=f"patent_lookup_{patent_number}_{int(time.time())}",
            type=PatentDataType.QUERY_RESULT,
            content={
                "query_parameters": search_params,
                "total_results": len(results),
                "patents": results
            },
            metadata={
                "search_timestamp": time.time(),
                "query_type": "patent_lookup"
            }
        )
    
    def _lookup_google_patents(self, patent_number: str) -> Optional[Dict[str, Any]]:
        """Look up patent details in Google Patents"""
        if not self.api_keys['searchapi']:
            return None
        
        params = {
            'engine': 'google_patents',
            'q': patent_number,
            'api_key': self.api_keys['searchapi']
        }
        
        try:
            response = requests.get(self.apis['google_patents'], params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'organic_results' in data and data['organic_results']:
                result = data['organic_results'][0]  # Take first match
                
                return {
                    "patent_number": result.get('publication_number', patent_number),
                    "title": result.get('title', ''),
                    "abstract": result.get('snippet', ''),
                    "inventors": result.get('inventors', []),
                    "assignees": result.get('assignees', []),
                    "publication_date": result.get('publication_date', ''),
                    "filing_date": result.get('filing_date', ''),
                    "source": "google_patents_lookup",
                    "url": result.get('link', ''),
                    "pdf_link": result.get('pdf', '')
                }
            
        except Exception as e:
            self.logger.error(f"Google Patents lookup error: {e}")
        
        return None
    
    def _lookup_espacenet(self, patent_number: str) -> Optional[Dict[str, Any]]:
        """Look up patent in Espacenet (simplified)"""
        # This would need proper Espacenet OPS API implementation
        # For now, return placeholder
        return None
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate patents from results"""
        seen_patents = set()
        unique_results = []
        
        for result in results:
            patent_key = result.get('patent_number', '').strip().upper()
            if patent_key and patent_key not in seen_patents:
                seen_patents.add(patent_key)
                unique_results.append(result)
        
        return unique_results
    
    # Convenience methods for real searches
    def search_foxp2_compounds(self, additional_terms: List[str] = None) -> PatentData:
        """Search for real FOXP2-related patents"""
        keywords = ["FOXP2", "forkhead", "transcription factor"]
        if additional_terms:
            keywords.extend(additional_terms)
        
        search_params = {
            'keywords': keywords,
            'max_results': 50
        }
        
        task = self.create_task("real_search_patents", search_params)
        return self.execute_task(task).result
    
    def search_nib_compounds(self) -> PatentData:
        """Search for NIB-related chemical patents"""
        search_params = {
            'compound_name': 'NIB',
            'keywords': ['indole', 'benzamide', 'small molecule']
        }
        
        task = self.create_task("chemical_search", search_params)
        return self.execute_task(task).result