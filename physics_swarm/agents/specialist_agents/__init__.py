"""
Specialist Physics Agents

This module contains specialized agents for physics research and analysis.
Each agent has a specific role in the physics swarm ecosystem.
"""

from .web_crawler_agent import WebCrawlerAgent, TavilySearchTool, BrightDataTool
from .physicist_master_agent import PhysicistMasterAgent, PhysicsKnowledgeBase, PhysicsAnalysisTool
from .tesla_principles_agent import TeslaPrinciplesAgent, FirstPrinciplesTool, InnovationTool
from .curious_questioner_agent import CuriousQuestionerAgent, SocraticQuestioningTool, CriticalAnalysisTool, QuestionPrioritizationTool

__all__ = [
    # Main Agent Classes
    "WebCrawlerAgent",
    "PhysicistMasterAgent", 
    "TeslaPrinciplesAgent",
    "CuriousQuestionerAgent",
    
    # Web Crawler Tools
    "TavilySearchTool",
    "BrightDataTool",
    
    # Physicist Master Tools
    "PhysicsKnowledgeBase",
    "PhysicsAnalysisTool",
    
    # Tesla Principles Tools
    "FirstPrinciplesTool",
    "InnovationTool",
    
    # Curious Questioner Tools
    "SocraticQuestioningTool",
    "CriticalAnalysisTool",
    "QuestionPrioritizationTool"
]

# Agent registry for easy access
SPECIALIST_AGENTS = {
    "web_crawler": WebCrawlerAgent,
    "physicist_master": PhysicistMasterAgent,
    "tesla_principles": TeslaPrinciplesAgent,
    "curious_questioner": CuriousQuestionerAgent
}

# Agent roles mapping
AGENT_ROLES = {
    "web_crawler": "Research and Source Validation",
    "physicist_master": "Orchestration and Expert Analysis", 
    "tesla_principles": "First-Principles Innovation",
    "curious_questioner": "Critical Inquiry and Deep Analysis"
}

# Agent descriptions
AGENT_DESCRIPTIONS = {
    "web_crawler": """
    Web Crawler Agent specializes in searching and validating physics sources using 
    Tavily API. Focuses on academic credibility, source quality assessment, and 
    comprehensive research gathering.
    """,
    
    "physicist_master": """
    Physicist Master Agent serves as the orchestrator and subject matter expert.
    Coordinates other agents, provides deep physics expertise, and synthesizes 
    findings from multiple sources.
    """,
    
    "tesla_principles": """
    Tesla Principles Agent applies first-principles thinking and innovative approaches.
    Challenges conventional wisdom, explores novel solutions, and generates 
    breakthrough insights inspired by Nikola Tesla's methodology.
    """,
    
    "curious_questioner": """
    Curious Questioner Agent generates probing questions to deepen understanding.
    Uses Socratic questioning, critical analysis, and identifies gaps in reasoning
    to guide deeper exploration.
    """
}

def get_agent_class(agent_name: str):
    """Get agent class by name"""
    return SPECIALIST_AGENTS.get(agent_name)

def get_agent_role(agent_name: str) -> str:
    """Get agent role description"""
    return AGENT_ROLES.get(agent_name, "Unknown role")

def get_agent_description(agent_name: str) -> str:
    """Get agent description"""
    return AGENT_DESCRIPTIONS.get(agent_name, "No description available").strip()

def list_available_agents() -> list:
    """List all available specialist agents"""
    return list(SPECIALIST_AGENTS.keys())

def create_agent_summary() -> dict:
    """Create a summary of all specialist agents"""
    return {
        agent_name: {
            "class": agent_class.__name__,
            "role": get_agent_role(agent_name),
            "description": get_agent_description(agent_name)
        }
        for agent_name, agent_class in SPECIALIST_AGENTS.items()
    }
