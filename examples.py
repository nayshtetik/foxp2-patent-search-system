#!/usr/bin/env python3
"""
Patent Search System Examples

This file demonstrates how to use the patent search system for various scenarios.
"""

import asyncio
import json
from typing import List, Dict, Any

from patent_search_system import (
    create_patent_search_system,
    PatentSearchCoordinator,
    get_config,
    load_config
)

def example_1_foxp2_search():
    """
    Example 1: Search for FOXP2 small molecule patents
    
    This example demonstrates searching for patents related to FOXP2 (Forkhead Box P2)
    small molecule modulators, particularly NIB-type compounds.
    """
    print("=== Example 1: FOXP2 Small Molecule Patent Search ===")
    
    # Create the patent search system
    coordinator = create_patent_search_system()
    
    try:
        # Search for FOXP2-related patents
        result = coordinator.search_foxp2_small_molecules([
            "modulator", "therapeutic", "autism", "speech disorder"
        ])
        
        print(f"Workflow completed: {result.success}")
        print(f"Execution time: {result.total_execution_time:.2f} seconds")
        print(f"Steps completed: {[step.value for step in result.steps_completed]}")
        
        if result.success:
            # Extract key results
            from patent_search_system.agent_coordinator import WorkflowStep
            
            if WorkflowStep.QUERY in result.results:
                query_result = result.results[WorkflowStep.QUERY]
                print(f"Found {query_result.content.get('total_results', 0)} patents")
            
            if WorkflowStep.ANALYZE in result.results:
                analysis_result = result.results[WorkflowStep.ANALYZE]
                analysis_data = analysis_result.content.get('analysis_result', {})
                print(f"Innovation score: {analysis_data.get('innovation_score', 'N/A')}")
                print(f"Key findings: {analysis_data.get('key_findings', [])}")
            
            if WorkflowStep.MARKETING in result.results:
                market_result = result.results[WorkflowStep.MARKETING]
                value_assessment = market_result.content.get('value_assessment', {})
                print(f"Technology value: ${value_assessment.get('risk_adjusted_value', 0):.0f}M")
        
        else:
            print("Workflow failed:")
            for error in result.error_messages:
                print(f"  - {error}")
        
        return result
    
    finally:
        coordinator.shutdown()

def example_2_specific_patent_analysis():
    """
    Example 2: Analyze a specific patent by number
    
    This example shows how to perform a quick evaluation of a specific patent.
    """
    print("\n=== Example 2: Specific Patent Analysis ===")
    
    coordinator = create_patent_search_system()
    
    try:
        # Analyze a specific patent (using a simulated patent number)
        patent_number = "US10123456B2"
        
        result = coordinator.quick_patent_evaluation(patent_number)
        
        print(f"Patent {patent_number} analysis completed: {result.success}")
        print(f"Execution time: {result.total_execution_time:.2f} seconds")
        
        if result.success:
            from patent_search_system.agent_coordinator import WorkflowStep
            
            if WorkflowStep.ANALYZE in result.results:
                analysis = result.results[WorkflowStep.ANALYZE]
                analysis_data = analysis.content.get('analysis_result', {})
                
                print(f"Novelty assessment: {analysis_data.get('novelty_assessment', 'N/A')}")
                print(f"Technical assessment: {analysis_data.get('technical_assessment', {}).get('technical_field', 'N/A')}")
                print(f"Commercial potential: {analysis_data.get('commercial_potential', {}).get('market_size', 'N/A')}")
        
        return result
    
    finally:
        coordinator.shutdown()

