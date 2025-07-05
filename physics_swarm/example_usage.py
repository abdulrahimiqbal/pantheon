"""
Physics AI Agent Swarm - Example Usage

This script demonstrates how to use the physics swarm to answer various types
of physics questions, from basic concepts to advanced research inquiries.
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

from shared.types import PhysicsQuery, ComplexityLevel
from shared.config import SwarmConfig, AgentConfig
from orchestration.swarm_orchestrator import SwarmManager


# Load environment variables
load_dotenv()


def setup_swarm_config() -> SwarmConfig:
    """Set up the swarm configuration"""
    agent_config = AgentConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        brightdata_api_key=os.getenv("BRIGHTDATA_API_KEY"),
        model=os.getenv("DEFAULT_MODEL", "gpt-4"),
        temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("MAX_TOKENS", "2000"))
    )
    
    swarm_config = SwarmConfig(
        agent_config=agent_config,
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        brightdata_api_key=os.getenv("BRIGHTDATA_API_KEY"),
        max_agents=4,
        orchestration_timeout=300,
        enable_parallel_processing=True
    )
    
    return swarm_config


async def demonstrate_basic_physics_question(manager: SwarmManager):
    """Demonstrate answering a basic physics question"""
    print("\n" + "="*80)
    print("🔬 BASIC PHYSICS QUESTION")
    print("="*80)
    
    response = await manager.ask_physics_question(
        question="What is Newton's first law of motion?",
        context="High school physics student learning about motion",
        complexity=ComplexityLevel.BASIC
    )
    
    print(f"Question: {response.query.question}")
    print(f"Complexity: {response.query.complexity_level.value}")
    print(f"Confidence: {response.confidence.value}")
    print(f"Processing Time: {response.processing_time:.2f} seconds")
    print(f"Agents Involved: {len(response.agent_responses)}")
    
    print("\n📝 Master Response:")
    print(response.master_response.content[:500] + "..." if len(response.master_response.content) > 500 else response.master_response.content)
    
    if response.agent_responses:
        print(f"\n🤖 Agent Contributions ({len(response.agent_responses)} agents):")
        for agent_name, agent_response in response.agent_responses.items():
            print(f"\n{agent_name.replace('_', ' ').title()}:")
            print(f"  Confidence: {agent_response.confidence.value}")
            print(f"  Sources: {len(agent_response.sources)}")
            preview = agent_response.content[:200] + "..." if len(agent_response.content) > 200 else agent_response.content
            print(f"  Preview: {preview}")


async def demonstrate_intermediate_physics_question(manager: SwarmManager):
    """Demonstrate answering an intermediate physics question"""
    print("\n" + "="*80)
    print("⚛️ INTERMEDIATE PHYSICS QUESTION")
    print("="*80)
    
    response = await manager.ask_physics_question(
        question="How does quantum entanglement work and what are its practical applications?",
        context="Undergraduate physics student studying quantum mechanics",
        complexity=ComplexityLevel.INTERMEDIATE
    )
    
    print(f"Question: {response.query.question}")
    print(f"Complexity: {response.query.complexity_level.value}")
    print(f"Confidence: {response.confidence.value}")
    print(f"Processing Time: {response.processing_time:.2f} seconds")
    
    print("\n📝 Master Response:")
    print(response.master_response.content[:500] + "..." if len(response.master_response.content) > 500 else response.master_response.content)
    
    # Show agent specializations
    if response.agent_responses:
        print(f"\n🔍 Agent Specializations:")
        for agent_name, agent_response in response.agent_responses.items():
            specialization = {
                "web_crawler": "Research & Source Validation",
                "physicist_master": "Expert Analysis & Orchestration",
                "tesla_principles": "First-Principles Innovation",
                "curious_questioner": "Critical Inquiry & Questions"
            }.get(agent_name, "General Analysis")
            
            print(f"\n{agent_name.replace('_', ' ').title()} ({specialization}):")
            print(f"  Confidence: {agent_response.confidence.value}")
            print(f"  Key Insights: {len(agent_response.metadata.get('key_insights', []))}")
            print(f"  Sources Found: {len(agent_response.sources)}")


async def demonstrate_advanced_physics_question(manager: SwarmManager):
    """Demonstrate answering an advanced physics question"""
    print("\n" + "="*80)
    print("🚀 ADVANCED PHYSICS QUESTION")
    print("="*80)
    
    response = await manager.ask_physics_question(
        question="What are the implications of the holographic principle for our understanding of black hole information paradox?",
        context="Graduate student researching theoretical physics and quantum gravity",
        complexity=ComplexityLevel.ADVANCED
    )
    
    print(f"Question: {response.query.question}")
    print(f"Complexity: {response.query.complexity_level.value}")
    print(f"Confidence: {response.confidence.value}")
    print(f"Processing Time: {response.processing_time:.2f} seconds")
    
    print("\n📝 Comprehensive Analysis:")
    print(response.master_response.content[:600] + "..." if len(response.master_response.content) > 600 else response.master_response.content)
    
    # Show synthesis information
    if hasattr(response, 'synthesis') and response.synthesis:
        synthesis = response.synthesis
        print(f"\n🧠 Synthesis Insights:")
        
        if 'key_insights' in synthesis:
            print(f"  Key Insights Identified: {len(synthesis['key_insights'])}")
            for insight in synthesis['key_insights'][:3]:
                print(f"    • {insight}")
        
        if 'contradictions' in synthesis and synthesis['contradictions']:
            print(f"  Contradictions Found: {len(synthesis['contradictions'])}")
        
        if 'gaps' in synthesis and synthesis['gaps']:
            print(f"  Knowledge Gaps: {len(synthesis['gaps'])}")


async def demonstrate_research_physics_question(manager: SwarmManager):
    """Demonstrate answering a research-level physics question"""
    print("\n" + "="*80)
    print("🔬 RESEARCH-LEVEL PHYSICS QUESTION")
    print("="*80)
    
    response = await manager.ask_physics_question(
        question="Could we develop a new approach to quantum computing based on topological quantum states that is more robust to decoherence?",
        context="Theoretical physics researcher exploring novel quantum computing architectures",
        complexity=ComplexityLevel.RESEARCH
    )
    
    print(f"Question: {response.query.question}")
    print(f"Complexity: {response.query.complexity_level.value}")
    print(f"Confidence: {response.confidence.value}")
    print(f"Processing Time: {response.processing_time:.2f} seconds")
    
    print("\n📝 Research Analysis:")
    print(response.master_response.content[:700] + "..." if len(response.master_response.content) > 700 else response.master_response.content)
    
    # Show innovative insights from Tesla Principles Agent
    if "tesla_principles" in response.agent_responses:
        tesla_response = response.agent_responses["tesla_principles"]
        print(f"\n⚡ Tesla Principles Innovation:")
        print(f"  Agent Confidence: {tesla_response.confidence.value}")
        
        if 'tesla_quote' in tesla_response.metadata:
            print(f"  Inspiration: \"{tesla_response.metadata['tesla_quote']}\"")
        
        if 'breakthrough_experiment' in tesla_response.metadata:
            experiment = tesla_response.metadata['breakthrough_experiment']
            print(f"  Proposed Experiment: {experiment.get('title', 'Novel Approach')}")
            print(f"  Breakthrough Potential: {experiment.get('breakthrough_potential', 'To be determined')}")
    
    # Show critical questions from Curious Questioner
    if "curious_questioner" in response.agent_responses:
        questioner_response = response.agent_responses["curious_questioner"]
        print(f"\n❓ Critical Questions Generated:")
        print(f"  Agent Confidence: {questioner_response.confidence.value}")
        
        if 'total_questions_generated' in questioner_response.metadata:
            print(f"  Total Questions: {questioner_response.metadata['total_questions_generated']}")
        
        if 'questioning_quote' in questioner_response.metadata:
            print(f"  Philosophy: \"{questioner_response.metadata['questioning_quote']}\"")


async def demonstrate_swarm_status(manager: SwarmManager):
    """Demonstrate getting swarm status"""
    print("\n" + "="*80)
    print("📊 SWARM STATUS & PERFORMANCE")
    print("="*80)
    
    status = manager.get_status()
    
    print(f"Active Agents: {len(status['agents'])}")
    print(f"Active Queries: {status['active_queries']}")
    print(f"Total Queries Processed: {status['total_queries_processed']}")
    print(f"Average Processing Time: {status['average_processing_time']:.2f} seconds")
    
    print(f"\n🤖 Agent Details:")
    for agent_name, agent_info in status['agents'].items():
        print(f"  {agent_name.replace('_', ' ').title()}:")
        print(f"    Status: {agent_info['status']}")
        print(f"    Class: {agent_info['class']}")
        print(f"    Config: {agent_info['config']}")


async def main():
    """Main demonstration function"""
    print("🔬🤖 Physics AI Agent Swarm - Demonstration")
    print("=" * 80)
    print("This demonstration shows the physics swarm answering questions")
    print("of increasing complexity using specialized AI agents.")
    print("=" * 80)
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file before running the demonstration.")
        return
    
    try:
        # Initialize the swarm
        print("\n🚀 Initializing Physics AI Agent Swarm...")
        config = setup_swarm_config()
        manager = SwarmManager(config)
        print("✅ Swarm initialized successfully!")
        
        # Run demonstrations
        await demonstrate_basic_physics_question(manager)
        await demonstrate_intermediate_physics_question(manager)
        await demonstrate_advanced_physics_question(manager)
        await demonstrate_research_physics_question(manager)
        await demonstrate_swarm_status(manager)
        
        print("\n" + "="*80)
        print("🎉 DEMONSTRATION COMPLETE")
        print("="*80)
        print("The physics swarm has successfully demonstrated its capabilities")
        print("across different complexity levels and question types.")
        print("\nKey Features Demonstrated:")
        print("• Multi-agent collaboration and specialization")
        print("• Academic source research and validation")
        print("• First-principles thinking and innovation")
        print("• Critical questioning and deep analysis")
        print("• Hierarchical orchestration and synthesis")
        print("• Confidence assessment and quality control")
        
        # Shutdown
        print("\n🔄 Shutting down swarm...")
        await manager.shutdown()
        print("✅ Shutdown complete!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        print("Please check your configuration and API keys.")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main()) 