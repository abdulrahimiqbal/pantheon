"""
Core type definitions for the Physics AI Agent Swarm.

This module defines all the data structures used across the agent swarm
for consistent communication and data validation.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Union, Any
from enum import Enum
from datetime import datetime
import uuid


class ConfidenceLevel(Enum):
    """Confidence levels for agent responses."""
    HIGH = "90-100%"
    MEDIUM = "70-89%"
    LOW = "50-69%"
    SPECULATION = "<50%"


class SourceType(Enum):
    """Types of data sources."""
    PEER_REVIEWED = "peer_reviewed"
    PREPRINT = "preprint"
    EXPERIMENTAL = "experimental"
    THEORETICAL = "theoretical"
    GOVERNMENT = "government"
    EDUCATIONAL = "educational"
    NEWS = "news"
    BOOK = "book"
    CONFERENCE = "conference"


class ComplexityLevel(Enum):
    """Complexity levels for physics queries."""
    BASIC = "basic"           # High school level
    INTERMEDIATE = "intermediate"  # Undergraduate level
    ADVANCED = "advanced"     # Graduate level
    RESEARCH = "research"     # Novel hypothesis/research level


class AgentRole(Enum):
    """Roles of different agents in the swarm."""
    WEB_CRAWLER = "web_crawler"
    PHYSICIST_MASTER = "physicist_master"
    TESLA_PRINCIPLES = "tesla_principles"
    CURIOUS_QUESTIONER = "curious_questioner"


class DataSource(BaseModel):
    """Represents a data source found during research."""
    url: str = Field(..., description="URL of the source")
    title: str = Field(..., description="Title of the source")
    source_type: SourceType = Field(..., description="Type of source")
    credibility_score: float = Field(..., ge=0.0, le=1.0, description="Credibility score 0-1")
    publication_date: Optional[str] = Field(None, description="Publication date if available")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    abstract: Optional[str] = Field(None, description="Abstract or summary")
    doi: Optional[str] = Field(None, description="DOI if available")
    citation_count: Optional[int] = Field(None, description="Number of citations")
    journal: Optional[str] = Field(None, description="Journal name")
    
    @validator('credibility_score')
    def validate_credibility(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Credibility score must be between 0 and 1')
        return v


class PhysicsQuery(BaseModel):
    """Represents a physics question submitted to the swarm."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique query ID")
    question: str = Field(..., min_length=10, description="The physics question")
    context: str = Field(..., description="Context or background for the question")
    complexity_level: ComplexityLevel = Field(..., description="Expected complexity level")
    required_confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM, description="Minimum required confidence")
    time_limit: int = Field(default=180, ge=30, le=600, description="Time limit in seconds")
    user_id: Optional[str] = Field(None, description="User who submitted the query")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When query was submitted")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    @validator('question')
    def validate_question(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Question must be at least 10 characters long')
        return v.strip()


class AgentResponse(BaseModel):
    """Response from an individual agent."""
    agent_name: AgentRole = Field(..., description="Which agent generated this response")
    content: str = Field(..., description="Main response content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level 0-1")
    sources: List[DataSource] = Field(default_factory=list, description="Sources used")
    reasoning: str = Field(..., description="Explanation of reasoning process")
    questions_raised: List[str] = Field(default_factory=list, description="Questions raised by this analysis")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    processing_time: float = Field(..., description="Time taken to generate response")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When response was generated")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0 and 1')
        return v


class SwarmResponse(BaseModel):
    """Complete response from the agent swarm."""
    query_id: str = Field(..., description="ID of the original query")
    query: PhysicsQuery = Field(..., description="Original query")
    
    # Individual agent responses
    web_crawler_response: Optional[AgentResponse] = Field(None, description="Web crawler findings")
    physicist_response: Optional[AgentResponse] = Field(None, description="Physicist analysis")
    tesla_response: Optional[AgentResponse] = Field(None, description="Tesla principles analysis")
    questioner_response: Optional[AgentResponse] = Field(None, description="Questions raised")
    
    # Synthesized results
    final_answer: str = Field(..., description="Synthesized final answer")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    key_findings: List[str] = Field(default_factory=list, description="Key findings")
    all_sources: List[DataSource] = Field(default_factory=list, description="All sources combined")
    all_questions: List[str] = Field(default_factory=list, description="All questions raised")
    
    # Metadata
    total_processing_time: float = Field(..., description="Total time taken")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When response was completed")
    status: str = Field(default="completed", description="Status of the response")


class ValidationResult(BaseModel):
    """Result of validating a data source."""
    is_valid: bool = Field(..., description="Whether source is valid")
    credibility_score: float = Field(..., ge=0.0, le=1.0, description="Calculated credibility")
    validation_notes: List[str] = Field(default_factory=list, description="Validation notes")
    peer_reviewed: bool = Field(default=False, description="Is peer reviewed")
    recent: bool = Field(default=False, description="Is recent publication")
    authoritative: bool = Field(default=False, description="From authoritative source")


class PhysicsKnowledge(BaseModel):
    """Represents a piece of physics knowledge."""
    topic: str = Field(..., description="Physics topic")
    concept: str = Field(..., description="Specific concept")
    description: str = Field(..., description="Description of the concept")
    equations: List[str] = Field(default_factory=list, description="Related equations")
    applications: List[str] = Field(default_factory=list, description="Applications")
    related_concepts: List[str] = Field(default_factory=list, description="Related concepts")
    difficulty_level: ComplexityLevel = Field(..., description="Difficulty level")
    sources: List[DataSource] = Field(default_factory=list, description="Supporting sources")


class HypothesisGeneration(BaseModel):
    """Represents a generated physics hypothesis."""
    hypothesis: str = Field(..., description="The hypothesis statement")
    rationale: str = Field(..., description="Reasoning behind the hypothesis")
    testable_predictions: List[str] = Field(default_factory=list, description="Testable predictions")
    required_experiments: List[str] = Field(default_factory=list, description="Experiments needed")
    potential_impact: str = Field(..., description="Potential impact if true")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in hypothesis")
    novelty_score: float = Field(..., ge=0.0, le=1.0, description="How novel is this hypothesis")
    feasibility_score: float = Field(..., ge=0.0, le=1.0, description="How feasible to test")


class AgentConfig(BaseModel):
    """Configuration for an individual agent."""
    agent_role: AgentRole = Field(..., description="Role of the agent")
    model_name: str = Field(default="gpt-4", description="LLM model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=2000, ge=100, le=4000, description="Max tokens for response")
    timeout: int = Field(default=120, ge=30, le=300, description="Timeout in seconds")
    retry_attempts: int = Field(default=3, ge=1, le=5, description="Number of retry attempts")
    
    # Agent-specific configs
    web_search_limit: Optional[int] = Field(default=10, description="Max web search results")
    source_validation_threshold: Optional[float] = Field(default=0.6, description="Min credibility threshold")
    enable_hypothesis_generation: Optional[bool] = Field(default=False, description="Enable hypothesis generation")


class SwarmConfig(BaseModel):
    """Configuration for the entire swarm."""
    swarm_name: str = Field(default="Physics Research Swarm", description="Name of the swarm")
    orchestration_model: str = Field(default="hierarchical", description="Orchestration model")
    max_parallel_agents: int = Field(default=4, ge=1, le=10, description="Max parallel agents")
    global_timeout: int = Field(default=600, ge=60, le=1800, description="Global timeout in seconds")
    
    # Agent configurations
    agent_configs: Dict[AgentRole, AgentConfig] = Field(default_factory=dict, description="Individual agent configs")
    
    # API configurations
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    tavily_api_key: Optional[str] = Field(None, description="Tavily API key")
    brightdata_api_key: Optional[str] = Field(None, description="BrightData API key")


# Type aliases for convenience
AgentResponseDict = Dict[AgentRole, AgentResponse]
SourceList = List[DataSource]
QuestionList = List[str] 