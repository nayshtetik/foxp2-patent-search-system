import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class APIConfig:
    """Configuration for external APIs"""
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_base_url: Optional[str] = None
    
    # Patent database APIs
    google_patents_api_key: Optional[str] = None
    espacenet_api_key: Optional[str] = None
    uspto_api_key: Optional[str] = None
    
    # Chemistry APIs
    pubchem_api_key: Optional[str] = None
    chemspider_api_key: Optional[str] = None
    
    # Rate limiting
    max_requests_per_minute: int = 60
    request_timeout_seconds: int = 30

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    max_concurrent_tasks: int = 5
    task_timeout_seconds: int = 300
    retry_attempts: int = 3
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600

@dataclass
class DatabaseConfig:
    """Configuration for data storage"""
    database_type: str = "sqlite"  # sqlite, postgresql, mongodb
    database_url: Optional[str] = None
    connection_pool_size: int = 10
    
    # File-based storage options
    data_directory: str = "./patent_data"
    cache_directory: str = "./cache"
    logs_directory: str = "./logs"

@dataclass
class SecurityConfig:
    """Security-related configuration"""
    encrypt_stored_data: bool = False
    encryption_key: Optional[str] = None
    api_key_storage: str = "environment"  # environment, file, encrypted_file
    max_data_retention_days: int = 365

@dataclass
class WorkflowConfig:
    """Configuration for workflow execution"""
    max_parallel_workflows: int = 3
    max_workflow_execution_time: int = 1800  # 30 minutes
    default_workflow_timeout: int = 600  # 10 minutes
    enable_workflow_caching: bool = True
    
    # Workflow-specific settings
    comprehensive_analysis_timeout: int = 900
    quick_evaluation_timeout: int = 300
    market_focused_timeout: int = 600

@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_file_logging: bool = True
    enable_console_logging: bool = True
    max_log_file_size_mb: int = 100
    max_log_files: int = 5

