from typing import Dict, Any, List, Union, Optional, Callable
import asyncio
import time
import logging
from dataclasses import dataclass
from enum import Enum
import uuid
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_agent import BasePatentAgent, PatentData, PatentDataType, Task, TaskStatus
from .patent_query_agent import PatentQueryAgent
from .patent_processing_agent import PatentProcessingAgent
from .deep_analysis_agent import DeepAnalysisAgent
from .coverage_analysis_agent import PatentCoverageAnalysisAgent
from .marketing_analysis_agent import MarketingAnalysisAgent

class WorkflowStep(Enum):
    QUERY = "query"
    PROCESS = "process"
    ANALYZE = "analyze"
    COVERAGE = "coverage"
    MARKETING = "marketing"

@dataclass
class WorkflowResult:
    workflow_id: str
    steps_completed: List[WorkflowStep]
    results: Dict[WorkflowStep, PatentData]
    total_execution_time: float
    success: bool
    error_messages: List[str]

@dataclass
class AgentWorkflow:
    workflow_id: str
    steps: List[WorkflowStep]
    input_data: Dict[str, Any]
    dependencies: Dict[WorkflowStep, List[WorkflowStep]]
    parallel_execution: bool = False
    timeout_seconds: int = 300

class PatentSearchCoordinator:
    """Coordinates multiple patent search agents to execute complex workflows"""
    
    def __init__(self, max_workers: int = 4):
        self.agents: Dict[WorkflowStep, BasePatentAgent] = {}
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize all agents
        self._initialize_agents()
        
        # Define default workflows
        self.predefined_workflows = self._define_predefined_workflows()
        
        # Track active workflows
        self.active_workflows: Dict[str, AgentWorkflow] = {}
        
    def _initialize_agents(self):
        """Initialize all patent search agents"""
        self.agents[WorkflowStep.QUERY] = PatentQueryAgent()
        self.agents[WorkflowStep.PROCESS] = PatentProcessingAgent()
        self.agents[WorkflowStep.ANALYZE] = DeepAnalysisAgent()
        self.agents[WorkflowStep.COVERAGE] = PatentCoverageAnalysisAgent()
        self.agents[WorkflowStep.MARKETING] = MarketingAnalysisAgent()
        
        self.logger.info(f"Initialized {len(self.agents)} patent search agents")
    
    def _define_predefined_workflows(self) -> Dict[str, AgentWorkflow]:
        """Define commonly used workflows"""
        return {
            "comprehensive_analysis": AgentWorkflow(
                workflow_id="comprehensive_analysis",
                steps=[
                    WorkflowStep.QUERY,
                    WorkflowStep.PROCESS, 
                    WorkflowStep.ANALYZE,
                    WorkflowStep.COVERAGE,
                    WorkflowStep.MARKETING
                ],
                input_data={},
                dependencies={
                    WorkflowStep.QUERY: [],
                    WorkflowStep.PROCESS: [WorkflowStep.QUERY],
                    WorkflowStep.ANALYZE: [WorkflowStep.PROCESS],
                    WorkflowStep.COVERAGE: [WorkflowStep.PROCESS],
                    WorkflowStep.MARKETING: [WorkflowStep.PROCESS, WorkflowStep.ANALYZE, WorkflowStep.COVERAGE]
                },
                parallel_execution=True
            ),
            
            "quick_evaluation": AgentWorkflow(
                workflow_id="quick_evaluation",
                steps=[
                    WorkflowStep.QUERY,
                    WorkflowStep.PROCESS,
                    WorkflowStep.ANALYZE
                ],
                input_data={},
                dependencies={
                    WorkflowStep.QUERY: [],
                    WorkflowStep.PROCESS: [WorkflowStep.QUERY],
                    WorkflowStep.ANALYZE: [WorkflowStep.PROCESS]
                },
                parallel_execution=False
            ),
            
            "market_focused": AgentWorkflow(
                workflow_id="market_focused",
                steps=[
                    WorkflowStep.QUERY,
                    WorkflowStep.PROCESS,
                    WorkflowStep.COVERAGE,
                    WorkflowStep.MARKETING
                ],
                input_data={},
                dependencies={
                    WorkflowStep.QUERY: [],
                    WorkflowStep.PROCESS: [WorkflowStep.QUERY],
                    WorkflowStep.COVERAGE: [WorkflowStep.PROCESS],
                    WorkflowStep.MARKETING: [WorkflowStep.PROCESS, WorkflowStep.COVERAGE]
                },
                parallel_execution=True
            )
        }
    
    async def execute_workflow(self, workflow_name: str, search_params: Dict[str, Any]) -> WorkflowResult:
        """Execute a predefined workflow"""
        if workflow_name not in self.predefined_workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow = self.predefined_workflows[workflow_name]
        workflow.input_data = search_params
        workflow.workflow_id = f"{workflow_name}_{str(uuid.uuid4())[:8]}"
        
        return await self._execute_workflow(workflow)
    
    async def execute_custom_workflow(self, workflow: AgentWorkflow) -> WorkflowResult:
        """Execute a custom workflow"""
        return await self._execute_workflow(workflow)
    
    async def _execute_workflow(self, workflow: AgentWorkflow) -> WorkflowResult:
        """Internal workflow execution logic"""
        start_time = time.time()
        workflow_id = workflow.workflow_id
        
        self.logger.info(f"Starting workflow {workflow_id} with steps: {[s.value for s in workflow.steps]}")
        
        # Track workflow
        self.active_workflows[workflow_id] = workflow
        
        # Initialize result tracking
        results: Dict[WorkflowStep, PatentData] = {}
        completed_steps: List[WorkflowStep] = []
        error_messages: List[str] = []
        
        try:
            if workflow.parallel_execution:
                results = await self._execute_parallel_workflow(workflow, completed_steps, error_messages)
            else:
                results = await self._execute_sequential_workflow(workflow, completed_steps, error_messages)
            
            success = len(completed_steps) == len(workflow.steps)
            execution_time = time.time() - start_time
            
            self.logger.info(f"Workflow {workflow_id} completed in {execution_time:.2f}s. Success: {success}")
            
            return WorkflowResult(
                workflow_id=workflow_id,
                steps_completed=completed_steps,
                results=results,
                total_execution_time=execution_time,
                success=success,
                error_messages=error_messages
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = f"Workflow {workflow_id} failed: {str(e)}"
            self.logger.error(error_message)
            error_messages.append(error_message)
            
            return WorkflowResult(
                workflow_id=workflow_id,
                steps_completed=completed_steps,
                results=results,
                total_execution_time=execution_time,
                success=False,
                error_messages=error_messages
            )
        
        finally:
            # Clean up
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
    
    async def _execute_sequential_workflow(self, workflow: AgentWorkflow, 
                                         completed_steps: List[WorkflowStep],
                                         error_messages: List[str]) -> Dict[WorkflowStep, PatentData]:
        """Execute workflow steps sequentially"""
        results: Dict[WorkflowStep, PatentData] = {}
        
        for step in workflow.steps:
            try:
                self.logger.info(f"Executing step: {step.value}")
                
                # Prepare input data for this step
                step_input = self._prepare_step_input(step, workflow.input_data, results)
                
                # Execute the step
                agent = self.agents[step]
                task = agent.create_task(
                    task_type=self._get_task_type_for_step(step),
                    input_data=step_input
                )
                
                executed_task = agent.execute_task(task)
                
                if executed_task.status == TaskStatus.COMPLETED:
                    results[step] = executed_task.result
                    completed_steps.append(step)
                else:
                    error_msg = f"Step {step.value} failed: {executed_task.error}"
                    error_messages.append(error_msg)
                    self.logger.error(error_msg)
                    break
                    
            except Exception as e:
                error_msg = f"Error in step {step.value}: {str(e)}"
                error_messages.append(error_msg)
                self.logger.error(error_msg)
                break
        
        return results
    
    async def _execute_parallel_workflow(self, workflow: AgentWorkflow,
                                       completed_steps: List[WorkflowStep], 
                                       error_messages: List[str]) -> Dict[WorkflowStep, PatentData]:
        """Execute workflow with parallel execution where possible"""
        results: Dict[WorkflowStep, PatentData] = {}
        remaining_steps = set(workflow.steps)
        
        while remaining_steps:
            # Find steps that can be executed (all dependencies met)
            executable_steps = []
            for step in remaining_steps:
                dependencies = workflow.dependencies.get(step, [])
                if all(dep in completed_steps for dep in dependencies):
                    executable_steps.append(step)
            
            if not executable_steps:
                error_msg = "Workflow deadlock: no executable steps remaining"
                error_messages.append(error_msg)
                break
            
            # Execute all executable steps in parallel
            futures = []
            for step in executable_steps:
                future = self.executor.submit(self._execute_single_step, step, workflow.input_data, results)
                futures.append((step, future))
            
            # Wait for completion
            for step, future in futures:
                try:
                    step_result = future.result(timeout=workflow.timeout_seconds)
                    if step_result:
                        results[step] = step_result
                        completed_steps.append(step)
                        remaining_steps.remove(step)
                    else:
                        error_msg = f"Step {step.value} returned no result"
                        error_messages.append(error_msg)
                        remaining_steps.remove(step)  # Remove to avoid infinite loop
                
                except Exception as e:
                    error_msg = f"Step {step.value} failed: {str(e)}"
                    error_messages.append(error_msg)
                    remaining_steps.remove(step)  # Remove to avoid infinite loop
        
        return results
    
    def _execute_single_step(self, step: WorkflowStep, workflow_input: Dict[str, Any], 
                           current_results: Dict[WorkflowStep, PatentData]) -> Optional[PatentData]:
        """Execute a single workflow step"""
        try:
            # Prepare input data
            step_input = self._prepare_step_input(step, workflow_input, current_results)
            
            # Get agent and execute
            agent = self.agents[step]
            task = agent.create_task(
                task_type=self._get_task_type_for_step(step),
                input_data=step_input
            )
            
            executed_task = agent.execute_task(task)
            
            if executed_task.status == TaskStatus.COMPLETED:
                return executed_task.result
            else:
                self.logger.error(f"Task failed for step {step.value}: {executed_task.error}")
                return None
                
        except Exception as e:
            self.logger.error(f"Exception in step {step.value}: {str(e)}")
            return None
    
    def _prepare_step_input(self, step: WorkflowStep, workflow_input: Dict[str, Any],
                          current_results: Dict[WorkflowStep, PatentData]) -> Union[Dict[str, Any], List[PatentData]]:
        """Prepare input data for a specific step"""
        
        if step == WorkflowStep.QUERY:
            # Query step uses the original workflow input
            return workflow_input
        
        elif step == WorkflowStep.PROCESS:
            # Process step needs query results
            if WorkflowStep.QUERY in current_results:
                return [current_results[WorkflowStep.QUERY]]
            else:
                raise ValueError("Process step requires query results")
        
        elif step == WorkflowStep.ANALYZE:
            # Analysis step needs processed patent documents
            if WorkflowStep.PROCESS in current_results:
                return current_results[WorkflowStep.PROCESS]
            else:
                raise ValueError("Analysis step requires processed patents")
        
        elif step == WorkflowStep.COVERAGE:
            # Coverage step needs processed patent documents
            if WorkflowStep.PROCESS in current_results:
                return current_results[WorkflowStep.PROCESS]
            else:
                raise ValueError("Coverage step requires processed patents")
        
        elif step == WorkflowStep.MARKETING:
            # Marketing step can use multiple inputs
            input_data = []
            
            if WorkflowStep.PROCESS in current_results:
                input_data.append(current_results[WorkflowStep.PROCESS])
            if WorkflowStep.ANALYZE in current_results:
                input_data.append(current_results[WorkflowStep.ANALYZE])
            if WorkflowStep.COVERAGE in current_results:
                input_data.append(current_results[WorkflowStep.COVERAGE])
            
            if not input_data:
                raise ValueError("Marketing step requires at least processed patent data")
            
            return input_data
        
        else:
            raise ValueError(f"Unknown workflow step: {step}")
    
    def _get_task_type_for_step(self, step: WorkflowStep) -> str:
        """Get the appropriate task type for each workflow step"""
        task_type_mapping = {
            WorkflowStep.QUERY: "search_patents",
            WorkflowStep.PROCESS: "process_patents",
            WorkflowStep.ANALYZE: "comprehensive_analysis",
            WorkflowStep.COVERAGE: "analyze_coverage",
            WorkflowStep.MARKETING: "market_analysis"
        }
        return task_type_mapping.get(step, "default_task")
    
    def search_foxp2_small_molecules(self, additional_keywords: List[str] = None) -> WorkflowResult:
        """Convenience method for searching FOXP2 small molecule patents"""
        keywords = ["FOXP2", "small molecule", "NIB"]
        if additional_keywords:
            keywords.extend(additional_keywords)
        
        search_params = {
            "keywords": keywords,
            "classification_codes": ["A61K", "A61P", "C07D"],  # Pharma and organic chemistry
            "max_results": 50
        }
        
        # Run comprehensive analysis workflow
        return asyncio.run(self.execute_workflow("comprehensive_analysis", search_params))
    
    def quick_patent_evaluation(self, patent_number: str) -> WorkflowResult:
        """Quick evaluation of a specific patent"""
        search_params = {
            "keywords": [patent_number],
            "max_results": 1
        }
        
        return asyncio.run(self.execute_workflow("quick_evaluation", search_params))
    
    def market_analysis_workflow(self, search_keywords: List[str], 
                                tech_focus: str = "pharmaceutical") -> WorkflowResult:
        """Market-focused analysis workflow"""
        classification_codes = {
            "pharmaceutical": ["A61K", "A61P"],
            "chemical": ["C07C", "C07D"],
            "biotech": ["C12N", "C07K"]
        }
        
        search_params = {
            "keywords": search_keywords,
            "classification_codes": classification_codes.get(tech_focus, ["A61K"]),
            "max_results": 30
        }
        
        return asyncio.run(self.execute_workflow("market_focused", search_params))
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an active workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return {
                "workflow_id": workflow_id,
                "steps": [s.value for s in workflow.steps],
                "status": "running"
            }
        return None
    
    def list_active_workflows(self) -> List[str]:
        """List all active workflow IDs"""
        return list(self.active_workflows.keys())
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        status = {}
        for step, agent in self.agents.items():
            status[step.value] = {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "capabilities": agent.get_capabilities(),
                "active_tasks": len(agent.tasks),
                "supported_inputs": [t.value for t in agent.get_supported_input_types()],
                "output_type": agent.get_output_type().value
            }
        return status
    
    def shutdown(self):
        """Shutdown the coordinator and cleanup resources"""
        self.logger.info("Shutting down Patent Search Coordinator")
        self.executor.shutdown(wait=True)
        self.active_workflows.clear()

# Convenience function to create and use coordinator
def create_patent_search_system() -> PatentSearchCoordinator:
    """Create a new patent search system coordinator"""
    return PatentSearchCoordinator()

# Example usage functions
def search_foxp2_patents():
    """Example: Search for FOXP2-related patents"""
    coordinator = create_patent_search_system()
    try:
        result = coordinator.search_foxp2_small_molecules(["NIB", "modulator", "therapeutic"])
        return result
    finally:
        coordinator.shutdown()

def analyze_patent_portfolio(patent_numbers: List[str]):
    """Example: Analyze a portfolio of patents"""
    coordinator = create_patent_search_system()
    results = []
    
    try:
        for patent_number in patent_numbers:
            result = coordinator.quick_patent_evaluation(patent_number)
            results.append(result)
        return results
    finally:
        coordinator.shutdown()

def market_analysis_pharmaceuticals(keywords: List[str]):
    """Example: Market analysis for pharmaceutical patents"""
    coordinator = create_patent_search_system()
    try:
        result = coordinator.market_analysis_workflow(keywords, "pharmaceutical")
        return result
    finally:
        coordinator.shutdown()