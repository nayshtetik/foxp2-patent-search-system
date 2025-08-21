from typing import Dict, Any, List, Union, Optional, Tuple
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from .base_agent import BasePatentAgent, PatentData, PatentDataType, Task

@dataclass
class MarketOpportunity:
    market_segment: str
    market_size: float  # in USD millions
    growth_rate: float  # annual %
    competitive_intensity: str
    barrier_to_entry: str
    regulatory_complexity: str
    time_to_market: str
    revenue_potential: Dict[str, float]  # years -> revenue
    risk_factors: List[str]
    success_probability: float

@dataclass
class CompetitivePosition:
    competitor_name: str
    market_share: float
    competitive_advantage: str
    patent_strength: str
    product_pipeline: List[str]
    threat_level: str
    differentiation_opportunities: List[str]

@dataclass
class ValueAssessment:
    technology_value: float  # in USD millions
    market_value: float
    strategic_value: float
    risk_adjusted_value: float
    licensing_value: Dict[str, float]  # different licensing scenarios
    acquisition_value: float
    valuation_confidence: float
    value_drivers: List[str]
    value_risks: List[str]

@dataclass
class CommercializationStrategy:
    recommended_path: str
    timeline: Dict[str, str]  # milestones -> dates
    investment_required: Dict[str, float]  # stages -> amounts
    partnership_opportunities: List[str]
    licensing_strategy: Dict[str, Any]
    go_to_market_approach: str
    success_metrics: List[str]