@dataclass
class PatentSearchConfig:
    """Main configuration class for the patent search system"""
    api: APIConfig = field(default_factory=APIConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # System settings
    system_name: str = "Patent Search System"
    version: str = "1.0.0"
    debug_mode: bool = False
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'PatentSearchConfig':
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        return cls.from_dict(config_data)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PatentSearchConfig':
        """Create configuration from dictionary"""
        config = cls()
        
        # Update API config
        if 'api' in config_dict:
            api_data = config_dict['api']
            config.api = APIConfig(**api_data)
        
        # Update agent config
        if 'agents' in config_dict:
            agent_data = config_dict['agents']
            config.agents = AgentConfig(**agent_data)
        
        # Update database config
        if 'database' in config_dict:
            db_data = config_dict['database']
            config.database = DatabaseConfig(**db_data)
        
        # Update security config
        if 'security' in config_dict:
            security_data = config_dict['security']
            config.security = SecurityConfig(**security_data)
        
        # Update workflow config
        if 'workflow' in config_dict:
            workflow_data = config_dict['workflow']
            config.workflow = WorkflowConfig(**workflow_data)
        
        # Update logging config
        if 'logging' in config_dict:
            logging_data = config_dict['logging']
            config.logging = LoggingConfig(**logging_data)
        
        # Update system settings
        if 'system_name' in config_dict:
            config.system_name = config_dict['system_name']
        if 'version' in config_dict:
            config.version = config_dict['version']
        if 'debug_mode' in config_dict:
            config.debug_mode = config_dict['debug_mode']
        
        return config
    
    @classmethod
    def from_environment(cls) -> 'PatentSearchConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # API configuration from environment
        config.api.openai_api_key = os.getenv('OPENAI_API_KEY')
        config.api.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4')
        config.api.google_patents_api_key = os.getenv('GOOGLE_PATENTS_API_KEY')
        config.api.espacenet_api_key = os.getenv('ESPACENET_API_KEY')
        config.api.uspto_api_key = os.getenv('USPTO_API_KEY')
        config.api.pubchem_api_key = os.getenv('PUBCHEM_API_KEY')
        config.api.chemspider_api_key = os.getenv('CHEMSPIDER_API_KEY')
        
        # Database configuration
        config.database.database_url = os.getenv('DATABASE_URL')
        config.database.data_directory = os.getenv('DATA_DIRECTORY', './patent_data')
        
        # Security configuration
        config.security.encryption_key = os.getenv('ENCRYPTION_KEY')
        config.security.encrypt_stored_data = os.getenv('ENCRYPT_DATA', 'false').lower() == 'true'
        
        # System settings
        config.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'api': {
                'openai_model': self.api.openai_model,
                'max_requests_per_minute': self.api.max_requests_per_minute,
                'request_timeout_seconds': self.api.request_timeout_seconds
            },
            'agents': {
                'max_concurrent_tasks': self.agents.max_concurrent_tasks,
                'task_timeout_seconds': self.agents.task_timeout_seconds,
                'retry_attempts': self.agents.retry_attempts,
                'cache_enabled': self.agents.cache_enabled,
                'cache_ttl_seconds': self.agents.cache_ttl_seconds
            },
            'database': {
                'database_type': self.database.database_type,
                'connection_pool_size': self.database.connection_pool_size,
                'data_directory': self.database.data_directory,
                'cache_directory': self.database.cache_directory,
                'logs_directory': self.database.logs_directory
            },
            'security': {
                'encrypt_stored_data': self.security.encrypt_stored_data,
                'api_key_storage': self.security.api_key_storage,
                'max_data_retention_days': self.security.max_data_retention_days
            },
            'workflow': {
                'max_parallel_workflows': self.workflow.max_parallel_workflows,
                'max_workflow_execution_time': self.workflow.max_workflow_execution_time,
                'default_workflow_timeout': self.workflow.default_workflow_timeout,
                'enable_workflow_caching': self.workflow.enable_workflow_caching
            },
            'logging': {
                'log_level': self.logging.log_level,
                'enable_file_logging': self.logging.enable_file_logging,
                'enable_console_logging': self.logging.enable_console_logging,
                'max_log_file_size_mb': self.logging.max_log_file_size_mb,
                'max_log_files': self.logging.max_log_files
            },
            'system_name': self.system_name,
            'version': self.version,
            'debug_mode': self.debug_mode
        }
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to JSON file"""
        config_dict = self.to_dict()
        
        # Create directory if it doesn't exist
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check required API keys based on usage
        if not self.api.openai_api_key:
            issues.append("OpenAI API key is required for deep analysis")
        
        # Validate directories exist or can be created
        directories = [
            self.database.data_directory,
            self.database.cache_directory,
            self.database.logs_directory
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create directory {directory}: {e}")
        
        # Validate timeout values
        if self.workflow.default_workflow_timeout <= 0:
            issues.append("Workflow timeout must be positive")
        
        if self.api.max_requests_per_minute <= 0:
            issues.append("Max requests per minute must be positive")
        
        return issues
    
    def setup_logging(self) -> None:
        """Setup logging based on configuration"""
        log_level = getattr(logging, self.logging.log_level.upper())
        
        # Create formatter
        formatter = logging.Formatter(self.logging.log_format)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if self.logging.enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(log_level)
            root_logger.addHandler(console_handler)
        
        # File handler
        if self.logging.enable_file_logging:
            log_file = Path(self.database.logs_directory) / "patent_search.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=self.logging.max_log_file_size_mb * 1024 * 1024,
                backupCount=self.logging.max_log_files
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            root_logger.addHandler(file_handler)

class ConfigManager:
    """Singleton configuration manager"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[PatentSearchConfig] = None
    
    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_config(self, config_path: Optional[str] = None) -> PatentSearchConfig:
        """Load configuration from file or environment"""
        if config_path and os.path.exists(config_path):
            self._config = PatentSearchConfig.load_from_file(config_path)
        else:
            self._config = PatentSearchConfig.from_environment()
        
        # Validate configuration
        issues = self._config.validate()
        if issues:
            raise ValueError(f"Configuration validation failed: {issues}")
        
        # Setup logging
        self._config.setup_logging()
        
        return self._config
    
    def get_config(self) -> PatentSearchConfig:
        """Get current configuration"""
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        if self._config is None:
            self._config = PatentSearchConfig()
        
        # Apply updates (simplified - in practice would need recursive update)
        for key, value in updates.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

# Global configuration instance
config_manager = ConfigManager()

def get_config() -> PatentSearchConfig:
    """Get global configuration instance"""
    return config_manager.get_config()

def load_config(config_path: Optional[str] = None) -> PatentSearchConfig:
    """Load configuration from file or environment"""
    return config_manager.load_config(config_path)