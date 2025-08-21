#!/usr/bin/env python3
"""
🤖 Modern ChatGPT-5 Enhanced Patent Analysis System
==================================================

Advanced patent intelligence using OpenAI's ChatGPT-5 Responses API for 
sophisticated analysis of FOXP2 therapeutic patents and drug discovery opportunities.
Uses the latest OpenAI Python client with reasoning capabilities.
"""

import os
import json
import time
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI

@dataclass
class PatentAnalysis:
    """Enhanced patent analysis using ChatGPT-5"""
    patent_number: str
    commercial_potential: str
    innovation_score: float
    technical_feasibility: str
    market_opportunity: str
    competitive_landscape: str
    investment_recommendation: str
    detailed_analysis: str
    reasoning_tokens: int

class ModernChatGPT5PatentAnalyzer:
    """Advanced patent analysis using OpenAI ChatGPT-5 Responses API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key"""
        # Initialize OpenAI client - reads from environment if no key provided
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        
        self.client = OpenAI()  # Automatically reads OPENAI_API_KEY
        
        # Model configuration for GPT-5 reasoning
        self.model = "gpt-5"
        self.reasoning_effort = "medium"  # low | medium | high
        self.max_completion_tokens = 4000
        
        print(f"🤖 Modern ChatGPT-5 Patent Analyzer Initialized")
        print(f"🎯 Model: {self.model}")
        print(f"🧠 Reasoning Effort: {self.reasoning_effort}")
    
    def test_api_connection(self) -> bool:
        """Test OpenAI Responses API connectivity"""
        try:
            print("🔍 Testing OpenAI Responses API connection...")
            
            response = self.client.responses.create(
                model=self.model,
                reasoning={"effort": "low"},  # Use low effort for quick test
                input="Test connection. Respond with 'API_CONNECTED'."
            )
            
            content = response.output_text
            reasoning_tokens = getattr(response, 'reasoning_tokens', 0)
            
            print("✅ OpenAI Responses API connection successful!")
            print(f"💬 Response: {content[:100]}...")
            print(f"🧠 Reasoning tokens used: {reasoning_tokens}")
            return True
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def analyze_patent_with_gpt5(self, patent_data: Dict) -> PatentAnalysis:
        """Deep patent analysis using ChatGPT-5 Responses API"""
        
        analysis_prompt = f"""
        You are an expert pharmaceutical patent analyst with deep expertise in drug discovery, 
        FOXP2 biology, and commercial biotechnology. Analyze this FOXP2-related therapeutic patent:
        
        PATENT: {patent_data.get('patent_number', 'Unknown')}
        TITLE: {patent_data.get('title', 'No title')}
        ABSTRACT: {patent_data.get('abstract', 'No abstract available')}
        THERAPEUTIC AREA: {patent_data.get('therapeutic_area', 'Unknown')}
        DEVELOPMENT STAGE: {patent_data.get('development_stage', 'Unknown')}
        MOLECULE TYPE: {patent_data.get('molecule_type', 'Unknown')}
        RELEVANCE SCORE: {patent_data.get('relevance_score', 'Unknown')}
        
        Provide a comprehensive analysis with DEEP REASONING covering:
        
        1. COMMERCIAL POTENTIAL (High/Medium/Low) - Analyze market size, revenue potential, competitive advantages
        2. INNOVATION SCORE (1-10) - Assess technical novelty, breakthrough potential, IP strength
        3. TECHNICAL FEASIBILITY - Evaluate development challenges, manufacturing complexity, success probability
        4. MARKET OPPORTUNITY - Identify target markets, patient populations, unmet medical needs
        5. COMPETITIVE LANDSCAPE - Analyze patent freedom to operate, competitor positioning, IP landscape
        6. INVESTMENT RECOMMENDATION - Provide strategic advice on licensing, development, partnerships
        7. DETAILED ANALYSIS - Comprehensive 300-word technical and commercial assessment
        
        Focus specifically on:
        - FOXP2's role in speech/language disorders, autism, neurodevelopment
        - Potential broader therapeutic applications beyond known indications  
        - Manufacturing feasibility and scale-up considerations
        - Regulatory pathway complexity and approval timeline
        - Commercial viability and market positioning
        
        Think step-by-step through each analysis dimension. Consider multiple scenarios and provide nuanced judgments.
        
        Format your response as structured JSON:
        {{
            "commercial_potential": "High/Medium/Low with detailed justification",
            "innovation_score": 8.5,
            "technical_feasibility": "detailed technical assessment with probability estimates",
            "market_opportunity": "comprehensive market analysis with size estimates",
            "competitive_landscape": "thorough competitor and IP analysis", 
            "investment_recommendation": "strategic advice with specific recommendations",
            "detailed_analysis": "comprehensive 300-word assessment covering all key factors"
        }}
        """
        
        try:
            print(f"🔬 Analyzing patent {patent_data.get('patent_number', 'Unknown')} with ChatGPT-5...")
            
            # Use Responses API with reasoning
            response = self.client.responses.create(
                model=self.model,
                reasoning={"effort": self.reasoning_effort},
                input=analysis_prompt
            )
            
            content = response.output_text
            reasoning_tokens = getattr(response, 'reasoning_tokens', 0)
            
            print(f"🧠 Reasoning tokens used: {reasoning_tokens}")
            
            # Parse JSON response
            try:
                # Look for JSON in the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    analysis_data = json.loads(json_content)
                    
                    return PatentAnalysis(
                        patent_number=patent_data.get('patent_number', 'Unknown'),
                        commercial_potential=analysis_data.get('commercial_potential', 'Unknown'),
                        innovation_score=float(analysis_data.get('innovation_score', 0)),
                        technical_feasibility=analysis_data.get('technical_feasibility', 'Unknown'),
                        market_opportunity=analysis_data.get('market_opportunity', 'Unknown'),
                        competitive_landscape=analysis_data.get('competitive_landscape', 'Unknown'),
                        investment_recommendation=analysis_data.get('investment_recommendation', 'Unknown'),
                        detailed_analysis=analysis_data.get('detailed_analysis', 'Unknown'),
                        reasoning_tokens=reasoning_tokens
                    )
                    
                else:
                    print(f"⚠️ No JSON found in response for {patent_data.get('patent_number')}")
                    return self._create_fallback_analysis(patent_data, content, reasoning_tokens)
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse JSON response for {patent_data.get('patent_number')}: {e}")
                return self._create_fallback_analysis(patent_data, content, reasoning_tokens)
                    
        except Exception as e:
            print(f"❌ Analysis failed for {patent_data.get('patent_number', 'Unknown')}: {e}")
            return self._create_error_analysis(patent_data, str(e))
    
    def _create_fallback_analysis(self, patent_data: Dict, raw_response: str, reasoning_tokens: int) -> PatentAnalysis:
        """Create fallback analysis when JSON parsing fails"""
        return PatentAnalysis(
            patent_number=patent_data.get('patent_number', 'Unknown'),
            commercial_potential="Medium - requires detailed review",
            innovation_score=7.0,
            technical_feasibility="Requires detailed technical review based on response content",
            market_opportunity="FOXP2 therapeutic market opportunity identified",
            competitive_landscape="Patent landscape requires detailed analysis",
            investment_recommendation="Further investigation recommended based on ChatGPT-5 analysis",
            detailed_analysis=raw_response[:500] + "..." if len(raw_response) > 500 else raw_response,
            reasoning_tokens=reasoning_tokens
        )
    
    def _create_error_analysis(self, patent_data: Dict, error_msg: str) -> PatentAnalysis:
        """Create error analysis when API call fails"""
        return PatentAnalysis(
            patent_number=patent_data.get('patent_number', 'Unknown'),
            commercial_potential="Unknown",
            innovation_score=0.0,
            technical_feasibility=f"Analysis error: {error_msg}",
            market_opportunity="Could not analyze due to error",
            competitive_landscape="Could not analyze due to error",
            investment_recommendation="Manual review required due to analysis error",
            detailed_analysis=f"ChatGPT-5 analysis failed: {error_msg}",
            reasoning_tokens=0
        )
    
    def analyze_patent_portfolio(self, patents_data: List[Dict]) -> List[PatentAnalysis]:
        """Analyze entire patent portfolio with ChatGPT-5 Responses API"""
        
        print(f"🚀 Starting ChatGPT-5 Responses API analysis of {len(patents_data)} patents")
        print("=" * 70)
        
        analyses = []
        total_reasoning_tokens = 0
        
        for i, patent in enumerate(patents_data, 1):
            print(f"\n📄 Patent {i}/{len(patents_data)}: {patent.get('patent_number', 'Unknown')}")
            
            analysis = self.analyze_patent_with_gpt5(patent)
            analyses.append(analysis)
            total_reasoning_tokens += analysis.reasoning_tokens
            
            print(f"✅ Analysis complete - Commercial Potential: {analysis.commercial_potential[:50]}...")
            print(f"📊 Innovation Score: {analysis.innovation_score}/10")
            print(f"🧠 Reasoning tokens: {analysis.reasoning_tokens}")
            
            # Rate limiting - respectful API usage
            if i < len(patents_data):
                print("⏳ Waiting 3 seconds (rate limiting)...")
                time.sleep(3)
        
        print(f"\n🏆 Portfolio analysis complete!")
        print(f"📊 Total patents analyzed: {len(analyses)}")
        print(f"🧠 Total reasoning tokens used: {total_reasoning_tokens:,}")
        print(f"💰 Estimated reasoning cost: ${(total_reasoning_tokens / 1000000) * 10:.2f}")
        
        return analyses
    
    def generate_investment_report(self, analyses: List[PatentAnalysis]) -> Dict:
        """Generate executive investment report from ChatGPT-5 analyses"""
        
        print("📊 Generating executive investment report...")
        
        # Calculate portfolio metrics
        high_potential = [a for a in analyses if 'High' in a.commercial_potential]
        medium_potential = [a for a in analyses if 'Medium' in a.commercial_potential] 
        low_potential = [a for a in analyses if 'Low' in a.commercial_potential]
        
        avg_innovation = sum(a.innovation_score for a in analyses if a.innovation_score > 0) / len([a for a in analyses if a.innovation_score > 0])
        top_innovations = sorted(analyses, key=lambda x: x.innovation_score, reverse=True)[:5]
        
        total_reasoning_tokens = sum(a.reasoning_tokens for a in analyses)
        
        report = {
            "executive_summary": {
                "total_patents": len(analyses),
                "high_commercial_potential": len(high_potential),
                "medium_commercial_potential": len(medium_potential),
                "low_commercial_potential": len(low_potential),
                "average_innovation_score": round(avg_innovation, 2),
                "total_reasoning_tokens": total_reasoning_tokens,
                "estimated_analysis_cost": round((total_reasoning_tokens / 1000000) * 10, 2),
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "model_used": self.model,
                "reasoning_effort": self.reasoning_effort
            },
            "top_opportunities": [
                {
                    "rank": idx + 1,
                    "patent": patent.patent_number,
                    "innovation_score": patent.innovation_score,
                    "commercial_potential": patent.commercial_potential[:100] + "..." if len(patent.commercial_potential) > 100 else patent.commercial_potential,
                    "recommendation": patent.investment_recommendation[:200] + "..." if len(patent.investment_recommendation) > 200 else patent.investment_recommendation,
                    "reasoning_tokens": patent.reasoning_tokens
                }
                for idx, patent in enumerate(top_innovations)
            ],
            "detailed_analyses": [
                {
                    "patent_number": analysis.patent_number,
                    "commercial_potential": analysis.commercial_potential,
                    "innovation_score": analysis.innovation_score,
                    "technical_feasibility": analysis.technical_feasibility,
                    "market_opportunity": analysis.market_opportunity,
                    "competitive_landscape": analysis.competitive_landscape,
                    "investment_recommendation": analysis.investment_recommendation,
                    "detailed_analysis": analysis.detailed_analysis,
                    "reasoning_tokens": analysis.reasoning_tokens
                }
                for analysis in analyses
            ]
        }
        
        return report
    
    def save_analysis_results(self, analyses: List[PatentAnalysis], report: Dict):
        """Save ChatGPT-5 analysis results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed analyses as CSV
        df_data = []
        for analysis in analyses:
            df_data.append({
                "patent_number": analysis.patent_number,
                "commercial_potential": analysis.commercial_potential[:300] + "..." if len(analysis.commercial_potential) > 300 else analysis.commercial_potential,
                "innovation_score": analysis.innovation_score,
                "technical_feasibility": analysis.technical_feasibility[:300] + "..." if len(analysis.technical_feasibility) > 300 else analysis.technical_feasibility,
                "market_opportunity": analysis.market_opportunity[:300] + "..." if len(analysis.market_opportunity) > 300 else analysis.market_opportunity,
                "competitive_landscape": analysis.competitive_landscape[:300] + "..." if len(analysis.competitive_landscape) > 300 else analysis.competitive_landscape,
                "investment_recommendation": analysis.investment_recommendation[:300] + "..." if len(analysis.investment_recommendation) > 300 else analysis.investment_recommendation,
                "detailed_analysis": analysis.detailed_analysis[:500] + "..." if len(analysis.detailed_analysis) > 500 else analysis.detailed_analysis,
                "reasoning_tokens": analysis.reasoning_tokens
            })
        
        df = pd.DataFrame(df_data)
        csv_path = f"patent_data/chatgpt5_analysis/modern_chatgpt5_analysis_{timestamp}.csv"
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        df.to_csv(csv_path, index=False)
        
        # Save full report as JSON
        json_path = f"patent_data/chatgpt5_analysis/modern_chatgpt5_report_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"💾 ChatGPT-5 Analysis Results Saved:")
        print(f"📊 CSV: {csv_path}")
        print(f"📄 JSON: {json_path}")
        
        return csv_path, json_path


def main():
    """Main execution function"""
    print("🚀 MODERN CHATGPT-5 ENHANCED FOXP2 PATENT ANALYSIS")
    print("=" * 60)
    
    # Initialize analyzer with API key from environment
    api_key = "YOUR_OPENAI_API_KEY_HERE"
    analyzer = ModernChatGPT5PatentAnalyzer(api_key)
    
    # Test API connection
    if not analyzer.test_api_connection():
        print("❌ API connection failed. Please check your API key.")
        return
    
    # Load human therapeutic patents
    try:
        df = pd.read_csv("patent_data/human_therapeutics/human_therapeutic_patents_20250821_065621.csv")
        patents_data = df.to_dict('records')
        
        print(f"\n📄 Loaded {len(patents_data)} human therapeutic patents")
        print(f"🎯 Starting comprehensive ChatGPT-5 Responses API analysis...")
        
        # Analyze patents with ChatGPT-5
        analyses = analyzer.analyze_patent_portfolio(patents_data)
        
        # Generate investment report
        report = analyzer.generate_investment_report(analyses)
        
        # Save results
        csv_path, json_path = analyzer.save_analysis_results(analyses, report)
        
        # Display summary
        print(f"\n🎯 CHATGPT-5 ANALYSIS SUMMARY:")
        print(f"=" * 40)
        print(f"📊 Total Patents Analyzed: {len(analyses)}")
        print(f"🔥 High Commercial Potential: {report['executive_summary']['high_commercial_potential']}")
        print(f"📈 Average Innovation Score: {report['executive_summary']['average_innovation_score']}/10")
        print(f"🧠 Total Reasoning Tokens: {report['executive_summary']['total_reasoning_tokens']:,}")
        print(f"💰 Estimated Cost: ${report['executive_summary']['estimated_analysis_cost']}")
        
        print(f"\n🏆 TOP 5 OPPORTUNITIES:")
        for opp in report['top_opportunities']:
            print(f"  {opp['rank']}. {opp['patent']} - Score: {opp['innovation_score']}/10")
            print(f"     Reasoning tokens: {opp['reasoning_tokens']}")
        
        print(f"\n✅ Modern ChatGPT-5 analysis complete!")
        
    except FileNotFoundError:
        print("❌ Human therapeutic patents file not found.")
        print("📄 Expected: patent_data/human_therapeutics/human_therapeutic_patents_20250821_065621.csv")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")


if __name__ == "__main__":
    main()