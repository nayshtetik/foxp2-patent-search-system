from typing import Dict, Any, List, Union, Optional
from dataclasses import dataclass
import requests
import time
import re
from urllib.parse import urlencode, quote
import xml.etree.ElementTree as ET

from .base_agent import BasePatentAgent, PatentData, PatentDataType, Task

@dataclass
class QueryParameters:
    keywords: List[str]
    inventors: Optional[List[str]] = None
    assignees: Optional[List[str]] = None
    classification_codes: Optional[List[str]] = None
    date_range: Optional[Dict[str, str]] = None
    countries: Optional[List[str]] = None
    patent_types: Optional[List[str]] = None
    max_results: int = 100

class PatentQueryAgent(BasePatentAgent):
    def __init__(self, agent_id: str = "patent_query_001"):
        super().__init__(
            agent_id=agent_id,
            name="Patent Query Agent",
            description="Searches patent databases using various APIs and parameters"
        )
        self.apis = {
            'uspto': 'https://developer.uspto.gov/ptab-api/swagger-ui.html',
            'espacenet': 'https://ops.epo.org/3.2/',
            'google_patents': 'https://patents.google.com/',
            'patentscope': 'https://patentscope.wipo.int/search/en/search.jsf'
        }
        
    def get_capabilities(self) -> List[str]:
        return [
            "keyword_search",
            "inventor_search", 
            "assignee_search",
            "classification_search",
            "date_range_search",
            "multi_database_search",
            "boolean_query_construction",
            "results_filtering",
            "pagination_handling"
        ]
    
    def get_supported_input_types(self) -> List[PatentDataType]:
        return []  # This is a starting agent, no input required
    
    def get_output_type(self) -> PatentDataType:
        return PatentDataType.QUERY_RESULT
    
    def process_task(self, task: Task) -> PatentData:
        if task.type == "search_patents":
            return self._search_patents(task.input_data)
        elif task.type == "advanced_search":
            return self._advanced_search(task.input_data)
        elif task.type == "bulk_search":
            return self._bulk_search(task.input_data)
        else:
            raise ValueError(f"Unsupported task type: {task.type}")
    
    def _search_patents(self, search_params: Dict[str, Any]) -> PatentData:
        """Basic patent search with keywords"""
        query_params = QueryParameters(**search_params)
        
        results = []
        
        # Search multiple databases
        if 'databases' not in search_params or 'google_patents' in search_params.get('databases', []):
            results.extend(self._search_google_patents(query_params))
        
        if 'databases' not in search_params or 'espacenet' in search_params.get('databases', []):
            results.extend(self._search_espacenet(query_params))
        
        # Deduplicate results by patent number
        unique_results = self._deduplicate_results(results)
        
        return PatentData(
            id=f"query_result_{int(time.time())}",
            type=PatentDataType.QUERY_RESULT,
            content={
                "query_parameters": search_params,
                "total_results": len(unique_results),
                "patents": unique_results
            },
            metadata={
                "search_timestamp": time.time(),
                "databases_searched": search_params.get('databases', ['google_patents', 'espacenet']),
                "query_type": "basic_search"
            }
        )
    
    def _advanced_search(self, search_params: Dict[str, Any]) -> PatentData:
        """Advanced patent search with complex boolean queries"""
        query_params = QueryParameters(**search_params)
        
        # Construct advanced boolean query
        boolean_query = self._construct_boolean_query(query_params)
        
        self.logger.info(f"Executing advanced search with query: {boolean_query}")
        
        results = []
        
        # Execute on multiple databases with advanced query
        for db in search_params.get('databases', ['google_patents', 'espacenet']):
            try:
                if db == 'google_patents':
                    db_results = self._advanced_google_patents_search(boolean_query, query_params)
                elif db == 'espacenet':
                    db_results = self._advanced_espacenet_search(boolean_query, query_params)
                else:
                    continue
                    
                results.extend(db_results)
            except Exception as e:
                self.logger.error(f"Error searching {db}: {e}")
                continue
        
        unique_results = self._deduplicate_results(results)
        
        return PatentData(
            id=f"advanced_query_result_{int(time.time())}",
            type=PatentDataType.QUERY_RESULT,
            content={
                "query_parameters": search_params,
                "boolean_query": boolean_query,
                "total_results": len(unique_results),
                "patents": unique_results
            },
            metadata={
                "search_timestamp": time.time(),
                "databases_searched": search_params.get('databases', ['google_patents', 'espacenet']),
                "query_type": "advanced_search"
            }
        )
    
    def _bulk_search(self, search_params: Dict[str, Any]) -> PatentData:
        """Bulk search for multiple queries"""
        queries = search_params.get('queries', [])
        all_results = []
        
        for i, query in enumerate(queries):
            self.logger.info(f"Processing bulk query {i+1}/{len(queries)}")
            try:
                single_result = self._search_patents(query)
                all_results.extend(single_result.content['patents'])
                
                # Rate limiting between queries
                if i < len(queries) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Error in bulk query {i+1}: {e}")
                continue
        
        unique_results = self._deduplicate_results(all_results)
        
        return PatentData(
            id=f"bulk_query_result_{int(time.time())}",
            type=PatentDataType.QUERY_RESULT,
            content={
                "query_parameters": search_params,
                "queries_executed": len(queries),
                "total_results": len(unique_results),
                "patents": unique_results
            },
            metadata={
                "search_timestamp": time.time(),
                "query_type": "bulk_search"
            }
        )
    
    def _search_google_patents(self, query_params: QueryParameters) -> List[Dict[str, Any]]:
        """Search Google Patents (simulated - would need actual API integration)"""
        # This is a placeholder implementation
        # In reality, would use Google Patents Public API or web scraping
        
        self.logger.info("Searching Google Patents...")
        
        # Simulate API response
        return [
            {
                "patent_number": f"US{10000000 + i}",
                "title": f"Patent related to {' '.join(query_params.keywords[:2])} - {i}",
                "inventors": [f"Inventor {i} Name"],
                "assignees": [f"Company {i}"],
                "publication_date": "2023-01-01",
                "abstract": f"This patent describes technology related to {' '.join(query_params.keywords)}...",
                "source": "google_patents",
                "url": f"https://patents.google.com/patent/US{10000000 + i}"
            }
            for i in range(min(query_params.max_results // 2, 50))
        ]
    
    def _search_espacenet(self, query_params: QueryParameters) -> List[Dict[str, Any]]:
        """Search Espacenet (European Patent Office)"""
        self.logger.info("Searching Espacenet...")
        
        # Simulate Espacenet API response
        return [
            {
                "patent_number": f"EP{3000000 + i}",
                "title": f"European patent for {' '.join(query_params.keywords[:2])} technology - {i}",
                "inventors": [f"EU Inventor {i}"],
                "assignees": [f"European Company {i}"],
                "publication_date": "2023-02-01",
                "abstract": f"European patent describing {' '.join(query_params.keywords)} innovations...",
                "source": "espacenet",
                "url": f"https://worldwide.espacenet.com/patent/search/family/EP{3000000 + i}"
            }
            for i in range(min(query_params.max_results // 2, 50))
        ]
    
    def _advanced_google_patents_search(self, boolean_query: str, query_params: QueryParameters) -> List[Dict[str, Any]]:
        """Execute advanced boolean search on Google Patents"""
        # Placeholder for advanced Google Patents search
        return self._search_google_patents(query_params)
    
    def _advanced_espacenet_search(self, boolean_query: str, query_params: QueryParameters) -> List[Dict[str, Any]]:
        """Execute advanced boolean search on Espacenet"""
        # Placeholder for advanced Espacenet search
        return self._search_espacenet(query_params)
    
    def _construct_boolean_query(self, query_params: QueryParameters) -> str:
        """Construct boolean search query from parameters"""
        query_parts = []
        
        # Keywords with OR logic within, AND logic between groups
        if query_params.keywords:
            keyword_part = " OR ".join(f'"{kw}"' for kw in query_params.keywords)
            query_parts.append(f"({keyword_part})")
        
        # Inventors
        if query_params.inventors:
            inventor_part = " OR ".join(f'inventor:"{inv}"' for inv in query_params.inventors)
            query_parts.append(f"({inventor_part})")
        
        # Assignees
        if query_params.assignees:
            assignee_part = " OR ".join(f'assignee:"{ass}"' for ass in query_params.assignees)
            query_parts.append(f"({assignee_part})")
        
        # Classification codes
        if query_params.classification_codes:
            class_part = " OR ".join(f'classification:"{cc}"' for cc in query_params.classification_codes)
            query_parts.append(f"({class_part})")
        
        # Date range
        if query_params.date_range:
            start_date = query_params.date_range.get('start_date', '')
            end_date = query_params.date_range.get('end_date', '')
            if start_date and end_date:
                query_parts.append(f"publication_date:[{start_date} TO {end_date}]")
        
        return " AND ".join(query_parts)
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate patents from results"""
        seen_patents = set()
        unique_results = []
        
        for result in results:
            patent_key = result.get('patent_number', '')
            if patent_key and patent_key not in seen_patents:
                seen_patents.add(patent_key)
                unique_results.append(result)
        
        return unique_results
    
    def search_by_keywords(self, keywords: List[str], **kwargs) -> PatentData:
        """Convenience method for keyword search"""
        search_params = {
            'keywords': keywords,
            **kwargs
        }
        task = self.create_task("search_patents", search_params)
        return self.execute_task(task).result
    
    def search_by_inventor(self, inventors: List[str], keywords: List[str] = None, **kwargs) -> PatentData:
        """Convenience method for inventor search"""
        search_params = {
            'inventors': inventors,
            'keywords': keywords or [],
            **kwargs
        }
        task = self.create_task("search_patents", search_params)
        return self.execute_task(task).result
    
    def search_by_company(self, companies: List[str], keywords: List[str] = None, **kwargs) -> PatentData:
        """Convenience method for company/assignee search"""
        search_params = {
            'assignees': companies,
            'keywords': keywords or [],
            **kwargs
        }
        task = self.create_task("search_patents", search_params)
        return self.execute_task(task).result