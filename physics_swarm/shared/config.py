"""
Configuration management for the Physics AI Agent Swarm.

This module handles environment variables, API keys, and system settings
using Pydantic Settings for type safety and validation.
"""

import os
from typing import Dict, Optional, List
from pydantic import BaseSettings, Field, validator
from pydantic_settings import BaseSettings as PydanticBaseSettings

from .types import AgentRole, AgentConfig, SwarmConfig, ComplexityLevel


class Settings(PydanticBaseSettings):
    """Main settings class for the Physics AI Agent Swarm."""
    
    # Application Settings
    app_name: str = Field(default="Physics AI Agent Swarm", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment (development/production)")
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    tavily_api_key: Optional[str] = Field(default=None, description="Tavily API key")
    brightdata_api_key: Optional[str] = Field(default=None, description="BrightData API key")
    
    # Database Settings
    database_url: str = Field(default="sqlite:///./physics_swarm.db", description="Database URL")
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    
    # FastAPI Settings
    host: str = Field(default="localhost", description="Host to bind to")
    port: int = Field(default=8000, description="Port to bind to")
    reload: bool = Field(default=True, description="Auto-reload on changes")
    
    # Agent Settings
    default_model: str = Field(default="gpt-4", description="Default LLM model")
    default_temperature: float = Field(default=0.7, description="Default temperature")
    default_max_tokens: int = Field(default=2000, description="Default max tokens")
    default_timeout: int = Field(default=120, description="Default timeout in seconds")
    
    # Web Search Settings
    max_search_results: int = Field(default=10, description="Maximum search results per query")
    source_credibility_threshold: float = Field(default=0.6, description="Minimum credibility score")
    
    # Swarm Settings
    max_parallel_agents: int = Field(default=4, description="Maximum parallel agents")
    global_timeout: int = Field(default=600, description="Global timeout in seconds")
    enable_hypothesis_generation: bool = Field(default=True, description="Enable hypothesis generation")
    
    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    
    # Security Settings
    secret_key: str = Field(default="your-secret-key-change-in-production", description="Secret key")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, description="Requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('environment')
    def validate_environment(cls, v):
        allowed = ['development', 'staging', 'production']
        if v.lower() not in allowed:
            raise ValueError(f'Environment must be one of: {allowed}')
        return v.lower()
    
    @validator('log_level')
    def validate_log_level(cls, v):
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f'Log level must be one of: {allowed}')
        return v.upper()
    
    @validator('default_temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v
    
    @validator('source_credibility_threshold')
    def validate_credibility_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Credibility threshold must be between 0.0 and 1.0')
        return v


class AgentSettings:
    """Factory class for creating agent-specific configurations."""
    
    @staticmethod
    def create_web_crawler_config(settings: Settings) -> AgentConfig:
        """Create configuration for Web Crawler Agent."""
        return AgentConfig(
            agent_role=AgentRole.WEB_CRAWLER,
            model_name=settings.default_model,
            temperature=0.3,  # Lower temperature for factual search
            max_tokens=1500,
            timeout=settings.default_timeout,
            retry_attempts=3,
            web_search_limit=settings.max_search_results,
            source_validation_threshold=settings.source_credibility_threshold,
            enable_hypothesis_generation=False
        )
    
    @staticmethod
    def create_physicist_master_config(settings: Settings) -> AgentConfig:
        """Create configuration for Physicist Master Agent."""
        return AgentConfig(
            agent_role=AgentRole.PHYSICIST_MASTER,
            model_name=settings.default_model,
            temperature=0.5,  # Balanced temperature for analysis
            max_tokens=settings.default_max_tokens,
            timeout=settings.default_timeout + 60,  # Extra time for analysis
            retry_attempts=3,
            web_search_limit=5,  # Limited search for validation
            source_validation_threshold=settings.source_credibility_threshold,
            enable_hypothesis_generation=settings.enable_hypothesis_generation
        )
    
    @staticmethod
    def create_tesla_principles_config(settings: Settings) -> AgentConfig:
        """Create configuration for Tesla Principles Agent."""
        return AgentConfig(
            agent_role=AgentRole.TESLA_PRINCIPLES,
            model_name=settings.default_model,
            temperature=0.8,  # Higher temperature for creativity
            max_tokens=settings.default_max_tokens,
            timeout=settings.default_timeout,
            retry_attempts=2,
            web_search_limit=3,  # Minimal search, focuses on principles
            source_validation_threshold=0.4,  # Lower threshold for innovative thinking
            enable_hypothesis_generation=True
        )
    
    @staticmethod
    def create_curious_questioner_config(settings: Settings) -> AgentConfig:
        """Create configuration for Curious Questioner Agent."""
        return AgentConfig(
            agent_role=AgentRole.CURIOUS_QUESTIONER,
            model_name=settings.default_model,
            temperature=0.7,  # Good balance for questioning
            max_tokens=1000,  # Shorter responses, focused on questions
            timeout=settings.default_timeout - 30,  # Faster questioning
            retry_attempts=2,
            web_search_limit=0,  # No web search, focuses on questioning
            source_validation_threshold=settings.source_credibility_threshold,
            enable_hypothesis_generation=False
        )


class SwarmConfigFactory:
    """Factory for creating swarm configurations."""
    
    @staticmethod
    def create_default_swarm_config(settings: Settings) -> SwarmConfig:
        """Create default swarm configuration."""
        agent_configs = {
            AgentRole.WEB_CRAWLER: AgentSettings.create_web_crawler_config(settings),
            AgentRole.PHYSICIST_MASTER: AgentSettings.create_physicist_master_config(settings),
            AgentRole.TESLA_PRINCIPLES: AgentSettings.create_tesla_principles_config(settings),
            AgentRole.CURIOUS_QUESTIONER: AgentSettings.create_curious_questioner_config(settings)
        }
        
        return SwarmConfig(
            swarm_name=settings.app_name,
            orchestration_model="hierarchical",
            max_parallel_agents=settings.max_parallel_agents,
            global_timeout=settings.global_timeout,
            agent_configs=agent_configs,
            openai_api_key=settings.openai_api_key,
            anthropic_api_key=settings.anthropic_api_key,
            tavily_api_key=settings.tavily_api_key,
            brightdata_api_key=settings.brightdata_api_key
        )


class PhysicsTopics:
    """Predefined physics topics and their complexity mappings."""
    
    BASIC_TOPICS = [
        "newton's laws",
        "kinematics",
        "energy conservation",
        "simple harmonic motion",
        "waves",
        "optics",
        "thermodynamics basics",
        "electric circuits",
        "magnetism"
    ]
    
    INTERMEDIATE_TOPICS = [
        "quantum mechanics basics",
        "special relativity",
        "electromagnetic theory",
        "statistical mechanics",
        "solid state physics",
        "nuclear physics",
        "particle physics basics",
        "astrophysics"
    ]
    
    ADVANCED_TOPICS = [
        "quantum field theory",
        "general relativity",
        "condensed matter physics",
        "cosmology",
        "high energy physics",
        "string theory",
        "quantum gravity",
        "dark matter",
        "dark energy"
    ]
    
    RESEARCH_TOPICS = [
        "quantum computing",
        "quantum entanglement applications",
        "multiverse theories",
        "consciousness and physics",
        "time travel paradoxes",
        "exotic matter",
        "wormholes",
        "extra dimensions"
    ]
    
    @classmethod
    def get_complexity_for_topic(cls, topic: str) -> ComplexityLevel:
        """Determine complexity level for a given topic."""
        topic_lower = topic.lower()
        
        if any(basic_topic in topic_lower for basic_topic in cls.BASIC_TOPICS):
            return ComplexityLevel.BASIC
        elif any(intermediate_topic in topic_lower for intermediate_topic in cls.INTERMEDIATE_TOPICS):
            return ComplexityLevel.INTERMEDIATE
        elif any(advanced_topic in topic_lower for advanced_topic in cls.ADVANCED_TOPICS):
            return ComplexityLevel.ADVANCED
        elif any(research_topic in topic_lower for research_topic in cls.RESEARCH_TOPICS):
            return ComplexityLevel.RESEARCH
        else:
            return ComplexityLevel.INTERMEDIATE  # Default


# Global settings instance
settings = Settings()

# Global swarm configuration
swarm_config = SwarmConfigFactory.create_default_swarm_config(settings) 