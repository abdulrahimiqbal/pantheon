"""
Agents module for the Physics AI Agent Swarm.

This module contains all the agent implementations for the physics research swarm.
"""

from .base_agent import BasePhysicsAgent, AgentCommunicationProtocol, communication_protocol

__version__ = "1.0.0"
__author__ = "Physics AI Agent Swarm Team"

__all__ = [
    "BasePhysicsAgent",
    "AgentCommunicationProtocol", 
    "communication_protocol"
]
