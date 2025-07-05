"""
Comprehensive Tests for Physics Agents

This module tests all the physics agents in the swarm to ensure they work correctly
individually and as a coordinated system.
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Import shared types and config
from ..shared.types import PhysicsQuery, ComplexityLevel, ConfidenceLevel, AgentRole
from ..shared.config import AgentConfig, SwarmConfig

# Import agents
from ..agents.specialist_agents import (
    WebCrawlerAgent, PhysicistMasterAgent, TeslaPrinciplesAgent, 
    CuriousQuestionerAgent, SPECIALIST_AGENTS
)
from ..orchestration.swarm_orchestrator import SwarmOrchestrator, SwarmManager


class TestAgentFoundation:
    """Test the foundation and basic functionality of all agents"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.test_config = AgentConfig(
            openai_api_key="test_key",
            anthropic_api_key="test_key",
            tavily_api_key="test_key",
            brightdata_api_key="test_key",
            agent_name="test_agent",
            role=AgentRole.RESEARCHER,
            model="gpt-4",
            temperature=0.7,
            max_tokens=2000
        )
        
        self.test_query = PhysicsQuery(
            question="What is quantum entanglement?",
            context="Graduate student studying quantum mechanics",
            complexity_level=ComplexityLevel.INTERMEDIATE,
            timestamp=datetime.now()
        )
    
    def test_agent_config_creation(self):
        """Test agent configuration creation"""
        assert self.test_config.agent_name == "test_agent"
        assert self.test_config.role == AgentRole.RESEARCHER
        assert self.test_config.model == "gpt-4"
        assert self.test_config.temperature == 0.7
    
    def test_physics_query_creation(self):
        """Test physics query creation"""
        assert self.test_query.question == "What is quantum entanglement?"
        assert self.test_query.complexity_level == ComplexityLevel.INTERMEDIATE
        assert isinstance(self.test_query.timestamp, datetime)
    
    def test_specialist_agents_registry(self):
        """Test that all specialist agents are registered"""
        expected_agents = ["web_crawler", "physicist_master", "tesla_principles", "curious_questioner"]
        
        for agent_name in expected_agents:
            assert agent_name in SPECIALIST_AGENTS
            assert SPECIALIST_AGENTS[agent_name] is not None


class TestWebCrawlerAgent:
    """Test the Web Crawler Agent"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = AgentConfig(
            openai_api_key="test_key",
            tavily_api_key="test_key",
            brightdata_api_key="test_key",
            agent_name="web_crawler",
            role=AgentRole.RESEARCHER,
            model="gpt-4",
            temperature=0.3
        )
        
        self.query = PhysicsQuery(
            question="What are the latest developments in quantum computing?",
            context="Research scientist",
            complexity_level=ComplexityLevel.ADVANCED,
            timestamp=datetime.now()
        )
    
    @patch('requests.post')
    def test_web_crawler_initialization(self, mock_post):
        """Test web crawler agent initialization"""
        agent = WebCrawlerAgent(self.config)
        
        assert agent.config.agent_name == "web_crawler"
        assert agent.tavily_tool is not None
        assert agent.brightdata_tool is not None
        assert agent.crew_agent is not None
    
    @patch('requests.post')
    def test_tavily_search_tool(self, mock_post):
        """Test Tavily search tool"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Quantum Computing Breakthrough",
                    "url": "https://arxiv.org/abs/2024.12345",
                    "content": "Recent advances in quantum computing...",
                    "score": 0.95
                }
            ]
        }
        mock_post.return_value = mock_response
        
        agent = WebCrawlerAgent(self.config)
        result = agent.tavily_tool._run("quantum computing")
        
        assert "results" in result
        assert len(result["results"]) > 0
        assert result["results"][0]["title"] == "Quantum Computing Breakthrough"
    
    def test_source_type_determination(self):
        """Test source type determination"""
        agent = WebCrawlerAgent(self.config)
        
        # Test different URL types
        assert agent._determine_source_type("https://arxiv.org/abs/2024.12345").name == "ACADEMIC_PAPER"
        assert agent._determine_source_type("https://journals.aps.org/prl/abstract").name == "PEER_REVIEWED_JOURNAL"
        assert agent._determine_source_type("https://mit.edu/physics/").name == "ACADEMIC_INSTITUTION"
        assert agent._determine_source_type("https://cern.ch/news/").name == "RESEARCH_INSTITUTION"
    
    def test_credibility_score_calculation(self):
        """Test credibility score calculation"""
        agent = WebCrawlerAgent(self.config)
        
        # Test high credibility source
        high_cred_result = {"url": "https://arxiv.org/abs/2024.12345", "title": "Test Paper"}
        from ..shared.types import SourceType
        score = agent._calculate_credibility_score(high_cred_result, SourceType.ACADEMIC_PAPER)
        assert score >= 0.8
        
        # Test lower credibility source
        low_cred_result = {"url": "https://example.com/blog", "title": "Blog Post"}
        score = agent._calculate_credibility_score(low_cred_result, SourceType.WEB_ARTICLE)
        assert score <= 0.6
    
    @patch('requests.post')
    async def test_process_query(self, mock_post):
        """Test processing a query"""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Quantum Computing Research",
                    "url": "https://arxiv.org/abs/2024.12345",
                    "content": "Advanced quantum computing research...",
                    "score": 0.9
                }
            ]
        }
        mock_post.return_value = mock_response
        
        agent = WebCrawlerAgent(self.config)
        
        # Mock the LLM to avoid actual API calls
        with patch.object(agent, 'llm', Mock()):
            response = await agent.process_query(self.query)
        
        assert response.agent_name == "Web Crawler Agent"
        assert response.confidence in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]
        assert isinstance(response.content, str)
        assert len(response.content) > 0


