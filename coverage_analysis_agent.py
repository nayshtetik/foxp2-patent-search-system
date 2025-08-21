from typing import Dict, Any, List, Union, Optional, Tuple
import requests
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from .base_agent import BasePatentAgent, PatentData, PatentDataType, Task

@dataclass
class GeographicCoverage:
    country_code: str
    country_name: str
    patent_number: str
    filing_date: str
    publication_date: str
    grant_date: Optional[str]
    expiry_date: Optional[str]
    legal_status: str
    family_id: str
    priority_claimed: bool
    fees_paid_until: Optional[str]
    renewal_required: bool
    next_renewal_date: Optional[str]

@dataclass
class PatentFamily:
    family_id: str
    priority_application: Dict[str, Any]
    family_members: List[GeographicCoverage]
    total_countries: int
    active_countries: int
    expired_countries: int
    pending_countries: int
    key_markets_covered: List[str]
    market_coverage_score: float

@dataclass
class CoverageGap:
    country: str
    market_importance: str
    gap_type: str  # "not_filed", "expired", "abandoned"
    estimated_market_value: float
    filing_opportunity: bool
    deadline: Optional[str]
    cost_estimate: float

class PatentCoverageAnalysisAgent(BasePatentAgent):
    def __init__(self, agent_id: str = "coverage_analyzer_001"):
        super().__init__(
            agent_id=agent_id,
            name="Patent Coverage Analysis Agent", 
            description="Analyzes patent coverage across different countries and jurisdictions"
        )
        self.patent_apis = {
            'espacenet': 'https://ops.epo.org/3.2/',
            'uspto': 'https://developer.uspto.gov/ptab-api/',
            'wipo': 'https://patentscope.wipo.int/search/en/',
            'google_patents': 'https://patents.google.com/'
        }
        self.country_data = self._load_country_market_data()
        
    def get_capabilities(self) -> List[str]:
        return [
            "patent_family_analysis",
            "geographic_coverage_mapping", 
            "legal_status_tracking",
            "market_coverage_assessment",
            "filing_gap_identification",
            "renewal_deadline_tracking",
            "competitive_coverage_analysis",
            "strategic_filing_recommendations",
            "patent_landscape_mapping",
            "freedom_to_operate_by_country"
        ]
    
    def get_supported_input_types(self) -> List[PatentDataType]:
        return [PatentDataType.PATENT_DOCUMENT, PatentDataType.QUERY_RESULT]
    
    def get_output_type(self) -> PatentDataType:
        return PatentDataType.COVERAGE_MAP
    
    def process_task(self, task: Task) -> PatentData:
        if task.type == "analyze_coverage":
            return self._analyze_patent_coverage(task.input_data)
        elif task.type == "family_analysis":
            return self._analyze_patent_family(task.input_data)
        elif task.type == "gap_analysis":
            return self._identify_coverage_gaps(task.input_data)
        elif task.type == "competitive_coverage":
            return self._analyze_competitive_coverage(task.input_data)
        elif task.type == "renewal_tracking":
            return self._track_renewal_deadlines(task.input_data)
        else:
            raise ValueError(f"Unsupported task type: {task.type}")
    
    def _analyze_patent_coverage(self, patent_data: Union[PatentData, List[PatentData]]) -> PatentData:
        """Comprehensive patent coverage analysis"""
        if isinstance(patent_data, list):
            patent_data = patent_data[0]  # Take first patent
        
        if patent_data.type != PatentDataType.PATENT_DOCUMENT:
            raise ValueError("Input must be a patent document")
        
        patent_doc = patent_data.content.get('patent_document', {})
        patent_number = patent_doc.get('patent_number', '')
        
        self.logger.info(f"Analyzing coverage for patent {patent_number}")
        
        # Find patent family
        patent_family = self._find_patent_family(patent_number)
        
        # Analyze geographic coverage
        geographic_coverage = self._analyze_geographic_coverage(patent_family)
        
        # Identify coverage gaps
        coverage_gaps = self._identify_gaps(patent_family, patent_doc)
        
        # Calculate market coverage
        market_analysis = self._calculate_market_coverage(patent_family, patent_doc)
        
        # Strategic recommendations
        recommendations = self._generate_coverage_recommendations(
            patent_family, coverage_gaps, market_analysis
        )
        
        return PatentData(
            id=f"coverage_analysis_{patent_number}_{int(time.time())}",
            type=PatentDataType.COVERAGE_MAP,
            content={
                "patent_number": patent_number,
                "patent_family": patent_family.__dict__ if patent_family else None,
                "geographic_coverage": geographic_coverage,
                "coverage_gaps": [gap.__dict__ for gap in coverage_gaps],
                "market_analysis": market_analysis,
                "strategic_recommendations": recommendations,
                "coverage_summary": {
                    "total_countries": len(geographic_coverage),
                    "active_countries": len([c for c in geographic_coverage if c.legal_status == "Active"]),
                    "key_markets_covered": market_analysis.get("key_markets_covered", []),
                    "coverage_score": market_analysis.get("coverage_score", 0.0)
                }
            },
            metadata={
                "analysis_timestamp": time.time(),
                "source_patent_id": patent_data.id,
                "family_id": patent_family.family_id if patent_family else None
            }
        )
    
    def _find_patent_family(self, patent_number: str) -> Optional[PatentFamily]:
        """Find patent family for given patent number"""
        self.logger.info(f"Finding patent family for {patent_number}")
        
        # Simulate patent family lookup
        # In reality, would use patent office APIs
        
        family_id = f"FAMILY_{patent_number}_001"
        
        # Simulate family members across different countries
        family_members = [
            GeographicCoverage(
                country_code="US",
                country_name="United States", 
                patent_number=patent_number,
                filing_date="2020-01-15",
                publication_date="2021-07-15", 
                grant_date="2022-03-10",
                expiry_date="2040-01-15",
                legal_status="Active",
                family_id=family_id,
                priority_claimed=True,
                fees_paid_until="2024-01-15",
                renewal_required=True,
                next_renewal_date="2025-01-15"
            ),
            GeographicCoverage(
                country_code="EP",
                country_name="European Patent Office",
                patent_number=f"EP{patent_number[2:]}",
                filing_date="2020-12-15",
                publication_date="2022-02-15",
                grant_date="2023-01-10", 
                expiry_date="2040-12-15",
                legal_status="Active",
                family_id=family_id,
                priority_claimed=True,
                fees_paid_until="2024-12-15",
                renewal_required=True,
                next_renewal_date="2024-12-15"
            ),
            GeographicCoverage(
                country_code="JP",
                country_name="Japan",
                patent_number=f"JP{patent_number[2:]}",
                filing_date="2020-12-15", 
                publication_date="2022-06-15",
                grant_date="2023-08-10",
                expiry_date="2040-12-15", 
                legal_status="Active",
                family_id=family_id,
                priority_claimed=True,
                fees_paid_until="2024-12-15",
                renewal_required=True,
                next_renewal_date="2024-12-15"
            ),
            GeographicCoverage(
                country_code="CN",
                country_name="China",
                patent_number=f"CN{patent_number[2:]}",
                filing_date="2020-12-15",
                publication_date="2022-06-15", 
                grant_date=None,  # Still pending
                expiry_date="2040-12-15",
                legal_status="Pending",
                family_id=family_id,
                priority_claimed=True,
                fees_paid_until="2024-12-15",
                renewal_required=False,
                next_renewal_date=None
            )
        ]
        
        key_markets = ["US", "EP", "JP", "CN"]
        covered_markets = [m.country_code for m in family_members if m.legal_status in ["Active", "Pending"]]
        
        return PatentFamily(
            family_id=family_id,
            priority_application={
                "country": "US",
                "number": patent_number,
                "date": "2020-01-15"
            },
            family_members=family_members,
            total_countries=len(family_members),
            active_countries=len([m for m in family_members if m.legal_status == "Active"]),
            expired_countries=len([m for m in family_members if m.legal_status == "Expired"]),
            pending_countries=len([m for m in family_members if m.legal_status == "Pending"]),
            key_markets_covered=covered_markets,
            market_coverage_score=len(covered_markets) / len(key_markets) * 100
        )
    
    def _analyze_geographic_coverage(self, patent_family: Optional[PatentFamily]) -> List[Dict[str, Any]]:
        """Analyze geographic distribution of patent family"""
        if not patent_family:
            return []
        
        geographic_data = []
        
        for member in patent_family.family_members:
            country_info = self.country_data.get(member.country_code, {})
            
            geographic_data.append({
                "country_code": member.country_code,
                "country_name": member.country_name,
                "patent_number": member.patent_number,
                "legal_status": member.legal_status,
                "filing_date": member.filing_date,
                "grant_date": member.grant_date,
                "expiry_date": member.expiry_date,
                "next_renewal": member.next_renewal_date,
                "market_size": country_info.get("market_size", "Unknown"),
                "market_importance": country_info.get("importance", "Medium"),
                "regulatory_environment": country_info.get("regulatory", "Standard"),
                "enforcement_strength": country_info.get("enforcement", "Medium")
            })
        
        return geographic_data
    
    def _identify_gaps(self, patent_family: Optional[PatentFamily], patent_doc: Dict[str, Any]) -> List[CoverageGap]:
        """Identify coverage gaps in key markets"""
        if not patent_family:
            return []
        
        covered_countries = {m.country_code for m in patent_family.family_members}
        key_markets = ["US", "EP", "JP", "CN", "CA", "AU", "IN", "BR", "KR", "GB"]
        
        gaps = []
        
        for country in key_markets:
            if country not in covered_countries:
                country_info = self.country_data.get(country, {})
                
                # Check if still possible to file
                priority_date = datetime.strptime(
                    patent_family.priority_application.get("date", "2020-01-01"), 
                    "%Y-%m-%d"
                )
                deadline = priority_date + timedelta(days=365)  # PCT deadline
                filing_possible = datetime.now() < deadline
                
                gaps.append(CoverageGap(
                    country=country,
                    market_importance=country_info.get("importance", "Medium"),
                    gap_type="not_filed",
                    estimated_market_value=country_info.get("market_value", 100000),
                    filing_opportunity=filing_possible,
                    deadline=deadline.strftime("%Y-%m-%d") if filing_possible else None,
                    cost_estimate=country_info.get("filing_cost", 50000)
                ))
        
        # Check for expired patents
        for member in patent_family.family_members:
            if member.legal_status == "Expired":
                country_info = self.country_data.get(member.country_code, {})
                gaps.append(CoverageGap(
                    country=member.country_code,
                    market_importance=country_info.get("importance", "Medium"),
                    gap_type="expired",
                    estimated_market_value=country_info.get("market_value", 100000),
                    filing_opportunity=False,
                    deadline=None,
                    cost_estimate=0
                ))
        
        return gaps
    
    def _calculate_market_coverage(self, patent_family: Optional[PatentFamily], patent_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate market coverage metrics"""
        if not patent_family:
            return {"coverage_score": 0, "key_markets_covered": []}
        
        # Key pharmaceutical markets
        key_pharma_markets = ["US", "EP", "JP", "CN", "CA"]
        covered_key_markets = [
            m.country_code for m in patent_family.family_members 
            if m.country_code in key_pharma_markets and m.legal_status in ["Active", "Pending"]
        ]
        
        # Calculate market value coverage
        total_market_value = 0
        covered_market_value = 0
        
        for country in key_pharma_markets:
            market_value = self.country_data.get(country, {}).get("market_value", 100000)
            total_market_value += market_value
            
            if country in covered_key_markets:
                covered_market_value += market_value
        
        coverage_score = (covered_market_value / total_market_value) * 100 if total_market_value > 0 else 0
        
        # Assess technology-specific coverage
        tech_field = patent_doc.get("classification_codes", [])
        tech_coverage = self._assess_technology_coverage(covered_key_markets, tech_field)
        
        return {
            "coverage_score": round(coverage_score, 2),
            "key_markets_covered": covered_key_markets,
            "total_market_value": total_market_value,
            "covered_market_value": covered_market_value,
            "technology_coverage": tech_coverage,
            "geographic_diversity": len(set(m.country_code for m in patent_family.family_members)),
            "active_jurisdictions": patent_family.active_countries,
            "pending_jurisdictions": patent_family.pending_countries
        }
    
    def _assess_technology_coverage(self, covered_countries: List[str], tech_field: List[str]) -> Dict[str, Any]:
        """Assess coverage specific to technology field"""
        # For pharmaceutical/biotech patents
        if any("A61" in code for code in tech_field):  # Medical/pharmaceutical IPC code
            pharma_markets = ["US", "EP", "JP", "CN", "CA"]
            pharma_covered = [c for c in covered_countries if c in pharma_markets]
            
            return {
                "field": "pharmaceutical",
                "key_markets": pharma_markets,
                "covered_markets": pharma_covered,
                "coverage_adequacy": len(pharma_covered) / len(pharma_markets) * 100,
                "regulatory_considerations": [
                    "FDA approval required for US market",
                    "EMA approval for European market", 
                    "PMDA approval for Japanese market"
                ]
            }
        
        # For chemical patents
        elif any("C07" in code for code in tech_field):  # Chemical IPC code
            chem_markets = ["US", "EP", "JP", "CN", "IN"]
            chem_covered = [c for c in covered_countries if c in chem_markets]
            
            return {
                "field": "chemical",
                "key_markets": chem_markets,
                "covered_markets": chem_covered,
                "coverage_adequacy": len(chem_covered) / len(chem_markets) * 100,
                "manufacturing_considerations": [
                    "Chemical manufacturing hubs in China and India",
                    "Environmental regulations vary by jurisdiction"
                ]
            }
        
        # Default coverage assessment
        return {
            "field": "general",
            "coverage_adequacy": len(covered_countries) / 5 * 100,  # Assume 5 key markets
            "considerations": ["Standard patent coverage analysis"]
        }
    
    def _generate_coverage_recommendations(self, patent_family: Optional[PatentFamily], 
                                         coverage_gaps: List[CoverageGap], 
                                         market_analysis: Dict[str, Any]) -> List[str]:
        """Generate strategic coverage recommendations"""
        recommendations = []
        
        if not patent_family:
            return ["Unable to generate recommendations - no patent family data"]
        
        # Priority filing recommendations
        high_value_gaps = [g for g in coverage_gaps if g.market_importance == "High" and g.filing_opportunity]
        if high_value_gaps:
            countries = [g.country for g in high_value_gaps]
            recommendations.append(f"Priority filing recommended in: {', '.join(countries)}")
        
        # Renewal recommendations
        upcoming_renewals = [
            m for m in patent_family.family_members 
            if m.next_renewal_date and datetime.strptime(m.next_renewal_date, "%Y-%m-%d") < datetime.now() + timedelta(days=180)
        ]
        if upcoming_renewals:
            countries = [m.country_name for m in upcoming_renewals]
            recommendations.append(f"Upcoming renewals required in: {', '.join(countries)}")
        
        # Market coverage recommendations
        coverage_score = market_analysis.get("coverage_score", 0)
        if coverage_score < 60:
            recommendations.append("Consider expanding geographic coverage to improve market position")
        
        # Technology-specific recommendations
        tech_coverage = market_analysis.get("technology_coverage", {})
        if tech_coverage.get("field") == "pharmaceutical":
            if "US" not in patent_family.key_markets_covered:
                recommendations.append("US filing critical for pharmaceutical market access")
            if "EP" not in patent_family.key_markets_covered:
                recommendations.append("European filing recommended for global pharma strategy")
        
        # Cost optimization
        expired_patents = [m for m in patent_family.family_members if m.legal_status == "Expired"]
        if expired_patents:
            countries = [m.country_name for m in expired_patents]
            recommendations.append(f"Consider refiling strategy in: {', '.join(countries)}")
        
        # Portfolio optimization
        if patent_family.total_countries > 10:
            recommendations.append("Consider portfolio optimization - evaluate maintenance costs vs market value")
        elif patent_family.total_countries < 5:
            recommendations.append("Limited geographic coverage - consider strategic expansion")
        
        return recommendations
    
    def _load_country_market_data(self) -> Dict[str, Dict[str, Any]]:
        """Load country-specific market data"""
        return {
            "US": {
                "market_size": "Large",
                "importance": "High", 
                "market_value": 1000000,
                "filing_cost": 75000,
                "regulatory": "FDA",
                "enforcement": "Strong"
            },
            "EP": {
                "market_size": "Large",
                "importance": "High",
                "market_value": 800000, 
                "filing_cost": 60000,
                "regulatory": "EMA", 
                "enforcement": "Strong"
            },
            "JP": {
                "market_size": "Medium",
                "importance": "High",
                "market_value": 400000,
                "filing_cost": 50000,
                "regulatory": "PMDA",
                "enforcement": "Strong" 
            },
            "CN": {
                "market_size": "Large",
                "importance": "High", 
                "market_value": 600000,
                "filing_cost": 30000,
                "regulatory": "NMPA",
                "enforcement": "Improving"
            },
            "CA": {
                "market_size": "Medium",
                "importance": "Medium",
                "market_value": 200000,
                "filing_cost": 40000,
                "regulatory": "Health Canada",
                "enforcement": "Strong"
            },
            "AU": {
                "market_size": "Small",
                "importance": "Medium", 
                "market_value": 150000,
                "filing_cost": 35000,
                "regulatory": "TGA",
                "enforcement": "Strong"
            },
            "IN": {
                "market_size": "Medium", 
                "importance": "Medium",
                "market_value": 300000,
                "filing_cost": 20000,
                "regulatory": "CDSCO",
                "enforcement": "Developing"
            },
            "BR": {
                "market_size": "Medium",
                "importance": "Medium",
                "market_value": 250000, 
                "filing_cost": 25000,
                "regulatory": "ANVISA",
                "enforcement": "Developing"
            },
            "KR": {
                "market_size": "Small",
                "importance": "Medium",
                "market_value": 180000,
                "filing_cost": 30000,
                "regulatory": "MFDS", 
                "enforcement": "Strong"
            },
            "GB": {
                "market_size": "Medium", 
                "importance": "Medium",
                "market_value": 200000,
                "filing_cost": 25000,
                "regulatory": "MHRA",
                "enforcement": "Strong"
            }
        }
    
    def _analyze_patent_family(self, patent_data: PatentData) -> PatentData:
        """Focused patent family analysis"""
        patent_doc = patent_data.content.get('patent_document', {})
        patent_number = patent_doc.get('patent_number', '')
        
        patent_family = self._find_patent_family(patent_number)
        
        return PatentData(
            id=f"family_analysis_{patent_number}_{int(time.time())}",
            type=PatentDataType.COVERAGE_MAP,
            content={
                "analysis_type": "family_only",
                "patent_family": patent_family.__dict__ if patent_family else None
            },
            metadata={
                "analysis_timestamp": time.time(),
                "analysis_scope": "family_only"
            }
        )
    
    def _identify_coverage_gaps(self, patent_data: PatentData) -> PatentData:
        """Focused coverage gap analysis"""
        patent_doc = patent_data.content.get('patent_document', {})
        patent_number = patent_doc.get('patent_number', '')
        
        patent_family = self._find_patent_family(patent_number)
        coverage_gaps = self._identify_gaps(patent_family, patent_doc)
        
        return PatentData(
            id=f"gap_analysis_{patent_number}_{int(time.time())}",
            type=PatentDataType.COVERAGE_MAP,
            content={
                "analysis_type": "gaps_only",
                "coverage_gaps": [gap.__dict__ for gap in coverage_gaps],
                "total_gaps": len(coverage_gaps),
                "high_priority_gaps": len([g for g in coverage_gaps if g.market_importance == "High"])
            },
            metadata={
                "analysis_timestamp": time.time(),
                "analysis_scope": "gaps_only"
            }
        )