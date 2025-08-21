from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import uuid

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class PatentDataType(Enum):
    QUERY_RESULT = "query_result"
    PATENT_DOCUMENT = "patent_document"
    CHEMICAL_STRUCTURE = "chemical_structure"
    ANALYSIS_REPORT = "analysis_report"
    COVERAGE_MAP = "coverage_map"
    MARKET_ASSESSMENT = "market_assessment"

@dataclass
class PatentData:
    id: str
    type: PatentDataType
    content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Task:
    id: str
    type: str
    input_data: Union[Dict[str, Any], List[PatentData]]
    agent_id: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Union[PatentData, List[PatentData]]] = None
    error: Optional[str] = None
    priority: int = 1

class BasePatentAgent(ABC):
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{agent_id}")
        self.tasks: Dict[str, Task] = {}
        self.data_store: Dict[str, PatentData] = {}
        
    @abstractmethod
    def process_task(self, task: Task) -> Union[PatentData, List[PatentData]]:
        """Process a task and return patent data"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this agent provides"""
        pass
    
    @abstractmethod
    def get_supported_input_types(self) -> List[PatentDataType]:
        """Return list of patent data types this agent can process"""
        pass
    
    @abstractmethod
    def get_output_type(self) -> PatentDataType:
        """Return the type of data this agent outputs"""
        pass
    
    def execute_task(self, task: Task) -> Task:
        """Execute a task and update its status"""
        self.logger.info(f"Executing task {task.id} of type {task.type}")
        task.status = TaskStatus.IN_PROGRESS
        self.tasks[task.id] = task
        
        try:
            result = self.process_task(task)
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Store result in data store
            if isinstance(result, PatentData):
                self.data_store[result.id] = result
            elif isinstance(result, list):
                for data in result:
                    if isinstance(data, PatentData):
                        self.data_store[data.id] = data
            
            self.logger.info(f"Task {task.id} completed successfully")
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            self.logger.error(f"Task {task.id} failed: {e}")
        
        return task
    
    def create_task(self, task_type: str, input_data: Union[Dict[str, Any], List[PatentData]], 
                   priority: int = 1) -> Task:
        """Create a new task for this agent"""
        task_id = str(uuid.uuid4())
        return Task(
            id=task_id,
            type=task_type,
            input_data=input_data,
            agent_id=self.agent_id,
            priority=priority
        )
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a specific task"""
        task = self.tasks.get(task_id)
        return task.status if task else None
    
    def get_task_result(self, task_id: str) -> Optional[Union[PatentData, List[PatentData]]]:
        """Get the result of a completed task"""
        task = self.tasks.get(task_id)
        return task.result if task and task.status == TaskStatus.COMPLETED else None
    
    def get_data(self, data_id: str) -> Optional[PatentData]:
        """Retrieve data from the agent's data store"""
        return self.data_store.get(data_id)
    
    def store_data(self, data: PatentData) -> None:
        """Store data in the agent's data store"""
        self.data_store[data.id] = data