class TestPhysicistMasterAgent:
    """Test the Physicist Master Agent"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = AgentConfig(
            openai_api_key="test_key",
            agent_name="physicist_master",
            role=AgentRole.ORCHESTRATOR,
            model="gpt-4",
            temperature=0.5
        )
        
        self.query = PhysicsQuery(
            question="How does quantum entanglement relate to information theory?",
            context="Theoretical physics research",
            complexity_level=ComplexityLevel.RESEARCH,
            timestamp=datetime.now()
        )
    
    def test_physicist_master_initialization(self):
        """Test physicist master agent initialization"""
        agent = PhysicistMasterAgent(self.config)
        
        assert agent.config.agent_name == "physicist_master"
        assert agent.knowledge_base is not None
        assert agent.analysis_tool is not None
        assert agent.crew_agent is not None
    
    def test_physics_knowledge_base(self):
        """Test physics knowledge base tool"""
        agent = PhysicistMasterAgent(self.config)
        
        # Test quantum mechanics domain
        result = agent.knowledge_base._run("quantum_mechanics")
        assert "domain" in result
        assert result["domain"] == "quantum_mechanics"
        assert "knowledge" in result
        
        # Test specific concept
        result = agent.knowledge_base._run("quantum_mechanics", "entanglement")
        assert "concept" in result
        assert result["concept"] == "entanglement"
    
    def test_physics_analysis_tool(self):
        """Test physics analysis tool"""
        agent = PhysicistMasterAgent(self.config)
        
        result = agent.analysis_tool._run("quantum entanglement")
        assert "domains" in result
        assert "concepts" in result
        assert "complexity_assessment" in result
        assert "quantum_mechanics" in result["domains"]
    
    def test_query_classification(self):
        """Test query classification"""
        agent = PhysicistMasterAgent(self.config)
        
        # Test different query types
        explanation_query = PhysicsQuery(
            question="What is Newton's first law?",
            context="",
            complexity_level=ComplexityLevel.BASIC,
            timestamp=datetime.now()
        )
        
        classification = agent._classify_query(explanation_query)
        assert classification["type"] == "explanation"
        
        hypothesis_query = PhysicsQuery(
            question="I propose a new theory of gravity",
            context="",
            complexity_level=ComplexityLevel.RESEARCH,
            timestamp=datetime.now()
        )
        
        classification = agent._classify_query(hypothesis_query)
        assert classification["type"] == "hypothesis"
    
    async def test_initial_analysis(self):
        """Test initial analysis of query"""
        agent = PhysicistMasterAgent(self.config)
        
        analysis = await agent._perform_initial_analysis(self.query)
        
        assert "domains" in analysis
        assert "concepts" in analysis
        assert "query_classification" in analysis
        assert len(analysis["domains"]) > 0
    
    async def test_process_query(self):
        """Test processing a query"""
        agent = PhysicistMasterAgent(self.config)
        
        # Mock the LLM to avoid actual API calls
        with patch.object(agent, 'llm', Mock()):
            response = await agent.process_query(self.query)
        
        assert response.agent_name == "Physicist Master Agent"
        assert response.confidence in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]
        assert isinstance(response.content, str)
        assert len(response.content) > 0


class TestTeslaPrinciplesAgent:
    """Test the Tesla Principles Agent"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = AgentConfig(
            openai_api_key="test_key",
            agent_name="tesla_principles",
            role=AgentRole.INNOVATOR,
            model="gpt-4",
            temperature=0.8
        )
        
        self.query = PhysicsQuery(
            question="How could we achieve wireless energy transmission?",
            context="Innovation research",
            complexity_level=ComplexityLevel.RESEARCH,
            timestamp=datetime.now()
        )
    
    def test_tesla_principles_initialization(self):
        """Test Tesla principles agent initialization"""
        agent = TeslaPrinciplesAgent(self.config)
        
        assert agent.config.agent_name == "tesla_principles"
        assert agent.first_principles_tool is not None
        assert agent.innovation_tool is not None
        assert agent.crew_agent is not None
    
    def test_first_principles_tool(self):
        """Test first principles analysis tool"""
        agent = TeslaPrinciplesAgent(self.config)
        
        result = agent.first_principles_tool._run("wireless energy transmission")
        
        assert "fundamental_principles" in result
        assert "assumptions_to_question" in result
        assert "novel_perspectives" in result
        assert "breakthrough_potential" in result
        assert len(result["fundamental_principles"]) > 0
    
    def test_innovation_tool(self):
        """Test innovation generation tool"""
        agent = TeslaPrinciplesAgent(self.config)
        
        result = agent.innovation_tool._run("wireless energy transmission")
        
        assert "breakthrough_ideas" in result
        assert "novel_experiments" in result
        assert "theoretical_innovations" in result
        assert "technological_applications" in result
        assert len(result["breakthrough_ideas"]) > 0
    
    async def test_apply_first_principles(self):
        """Test applying first principles to a query"""
        agent = TeslaPrinciplesAgent(self.config)
        
        analysis = await agent.apply_first_principles(self.query)
        
        assert "fundamental_principles" in analysis
        assert "tesla_insights" in analysis
        assert len(analysis["tesla_insights"]) > 0
    
    async def test_generate_innovations(self):
        """Test generating innovations"""
        agent = TeslaPrinciplesAgent(self.config)
        
        innovations = await agent.generate_innovations(self.query)
        
        assert "breakthrough_ideas" in innovations
        assert "tesla_specific" in innovations
        assert len(innovations["breakthrough_ideas"]) > 0
    
    async def test_challenge_assumptions(self):
        """Test challenging assumptions"""
        agent = TeslaPrinciplesAgent(self.config)
        
        challenges = await agent.challenge_assumptions(self.query, "conventional wisdom")
        
        assert isinstance(challenges, list)
        assert len(challenges) > 0
        assert all(isinstance(challenge, str) for challenge in challenges)
    
    async def test_process_query(self):
        """Test processing a query"""
        agent = TeslaPrinciplesAgent(self.config)
        
        # Mock the LLM to avoid actual API calls
        with patch.object(agent, 'llm', Mock()):
            response = await agent.process_query(self.query)
        
        assert response.agent_name == "Tesla Principles Agent"
        assert response.confidence in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]
        assert isinstance(response.content, str)
        assert len(response.content) > 0
        assert "tesla_quote" in response.metadata