class MarketingAnalysisAgent(BasePatentAgent):
    def __init__(self, agent_id: str = "marketing_analyzer_001"):
        super().__init__(
            agent_id=agent_id,
            name="Marketing Analysis Agent",
            description="Analyzes market potential and commercial value of patent technologies"
        )
        self.market_data_sources = {
            'pharmaceutical': self._load_pharma_market_data(),
            'chemical': self._load_chemical_market_data(),
            'biotech': self._load_biotech_market_data()
        }
        
    def get_capabilities(self) -> List[str]:
        return [
            "market_size_analysis",
            "competitive_landscape_assessment", 
            "technology_valuation",
            "commercialization_strategy",
            "licensing_opportunity_analysis",
            "partnership_identification",
            "go_to_market_planning",
            "risk_assessment",
            "revenue_forecasting",
            "strategic_positioning",
            "investment_requirements_analysis",
            "regulatory_pathway_analysis"
        ]
    
    def get_supported_input_types(self) -> List[PatentDataType]:
        return [PatentDataType.PATENT_DOCUMENT, PatentDataType.ANALYSIS_REPORT, PatentDataType.COVERAGE_MAP]
    
    def get_output_type(self) -> PatentDataType:
        return PatentDataType.MARKET_ASSESSMENT
    
    def process_task(self, task: Task) -> PatentData:
        if task.type == "market_analysis":
            return self._comprehensive_market_analysis(task.input_data)
        elif task.type == "valuation_analysis":
            return self._technology_valuation(task.input_data)
        elif task.type == "competitive_analysis":
            return self._competitive_analysis(task.input_data)
        elif task.type == "commercialization_strategy":
            return self._commercialization_strategy(task.input_data)
        elif task.type == "licensing_analysis":
            return self._licensing_opportunity_analysis(task.input_data)
        else:
            raise ValueError(f"Unsupported task type: {task.type}")
    
    def _comprehensive_market_analysis(self, input_data: Union[PatentData, List[PatentData]]) -> PatentData:
        """Comprehensive market analysis combining patent, analysis, and coverage data"""
        
        # Extract data from different input types
        patent_doc = None
        analysis_report = None
        coverage_map = None
        
        if isinstance(input_data, list):
            for data in input_data:
                if data.type == PatentDataType.PATENT_DOCUMENT:
                    patent_doc = data.content.get('patent_document', {})
                elif data.type == PatentDataType.ANALYSIS_REPORT:
                    analysis_report = data.content.get('analysis_result', {})
                elif data.type == PatentDataType.COVERAGE_MAP:
                    coverage_map = data.content
        else:
            if input_data.type == PatentDataType.PATENT_DOCUMENT:
                patent_doc = input_data.content.get('patent_document', {})
        
        if not patent_doc:
            raise ValueError("Patent document required for market analysis")
        
        patent_number = patent_doc.get('patent_number', '')
        self.logger.info(f"Conducting market analysis for patent {patent_number}")
        
        # Identify technology sector
        tech_sector = self._identify_technology_sector(patent_doc)
        
        # Analyze market opportunities
        market_opportunities = self._analyze_market_opportunities(patent_doc, tech_sector, analysis_report)
        
        # Assess competitive position
        competitive_positions = self._assess_competitive_positions(patent_doc, tech_sector)
        
        # Calculate technology valuation
        value_assessment = self._calculate_technology_value(patent_doc, analysis_report, coverage_map, market_opportunities)
        
        # Develop commercialization strategy
        commercialization_strategy = self._develop_commercialization_strategy(
            patent_doc, market_opportunities, competitive_positions, value_assessment
        )
        
        # Generate strategic recommendations
        strategic_recommendations = self._generate_strategic_recommendations(
            market_opportunities, competitive_positions, value_assessment, commercialization_strategy
        )
        
        return PatentData(
            id=f"market_analysis_{patent_number}_{int(time.time())}",
            type=PatentDataType.MARKET_ASSESSMENT,
            content={
                "patent_number": patent_number,
                "technology_sector": tech_sector,
                "market_opportunities": [opp.__dict__ for opp in market_opportunities],
                "competitive_positions": [pos.__dict__ for pos in competitive_positions],
                "value_assessment": value_assessment.__dict__,
                "commercialization_strategy": commercialization_strategy.__dict__,
                "strategic_recommendations": strategic_recommendations,
                "executive_summary": self._generate_executive_summary(
                    market_opportunities, value_assessment, commercialization_strategy
                )
            },
            metadata={
                "analysis_timestamp": time.time(),
                "technology_sector": tech_sector,
                "valuation_confidence": value_assessment.valuation_confidence
            }
        )
    
    def _identify_technology_sector(self, patent_doc: Dict[str, Any]) -> str:
        """Identify primary technology sector based on patent content"""
        
        title = patent_doc.get('title', '').lower()
        abstract = patent_doc.get('abstract', '').lower()
        classification_codes = patent_doc.get('classification_codes', [])
        
        # Check for pharmaceutical/biotech indicators
        pharma_keywords = ['drug', 'pharmaceutical', 'therapeutic', 'medicine', 'treatment', 'therapy', 'foxp2', 'compound']
        biotech_keywords = ['protein', 'gene', 'dna', 'rna', 'antibody', 'vaccine', 'biomarker']
        chemical_keywords = ['chemical', 'synthesis', 'molecule', 'reaction', 'catalyst', 'polymer']
        
        text_content = f"{title} {abstract}".lower()
        
        pharma_score = sum(1 for kw in pharma_keywords if kw in text_content)
        biotech_score = sum(1 for kw in biotech_keywords if kw in text_content)
        chemical_score = sum(1 for kw in chemical_keywords if kw in text_content)
        
        # Also check classification codes
        pharma_classes = ['A61K', 'A61P']  # Pharmaceutical preparations
        biotech_classes = ['C12N', 'C07K']  # Biotechnology, proteins
        chemical_classes = ['C07C', 'C07D']  # Organic chemistry
        
        for code in classification_codes:
            if any(pc in code for pc in pharma_classes):
                pharma_score += 2
            elif any(bc in code for bc in biotech_classes):
                biotech_score += 2
            elif any(cc in code for cc in chemical_classes):
                chemical_score += 2
        
        # Determine primary sector
        if pharma_score >= biotech_score and pharma_score >= chemical_score:
            return 'pharmaceutical'
        elif biotech_score >= chemical_score:
            return 'biotech'
        else:
            return 'chemical'
    
    def _analyze_market_opportunities(self, patent_doc: Dict[str, Any], tech_sector: str, 
                                    analysis_report: Optional[Dict[str, Any]]) -> List[MarketOpportunity]:
        """Analyze market opportunities for the technology"""
        
        opportunities = []
        sector_data = self.market_data_sources.get(tech_sector, {})
        
        if tech_sector == 'pharmaceutical':
            # For FOXP2-related small molecules
            if 'foxp2' in patent_doc.get('title', '').lower() or 'foxp2' in patent_doc.get('abstract', '').lower():
                opportunities.append(MarketOpportunity(
                    market_segment="Autism Spectrum Disorders",
                    market_size=2500.0,  # USD millions
                    growth_rate=8.5,  # annual %
                    competitive_intensity="Low",
                    barrier_to_entry="High",
                    regulatory_complexity="High",
                    time_to_market="8-12 years",
                    revenue_potential={
                        "year_5": 0,
                        "year_10": 250.0,
                        "year_15": 800.0,
                        "year_20": 1200.0
                    },
                    risk_factors=[
                        "Clinical trial failure risk",
                        "FDA approval uncertainty", 
                        "Long development timeline",
                        "High development costs"
                    ],
                    success_probability=0.15  # Typical for CNS drugs
                ))
                
                opportunities.append(MarketOpportunity(
                    market_segment="Speech and Language Disorders",
                    market_size=800.0,
                    growth_rate=6.2,
                    competitive_intensity="Very Low",
                    barrier_to_entry="High",
                    regulatory_complexity="High", 
                    time_to_market="8-12 years",
                    revenue_potential={
                        "year_5": 0,
                        "year_10": 80.0,
                        "year_15": 300.0,
                        "year_20": 450.0
                    },
                    risk_factors=[
                        "Limited treatment precedent",
                        "Pediatric development challenges",
                        "Market size uncertainty"
                    ],
                    success_probability=0.20
                ))
        
        elif tech_sector == 'biotech':
            # Generic biotech opportunity
            opportunities.append(MarketOpportunity(
                market_segment="Biotechnology Tools",
                market_size=1200.0,
                growth_rate=12.3,
                competitive_intensity="Medium",
                barrier_to_entry="Medium",
                regulatory_complexity="Medium",
                time_to_market="3-5 years",
                revenue_potential={
                    "year_3": 25.0,
                    "year_5": 100.0,
                    "year_10": 300.0
                },
                risk_factors=[
                    "Technology adoption challenges",
                    "Competitive pressure"
                ],
                success_probability=0.40
            ))
        
        elif tech_sector == 'chemical':
            # Generic chemical opportunity
            opportunities.append(MarketOpportunity(
                market_segment="Specialty Chemicals",
                market_size=800.0,
                growth_rate=5.8,
                competitive_intensity="High",
                barrier_to_entry="Medium",
                regulatory_complexity="Medium",
                time_to_market="2-4 years",
                revenue_potential={
                    "year_2": 10.0,
                    "year_5": 50.0,
                    "year_10": 120.0
                },
                risk_factors=[
                    "Commodity pricing pressure",
                    "Environmental regulations"
                ],
                success_probability=0.60
            ))
        
        return opportunities
    
    def _assess_competitive_positions(self, patent_doc: Dict[str, Any], tech_sector: str) -> List[CompetitivePosition]:
        """Assess competitive positions in the market"""
        
        positions = []
        
        if tech_sector == 'pharmaceutical':
            # Major pharmaceutical companies
            positions.extend([
                CompetitivePosition(
                    competitor_name="Roche",
                    market_share=15.2,
                    competitive_advantage="Strong CNS pipeline and expertise",
                    patent_strength="Strong",
                    product_pipeline=["CNS drug candidates", "Autism therapeutics research"],
                    threat_level="High",
                    differentiation_opportunities=["First-in-class FOXP2 modulator", "Pediatric focus"]
                ),
                CompetitivePosition(
                    competitor_name="Novartis",
                    market_share=12.8,
                    competitive_advantage="Neuroscience expertise and infrastructure",
                    patent_strength="Strong",
                    product_pipeline=["Neurological therapeutics", "Gene therapy"],
                    threat_level="High", 
                    differentiation_opportunities=["Novel mechanism of action", "Oral bioavailability"]
                ),
                CompetitivePosition(
                    competitor_name="Biogen",
                    market_share=8.5,
                    competitive_advantage="CNS specialization",
                    patent_strength="Medium",
                    product_pipeline=["Neurodegeneration", "Rare CNS disorders"],
                    threat_level="Medium",
                    differentiation_opportunities=["Small molecule approach vs biologics", "Broader indication potential"]
                )
            ])
        
        elif tech_sector == 'biotech':
            positions.append(CompetitivePosition(
                competitor_name="Generic Biotech Competitors",
                market_share=25.0,
                competitive_advantage="Established market presence",
                patent_strength="Medium",
                product_pipeline=["Various biotech tools"],
                threat_level="Medium",
                differentiation_opportunities=["Superior performance", "Cost advantage"]
            ))
        
        return positions
    
    def _calculate_technology_value(self, patent_doc: Dict[str, Any], 
                                  analysis_report: Optional[Dict[str, Any]],
                                  coverage_map: Optional[Dict[str, Any]], 
                                  market_opportunities: List[MarketOpportunity]) -> ValueAssessment:
        """Calculate comprehensive technology valuation"""
        
        # Base technology value calculation
        innovation_score = 8.2  # From analysis report if available
        if analysis_report:
            innovation_score = analysis_report.get('innovation_score', 8.2)
        
        # Market-based valuation
        total_market_value = sum(opp.market_size for opp in market_opportunities)
        risk_adjusted_market_value = sum(
            opp.market_size * opp.success_probability 
            for opp in market_opportunities
        )
        
        # Patent strength factor
        patent_strength_multiplier = 1.0
        if coverage_map:
            coverage_score = coverage_map.get('coverage_summary', {}).get('coverage_score', 50)
            patent_strength_multiplier = 0.5 + (coverage_score / 100) * 0.8
        
        # Technology valuation components
        technology_value = (innovation_score / 10) * 200  # Base: $200M for perfect innovation
        market_value = risk_adjusted_market_value * 0.05  # 5% market capture assumption
        strategic_value = technology_value * 0.3  # 30% premium for strategic value
        
        risk_adjusted_value = (technology_value + market_value + strategic_value) * patent_strength_multiplier
        
        # Licensing scenarios
        licensing_scenarios = {
            "exclusive_license": risk_adjusted_value * 0.8,
            "non_exclusive_license": risk_adjusted_value * 0.3,
            "co_development": risk_adjusted_value * 0.6,
            "milestone_based": risk_adjusted_value * 0.4
        }
        
        # Acquisition value (premium for full ownership)
        acquisition_value = risk_adjusted_value * 1.5
        
        # Value drivers and risks
        value_drivers = [
            "First-in-class mechanism",
            "Large addressable market",
            "Strong patent protection",
            "Multiple indication potential",
            "Unmet medical need"
        ]
        
        value_risks = [
            "Clinical development risk",
            "Regulatory approval uncertainty",
            "Competition from alternative approaches",
            "Manufacturing complexity",
            "Market adoption challenges"
        ]
        
        # Confidence based on data quality
        valuation_confidence = 0.75
        if analysis_report and coverage_map:
            valuation_confidence = 0.85
        
        return ValueAssessment(
            technology_value=technology_value,
            market_value=market_value,
            strategic_value=strategic_value,
            risk_adjusted_value=risk_adjusted_value,
            licensing_value=licensing_scenarios,
            acquisition_value=acquisition_value,
            valuation_confidence=valuation_confidence,
            value_drivers=value_drivers,
            value_risks=value_risks
        )
    
    def _develop_commercialization_strategy(self, patent_doc: Dict[str, Any],
                                          market_opportunities: List[MarketOpportunity],
                                          competitive_positions: List[CompetitivePosition],
                                          value_assessment: ValueAssessment) -> CommercializationStrategy:
        """Develop comprehensive commercialization strategy"""
        
        # Determine recommended path based on risk/value profile
        if value_assessment.risk_adjusted_value > 500:  # High value
            if any(pos.threat_level == "High" for pos in competitive_positions):
                recommended_path = "Strategic Partnership with Major Pharma"
            else:
                recommended_path = "Independent Development with Series Funding"
        else:  # Lower value
            recommended_path = "Licensing to Established Player"
        
        # Timeline based on technology sector and regulatory requirements
        tech_sector = self._identify_technology_sector(patent_doc)
        
        if tech_sector == 'pharmaceutical':
            timeline = {
                "IND Filing": "Year 2",
                "Phase I Completion": "Year 4", 
                "Phase II Completion": "Year 7",
                "Phase III Completion": "Year 10",
                "NDA Submission": "Year 11",
                "FDA Approval": "Year 12",
                "Market Launch": "Year 13"
            }
            
            investment_required = {
                "Preclinical": 25.0,  # millions USD
                "Phase I": 15.0,
                "Phase II": 75.0,
                "Phase III": 300.0,
                "Regulatory": 25.0,
                "Launch": 100.0
            }
        else:
            timeline = {
                "Prototype Development": "Year 1",
                "Market Testing": "Year 2",
                "Regulatory Approval": "Year 3",
                "Market Launch": "Year 4"
            }
            
            investment_required = {
                "Development": 5.0,
                "Testing": 2.0,
                "Regulatory": 1.0,
                "Launch": 10.0
            }
        
        # Partnership opportunities
        partnership_opportunities = [
            "Big Pharma co-development deal",
            "Specialty pharma licensing",
            "Academic medical center collaboration",
            "Patient advocacy group partnership",
            "Government research grants"
        ]
        
        # Licensing strategy
        licensing_strategy = {
            "preferred_structure": "Milestone + royalty based",
            "upfront_payment": value_assessment.licensing_value.get("milestone_based", 0) * 0.1,
            "milestone_payments": value_assessment.licensing_value.get("milestone_based", 0) * 0.6,
            "royalty_rate": "8-12% of net sales",
            "exclusive_territories": ["US", "EU", "Japan"],
            "development_milestones": list(timeline.keys())
        }
        
        # Go-to-market approach
        if tech_sector == 'pharmaceutical':
            go_to_market = "B2B2C - Partner with established pharma for clinical development and commercialization"
        else:
            go_to_market = "Direct B2B sales with specialized distribution partners"
        
        # Success metrics
        success_metrics = [
            "FDA IND acceptance",
            "Phase I safety data",
            "Partnership deal completion",
            "Patent family expansion",
            "Market penetration metrics"
        ]
        
        return CommercializationStrategy(
            recommended_path=recommended_path,
            timeline=timeline,
            investment_required=investment_required,
            partnership_opportunities=partnership_opportunities,
            licensing_strategy=licensing_strategy,
            go_to_market_approach=go_to_market,
            success_metrics=success_metrics
        )
    
    def _generate_strategic_recommendations(self, market_opportunities: List[MarketOpportunity],
                                          competitive_positions: List[CompetitivePosition],
                                          value_assessment: ValueAssessment,
                                          commercialization_strategy: CommercializationStrategy) -> List[str]:
        """Generate strategic recommendations"""
        
        recommendations = []
        
        # Market opportunity recommendations
        high_potential_markets = [opp for opp in market_opportunities if opp.success_probability > 0.3]
        if high_potential_markets:
            market_names = [opp.market_segment for opp in high_potential_markets]
            recommendations.append(f"Focus on high-potential markets: {', '.join(market_names)}")
        
        # Competitive positioning
        high_threat_competitors = [pos for pos in competitive_positions if pos.threat_level == "High"]
        if high_threat_competitors:
            recommendations.append("Establish strong IP position and seek first-mover advantage given high competitive threat")
        
        # Valuation-based recommendations
        if value_assessment.risk_adjusted_value > 300:
            recommendations.append("High-value technology - prioritize strategic partnerships over independent development")
        
        if value_assessment.valuation_confidence < 0.7:
            recommendations.append("Conduct additional market research to improve valuation confidence")
        
        # Commercialization recommendations
        if "Partnership" in commercialization_strategy.recommended_path:
            recommendations.append("Initiate early discussions with potential pharma partners")
        
        if commercialization_strategy.investment_required.get("Phase III", 0) > 200:
            recommendations.append("Secure Series B funding or partnership before Phase III initiation")
        
        # Technology-specific recommendations
        recommendations.extend([
            "File continuation patents to strengthen IP position",
            "Conduct Freedom-to-Operate analysis in key markets",
            "Establish clinical advisory board with KOLs",
            "Consider orphan drug designation for regulatory advantages",
            "Develop comprehensive regulatory strategy early",
            "Build relationships with patient advocacy groups"
        ])
        
        return recommendations
    
    def _generate_executive_summary(self, market_opportunities: List[MarketOpportunity],
                                  value_assessment: ValueAssessment,
                                  commercialization_strategy: CommercializationStrategy) -> str:
        """Generate executive summary of market analysis"""
        
        total_market_size = sum(opp.market_size for opp in market_opportunities)
        avg_success_prob = sum(opp.success_probability for opp in market_opportunities) / len(market_opportunities)
        
        summary = f"""
        EXECUTIVE SUMMARY - Patent Technology Market Analysis
        
        Market Opportunity: ${total_market_size:.0f}M addressable market across {len(market_opportunities)} key segments
        with average success probability of {avg_success_prob*100:.0f}%.
        
        Technology Valuation: Risk-adjusted value of ${value_assessment.risk_adjusted_value:.0f}M 
        (confidence: {value_assessment.valuation_confidence*100:.0f}%).
        
        Commercialization Strategy: {commercialization_strategy.recommended_path} with estimated 
        total investment requirement of ${sum(commercialization_strategy.investment_required.values()):.0f}M.
        
        Key Value Drivers: {', '.join(value_assessment.value_drivers[:3])}.
        
        Primary Risks: {', '.join(value_assessment.value_risks[:3])}.
        
        Strategic Recommendation: Pursue {commercialization_strategy.recommended_path.lower()} to maximize 
        value realization while managing development risks.
        """
        
        return summary.strip()
    
    def _load_pharma_market_data(self) -> Dict[str, Any]:
        """Load pharmaceutical market data"""
        return {
            "cns_disorders": {
                "market_size": 3500,
                "growth_rate": 7.2,
                "key_players": ["Roche", "Novartis", "Biogen", "Eisai"]
            },
            "rare_diseases": {
                "market_size": 2200,
                "growth_rate": 11.8,
                "key_players": ["Roche", "Sanofi", "Novartis", "BioMarin"]
            }
        }
    
    def _load_biotech_market_data(self) -> Dict[str, Any]:
        """Load biotechnology market data"""
        return {
            "research_tools": {
                "market_size": 1200,
                "growth_rate": 9.5,
                "key_players": ["Thermo Fisher", "Danaher", "Agilent"]
            }
        }
    
    def _load_chemical_market_data(self) -> Dict[str, Any]:
        """Load chemical market data"""
        return {
            "specialty_chemicals": {
                "market_size": 800,
                "growth_rate": 5.2,
                "key_players": ["BASF", "Dow", "DuPont"]
            }
        }
    
    def _technology_valuation(self, patent_data: PatentData) -> PatentData:
        """Focused technology valuation analysis"""
        patent_doc = patent_data.content.get('patent_document', {})
        tech_sector = self._identify_technology_sector(patent_doc)
        market_opportunities = self._analyze_market_opportunities(patent_doc, tech_sector, None)
        value_assessment = self._calculate_technology_value(patent_doc, None, None, market_opportunities)
        
        return PatentData(
            id=f"valuation_{patent_doc.get('patent_number', 'unknown')}_{int(time.time())}",
            type=PatentDataType.MARKET_ASSESSMENT,
            content={
                "analysis_type": "valuation_only",
                "value_assessment": value_assessment.__dict__
            },
            metadata={
                "analysis_timestamp": time.time(),
                "analysis_scope": "valuation_only"
            }
        )