def example_3_market_analysis_workflow():
    """
    Example 3: Market-focused analysis for pharmaceutical patents
    
    This example demonstrates how to perform market analysis for a set of keywords.
    """
    print("\n=== Example 3: Market-Focused Analysis ===")
    
    coordinator = create_patent_search_system()
    
    try:
        # Market analysis for neurodevelopmental therapeutics
        keywords = ["autism", "neurodevelopmental", "therapeutic", "small molecule"]
        
        result = coordinator.market_analysis_workflow(keywords, "pharmaceutical")
        
        print(f"Market analysis completed: {result.success}")
        print(f"Execution time: {result.total_execution_time:.2f} seconds")
        
        if result.success:
            from patent_search_system.agent_coordinator import WorkflowStep
            
            if WorkflowStep.MARKETING in result.results:
                market_data = result.results[WorkflowStep.MARKETING]
                
                # Extract market opportunities
                market_opportunities = market_data.content.get('market_opportunities', [])
                print(f"Market opportunities identified: {len(market_opportunities)}")
                
                for i, opp in enumerate(market_opportunities[:3]):  # Show first 3
                    print(f"  {i+1}. {opp.get('market_segment', 'Unknown')}: "
                          f"${opp.get('market_size', 0):.0f}M market")
                
                # Show value assessment
                value_assessment = market_data.content.get('value_assessment', {})
                print(f"Risk-adjusted value: ${value_assessment.get('risk_adjusted_value', 0):.0f}M")
                
                # Show strategic recommendations  
                recommendations = market_data.content.get('strategic_recommendations', [])
                print(f"Strategic recommendations ({len(recommendations)}):")
                for rec in recommendations[:3]:  # Show first 3
                    print(f"  - {rec}")
        
        return result
    
    finally:
        coordinator.shutdown()

def example_4_custom_workflow():
    """
    Example 4: Create and execute a custom workflow
    
    This example shows how to create a custom workflow with specific steps and dependencies.
    """
    print("\n=== Example 4: Custom Workflow ===")
    
    from patent_search_system.agent_coordinator import AgentWorkflow, WorkflowStep
    
    coordinator = create_patent_search_system()
    
    try:
        # Define a custom workflow that focuses on chemical analysis
        custom_workflow = AgentWorkflow(
            workflow_id="chemical_analysis_custom",
            steps=[
                WorkflowStep.QUERY,
                WorkflowStep.PROCESS,
                WorkflowStep.ANALYZE,  # Focus on chemical analysis
                WorkflowStep.COVERAGE  # Skip marketing for this example
            ],
            input_data={
                "keywords": ["chemical compound", "synthesis", "pharmaceutical"],
                "classification_codes": ["C07D", "C07C"],  # Organic chemistry codes
                "max_results": 20
            },
            dependencies={
                WorkflowStep.QUERY: [],
                WorkflowStep.PROCESS: [WorkflowStep.QUERY],
                WorkflowStep.ANALYZE: [WorkflowStep.PROCESS],
                WorkflowStep.COVERAGE: [WorkflowStep.PROCESS]
            },
            parallel_execution=True,
            timeout_seconds=600
        )
        
        # Execute the custom workflow
        result = asyncio.run(coordinator.execute_custom_workflow(custom_workflow))
        
        print(f"Custom workflow completed: {result.success}")
        print(f"Steps completed: {[step.value for step in result.steps_completed]}")
        
        if result.success and WorkflowStep.ANALYZE in result.results:
            analysis = result.results[WorkflowStep.ANALYZE]
            chemical_analysis = analysis.content.get('analysis_components', {}).get('chemical', {})
            
            print(f"Chemical compounds found: {chemical_analysis.get('chemical_count', 0)}")
            print(f"Compound types: {chemical_analysis.get('compound_types', [])}")
            print(f"Synthesis complexity: {chemical_analysis.get('synthesis_complexity', 'N/A')}")
        
        return result
    
    finally:
        coordinator.shutdown()