class TestCuriousQuestionerAgent:
    """Test the Curious Questioner Agent"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = AgentConfig(
            openai_api_key="test_key",
            agent_name="curious_questioner",
            role=AgentRole.ANALYST,
            model="gpt-4",
            temperature=0.7
        )
        
        self.query = PhysicsQuery(
            question="What is dark matter?",
            context="Astrophysics research",
            complexity_level=ComplexityLevel.ADVANCED,
            timestamp=datetime.now()
        )
    
    def test_curious_questioner_initialization(self):
        """Test curious questioner agent initialization"""
        agent = CuriousQuestionerAgent(self.config)
        
        assert agent.config.agent_name == "curious_questioner"
        assert agent.socratic_tool is not None
        assert agent.critical_analysis_tool is not None
        assert agent.prioritization_tool is not None
        assert agent.crew_agent is not None
    
    def test_socratic_questioning_tool(self):
        """Test Socratic questioning tool"""
        agent = CuriousQuestionerAgent(self.config)
        
        result = agent.socratic_tool._run("dark matter")
        
        assert "generated_questions" in result
        assert "follow_up_paths" in result
        assert "depth_levels" in result
        assert len(result["generated_questions"]) > 0
    
    def test_critical_analysis_tool(self):
        """Test critical analysis tool"""
        agent = CuriousQuestionerAgent(self.config)
        
        content = "Dark matter is a mysterious substance that makes up most of the universe."
        result = agent.critical_analysis_tool._run(content)
        
        assert "framework_analyses" in result
        assert "identified_gaps" in result
        assert "critical_questions" in result
        assert len(result["framework_analyses"]) > 0
    
    def test_question_prioritization_tool(self):
        """Test question prioritization tool"""
        agent = CuriousQuestionerAgent(self.config)
        
        questions = [
            "What is dark matter?",
            "How do we detect dark matter?",
            "Why is dark matter important?",
            "What are the implications of dark matter?"
        ]
        
        result = agent.prioritization_tool._run(questions)
        
        assert "prioritized_questions" in result
        assert "recommendations" in result
        assert len(result["prioritized_questions"]) == len(questions)
    
    async def test_generate_socratic_questions(self):
        """Test generating Socratic questions"""
        agent = CuriousQuestionerAgent(self.config)
        
        analysis = await agent.generate_socratic_questions(self.query)
        
        assert "generated_questions" in analysis
        assert "physics_specific" in analysis
        assert len(analysis["physics_specific"]) > 0
    
    async def test_perform_critical_analysis(self):
        """Test performing critical analysis"""
        agent = CuriousQuestionerAgent(self.config)
        
        analysis = await agent.perform_critical_analysis("Dark matter is mysterious")
        
        assert "framework_analyses" in analysis
        assert "follow_up_questions" in analysis
        assert len(analysis["follow_up_questions"]) > 0
    
    async def test_prioritize_questions(self):
        """Test prioritizing questions"""
        agent = CuriousQuestionerAgent(self.config)
        
        questions = ["What is dark matter?", "How do we detect it?", "Why is it important?"]
        prioritization = await agent.prioritize_questions(questions)
        
        assert "prioritized_questions" in prioritization
        assert "investigation_strategy" in prioritization
        assert len(prioritization["prioritized_questions"]) == len(questions)
    
    async def test_guide_deeper_inquiry(self):
        """Test guiding deeper inquiry"""
        agent = CuriousQuestionerAgent(self.config)
        
        guidance = await agent.guide_deeper_inquiry("dark matter", "current understanding")
        
        assert "deeper_questions" in guidance
        assert "unexplored_angles" in guidance
        assert "connection_opportunities" in guidance
        assert "breakthrough_potential" in guidance
        assert len(guidance["deeper_questions"]) > 0
    
    async def test_process_query(self):
        """Test processing a query"""
        agent = CuriousQuestionerAgent(self.config)
        
        # Mock the LLM to avoid actual API calls
        with patch.object(agent, 'llm', Mock()):
            response = await agent.process_query(self.query)
        
        assert response.agent_name == "Curious Questioner Agent"
        assert response.confidence in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]
        assert isinstance(response.content, str)
        assert len(response.content) > 0
        assert "questioning_quote" in response.metadata


class TestSwarmOrchestration:
    """Test the swarm orchestration system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.swarm_config = SwarmConfig(
            agent_config=AgentConfig(
                openai_api_key="test_key",
                anthropic_api_key="test_key",
                tavily_api_key="test_key",
                brightdata_api_key="test_key",
                model="gpt-4",
                temperature=0.7
            ),
            tavily_api_key="test_key",
            brightdata_api_key="test_key",
            max_agents=4,
            orchestration_timeout=300,
            enable_parallel_processing=True
        )
        
        self.query = PhysicsQuery(
            question="Explain quantum entanglement and its applications",
            context="University physics course",
            complexity_level=ComplexityLevel.INTERMEDIATE,
            timestamp=datetime.now()
        )
    
    def test_swarm_orchestrator_initialization(self):
        """Test swarm orchestrator initialization"""
        with patch('openai.OpenAI'), patch('anthropic.Anthropic'):
            orchestrator = SwarmOrchestrator(self.swarm_config)
            
            assert len(orchestrator.agents) == 4
            assert "web_crawler" in orchestrator.agents
            assert "physicist_master" in orchestrator.agents
            assert "tesla_principles" in orchestrator.agents
            assert "curious_questioner" in orchestrator.agents
    
    def test_query_analysis_and_planning(self):
        """Test query analysis and planning"""
        with patch('openai.OpenAI'), patch('anthropic.Anthropic'):
            orchestrator = SwarmOrchestrator(self.swarm_config)
            
            # Mock the async method
            async def test_analysis():
                plan = await orchestrator._analyze_and_plan_query(self.query)
                
                assert "query_type" in plan
                assert "complexity_assessment" in plan
                assert "required_agents" in plan
                assert "execution_strategy" in plan
                assert "success_criteria" in plan
            
            # Run the async test
            asyncio.run(test_analysis())
    
    def test_task_distribution(self):
        """Test task distribution to agents"""
        with patch('openai.OpenAI'), patch('anthropic.Anthropic'):
            orchestrator = SwarmOrchestrator(self.swarm_config)
            
            async def test_distribution():
                plan = await orchestrator._analyze_and_plan_query(self.query)
                tasks = await orchestrator._distribute_tasks(self.query, plan)
                
                assert isinstance(tasks, dict)
                assert len(tasks) > 0
                assert "physicist_master" in tasks
            
            asyncio.run(test_distribution())
    
    def test_swarm_manager_initialization(self):
        """Test swarm manager initialization"""
        with patch('openai.OpenAI'), patch('anthropic.Anthropic'):
            manager = SwarmManager(self.swarm_config)
            
            assert manager.orchestrator is not None
            assert manager.logger is not None
    
    def test_swarm_status(self):
        """Test getting swarm status"""
        with patch('openai.OpenAI'), patch('anthropic.Anthropic'):
            orchestrator = SwarmOrchestrator(self.swarm_config)
            
            status = orchestrator.get_swarm_status()
            
            assert "agents" in status
            assert "active_queries" in status
            assert "total_queries_processed" in status
            assert len(status["agents"]) == 4


