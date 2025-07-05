"""
Base Agent class for the Physics AI Agent Swarm.

This module provides the foundation for all agents in the swarm,
including communication protocols, state management, and common functionality.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Union
from datetime import datetime

from crewai import Agent, Task, Crew
from crewai.tools import BaseTool

from shared import (
    AgentRole, AgentConfig, PhysicsQuery, AgentResponse, DataSource,
    ConfidenceLevel, ComplexityLevel, Timer, setup_logger, calculate_confidence
)


class BasePhysicsAgent(ABC):
    """
    Base class for all physics agents in the swarm.
    
    This class provides common functionality including:
    - Agent configuration and initialization
    - Communication protocols
    - State management
    - Error handling and retry logic
    - Performance monitoring
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the base agent with configuration."""
        self.config = config
        self.role = config.agent_role
        self.logger = setup_logger(f"{self.role.value}_agent")
        self.state = {}
        self.performance_metrics = {}
        self.is_initialized = False
        
        # CrewAI agent instance
        self.crew_agent: Optional[Agent] = None
        
        # Initialize the agent
        self._initialize()
    
    def _initialize(self):
        """Initialize the agent with CrewAI framework."""
        try:
            self.crew_agent = Agent(
                role=self._get_role_description(),
                goal=self._get_goal_description(),
                backstory=self._get_backstory(),
                verbose=True,
                allow_delegation=False,
                tools=self._get_tools(),
                llm=self._get_llm_config()
            )
            
            self.is_initialized = True
            self.logger.info(f"Agent {self.role.value} initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent {self.role.value}: {str(e)}")
            raise
    
    @abstractmethod
    def _get_role_description(self) -> str:
        """Get the role description for CrewAI."""
        pass
    
    @abstractmethod
    def _get_goal_description(self) -> str:
        """Get the goal description for CrewAI."""
        pass
    
    @abstractmethod
    def _get_backstory(self) -> str:
        """Get the backstory for CrewAI."""
        pass
    
    @abstractmethod
    def _get_tools(self) -> List[BaseTool]:
        """Get the tools available to this agent."""
        pass
    
    def _get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration for this agent."""
        return {
            "model": self.config.model_name,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "timeout": self.config.timeout
        }
    
    async def process_query(self, query: PhysicsQuery) -> AgentResponse:
        """
        Process a physics query and return an agent response.
        
        This is the main entry point for agent processing.
        """
        if not self.is_initialized:
            raise RuntimeError(f"Agent {self.role.value} is not initialized")
        
        start_time = time.time()
        
        try:
            with Timer(f"{self.role.value} processing query"):
                # Create CrewAI task
                task = Task(
                    description=self._create_task_description(query),
                    agent=self.crew_agent,
                    expected_output=self._get_expected_output_format()
                )
                
                # Execute task
                crew = Crew(
                    agents=[self.crew_agent],
                    tasks=[task],
                    verbose=True
                )
                
                result = crew.kickoff()
                
                # Process the result
                response = await self._process_result(query, result)
                
                # Update performance metrics
                processing_time = time.time() - start_time
                self._update_performance_metrics(processing_time, response)
                
                return response
                
        except Exception as e:
            self.logger.error(f"Error processing query in {self.role.value}: {str(e)}")
            
            # Return error response
            return AgentResponse(
                agent_name=self.role,
                content=f"Error processing query: {str(e)}",
                confidence=0.0,
                sources=[],
                reasoning=f"Agent encountered an error: {str(e)}",
                questions_raised=[],
                metadata={"error": str(e)},
                processing_time=time.time() - start_time,
                timestamp=datetime.utcnow()
            )
    
    @abstractmethod
    def _create_task_description(self, query: PhysicsQuery) -> str:
        """Create a task description for CrewAI based on the query."""
        pass
    
    @abstractmethod
    def _get_expected_output_format(self) -> str:
        """Get the expected output format for CrewAI."""
        pass
    
    @abstractmethod
    async def _process_result(self, query: PhysicsQuery, result: Any) -> AgentResponse:
        """Process the result from CrewAI and create an AgentResponse."""
        pass
    
    def _update_performance_metrics(self, processing_time: float, response: AgentResponse):
        """Update performance metrics for this agent."""
        if "processing_times" not in self.performance_metrics:
            self.performance_metrics["processing_times"] = []
        if "confidence_scores" not in self.performance_metrics:
            self.performance_metrics["confidence_scores"] = []
        if "total_queries" not in self.performance_metrics:
            self.performance_metrics["total_queries"] = 0
        
        self.performance_metrics["processing_times"].append(processing_time)
        self.performance_metrics["confidence_scores"].append(response.confidence)
        self.performance_metrics["total_queries"] += 1
        
        # Keep only last 100 entries
        if len(self.performance_metrics["processing_times"]) > 100:
            self.performance_metrics["processing_times"] = self.performance_metrics["processing_times"][-100:]
            self.performance_metrics["confidence_scores"] = self.performance_metrics["confidence_scores"][-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of agent performance."""
        if not self.performance_metrics.get("processing_times"):
            return {"status": "No data available"}
        
        processing_times = self.performance_metrics["processing_times"]
        confidence_scores = self.performance_metrics["confidence_scores"]
        
        return {
            "agent_role": self.role.value,
            "total_queries": self.performance_metrics["total_queries"],
            "avg_processing_time": sum(processing_times) / len(processing_times),
            "min_processing_time": min(processing_times),
            "max_processing_time": max(processing_times),
            "avg_confidence": sum(confidence_scores) / len(confidence_scores),
            "min_confidence": min(confidence_scores),
            "max_confidence": max(confidence_scores)
        }
    
    def update_state(self, key: str, value: Any):
        """Update agent state."""
        self.state[key] = value
        self.logger.debug(f"Updated state: {key} = {value}")
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get value from agent state."""
        return self.state.get(key, default)
    
    def reset_state(self):
        """Reset agent state."""
        self.state = {}
        self.logger.info(f"Reset state for agent {self.role.value}")
    
    async def validate_sources(self, sources: List[DataSource]) -> List[DataSource]:
        """Validate a list of data sources."""
        from shared import validate_source
        
        validated_sources = []
        threshold = self.config.source_validation_threshold or 0.6
        
        for source in sources:
            try:
                validation_result = validate_source(source)
                if validation_result.is_valid and validation_result.credibility_score >= threshold:
                    validated_sources.append(source)
                else:
                    self.logger.debug(f"Source rejected: {source.url} (credibility: {validation_result.credibility_score:.2f})")
            except Exception as e:
                self.logger.warning(f"Error validating source {source.url}: {str(e)}")
        
        self.logger.info(f"Validated {len(validated_sources)} out of {len(sources)} sources")
        return validated_sources
    
    def calculate_response_confidence(self, sources: List[DataSource], content_quality: float = 0.7) -> float:
        """Calculate confidence score for a response."""
        return calculate_confidence(
            sources=sources,
            source_agreement=0.8,  # Assume good agreement for now
            content_quality=content_quality,
            reasoning_strength=0.6  # Agent-specific reasoning strength
        )
    
    def create_standard_response(
        self,
        content: str,
        sources: List[DataSource],
        reasoning: str,
        questions_raised: List[str] = None,
        metadata: Dict[str, Any] = None,
        processing_time: float = 0.0
    ) -> AgentResponse:
        """Create a standard agent response."""
        questions_raised = questions_raised or []
        metadata = metadata or {}
        
        confidence = self.calculate_response_confidence(sources)
        
        return AgentResponse(
            agent_name=self.role,
            content=content,
            confidence=confidence,
            sources=sources,
            reasoning=reasoning,
            questions_raised=questions_raised,
            metadata=metadata,
            processing_time=processing_time,
            timestamp=datetime.utcnow()
        )
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"BasePhysicsAgent(role={self.role.value}, initialized={self.is_initialized})"
    
    def __repr__(self) -> str:
        """Detailed representation of the agent."""
        return f"BasePhysicsAgent(role={self.role.value}, config={self.config}, initialized={self.is_initialized})"


class AgentCommunicationProtocol:
    """
    Protocol for inter-agent communication.
    
    This class handles message passing between agents in the swarm.
    """
    
    def __init__(self):
        self.message_queue = asyncio.Queue()
        self.subscribers = {}
        self.logger = setup_logger("AgentCommunication")
    
    async def publish_message(self, sender: AgentRole, message_type: str, content: Any):
        """Publish a message to all subscribers."""
        message = {
            "sender": sender,
            "type": message_type,
            "content": content,
            "timestamp": datetime.utcnow()
        }
        
        await self.message_queue.put(message)
        self.logger.debug(f"Published message from {sender.value}: {message_type}")
    
    async def subscribe(self, agent_role: AgentRole, message_types: List[str]):
        """Subscribe an agent to specific message types."""
        if agent_role not in self.subscribers:
            self.subscribers[agent_role] = []
        
        self.subscribers[agent_role].extend(message_types)
        self.logger.info(f"Agent {agent_role.value} subscribed to: {message_types}")
    
    async def get_messages_for_agent(self, agent_role: AgentRole) -> List[Dict[str, Any]]:
        """Get messages for a specific agent."""
        messages = []
        
        # This is a simplified implementation
        # In a real system, you'd want proper message filtering and queuing
        
        return messages


# Global communication protocol instance
communication_protocol = AgentCommunicationProtocol() 