def example_5_agent_status_monitoring():
    """
    Example 5: Monitor agent status and system health
    
    This example demonstrates how to check the status of agents and workflows.
    """
    print("\n=== Example 5: System Status Monitoring ===")
    
    coordinator = create_patent_search_system()
    
    try:
        # Get agent status
        agent_status = coordinator.get_agent_status()
        print("Agent Status:")
        for agent_name, status in agent_status.items():
            print(f"  {agent_name}:")
            print(f"    Name: {status['name']}")
            print(f"    Capabilities: {len(status['capabilities'])} capabilities")
            print(f"    Active tasks: {status['active_tasks']}")
            print(f"    Input types: {status['supported_inputs']}")
            print(f"    Output type: {status['output_type']}")
        
        # List active workflows
        active_workflows = coordinator.list_active_workflows()
        print(f"\nActive workflows: {len(active_workflows)}")
        for workflow_id in active_workflows:
            workflow_status = coordinator.get_workflow_status(workflow_id)
            if workflow_status:
                print(f"  {workflow_id}: {workflow_status['status']}")
        
        # Get system configuration
        config = get_config()
        print(f"\nSystem Configuration:")
        print(f"  System name: {config.system_name}")
        print(f"  Version: {config.version}")
        print(f"  Debug mode: {config.debug_mode}")
        print(f"  Max parallel workflows: {config.workflow.max_parallel_workflows}")
        print(f"  Default timeout: {config.workflow.default_workflow_timeout}s")
    
    finally:
        coordinator.shutdown()

def example_6_configuration_management():
    """
    Example 6: Configuration management examples
    
    This example shows how to load, modify, and save system configuration.
    """
    print("\n=== Example 6: Configuration Management ===")
    
    # Create default configuration
    from patent_search_system.config import PatentSearchConfig
    
    config = PatentSearchConfig()
    
    # Modify some settings
    config.api.openai_model = "gpt-4"
    config.api.max_requests_per_minute = 100
    config.workflow.max_parallel_workflows = 5
    config.agents.cache_enabled = True
    config.debug_mode = True
    
    # Save configuration to file
    config_file = "/tmp/patent_search_config.json"
    config.save_to_file(config_file)
    print(f"Configuration saved to: {config_file}")
    
    # Load configuration from file
    loaded_config = PatentSearchConfig.load_from_file(config_file)
    print(f"Loaded configuration - Debug mode: {loaded_config.debug_mode}")
    
    # Validate configuration
    issues = loaded_config.validate()
    if issues:
        print(f"Configuration issues: {issues}")
    else:
        print("Configuration is valid")
    
    # Show configuration as dictionary
    config_dict = loaded_config.to_dict()
    print(f"Configuration keys: {list(config_dict.keys())}")

