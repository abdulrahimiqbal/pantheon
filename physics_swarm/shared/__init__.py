"""
Shared module for the Physics AI Agent Swarm.

This module provides common types, configuration, and utilities
used across all agents in the swarm.
"""

from .types import (
    # Enums
    ConfidenceLevel,
    SourceType,
    ComplexityLevel,
    AgentRole,
    
    # Data Models
    DataSource,
    PhysicsQuery,
    AgentResponse,
    SwarmResponse,
    ValidationResult,
    PhysicsKnowledge,
    HypothesisGeneration,
    AgentConfig,
    SwarmConfig,
    
    # Type Aliases
    AgentResponseDict,
    SourceList,
    QuestionList
)

from .config import (
    Settings,
    AgentSettings,
    SwarmConfigFactory,
    PhysicsTopics,
    settings,
    swarm_config
)

from .utils import (
    # Classes
    Logger,
    Timer,
    URLValidator,
    SourceValidator,
    TextProcessor,
    ConfidenceCalculator,
    DataFormatter,
    HashGenerator,
    JSONEncoder,
    
    # Convenience functions
    setup_logger,
    validate_source,
    calculate_confidence
)

__version__ = "1.0.0"
__author__ = "Physics AI Agent Swarm Team"

# Export all public classes and functions
__all__ = [
    # Types
    "ConfidenceLevel",
    "SourceType", 
    "ComplexityLevel",
    "AgentRole",
    "DataSource",
    "PhysicsQuery",
    "AgentResponse",
    "SwarmResponse",
    "ValidationResult",
    "PhysicsKnowledge",
    "HypothesisGeneration",
    "AgentConfig",
    "SwarmConfig",
    "AgentResponseDict",
    "SourceList",
    "QuestionList",
    
    # Config
    "Settings",
    "AgentSettings",
    "SwarmConfigFactory",
    "PhysicsTopics",
    "settings",
    "swarm_config",
    
    # Utils
    "Logger",
    "Timer",
    "URLValidator",
    "SourceValidator",
    "TextProcessor",
    "ConfidenceCalculator",
    "DataFormatter",
    "HashGenerator",
    "JSONEncoder",
    "setup_logger",
    "validate_source",
    "calculate_confidence"
]
