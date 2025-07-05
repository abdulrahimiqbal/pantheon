# Physics AI Agent Swarm 🔬🤖

A sophisticated multi-agent system designed for physics research, education, and hypothesis generation. Built with CrewAI framework and powered by state-of-the-art LLMs.

## 🎯 Overview

The Physics AI Agent Swarm consists of 4 specialized agents working together to provide comprehensive physics research and analysis:

1. **Web Crawler Agent** - Searches and validates physics sources using Tavily API
2. **Physicist Master Agent** - Subject matter expert and orchestrator
3. **Tesla Principles Agent** - First-principles thinking and innovative approaches
4. **Curious Questioner Agent** - Probing questions to deepen understanding

## 🏗️ Architecture

```
Physics AI Agent Swarm
├── 🧠 Physicist Master (Orchestrator)
├── 🌐 Web Crawler (Research)
├── ⚡ Tesla Principles (Innovation)
└── ❓ Curious Questioner (Analysis)
```

## 🚀 Features

- **Multi-Agent Collaboration**: Agents work together with hierarchical orchestration
- **Source Validation**: Automated credibility scoring and validation
- **Hypothesis Generation**: Novel physics hypothesis creation and testing
- **Complexity Adaptation**: Adjusts responses based on query complexity
- **Real-time Research**: Live web research with academic source prioritization
- **Confidence Scoring**: Transparent confidence levels for all responses

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Anthropic API key (optional)
- Tavily API key
- BrightData API key (optional)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd physics_swarm
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Test the foundation setup**
   ```bash
   python tests/test_foundation.py
   ```

## 🔧 Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional
BRIGHTDATA_API_KEY=your_brightdata_api_key_here

# Agent Configuration
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0.7
MAX_SEARCH_RESULTS=10
```

### Agent Configurations

Each agent has specific configurations:

- **Web Crawler**: Low temperature (0.3) for factual accuracy
- **Physicist Master**: Balanced temperature (0.5) for analysis
- **Tesla Principles**: High temperature (0.8) for creativity
- **Curious Questioner**: Medium temperature (0.7) for questioning

## 📊 Project Structure

```
physics_swarm/
├── agents/                 # Agent implementations
│   ├── base_agent.py      # Base agent class
│   └── __init__.py
├── shared/                 # Shared modules
│   ├── types.py           # Type definitions
│   ├── config.py          # Configuration management
│   ├── utils.py           # Utility functions
│   └── __init__.py
├── orchestration/         # Orchestration system
├── api/                   # FastAPI endpoints
├── frontend/              # Web interface
├── tests/                 # Test suite
│   └── test_foundation.py # Foundation tests
├── data/                  # Data storage
├── requirements.txt       # Dependencies
├── env.example           # Environment template
└── README.md             # This file
```

## 🧪 Testing

Run the foundation tests to verify setup:

```bash
python tests/test_foundation.py
```

Expected output:
```
🧪 Physics AI Agent Swarm - Foundation Test Suite
============================================================
Testing shared module imports...
✅ All shared imports successful

Testing type definitions...
✅ DataSource created: Test Physics Paper
✅ PhysicsQuery created: What is quantum entanglement?

...

Test Results: 6/6 tests passed
🎉 All foundation tests passed! Ready for Phase 2.
```

## 🔄 Development Phases

### ✅ Phase 1: Foundation Setup (COMPLETED)
- [x] Shared foundation modules (types, config, utils)
- [x] Base agent framework with CrewAI integration
- [x] Configuration management
- [x] Testing framework

### ✅ Phase 2: Agent Implementation (COMPLETED)
- [x] Web Crawler Agent with Tavily API
- [x] Physicist Master Agent
- [x] Tesla Principles Agent
- [x] Curious Questioner Agent

### ✅ Phase 3: Orchestration System (COMPLETED)
- [x] Hierarchical orchestration
- [x] Inter-agent communication
- [x] Task routing and coordination
- [x] SwarmOrchestrator and SwarmManager

### 🔄 Phase 4: API & Frontend (READY TO IMPLEMENT)
- [ ] FastAPI backend
- [ ] Web interface
- [ ] Real-time query processing

### ✅ Phase 5: Testing & Validation (COMPLETED)
- [x] Comprehensive agent tests
- [x] Integration testing
- [x] Example usage demonstrations
- [x] Performance monitoring

## 📚 Usage Examples

### Quick Start - Basic Physics Question
```python
import asyncio
from orchestration.swarm_orchestrator import SwarmManager
from shared.config import SwarmConfig, AgentConfig
from shared.types import ComplexityLevel

# Set up configuration
agent_config = AgentConfig(
    openai_api_key="your_openai_key",
    tavily_api_key="your_tavily_key",
    model="gpt-4"
)

swarm_config = SwarmConfig(
    agent_config=agent_config,
    tavily_api_key="your_tavily_key",
    max_agents=4
)

# Initialize the swarm
manager = SwarmManager(swarm_config)

# Ask a physics question
async def ask_question():
    response = await manager.ask_physics_question(
        question="What is quantum entanglement?",
        context="University physics student",
        complexity=ComplexityLevel.INTERMEDIATE
    )
    
    print(f"Answer: {response.master_response.content}")
    print(f"Confidence: {response.confidence.value}")
    print(f"Agents involved: {len(response.agent_responses)}")

# Run the example
asyncio.run(ask_question())
```

### Advanced Research Query with Full Swarm
```python
# Research-level question with specialized agent coordination
response = await manager.ask_physics_question(
    question="How might topological quantum computing overcome decoherence challenges?",
    context="Quantum computing research",
    complexity=ComplexityLevel.RESEARCH
)

# Access specialized agent insights
tesla_insights = response.agent_responses["tesla_principles"]
research_sources = response.agent_responses["web_crawler"] 
critical_questions = response.agent_responses["curious_questioner"]

print(f"Tesla Innovation: {tesla_insights.metadata.get('breakthrough_experiment', {}).get('title')}")
print(f"Research Sources: {len(research_sources.sources)}")
print(f"Questions Generated: {critical_questions.metadata.get('total_questions_generated')}")
```

### Running the Comprehensive Demonstration
```bash
# Set up environment variables in .env file
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here

# Run the full demonstration
cd physics_swarm
python example_usage.py
```

### Individual Agent Testing
```python
# Test individual agents
python tests/test_agents.py

# Run foundation tests
python tests/test_foundation.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- CrewAI framework for multi-agent orchestration
- Tavily API for web research capabilities
- OpenAI and Anthropic for LLM services
- The physics research community for inspiration

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the documentation
- Review the test suite for examples

---

**Status**: Core Implementation Complete ✅ | Phases 1-3 Done | Ready for API & Frontend 🚀

**Features Implemented**:
- ✅ 4 Specialized Physics Agents (Web Crawler, Master Physicist, Tesla Principles, Curious Questioner)
- ✅ Hierarchical Swarm Orchestration with CrewAI
- ✅ Academic Source Research and Validation
- ✅ First-Principles Thinking and Innovation
- ✅ Critical Questioning and Deep Analysis
- ✅ Comprehensive Testing Suite
- ✅ Example Usage Demonstrations
