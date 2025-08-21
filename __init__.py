"""
Patent Search System - A comprehensive patent analysis platform

This system provides:
- Patent query and retrieval from multiple databases
- Document processing with chemical structure recognition
- Deep analysis using GPT-powered insights
- Geographic coverage analysis
- Market potential assessment

Main Components:
- PatentQueryAgent: Search patents across databases
- PatentProcessingAgent: Extract and process patent content
- DeepAnalysisAgent: AI-powered patent analysis
- PatentCoverageAnalysisAgent: Geographic coverage mapping  
- MarketingAnalysisAgent: Commercial value assessment
- PatentSearchCoordinator: Orchestrates multi-agent workflows

Usage:
    from patent_search_system import create_patent_search_system
    
    coordinator = create_patent_search_system()
    result = coordinator.search_foxp2_small_molecules()
"""

from .base_agent import BasePatentAgent, PatentData, PatentDataType, Task, TaskStatus
from .patent_query_agent import PatentQueryAgent
from .patent_processing_agent import PatentProcessingAgent
from .deep_analysis_agent import DeepAnalysisAgent
from .coverage_analysis_agent import PatentCoverageAnalysisAgent
from .marketing_analysis_agent import MarketingAnalysisAgent
from .agent_coordinator import PatentSearchCoordinator, create_patent_search_system
from .config import PatentSearchConfig, get_config, load_config

__version__ = "1.0.0"
__author__ = "Patent Search System"
__description__ = "A comprehensive patent search and analysis system"

# Main exports
__all__ = [
    # Core classes
    'BasePatentAgent',
    'PatentData', 
    'PatentDataType',
    'Task',
    'TaskStatus',
    
    # Agent classes
    'PatentQueryAgent',
    'PatentProcessingAgent', 
    'DeepAnalysisAgent',
    'PatentCoverageAnalysisAgent',
    'MarketingAnalysisAgent',
    
    # Coordination
    'PatentSearchCoordinator',
    'create_patent_search_system',
    
    # Configuration
    'PatentSearchConfig',
    'get_config',
    'load_config'
]