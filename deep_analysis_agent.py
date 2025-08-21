from typing import Dict, Any, List, Union, Optional
import openai
import time
import json
from dataclasses import dataclass

from .base_agent import BasePatentAgent, PatentData, PatentDataType, Task

@dataclass
class AnalysisResult:
    analysis_type: str
    summary: str
    key_findings: List[str]
    technical_assessment: Dict[str, Any]
    innovation_score: float
    novelty_assessment: str
    prior_art_analysis: List[Dict[str, Any]]
    claims_analysis: Dict[str, Any]
    commercial_potential: Dict[str, Any]
    competitive_landscape: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float

class DeepAnalysisAgent(BasePatentAgent):
    def __init__(self, agent_id: str = "deep_analyzer_001", gpt_model: str = "gpt-4"):
        super().__init__(
            agent_id=agent_id,
            name="Deep Analysis Agent",
            description="Performs comprehensive analysis of patents using advanced AI models"
        )
        self.gpt_model = gpt_model
        self.analysis_templates = self._load_analysis_templates()
        
    def get_capabilities(self) -> List[str]:
        return [
            "technical_analysis",
            "novelty_assessment",
            "prior_art_comparison",
            "claims_evaluation",
            "innovation_scoring",
            "commercial_assessment",
            "competitive_analysis",
            "infringement_analysis",
            "patent_quality_scoring",
            "technology_trend_analysis",
            "chemical_mechanism_analysis",
            "bioactivity_prediction"
        ]
    
    def get_supported_input_types(self) -> List[PatentDataType]:
        return [PatentDataType.PATENT_DOCUMENT, PatentDataType.CHEMICAL_STRUCTURE]
    
    def get_output_type(self) -> PatentDataType:
        return PatentDataType.ANALYSIS_REPORT
    
    def process_task(self, task: Task) -> PatentData:
        if task.type == "comprehensive_analysis":
            return self._comprehensive_patent_analysis(task.input_data)
        elif task.type == "technical_analysis":
            return self._technical_analysis(task.input_data)
        elif task.type == "chemical_analysis":
            return self._chemical_analysis(task.input_data)
        elif task.type == "novelty_analysis":
            return self._novelty_analysis(task.input_data)
        elif task.type == "competitive_analysis":
            return self._competitive_analysis(task.input_data)
        elif task.type == "infringement_analysis":
            return self._infringement_analysis(task.input_data)
        else:
            raise ValueError(f"Unsupported task type: {task.type}")
    
    def _comprehensive_patent_analysis(self, patent_data: Union[PatentData, List[PatentData]]) -> PatentData:
        """Perform comprehensive analysis of patent documents"""
        if isinstance(patent_data, list):
            patent_data = patent_data[0]  # Take first patent for single analysis
        
        if patent_data.type != PatentDataType.PATENT_DOCUMENT:
            raise ValueError("Input must be a patent document")
        
        patent_doc = patent_data.content.get('patent_document', {})
        
        self.logger.info(f"Starting comprehensive analysis for patent {patent_doc.get('patent_number')}")
        
        # Perform multiple analysis components
        technical_analysis = self._analyze_technical_content(patent_doc)
        novelty_analysis = self._analyze_novelty(patent_doc)
        claims_analysis = self._analyze_claims(patent_doc)
        chemical_analysis = self._analyze_chemical_aspects(patent_doc)
        commercial_analysis = self._analyze_commercial_potential(patent_doc)
        competitive_analysis = self._analyze_competitive_landscape(patent_doc)
        
        # Generate overall assessment
        overall_assessment = self._generate_overall_assessment({
            'technical': technical_analysis,
            'novelty': novelty_analysis,
            'claims': claims_analysis,
            'chemical': chemical_analysis,
            'commercial': commercial_analysis,
            'competitive': competitive_analysis
        })
        
        analysis_result = AnalysisResult(
            analysis_type="comprehensive",
            summary=overall_assessment.get('summary', ''),
            key_findings=overall_assessment.get('key_findings', []),
            technical_assessment=technical_analysis,
            innovation_score=overall_assessment.get('innovation_score', 0.0),
            novelty_assessment=novelty_analysis.get('assessment', ''),
            prior_art_analysis=novelty_analysis.get('prior_art', []),
            claims_analysis=claims_analysis,
            commercial_potential=commercial_analysis,
            competitive_landscape=competitive_analysis,
            recommendations=overall_assessment.get('recommendations', []),
            confidence_score=overall_assessment.get('confidence_score', 0.0)
        )
        
        return PatentData(
            id=f"analysis_{patent_doc.get('patent_number', 'unknown')}_{int(time.time())}",
            type=PatentDataType.ANALYSIS_REPORT,
            content={
                "patent_number": patent_doc.get('patent_number', ''),
                "analysis_result": analysis_result.__dict__,
                "analysis_components": {
                    'technical': technical_analysis,
                    'novelty': novelty_analysis,
                    'claims': claims_analysis,
                    'chemical': chemical_analysis,
                    'commercial': commercial_analysis,
                    'competitive': competitive_analysis
                }
            },
            metadata={
                "analysis_timestamp": time.time(),
                "gpt_model_used": self.gpt_model,
                "source_patent_id": patent_data.id
            }
        )
    
    def _analyze_technical_content(self, patent_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical content of patent using GPT"""
        
        # Prepare prompt for technical analysis
        prompt = self._build_technical_analysis_prompt(patent_doc)
        
        # Call GPT API (simulated)
        gpt_response = self._call_gpt_api(prompt, "technical_analysis")
        
        return {
            "technical_field": gpt_response.get("technical_field", ""),
            "problem_statement": gpt_response.get("problem_statement", ""),
            "solution_approach": gpt_response.get("solution_approach", ""),
            "technical_advantages": gpt_response.get("technical_advantages", []),
            "implementation_complexity": gpt_response.get("implementation_complexity", ""),
            "technical_feasibility": gpt_response.get("technical_feasibility", ""),
            "key_technical_features": gpt_response.get("key_technical_features", []),
            "potential_limitations": gpt_response.get("potential_limitations", [])
        }
    
    def _analyze_novelty(self, patent_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze novelty and non-obviousness"""
        
        prompt = self._build_novelty_analysis_prompt(patent_doc)
        gpt_response = self._call_gpt_api(prompt, "novelty_analysis")
        
        return {
            "novelty_score": gpt_response.get("novelty_score", 0.0),
            "assessment": gpt_response.get("assessment", ""),
            "novel_aspects": gpt_response.get("novel_aspects", []),
            "prior_art": gpt_response.get("prior_art_analysis", []),
            "obviousness_assessment": gpt_response.get("obviousness_assessment", ""),
            "inventive_step": gpt_response.get("inventive_step", "")
        }
    
    def _analyze_claims(self, patent_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patent claims structure and quality"""
        
        claims = patent_doc.get('claims', [])
        
        prompt = self._build_claims_analysis_prompt(claims)
        gpt_response = self._call_gpt_api(prompt, "claims_analysis")
        
        return {
            "total_claims": len(claims),
            "independent_claims": gpt_response.get("independent_claims_count", 0),
            "dependent_claims": gpt_response.get("dependent_claims_count", 0),
            "claim_scope": gpt_response.get("claim_scope", ""),
            "claim_clarity": gpt_response.get("claim_clarity", ""),
            "claim_strength": gpt_response.get("claim_strength", ""),
            "potential_infringement_scope": gpt_response.get("infringement_scope", ""),
            "claim_dependencies": gpt_response.get("claim_dependencies", {}),
            "broadest_claims": gpt_response.get("broadest_claims", []),
            "narrowest_claims": gpt_response.get("narrowest_claims", [])
        }
    
    def _analyze_chemical_aspects(self, patent_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze chemical structures and mechanisms"""
        
        chemical_structures = patent_doc.get('chemical_structures', [])
        
        if not chemical_structures:
            return {"chemical_content": "No chemical structures found"}
        
        prompt = self._build_chemical_analysis_prompt(patent_doc, chemical_structures)
        gpt_response = self._call_gpt_api(prompt, "chemical_analysis")
        
        return {
            "chemical_count": len(chemical_structures),
            "compound_types": gpt_response.get("compound_types", []),
            "mechanism_of_action": gpt_response.get("mechanism_of_action", ""),
            "bioactivity_prediction": gpt_response.get("bioactivity_prediction", ""),
            "synthesis_complexity": gpt_response.get("synthesis_complexity", ""),
            "drug_likeness": gpt_response.get("drug_likeness", ""),
            "safety_concerns": gpt_response.get("safety_concerns", []),
            "therapeutic_applications": gpt_response.get("therapeutic_applications", []),
            "chemical_novelty": gpt_response.get("chemical_novelty", ""),
            "structure_activity_relationships": gpt_response.get("sar_analysis", "")
        }
    
    def _analyze_commercial_potential(self, patent_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze commercial potential and market opportunities"""
        
        prompt = self._build_commercial_analysis_prompt(patent_doc)
        gpt_response = self._call_gpt_api(prompt, "commercial_analysis")
        
        return {
            "market_size": gpt_response.get("market_size_estimate", ""),
            "target_markets": gpt_response.get("target_markets", []),
            "commercialization_timeline": gpt_response.get("commercialization_timeline", ""),
            "development_costs": gpt_response.get("development_costs", ""),
            "revenue_potential": gpt_response.get("revenue_potential", ""),
            "licensing_opportunities": gpt_response.get("licensing_opportunities", []),
            "partnership_potential": gpt_response.get("partnership_potential", ""),
            "regulatory_hurdles": gpt_response.get("regulatory_hurdles", []),
            "competitive_advantages": gpt_response.get("competitive_advantages", []),
            "commercialization_risks": gpt_response.get("commercialization_risks", [])
        }
    
    def _analyze_competitive_landscape(self, patent_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive landscape and patent positioning"""
        
        prompt = self._build_competitive_analysis_prompt(patent_doc)
        gpt_response = self._call_gpt_api(prompt, "competitive_analysis")
        
        return {
            "key_competitors": gpt_response.get("key_competitors", []),
            "competing_technologies": gpt_response.get("competing_technologies", []),
            "patent_landscape": gpt_response.get("patent_landscape", ""),
            "white_space_opportunities": gpt_response.get("white_space_opportunities", []),
            "freedom_to_operate": gpt_response.get("freedom_to_operate", ""),
            "blocking_patents": gpt_response.get("blocking_patents", []),
            "design_around_opportunities": gpt_response.get("design_around_opportunities", []),
            "cross_licensing_potential": gpt_response.get("cross_licensing_potential", "")
        }
    
    def _generate_overall_assessment(self, component_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall assessment from component analyses"""
        
        prompt = self._build_overall_assessment_prompt(component_analyses)
        gpt_response = self._call_gpt_api(prompt, "overall_assessment")
        
        return gpt_response
    
    def _build_technical_analysis_prompt(self, patent_doc: Dict[str, Any]) -> str:
        """Build prompt for technical analysis"""
        return f"""
        Analyze the following patent for its technical content:
        
        Title: {patent_doc.get('title', '')}
        Abstract: {patent_doc.get('abstract', '')[:1000]}...
        Claims (first 3): {patent_doc.get('claims', [])[:3]}
        
        Provide analysis in the following areas:
        1. Technical field and domain
        2. Problem statement being addressed
        3. Solution approach taken
        4. Key technical advantages
        5. Implementation complexity
        6. Technical feasibility assessment
        7. Key technical features
        8. Potential technical limitations
        
        Respond in JSON format with these keys: technical_field, problem_statement, solution_approach, technical_advantages, implementation_complexity, technical_feasibility, key_technical_features, potential_limitations
        """
    
    def _build_novelty_analysis_prompt(self, patent_doc: Dict[str, Any]) -> str:
        """Build prompt for novelty analysis"""
        return f"""
        Analyze the novelty and non-obviousness of this patent:
        
        Title: {patent_doc.get('title', '')}
        Abstract: {patent_doc.get('abstract', '')}
        Key Claims: {patent_doc.get('claims', [])[:5]}
        
        Assess:
        1. Overall novelty score (0-10)
        2. Novel aspects of the invention
        3. Prior art analysis and comparison
        4. Obviousness assessment
        5. Inventive step evaluation
        
        Consider the technical field: {patent_doc.get('classification_codes', [])}
        
        Respond in JSON format with keys: novelty_score, assessment, novel_aspects, prior_art_analysis, obviousness_assessment, inventive_step
        """
    
    def _build_claims_analysis_prompt(self, claims: List[str]) -> str:
        """Build prompt for claims analysis"""
        claims_text = "\n".join([f"Claim {i+1}: {claim}" for i, claim in enumerate(claims[:10])])
        
        return f"""
        Analyze the following patent claims:
        
        {claims_text}
        
        Provide analysis on:
        1. Count of independent vs dependent claims
        2. Scope of claims (broad vs narrow)
        3. Clarity of claim language
        4. Strength of claims for enforcement
        5. Potential infringement scope
        6. Claim dependencies structure
        7. Identify broadest and narrowest claims
        
        Respond in JSON format with keys: independent_claims_count, dependent_claims_count, claim_scope, claim_clarity, claim_strength, infringement_scope, claim_dependencies, broadest_claims, narrowest_claims
        """
    
    def _build_chemical_analysis_prompt(self, patent_doc: Dict[str, Any], chemical_structures: List[Any]) -> str:
        """Build prompt for chemical analysis"""
        chem_info = []
        for i, struct in enumerate(chemical_structures[:5]):
            if hasattr(struct, 'mol_formula') and hasattr(struct, 'iupac_name'):
                chem_info.append(f"Compound {i+1}: {struct.mol_formula} - {struct.iupac_name}")
        
        return f"""
        Analyze the chemical aspects of this patent:
        
        Title: {patent_doc.get('title', '')}
        Chemical Structures Found: {chr(10).join(chem_info)}
        
        For compounds mentioned, particularly focusing on FOXP2-related small molecules or NIB compounds, analyze:
        1. Types of compounds (small molecules, biologics, etc.)
        2. Predicted mechanism of action
        3. Bioactivity predictions
        4. Synthesis complexity
        5. Drug-likeness assessment
        6. Safety concerns
        7. Therapeutic applications
        8. Chemical novelty
        9. Structure-activity relationships
        
        Respond in JSON format with keys: compound_types, mechanism_of_action, bioactivity_prediction, synthesis_complexity, drug_likeness, safety_concerns, therapeutic_applications, chemical_novelty, sar_analysis
        """
    
    def _build_commercial_analysis_prompt(self, patent_doc: Dict[str, Any]) -> str:
        """Build prompt for commercial analysis"""
        return f"""
        Analyze the commercial potential of this patent:
        
        Title: {patent_doc.get('title', '')}
        Abstract: {patent_doc.get('abstract', '')}
        Technical Field: {patent_doc.get('classification_codes', [])}
        Assignees: {patent_doc.get('assignees', [])}
        
        Assess:
        1. Market size estimation
        2. Target markets and applications
        3. Commercialization timeline
        4. Development costs estimation
        5. Revenue potential
        6. Licensing opportunities
        7. Partnership potential
        8. Regulatory hurdles
        9. Competitive advantages
        10. Commercialization risks
        
        Consider pharmaceutical/biotech applications if relevant.
        
        Respond in JSON format with keys: market_size_estimate, target_markets, commercialization_timeline, development_costs, revenue_potential, licensing_opportunities, partnership_potential, regulatory_hurdles, competitive_advantages, commercialization_risks
        """
    
    def _build_competitive_analysis_prompt(self, patent_doc: Dict[str, Any]) -> str:
        """Build prompt for competitive analysis"""
        return f"""
        Analyze the competitive landscape for this patent:
        
        Title: {patent_doc.get('title', '')}
        Assignees: {patent_doc.get('assignees', [])}
        Technical Field: {patent_doc.get('classification_codes', [])}
        
        Analyze:
        1. Key competitors in this space
        2. Competing technologies
        3. Patent landscape overview
        4. White space opportunities
        5. Freedom to operate assessment
        6. Potential blocking patents
        7. Design-around opportunities
        8. Cross-licensing potential
        
        Respond in JSON format with keys: key_competitors, competing_technologies, patent_landscape, white_space_opportunities, freedom_to_operate, blocking_patents, design_around_opportunities, cross_licensing_potential
        """
    
    def _build_competitive_analysis_prompt(self, patent_doc: Dict[str, Any]) -> str:
        """Build prompt for competitive analysis"""
        return f"""
        Analyze the competitive landscape for this patent:
        
        Title: {patent_doc.get('title', '')}
        Assignees: {patent_doc.get('assignees', [])}
        Technical Field: {patent_doc.get('classification_codes', [])}
        
        Analyze:
        1. Key competitors in this space
        2. Competing technologies
        3. Patent landscape overview
        4. White space opportunities
        5. Freedom to operate assessment
        6. Potential blocking patents
        7. Design-around opportunities
        8. Cross-licensing potential
        
        Respond in JSON format with keys: key_competitors, competing_technologies, patent_landscape, white_space_opportunities, freedom_to_operate, blocking_patents, design_around_opportunities, cross_licensing_potential
        """
    
    def _build_overall_assessment_prompt(self, component_analyses: Dict[str, Any]) -> str:
        """Build prompt for overall assessment"""
        return f"""
        Based on the following component analyses, provide an overall assessment:
        
        Technical Analysis: {json.dumps(component_analyses.get('technical', {}), indent=2)}
        Novelty Analysis: {json.dumps(component_analyses.get('novelty', {}), indent=2)}
        Commercial Analysis: {json.dumps(component_analyses.get('commercial', {}), indent=2)}
        Competitive Analysis: {json.dumps(component_analyses.get('competitive', {}), indent=2)}
        
        Provide:
        1. Executive summary (2-3 paragraphs)
        2. Top 5 key findings
        3. Overall innovation score (0-10)
        4. Strategic recommendations (5-7 points)
        5. Confidence score in this assessment (0-1)
        
        Respond in JSON format with keys: summary, key_findings, innovation_score, recommendations, confidence_score
        """
    
    def _call_gpt_api(self, prompt: str, analysis_type: str) -> Dict[str, Any]:
        """Call GPT API for analysis (simulated)"""
        # In a real implementation, this would call OpenAI's API
        # For now, return simulated responses
        
        self.logger.info(f"Calling GPT API for {analysis_type}")
        
        # Simulated responses based on analysis type
        if analysis_type == "technical_analysis":
            return {
                "technical_field": "Pharmaceutical chemistry / Drug discovery",
                "problem_statement": "Development of small molecule modulators for FOXP2 protein",
                "solution_approach": "Novel small molecule design targeting FOXP2 binding sites",
                "technical_advantages": ["High specificity", "Good bioavailability", "Low toxicity"],
                "implementation_complexity": "Moderate - requires specialized synthesis",
                "technical_feasibility": "High - established synthetic routes available",
                "key_technical_features": ["FOXP2 binding specificity", "NIB-based structure", "Oral bioavailability"],
                "potential_limitations": ["Metabolic stability concerns", "Potential off-target effects"]
            }
        
        elif analysis_type == "novelty_analysis":
            return {
                "novelty_score": 8.5,
                "assessment": "High novelty in FOXP2 small molecule modulation approach",
                "novel_aspects": ["First small molecule FOXP2 modulator", "Novel NIB scaffold", "Unique binding mechanism"],
                "prior_art_analysis": [
                    {"patent": "US123456", "relevance": "Partial - different target"},
                    {"patent": "EP789012", "relevance": "Low - different chemical class"}
                ],
                "obviousness_assessment": "Non-obvious due to novel target approach",
                "inventive_step": "Strong inventive step demonstrated"
            }
        
        elif analysis_type == "claims_analysis":
            return {
                "independent_claims_count": 3,
                "dependent_claims_count": 15,
                "claim_scope": "Appropriately broad with specific limitations",
                "claim_clarity": "Clear and well-defined",
                "claim_strength": "Strong - covers key aspects of invention",
                "infringement_scope": "Good coverage of commercial embodiments",
                "claim_dependencies": {"1": [2, 3, 4], "5": [6, 7, 8]},
                "broadest_claims": ["Claim 1 - compound genus"],
                "narrowest_claims": ["Claim 15 - specific pharmaceutical formulation"]
            }
        
        elif analysis_type == "chemical_analysis":
            return {
                "compound_types": ["Small molecule heterocycles", "NIB derivatives"],
                "mechanism_of_action": "Allosteric modulation of FOXP2 transcriptional activity",
                "bioactivity_prediction": "Predicted CNS activity with moderate potency",
                "synthesis_complexity": "Moderate - 8-12 synthetic steps",
                "drug_likeness": "Good Lipinski compliance",
                "safety_concerns": ["Potential CNS effects", "Metabolite toxicity"],
                "therapeutic_applications": ["Neurodevelopmental disorders", "Speech/language therapy"],
                "chemical_novelty": "High - novel scaffold for FOXP2 modulation",
                "sar_analysis": "Structure-activity relationships favor benzyl substitutions"
            }
        
        elif analysis_type == "commercial_analysis":
            return {
                "market_size_estimate": "$2-5 billion (rare disease therapeutics)",
                "target_markets": ["Autism spectrum disorders", "Language disorders", "Neurodevelopmental conditions"],
                "commercialization_timeline": "8-12 years (includes clinical development)",
                "development_costs": "$500M-1B (typical orphan drug development)",
                "revenue_potential": "High for rare disease indication",
                "licensing_opportunities": ["Big pharma partnerships", "Specialty pharma deals"],
                "partnership_potential": "High - requires specialized development expertise",
                "regulatory_hurdles": ["FDA orphan drug designation", "EMA pediatric studies"],
                "competitive_advantages": ["First-in-class mechanism", "Strong IP position"],
                "commercialization_risks": ["Clinical trial failures", "Regulatory delays"]
            }
        
        elif analysis_type == "competitive_analysis":
            return {
                "key_competitors": ["Roche", "Novartis", "Biogen"],
                "competing_technologies": ["Gene therapy approaches", "Protein replacement"],
                "patent_landscape": "Sparse - early stage field with limited competition",
                "white_space_opportunities": ["Alternative FOXP2 modulators", "Combination therapies"],
                "freedom_to_operate": "Good - few blocking patents identified",
                "blocking_patents": [],
                "design_around_opportunities": ["Alternative chemical scaffolds", "Different binding sites"],
                "cross_licensing_potential": "Limited - few relevant patents in field"
            }
        
        elif analysis_type == "overall_assessment":
            return {
                "summary": "This patent represents a significant advancement in FOXP2-targeted therapeutics with strong technical merit and commercial potential. The novel small molecule approach addresses a critical unmet need in neurodevelopmental disorders. While development risks exist, the first-in-class nature and strong IP position provide substantial competitive advantages.",
                "key_findings": [
                    "First small molecule FOXP2 modulator with novel mechanism",
                    "Strong patent claims covering key commercial embodiments", 
                    "High market potential in rare neurodevelopmental disorders",
                    "Clear freedom to operate with minimal blocking patents",
                    "Significant development timeline and costs required"
                ],
                "innovation_score": 8.2,
                "recommendations": [
                    "Pursue orphan drug designation early",
                    "Establish partnerships with neurodevelopmental disorder specialists",
                    "Conduct extensive safety studies given CNS target",
                    "File continuation applications to strengthen IP position",
                    "Consider platform approach for multiple FOXP2-related conditions",
                    "Explore pediatric development pathways",
                    "Build specialized clinical development team"
                ],
                "confidence_score": 0.85
            }
        
        # Default fallback
        return {"error": "Analysis type not implemented"}
    
    def _load_analysis_templates(self) -> Dict[str, str]:
        """Load analysis prompt templates"""
        return {
            "technical": "Technical analysis template...",
            "novelty": "Novelty analysis template...",
            "commercial": "Commercial analysis template...",
            "competitive": "Competitive analysis template..."
        }
    
    def _technical_analysis(self, patent_data: PatentData) -> PatentData:
        """Perform focused technical analysis"""
        if patent_data.type != PatentDataType.PATENT_DOCUMENT:
            raise ValueError("Input must be a patent document")
        
        patent_doc = patent_data.content.get('patent_document', {})
        technical_analysis = self._analyze_technical_content(patent_doc)
        
        return PatentData(
            id=f"tech_analysis_{patent_doc.get('patent_number', 'unknown')}_{int(time.time())}",
            type=PatentDataType.ANALYSIS_REPORT,
            content={
                "analysis_type": "technical_only",
                "patent_number": patent_doc.get('patent_number', ''),
                "technical_analysis": technical_analysis
            },
            metadata={
                "analysis_timestamp": time.time(),
                "analysis_scope": "technical_only"
            }
        )
    
    def _chemical_analysis(self, patent_data: PatentData) -> PatentData:
        """Perform focused chemical analysis"""
        if patent_data.type not in [PatentDataType.PATENT_DOCUMENT, PatentDataType.CHEMICAL_STRUCTURE]:
            raise ValueError("Input must be patent document or chemical structure data")
        
        if patent_data.type == PatentDataType.PATENT_DOCUMENT:
            patent_doc = patent_data.content.get('patent_document', {})
            chemical_analysis = self._analyze_chemical_aspects(patent_doc)
        else:
            # Handle chemical structure data directly
            chemical_structures = patent_data.content.get('chemical_structures', [])
            chemical_analysis = {"structures_analyzed": len(chemical_structures)}
        
        return PatentData(
            id=f"chem_analysis_{int(time.time())}",
            type=PatentDataType.ANALYSIS_REPORT,
            content={
                "analysis_type": "chemical_only",
                "chemical_analysis": chemical_analysis
            },
            metadata={
                "analysis_timestamp": time.time(),
                "analysis_scope": "chemical_only"
            }
        )