#!/usr/bin/env python3
"""
🤖 ChatGPT-5 Enhanced Patent Analysis System
===========================================

Advanced patent intelligence using OpenAI's ChatGPT-5 API for sophisticated
analysis of FOXP2 therapeutic patents and drug discovery opportunities.
"""

import os
import json
import time
import requests
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

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

class ChatGPT5PatentAnalyzer:
    """Advanced patent analysis using OpenAI ChatGPT-5 API"""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Model configuration - Using GPT-5 full model
        self.model = "gpt-5"  # GPT-5 full model for best analysis
        self.max_completion_tokens = 4000  # Updated parameter for GPT-5
        # Note: GPT-5 only supports default temperature (1)
        self.reasoning_effort = "medium"  # GPT-5 reasoning capability
        
        print(f"🤖 ChatGPT-5 Patent Analyzer Initialized")
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"🎯 Model: {self.model}")
    
    def test_api_connection(self) -> bool:
        """Test OpenAI API connectivity"""
        try:
            print("🔍 Testing OpenAI API connection...")
            
            test_data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": "Test connection. Respond with 'API_CONNECTED'."}
                ],
                "max_completion_tokens": 50
                # GPT-5 uses default temperature only
            }
            
            response = requests.post(
                self.base_url, 
                headers=self.headers, 
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                print("✅ OpenAI API connection successful!")
                print(f"📊 Model: {result.get('model', 'Unknown')}")
                print(f"💬 Response: {content[:100]}...")
                return True
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def analyze_patent_with_gpt5(self, patent_data: Dict) -> PatentAnalysis:
        """Deep patent analysis using ChatGPT-5"""
        
        prompt = f"""
        You are an expert pharmaceutical patent analyst with deep expertise in drug discovery, 
        FOXP2 biology, and commercial biotechnology. Analyze this FOXP2-related therapeutic patent:
        
        PATENT: {patent_data.get('patent_number', 'Unknown')}
        TITLE: {patent_data.get('title', 'No title')}
        ABSTRACT: {patent_data.get('abstract', 'No abstract available')}
        THERAPEUTIC AREA: {patent_data.get('therapeutic_area', 'Unknown')}
        DEVELOPMENT STAGE: {patent_data.get('development_stage', 'Unknown')}
        MOLECULE TYPE: {patent_data.get('molecule_type', 'Unknown')}
        RELEVANCE SCORE: {patent_data.get('relevance_score', 'Unknown')}
        
        Provide a comprehensive analysis covering:
        
        1. COMMERCIAL POTENTIAL (High/Medium/Low) - Market size and revenue potential
        2. INNOVATION SCORE (1-10) - Technical novelty and breakthrough potential  
        3. TECHNICAL FEASIBILITY - Development challenges and success probability
        4. MARKET OPPORTUNITY - Target markets, patient populations, competitive advantages
        5. COMPETITIVE LANDSCAPE - Patent freedom to operate, competitor analysis
        6. INVESTMENT RECOMMENDATION - Licensing, development, or partnership advice
        7. DETAILED ANALYSIS - Comprehensive 200-word technical and commercial assessment
        
        Focus on FOXP2's role in speech/language disorders, autism, and potential broader 
        therapeutic applications. Consider manufacturing feasibility, regulatory pathway,
        and commercial viability.
        
        Format your response as structured JSON:
        {{
            "commercial_potential": "High/Medium/Low",
            "innovation_score": 8.5,
            "technical_feasibility": "detailed assessment",
            "market_opportunity": "market analysis",
            "competitive_landscape": "competitor analysis", 
            "investment_recommendation": "strategic advice",
            "detailed_analysis": "comprehensive assessment"
        }}
        """
        
        try:
            print(f"🔬 Analyzing patent {patent_data.get('patent_number', 'Unknown')} with ChatGPT-5...")
            
            request_data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert pharmaceutical patent analyst specializing in FOXP2 therapeutics and drug discovery."},
                    {"role": "user", "content": prompt}
                ],
                "max_completion_tokens": self.max_completion_tokens,
                "reasoning_effort": self.reasoning_effort
                # GPT-5 uses default temperature (1) only
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON response
                try:
                    analysis_data = json.loads(content)
                    
                    return PatentAnalysis(
                        patent_number=patent_data.get('patent_number', 'Unknown'),
                        commercial_potential=analysis_data.get('commercial_potential', 'Unknown'),
                        innovation_score=float(analysis_data.get('innovation_score', 0)),
                        technical_feasibility=analysis_data.get('technical_feasibility', 'Unknown'),
                        market_opportunity=analysis_data.get('market_opportunity', 'Unknown'),
                        competitive_landscape=analysis_data.get('competitive_landscape', 'Unknown'),
                        investment_recommendation=analysis_data.get('investment_recommendation', 'Unknown'),
                        detailed_analysis=analysis_data.get('detailed_analysis', 'Unknown')
                    )
                    
                except json.JSONDecodeError:
                    print(f"⚠️ Failed to parse JSON response for {patent_data.get('patent_number')}")
                    print(f"📄 Raw response: {content[:200]}...")
                    return self._create_fallback_analysis(patent_data, content)
                    
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return self._create_error_analysis(patent_data, f"API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Analysis failed for {patent_data.get('patent_number', 'Unknown')}: {e}")
            return self._create_error_analysis(patent_data, str(e))
    
    def _create_fallback_analysis(self, patent_data: Dict, raw_response: str) -> PatentAnalysis:
        """Create fallback analysis when JSON parsing fails"""
        return PatentAnalysis(
            patent_number=patent_data.get('patent_number', 'Unknown'),
            commercial_potential="Medium",
            innovation_score=7.0,
            technical_feasibility="Requires detailed technical review",
            market_opportunity="FOXP2 therapeutic market opportunity",
            competitive_landscape="Patent landscape requires analysis",
            investment_recommendation="Further investigation recommended",
            detailed_analysis=raw_response[:500]
        )
    
    def _create_error_analysis(self, patent_data: Dict, error_msg: str) -> PatentAnalysis:
        """Create error analysis when API call fails"""
        return PatentAnalysis(
            patent_number=patent_data.get('patent_number', 'Unknown'),
            commercial_potential="Unknown",
            innovation_score=0.0,
            technical_feasibility=f"Analysis error: {error_msg}",
            market_opportunity="Could not analyze",
            competitive_landscape="Could not analyze",
            investment_recommendation="Manual review required",
            detailed_analysis=f"ChatGPT-5 analysis failed: {error_msg}"
        )
    
    def analyze_patent_portfolio(self, patents_data: List[Dict]) -> List[PatentAnalysis]:
        """Analyze entire patent portfolio with ChatGPT-5"""
        
        print(f"🚀 Starting ChatGPT-5 analysis of {len(patents_data)} patents")
        print("=" * 60)
        
        analyses = []
        
        for i, patent in enumerate(patents_data, 1):
            print(f"\n📄 Patent {i}/{len(patents_data)}: {patent.get('patent_number', 'Unknown')}")
            
            analysis = self.analyze_patent_with_gpt5(patent)
            analyses.append(analysis)
            
            print(f"✅ Analysis complete - Commercial Potential: {analysis.commercial_potential}")
            print(f"📊 Innovation Score: {analysis.innovation_score}/10")
            
            # Rate limiting - respectful API usage
            if i < len(patents_data):
                print("⏳ Waiting 2 seconds (rate limiting)...")
                time.sleep(2)
        
        print(f"\n🏆 Portfolio analysis complete! {len(analyses)} patents analyzed.")
        return analyses
    
    def generate_investment_report(self, analyses: List[PatentAnalysis]) -> Dict:
        """Generate executive investment report from analyses"""
        
        print("📊 Generating executive investment report...")
        
        # Calculate portfolio metrics
        high_potential = [a for a in analyses if a.commercial_potential == "High"]
        medium_potential = [a for a in analyses if a.commercial_potential == "Medium"] 
        low_potential = [a for a in analyses if a.commercial_potential == "Low"]
        
        avg_innovation = sum(a.innovation_score for a in analyses) / len(analyses)
        top_innovations = sorted(analyses, key=lambda x: x.innovation_score, reverse=True)[:3]
        
        report = {
            "executive_summary": {
                "total_patents": len(analyses),
                "high_potential": len(high_potential),
                "medium_potential": len(medium_potential),
                "low_potential": len(low_potential),
                "average_innovation_score": round(avg_innovation, 2),
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "top_opportunities": [
                {
                    "patent": patent.patent_number,
                    "innovation_score": patent.innovation_score,
                    "commercial_potential": patent.commercial_potential,
                    "recommendation": patent.investment_recommendation
                }
                for patent in top_innovations
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
                    "detailed_analysis": analysis.detailed_analysis
                }
                for analysis in analyses
            ]
        }
        
        return report
    
    def save_analysis_results(self, analyses: List[PatentAnalysis], report: Dict):
        """Save analysis results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed analyses as CSV
        df_data = []
        for analysis in analyses:
            df_data.append({
                "patent_number": analysis.patent_number,
                "commercial_potential": analysis.commercial_potential,
                "innovation_score": analysis.innovation_score,
                "technical_feasibility": analysis.technical_feasibility[:200] + "...",
                "market_opportunity": analysis.market_opportunity[:200] + "...",
                "competitive_landscape": analysis.competitive_landscape[:200] + "...",
                "investment_recommendation": analysis.investment_recommendation[:200] + "...",
                "detailed_analysis": analysis.detailed_analysis[:300] + "..."
            })
        
        df = pd.DataFrame(df_data)
        csv_path = f"patent_data/chatgpt5_analysis/chatgpt5_patent_analysis_{timestamp}.csv"
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        df.to_csv(csv_path, index=False)
        
        # Save full report as JSON
        json_path = f"patent_data/chatgpt5_analysis/chatgpt5_investment_report_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"💾 Results saved:")
        print(f"📊 CSV: {csv_path}")
        print(f"📄 JSON: {json_path}")
        
        return csv_path, json_path


def main():
    """Main execution function"""
    print("🚀 CHATGPT-5 ENHANCED FOXP2 PATENT ANALYSIS")
    print("=" * 50)
    
    # Initialize analyzer
    api_key = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY_HERE')
    analyzer = ChatGPT5PatentAnalyzer(api_key)
    
    # Test API connection
    if not analyzer.test_api_connection():
        print("❌ API connection failed. Please check your API key.")
        return
    
    # Load human therapeutic patents
    try:
        df = pd.read_csv("patent_data/human_therapeutics/human_therapeutic_patents_20250821_065621.csv")
        patents_data = df.to_dict('records')
        
        print(f"📄 Loaded {len(patents_data)} human therapeutic patents")
        
        # Analyze patents with ChatGPT-5
        analyses = analyzer.analyze_patent_portfolio(patents_data)
        
        # Generate investment report
        report = analyzer.generate_investment_report(analyses)
        
        # Save results
        csv_path, json_path = analyzer.save_analysis_results(analyses, report)
        
        # Display summary
        print(f"\n🎯 ANALYSIS SUMMARY:")
        print(f"📊 Total Patents Analyzed: {len(analyses)}")
        print(f"🔥 High Commercial Potential: {report['executive_summary']['high_potential']}")
        print(f"📈 Average Innovation Score: {report['executive_summary']['average_innovation_score']}/10")
        
        print(f"\n🏆 TOP 3 OPPORTUNITIES:")
        for i, opp in enumerate(report['top_opportunities'], 1):
            print(f"  {i}. {opp['patent']} - Score: {opp['innovation_score']}/10")
        
        print(f"\n✅ ChatGPT-5 analysis complete!")
        
    except FileNotFoundError:
        print("❌ Human therapeutic patents file not found.")
        print("📄 Expected: patent_data/human_therapeutics/human_therapeutic_patents_20250821_065621.csv")


if __name__ == "__main__":
    main()