def example_7_comprehensive_demo():
    """
    Example 7: Comprehensive demonstration
    
    This example runs a complete analysis workflow and shows detailed results.
    """
    print("\n=== Example 7: Comprehensive Demonstration ===")
    
    coordinator = create_patent_search_system()
    
    try:
        # Run comprehensive analysis for FOXP2 NIB compounds
        print("Searching for FOXP2 NIB small molecule patents...")
        
        result = coordinator.search_foxp2_small_molecules([
            "NIB", "modulator", "autism spectrum disorder", "speech therapy"
        ])
        
        if result.success:
            print("\n=== COMPREHENSIVE ANALYSIS RESULTS ===")
            
            from patent_search_system.agent_coordinator import WorkflowStep
            
            # Query Results
            if WorkflowStep.QUERY in result.results:
                query_data = result.results[WorkflowStep.QUERY]
                patents = query_data.content.get('patents', [])
                print(f"\n1. PATENT SEARCH RESULTS:")
                print(f"   Patents found: {len(patents)}")
                for i, patent in enumerate(patents[:3]):  # Show first 3
                    print(f"   {i+1}. {patent.get('patent_number', 'N/A')}: {patent.get('title', 'N/A')}")
            
            # Processing Results
            if WorkflowStep.PROCESS in result.results:
                process_data = result.results[WorkflowStep.PROCESS]
                if isinstance(process_data, list) and process_data:
                    process_stats = process_data[0].content.get('processing_stats', {})
                    print(f"\n2. PATENT PROCESSING:")
                    print(f"   Chemicals found: {process_stats.get('chemicals_found', 0)}")
                    print(f"   Claims count: {process_stats.get('claims_count', 0)}")
                    print(f"   Images count: {process_stats.get('images_count', 0)}")
            
            # Analysis Results
            if WorkflowStep.ANALYZE in result.results:
                analysis_data = result.results[WorkflowStep.ANALYZE]
                analysis_result = analysis_data.content.get('analysis_result', {})
                print(f"\n3. DEEP ANALYSIS:")
                print(f"   Innovation score: {analysis_result.get('innovation_score', 0)}/10")
                print(f"   Novelty assessment: {analysis_result.get('novelty_assessment', 'N/A')}")
                
                key_findings = analysis_result.get('key_findings', [])
                print(f"   Key findings:")
                for finding in key_findings[:3]:
                    print(f"     - {finding}")
            
            # Coverage Analysis
            if WorkflowStep.COVERAGE in result.results:
                coverage_data = result.results[WorkflowStep.COVERAGE]
                coverage_summary = coverage_data.content.get('coverage_summary', {})
                print(f"\n4. GEOGRAPHIC COVERAGE:")
                print(f"   Total countries: {coverage_summary.get('total_countries', 0)}")
                print(f"   Active countries: {coverage_summary.get('active_countries', 0)}")
                print(f"   Coverage score: {coverage_summary.get('coverage_score', 0):.1f}%")
                
                key_markets = coverage_summary.get('key_markets_covered', [])
                print(f"   Key markets: {', '.join(key_markets) if key_markets else 'None'}")
            
            # Market Analysis
            if WorkflowStep.MARKETING in result.results:
                market_data = result.results[WorkflowStep.MARKETING]
                value_assessment = market_data.content.get('value_assessment', {})
                print(f"\n5. MARKET ANALYSIS:")
                print(f"   Technology value: ${value_assessment.get('technology_value', 0):.0f}M")
                print(f"   Market value: ${value_assessment.get('market_value', 0):.0f}M")
                print(f"   Risk-adjusted value: ${value_assessment.get('risk_adjusted_value', 0):.0f}M")
                
                market_opportunities = market_data.content.get('market_opportunities', [])
                print(f"   Market opportunities: {len(market_opportunities)}")
                
                recommendations = market_data.content.get('strategic_recommendations', [])
                print(f"   Strategic recommendations:")
                for rec in recommendations[:3]:
                    print(f"     - {rec}")
            
            # Executive Summary
            if WorkflowStep.MARKETING in result.results:
                executive_summary = market_data.content.get('executive_summary', '')
                if executive_summary:
                    print(f"\n6. EXECUTIVE SUMMARY:")
                    # Print first paragraph only for brevity
                    summary_lines = executive_summary.split('\n')
                    for line in summary_lines[:5]:
                        if line.strip():
                            print(f"   {line.strip()}")
        
        else:
            print("Analysis failed:")
            for error in result.error_messages:
                print(f"  - {error}")
        
        return result
    
    finally:
        coordinator.shutdown()

def main():
    """Run all examples"""
    print("Patent Search System - Examples and Demonstrations")
    print("=" * 60)
    
    # Run examples
    examples = [
        example_1_foxp2_search,
        example_2_specific_patent_analysis,
        example_3_market_analysis_workflow,
        example_4_custom_workflow,
        example_5_agent_status_monitoring,
        example_6_configuration_management,
        example_7_comprehensive_demo
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            print(f"\nRunning Example {i}...")
            example_func()
        except Exception as e:
            print(f"Example {i} failed: {e}")
        
        if i < len(examples):
            input("\nPress Enter to continue to next example...")
    
    print("\n" + "=" * 60)
    print("All examples completed!")

if __name__ == "__main__":
    main()