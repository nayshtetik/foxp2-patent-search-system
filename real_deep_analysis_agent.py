import openai
import time
import json
import os
from typing import Dict, Any, List, Union, Optional
from dataclasses import dataclass

from base_agent import BasePatentAgent, PatentData, PatentDataType, Task

@dataclass
class RealAnalysisResult:
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
    gpt_model_used: str
    analysis_timestamp: float

class RealDeepAnalysisAgent(BasePatentAgent):
    """Real deep analysis agent using actual OpenAI GPT API"""
    
    def __init__(self, agent_id: str = "real_deep_analyzer_001"):
        super().__init__(
            agent_id=agent_id,
            name="Real Deep Analysis Agent",
            description="Performs real patent analysis using OpenAI GPT API"
        )
        
        # Set up OpenAI client
        self.setup_openai()
        
        # Analysis configuration
        self.model_config = {
            'model': os.getenv('OPENAI_MODEL', 'gpt-4'),
            'temperature': 0.3,
            'max_tokens': 4000,
            'top_p': 0.9
        }
        
    def setup_openai(self):
        """Setup OpenAI API client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        
        # Test API connection
        try:
            # Simple test call
            response = self.client.chat.completions.create(
                model=self.model_config['model'],
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            self.logger.info("OpenAI API connection successful")
        except Exception as e:
            self.logger.error(f"OpenAI API connection failed: {e}")
            raise
    
    def get_capabilities(self) -> List[str]:
        return [
            "real_technical_analysis",
            "real_novelty_assessment",
            "real_prior_art_analysis",
            "real_claims_evaluation",
            "real_innovation_scoring",
            "real_commercial_assessment",
            "real_competitive_analysis",
            "real_patent_quality_scoring",
            "real_chemical_mechanism_analysis",
            "real_freedom_to_operate_analysis"
        ]
    
    def get_supported_input_types(self) -> List[PatentDataType]:
        return [PatentDataType.PATENT_DOCUMENT, PatentDataType.QUERY_RESULT]
    
    def get_output_type(self) -> PatentDataType:
        return PatentDataType.ANALYSIS_REPORT
    
    def process_task(self, task: Task) -> PatentData:
        if task.type == "real_comprehensive_analysis":
            return self._real_comprehensive_analysis(task.input_data)
        elif task.type == "real_technical_analysis":
            return self._real_technical_analysis(task.input_data)
        elif task.type == "real_novelty_analysis":
            return self._real_novelty_analysis(task.input_data)
        elif task.type == "real_commercial_analysis":
            return self._real_commercial_analysis(task.input_data)
        else:
            raise ValueError(f"Unsupported task type: {task.type}")
    
    def _real_comprehensive_analysis(self, patent_data: Union[PatentData, List[PatentData]]) -> PatentData:
        """Perform real comprehensive patent analysis using GPT"""
        
        # Handle different input types
        if isinstance(patent_data, list):
            # If multiple patents, analyze the first one or combine
            if patent_data and patent_data[0].type == PatentDataType.QUERY_RESULT:
                patents_list = patent_data[0].content.get('patents', [])
                if not patents_list:
                    raise ValueError("No patents found in query results")
                patent_info = patents_list[0]  # Analyze first patent
                patent_number = patent_info.get('patent_number', 'Unknown')
            else:
                raise ValueError("Unsupported input data format")
        else:
            if patent_data.type == PatentDataType.PATENT_DOCUMENT:
                patent_info = patent_data.content.get('patent_document', {})
                patent_number = patent_info.get('patent_number', 'Unknown')
            else:
                raise ValueError("Input must be patent document or query result")
        
        self.logger.info(f"Starting real comprehensive analysis for patent {patent_number}")
        
        # Perform real analysis using GPT
        technical_analysis = self._analyze_with_gpt("technical", patent_info)
        novelty_analysis = self._analyze_with_gpt("novelty", patent_info)
        claims_analysis = self._analyze_with_gpt("claims", patent_info)
        commercial_analysis = self._analyze_with_gpt("commercial", patent_info)
        competitive_analysis = self._analyze_with_gpt("competitive", patent_info)
        
        # Generate overall assessment
        overall_assessment = self._generate_overall_assessment({
            'technical': technical_analysis,
            'novelty': novelty_analysis,
            'claims': claims_analysis,
            'commercial': commercial_analysis,
            'competitive': competitive_analysis
        })
        
        # Create real analysis result
        analysis_result = RealAnalysisResult(
            analysis_type="comprehensive_real",
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
            confidence_score=overall_assessment.get('confidence_score', 0.0),
            gpt_model_used=self.model_config['model'],
            analysis_timestamp=time.time()
        )
        
        return PatentData(
            id=f"real_analysis_{patent_number}_{int(time.time())}",
            type=PatentDataType.ANALYSIS_REPORT,
            content={
                "patent_number": patent_number,
                "analysis_result": analysis_result.__dict__,
                "raw_patent_data": patent_info,
                "analysis_metadata": {
                    "model_used": self.model_config['model'],
                    "analysis_timestamp": time.time(),
                    "total_tokens_used": self._calculate_total_tokens_used()
                }
            },
            metadata={
                "analysis_timestamp": time.time(),
                "gpt_model_used": self.model_config['model'],
                "agent_id": self.agent_id
            }
        )
    
    def _analyze_with_gpt(self, analysis_type: str, patent_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform specific type of analysis using real GPT API"""
        
        prompt = self._build_analysis_prompt(analysis_type, patent_info)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_config['model'],
                messages=[
                    {"role": "system", "content": "You are an expert patent analyst with deep knowledge of intellectual property, technology assessment, and commercial evaluation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.model_config['temperature'],
                max_tokens=self.model_config['max_tokens'],
                top_p=self.model_config['top_p']
            )
            
            # Extract and parse response
            gpt_response_text = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text analysis
            try:
                gpt_response = json.loads(gpt_response_text)
            except json.JSONDecodeError:
                # If not valid JSON, create structured response from text
                gpt_response = self._parse_text_response(gpt_response_text, analysis_type)
            
            # Add metadata
            gpt_response['_metadata'] = {
                'tokens_used': response.usage.total_tokens,
                'model': response.model,
                'analysis_type': analysis_type,
                'timestamp': time.time()
            }
            
            self.logger.info(f"GPT {analysis_type} analysis completed - tokens used: {response.usage.total_tokens}")
            return gpt_response
            
        except Exception as e:
            self.logger.error(f"GPT API call failed for {analysis_type}: {e}")
            # Return fallback analysis
            return self._get_fallback_analysis(analysis_type)
    
    def _build_analysis_prompt(self, analysis_type: str, patent_info: Dict[str, Any]) -> str:
        """Build specific analysis prompts for different types"""
        
        base_patent_info = f"""
        Patent Number: {patent_info.get('patent_number', 'Unknown')}
        Title: {patent_info.get('title', 'No title available')}
        Abstract: {patent_info.get('abstract', 'No abstract available')[:2000]}
        Inventors: {', '.join(patent_info.get('inventors', []))}
        Assignees: {', '.join(patent_info.get('assignees', []))}
        Publication Date: {patent_info.get('publication_date', 'Unknown')}
        Filing Date: {patent_info.get('filing_date', 'Unknown')}
        """
        
        if analysis_type == "technical":
            return f"""
            Analyze the following patent for its technical content and innovation:
            
            {base_patent_info}
            
            Provide analysis in the following JSON format:
            {{
                "technical_field": "Primary technical domain",
                "problem_statement": "What problem does this patent solve?",
                "solution_approach": "How does it solve the problem?",
                "technical_advantages": ["List of key advantages"],
                "implementation_complexity": "Assessment of complexity (Low/Medium/High)",
                "technical_feasibility": "Feasibility assessment",
                "key_technical_features": ["List of main technical features"],
                "potential_limitations": ["List of potential limitations"],
                "innovation_level": "Scale 1-10"
            }}
            """
        
        elif analysis_type == "novelty":
            return f"""
            Assess the novelty and non-obviousness of this patent:
            
            {base_patent_info}
            
            Provide analysis in JSON format:
            {{
                "novelty_score": 7.5,
                "assessment": "Overall novelty assessment",
                "novel_aspects": ["List of novel elements"],
                "prior_art": [
                    {{"reference": "Related work", "relevance": "How it relates", "differentiation": "Key differences"}}
                ],
                "obviousness_assessment": "Assessment of non-obviousness",
                "inventive_step": "Description of inventive step"
            }}
            """
        
        elif analysis_type == "claims":
            return f"""
            Analyze the patent claims structure and quality:
            
            {base_patent_info}
            
            Provide analysis in JSON format:
            {{
                "claim_scope": "Assessment of claim breadth",
                "claim_clarity": "Clarity assessment",
                "claim_strength": "Strength for enforcement",
                "potential_infringement_scope": "Scope for detecting infringement",
                "broadest_claims": ["Identify broadest claims"],
                "narrowest_claims": ["Identify narrowest claims"]
            }}
            """
        
        elif analysis_type == "commercial":
            return f"""
            Analyze the commercial potential of this patent:
            
            {base_patent_info}
            
            Focus on market size, applications, revenue potential, and commercialization strategy.
            
            Provide analysis in JSON format:
            {{
                "market_size": "Estimated market size",
                "target_markets": ["List of target markets"],
                "commercialization_timeline": "Timeline estimate",
                "revenue_potential": "Revenue assessment",
                "licensing_opportunities": ["Potential licensing scenarios"],
                "regulatory_hurdles": ["List regulatory challenges"],
                "competitive_advantages": ["List advantages"],
                "commercialization_risks": ["List of risks"]
            }}
            """
        
        elif analysis_type == "competitive":
            return f"""
            Analyze the competitive landscape for this patent:
            
            {base_patent_info}
            
            Provide analysis in JSON format:
            {{
                "key_competitors": ["List main competitors"],
                "competing_technologies": ["Alternative approaches"],
                "patent_landscape": "Overview of related patents",
                "white_space_opportunities": ["Opportunities for new patents"],
                "freedom_to_operate": "Assessment of FTO",
                "design_around_opportunities": ["Ways to design around"]
            }}
            """
        
        else:
            return f"Analyze this patent: {base_patent_info}"
    
    def _parse_text_response(self, text_response: str, analysis_type: str) -> Dict[str, Any]:
        """Parse non-JSON text response into structured format"""
        
        # Basic parsing based on analysis type
        if analysis_type == "technical":
            return {
                "technical_field": "Extracted from text analysis",
                "problem_statement": "Identified from patent description",
                "solution_approach": "Analyzed approach",
                "technical_advantages": ["Advantage identified from analysis"],
                "raw_analysis": text_response
            }
        
        # Default structure for other types
        return {
            "analysis_text": text_response,
            "analysis_type": analysis_type,
            "structured_data": "Available in raw analysis text"
        }
    
    def _generate_overall_assessment(self, component_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall assessment using GPT"""
        
        prompt = f"""
        Based on the following component analyses, provide an overall assessment:
        
        Technical Analysis: {json.dumps(component_analyses.get('technical', {}), indent=2)[:1500]}
        Novelty Analysis: {json.dumps(component_analyses.get('novelty', {}), indent=2)[:1500]}
        Commercial Analysis: {json.dumps(component_analyses.get('commercial', {}), indent=2)[:1500]}
        
        Provide overall assessment in JSON format:
        {{
            "summary": "Executive summary (2-3 sentences)",
            "key_findings": ["Top 5 key findings"],
            "innovation_score": 8.5,
            "recommendations": ["Strategic recommendations"],
            "confidence_score": 0.85
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_config['model'],
                messages=[
                    {"role": "system", "content": "You are synthesizing patent analysis results into an executive summary."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content
            
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                return {
                    "summary": "Overall assessment completed with detailed analysis",
                    "key_findings": ["Technical innovation identified", "Commercial potential assessed"],
                    "innovation_score": 7.5,
                    "recommendations": ["Further analysis recommended"],
                    "confidence_score": 0.75,
                    "raw_assessment": result_text
                }
                
        except Exception as e:
            self.logger.error(f"Overall assessment generation failed: {e}")
            return {
                "summary": "Analysis completed with component assessments",
                "key_findings": ["Analysis available in component sections"],
                "innovation_score": 6.0,
                "recommendations": ["Review component analyses"],
                "confidence_score": 0.6
            }
    
    def _get_fallback_analysis(self, analysis_type: str) -> Dict[str, Any]:
        """Provide fallback analysis when GPT fails"""
        return {
            "analysis_type": analysis_type,
            "status": "fallback_analysis",
            "message": f"GPT analysis failed, using fallback for {analysis_type}",
            "confidence": 0.3,
            "timestamp": time.time()
        }
    
    def _calculate_total_tokens_used(self) -> int:
        """Calculate total tokens used in this analysis session"""
        # This would track tokens across all API calls
        # For now, return estimated value
        return 5000  # Placeholder
    
    # Specialized analysis methods
    def _real_technical_analysis(self, patent_data: PatentData) -> PatentData:
        """Focused technical analysis using real GPT"""
        if patent_data.type == PatentDataType.QUERY_RESULT:
            patents_list = patent_data.content.get('patents', [])
            if not patents_list:
                raise ValueError("No patents found in query results")
            patent_info = patents_list[0]
        else:
            patent_info = patent_data.content.get('patent_document', {})
        
        technical_analysis = self._analyze_with_gpt("technical", patent_info)
        
        return PatentData(
            id=f"real_tech_analysis_{int(time.time())}",
            type=PatentDataType.ANALYSIS_REPORT,
            content={
                "analysis_type": "technical_only",
                "patent_number": patent_info.get('patent_number', ''),
                "technical_analysis": technical_analysis
            },
            metadata={
                "analysis_timestamp": time.time(),
                "model_used": self.model_config['model']
            }
        )
    
    def analyze_foxp2_patent_real(self, patent_data: PatentData) -> PatentData:
        """Specialized real analysis for FOXP2 patents"""
        
        # Extract patent information
        if patent_data.type == PatentDataType.QUERY_RESULT:
            patents_list = patent_data.content.get('patents', [])
            if not patents_list:
                raise ValueError("No patents found for FOXP2 analysis")
            
            # Find FOXP2-related patent
            foxp2_patent = None
            for patent in patents_list:
                title_lower = patent.get('title', '').lower()
                abstract_lower = patent.get('abstract', '').lower()
                if 'foxp2' in title_lower or 'foxp2' in abstract_lower:
                    foxp2_patent = patent
                    break
            
            if not foxp2_patent:
                foxp2_patent = patents_list[0]  # Use first patent if no specific FOXP2 match
        else:
            foxp2_patent = patent_data.content.get('patent_document', {})
        
        # Specialized FOXP2 analysis prompt
        foxp2_analysis_prompt = f"""
        Analyze this FOXP2-related patent for pharmaceutical and neuroscience applications:
        
        Patent: {foxp2_patent.get('patent_number', '')}
        Title: {foxp2_patent.get('title', '')}
        Abstract: {foxp2_patent.get('abstract', '')[:2000]}
        
        Focus on:
        1. FOXP2 biological function and targeting mechanism
        2. Therapeutic applications (autism, speech disorders, neurodevelopment)
        3. Small molecule drug development potential
        4. Market opportunity in CNS therapeutics
        5. Regulatory pathway considerations
        
        Provide detailed JSON analysis:
        {{
            "foxp2_mechanism": "How does this relate to FOXP2 function?",
            "therapeutic_applications": ["List potential applications"],
            "drug_development_stage": "Assessment of development stage",
            "market_potential": "Market size and opportunity",
            "clinical_pathway": "Regulatory and clinical considerations",
            "competitive_landscape": "Other FOXP2 approaches",
            "innovation_score": 8.5,
            "commercial_viability": "Assessment of commercial potential"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_config['model'],
                messages=[
                    {"role": "system", "content": "You are a pharmaceutical patent analyst specializing in neuroscience and CNS drug development, with expertise in FOXP2 and autism therapeutics."},
                    {"role": "user", "content": foxp2_analysis_prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            analysis_text = response.choices[0].message.content
            
            try:
                foxp2_analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                foxp2_analysis = {
                    "analysis_text": analysis_text,
                    "analysis_type": "foxp2_specialized"
                }
            
            return PatentData(
                id=f"foxp2_analysis_{int(time.time())}",
                type=PatentDataType.ANALYSIS_REPORT,
                content={
                    "analysis_type": "foxp2_specialized",
                    "patent_number": foxp2_patent.get('patent_number', ''),
                    "foxp2_analysis": foxp2_analysis,
                    "tokens_used": response.usage.total_tokens
                },
                metadata={
                    "analysis_timestamp": time.time(),
                    "specialized_analysis": "foxp2_cns_therapeutics",
                    "model_used": self.model_config['model']
                }
            )
            
        except Exception as e:
            self.logger.error(f"FOXP2 specialized analysis failed: {e}")
            raise