class TestIntegration:
    """Integration tests for the complete system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.swarm_config = SwarmConfig(
            agent_config=AgentConfig(
                openai_api_key="test_key",
                anthropic_api_key="test_key",
                tavily_api_key="test_key",
                brightdata_api_key="test_key",
                model="gpt-4",
                temperature=0.7
            ),
            tavily_api_key="test_key",
            brightdata_api_key="test_key",
            max_agents=4,
            orchestration_timeout=300,
            enable_parallel_processing=True
        )
    
    @patch('requests.post')
    async def test_simple_physics_question(self, mock_post):
        """Test processing a simple physics question"""
        # Mock API responses
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Newton's Laws of Motion",
                    "url": "https://physics.example.com/newton",
                    "content": "Newton's laws describe the motion of objects...",
                    "score": 0.9
                }
            ]
        }
        mock_post.return_value = mock_response
        
        with patch('openai.OpenAI'), patch('anthropic.Anthropic'):
            manager = SwarmManager(self.swarm_config)
            
            # Mock all LLM calls
            for agent in manager.orchestrator.agents.values():
                with patch.object(agent, 'llm', Mock()):
                    pass
            
            # Test a simple question
            response = await manager.ask_physics_question(
                "What is Newton's first law of motion?",
                complexity=ComplexityLevel.BASIC
            )
            
            assert response is not None
            assert response.query.question == "What is Newton's first law of motion?"
            assert response.confidence in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]
    
    async def test_complex_physics_research(self):
        """Test processing a complex physics research question"""
        with patch('openai.OpenAI'), patch('anthropic.Anthropic'):
            manager = SwarmManager(self.swarm_config)
            
            # Mock all LLM calls
            for agent in manager.orchestrator.agents.values():
                with patch.object(agent, 'llm', Mock()):
                    pass
            
            # Test a complex research question
            response = await manager.ask_physics_question(
                "How might quantum entanglement be used to develop new communication protocols?",
                context="Quantum information research",
                complexity=ComplexityLevel.RESEARCH
            )
            
            assert response is not None
            assert response.query.complexity_level == ComplexityLevel.RESEARCH
            assert len(response.agent_responses) > 0


def run_all_tests():
    """Run all tests"""
    print("🧪 Physics AI Agent Swarm - Test Suite")
    print("=" * 60)
    
    # Test categories
    test_classes = [
        TestAgentFoundation,
        TestWebCrawlerAgent,
        TestPhysicistMasterAgent,
        TestTeslaPrinciplesAgent,
        TestCuriousQuestionerAgent,
        TestSwarmOrchestration,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}...")
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            
            try:
                # Create test instance
                test_instance = test_class()
                
                # Run setup if exists
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                # Run test method
                method = getattr(test_instance, test_method)
                
                if asyncio.iscoroutinefunction(method):
                    asyncio.run(method())
                else:
                    method()
                
                print(f"  ✅ {test_method}")
                passed_tests += 1
                
            except Exception as e:
                print(f"  ❌ {test_method}: {str(e)}")
                failed_tests += 1
    
    print(f"\n📊 Test Results:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! The physics swarm is ready.")
    else:
        print(f"\n⚠️  {failed_tests} tests failed. Please review and fix issues.")


if __name__ == "__main__":
    run_all_tests() 