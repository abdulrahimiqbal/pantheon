"""
Physics Swarm Orchestrator

This module coordinates the entire physics AI agent swarm, managing agent interactions,
task distribution, and result synthesis. It serves as the central coordinator for
complex physics research and analysis tasks.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
from crewai import Crew, Task, Agent
from crewai.process import Process

from ..shared.types import (
    PhysicsQuery, SwarmResponse, AgentResponse, ConfidenceLevel, 
    ComplexityLevel, AgentRole, DataSource
)
from ..shared.config import SwarmConfig, AgentConfig
from ..shared.utils import SwarmLogger, PerformanceMonitor, ResultSynthesizer
from ..agents.specialist_agents import (
    WebCrawlerAgent, PhysicistMasterAgent, TeslaPrinciplesAgent, 
    CuriousQuestionerAgent, SPECIALIST_AGENTS
)


class SwarmOrchestrator:
    """
    Physics Swarm Orchestrator
    
    Coordinates the entire physics AI agent swarm:
    - Manages agent lifecycle and communication
    - Distributes tasks based on query complexity
    - Synthesizes results from multiple agents
    - Ensures quality and consistency
    - Provides comprehensive physics analysis
    """
    
    def __init__(self, config: SwarmConfig):
        self.config = config
        self.logger = SwarmLogger("SwarmOrchestrator")
        self.performance_monitor = PerformanceMonitor()
        self.result_synthesizer = ResultSynthesizer()
        
        # Initialize agents
        self.agents = {}
        self.agent_configs = {}
        self.crew = None
        
        # Orchestration state
        self.active_queries = {}
        self.orchestration_history = []
        self.performance_metrics = {}
        
        # Initialize the swarm
        self._initialize_swarm()
    
    def _initialize_swarm(self):
        """Initialize all agents in the swarm"""
        self.logger.info("Initializing physics swarm...")
        
        try:
            # Create agent configurations
            self._create_agent_configs()
            
            # Initialize specialist agents
            self._initialize_agents()
            
            # Create CrewAI crew
            self._create_crew()
            
            self.logger.info("Physics swarm initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize swarm: {str(e)}")
            raise
    
    def _create_agent_configs(self):
        """Create configurations for each agent"""
        base_config = self.config.agent_config
        
        # Web Crawler Agent config
        self.agent_configs["web_crawler"] = AgentConfig(
            **base_config.dict(),
            agent_name="web_crawler",
            role=AgentRole.RESEARCHER,
            temperature=0.3,  # Low for factual accuracy
            max_tokens=2000,
            tavily_api_key=self.config.tavily_api_key,
            brightdata_api_key=self.config.brightdata_api_key
        )
        
        # Physicist Master Agent config
        self.agent_configs["physicist_master"] = AgentConfig(
            **base_config.dict(),
            agent_name="physicist_master",
            role=AgentRole.ORCHESTRATOR,
            temperature=0.5,  # Balanced for analysis
            max_tokens=3000
        )
        
        # Tesla Principles Agent config
        self.agent_configs["tesla_principles"] = AgentConfig(
            **base_config.dict(),
            agent_name="tesla_principles",
            role=AgentRole.INNOVATOR,
            temperature=0.8,  # High for creativity
            max_tokens=2500
        )
        
        # Curious Questioner Agent config
        self.agent_configs["curious_questioner"] = AgentConfig(
            **base_config.dict(),
            agent_name="curious_questioner",
            role=AgentRole.ANALYST,
            temperature=0.7,  # Balanced for questioning
            max_tokens=2000
        )
    
    def _initialize_agents(self):
        """Initialize all specialist agents"""
        for agent_name, agent_config in self.agent_configs.items():
            try:
                agent_class = SPECIALIST_AGENTS[agent_name]
                agent_instance = agent_class(agent_config)
                self.agents[agent_name] = agent_instance
                self.logger.info(f"Initialized {agent_name} agent")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize {agent_name}: {str(e)}")
                raise
    
    def _create_crew(self):
        """Create CrewAI crew for coordinated execution"""
        # Extract CrewAI agents from our agent instances
        crew_agents = [agent.crew_agent for agent in self.agents.values()]
        
        # Create the crew with hierarchical process
        self.crew = Crew(
            agents=crew_agents,
            process=Process.hierarchical,
            manager_llm=self.agents["physicist_master"].llm,
            verbose=True
        )
        
        self.logger.info("CrewAI crew created with hierarchical process")
    
    async def process_physics_query(self, query: PhysicsQuery) -> SwarmResponse:
        """
        Process a physics query using the entire swarm
        
        Args:
            query: The physics query to process
            
        Returns:
            SwarmResponse with comprehensive analysis
        """
        self.logger.info(f"Processing physics query: {query.question}")
        
        start_time = datetime.now()
        query_id = self._generate_query_id(query)
        
        # Track active query
        self.active_queries[query_id] = {
            "query": query,
            "start_time": start_time,
            "status": "processing"
        }
        
        try:
            # Phase 1: Query Analysis and Planning
            analysis_plan = await self._analyze_and_plan_query(query)
            
            # Phase 2: Agent Task Distribution
            agent_tasks = await self._distribute_tasks(query, analysis_plan)
            
            # Phase 3: Execute Agent Tasks
            agent_responses = await self._execute_agent_tasks(agent_tasks)
            
            # Phase 4: Master Agent Orchestration
            orchestrated_response = await self._orchestrate_with_master(query, agent_responses)
            
            # Phase 5: Result Synthesis and Validation
            final_response = await self._synthesize_and_validate(query, orchestrated_response, agent_responses)
            
            # Update query status
            self.active_queries[query_id]["status"] = "completed"
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Record performance metrics
            self._record_performance_metrics(query, processing_time, final_response)
            
            return final_response
            
        except Exception as e:
            self.logger.error(f"Error processing query {query_id}: {str(e)}")
            self.active_queries[query_id]["status"] = "failed"
            
            # Return error response
            return SwarmResponse(
                query=query,
                master_response=AgentResponse(
                    agent_name="Swarm Orchestrator",
                    content=f"Error processing query: {str(e)}",
                    confidence=ConfidenceLevel.LOW,
                    sources=[],
                    metadata={"error": str(e)},
                    timestamp=datetime.now()
                ),
                agent_responses={},
                synthesis={},
                confidence=ConfidenceLevel.LOW,
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now()
            )
    
    async def _analyze_and_plan_query(self, query: PhysicsQuery) -> Dict[str, Any]:
        """Analyze query and create execution plan"""
        self.logger.info("Analyzing query and creating execution plan")
        
        plan = {
            "query_type": self._classify_query_type(query),
            "complexity_assessment": self._assess_query_complexity(query),
            "required_agents": self._determine_required_agents(query),
            "execution_strategy": self._determine_execution_strategy(query),
            "success_criteria": self._define_success_criteria(query)
        }
        
        return plan
    
    def _classify_query_type(self, query: PhysicsQuery) -> str:
        """Classify the type of physics query"""
        question_lower = query.question.lower()
        
        if any(word in question_lower for word in ["what is", "define", "explain"]):
            return "explanation"
        elif any(word in question_lower for word in ["how", "mechanism", "process"]):
            return "mechanism"
        elif any(word in question_lower for word in ["why", "reason", "cause"]):
            return "causation"
        elif any(word in question_lower for word in ["calculate", "solve", "find", "compute"]):
            return "calculation"
        elif any(word in question_lower for word in ["hypothesis", "theory", "propose", "novel"]):
            return "hypothesis_generation"
        elif any(word in question_lower for word in ["research", "latest", "current", "recent"]):
            return "research"
        else:
            return "general_inquiry"
    
    def _assess_query_complexity(self, query: PhysicsQuery) -> Dict[str, Any]:
        """Assess the complexity of the query"""
        complexity = {
            "level": query.complexity_level,
            "factors": [],
            "estimated_processing_time": 0,
            "resource_requirements": []
        }
        
        question_lower = query.question.lower()
        
        # Complexity factors
        if any(term in question_lower for term in ["quantum", "relativistic", "field theory"]):
            complexity["factors"].append("advanced_physics")
            complexity["estimated_processing_time"] += 30
        
        if any(term in question_lower for term in ["interdisciplinary", "multiple", "complex"]):
            complexity["factors"].append("interdisciplinary")
            complexity["estimated_processing_time"] += 20
        
        if any(term in question_lower for term in ["novel", "breakthrough", "innovative"]):
            complexity["factors"].append("innovative_thinking")
            complexity["estimated_processing_time"] += 25
        
        # Base processing time
        complexity["estimated_processing_time"] += 15
        
        return complexity
    
    def _determine_required_agents(self, query: PhysicsQuery) -> List[str]:
        """Determine which agents are required for the query"""
        required_agents = ["physicist_master"]  # Master is always required
        
        question_lower = query.question.lower()
        
        # Web Crawler for research queries
        if any(word in question_lower for word in ["research", "latest", "current", "study", "evidence"]):
            required_agents.append("web_crawler")
        
        # Tesla Principles for innovation queries
        if any(word in question_lower for word in ["novel", "innovative", "breakthrough", "first principles"]):
            required_agents.append("tesla_principles")
        
        # Curious Questioner for complex analysis
        if query.complexity_level in [ComplexityLevel.ADVANCED, ComplexityLevel.RESEARCH]:
            required_agents.append("curious_questioner")
        
        # Default: include all agents for comprehensive analysis
        if len(required_agents) == 1:
            required_agents.extend(["web_crawler", "tesla_principles", "curious_questioner"])
        
        return required_agents
    
    def _determine_execution_strategy(self, query: PhysicsQuery) -> str:
        """Determine the execution strategy"""
        if query.complexity_level == ComplexityLevel.BASIC:
            return "sequential_simple"
        elif query.complexity_level == ComplexityLevel.INTERMEDIATE:
            return "parallel_moderate"
        elif query.complexity_level == ComplexityLevel.ADVANCED:
            return "hierarchical_complex"
        else:  # RESEARCH
            return "full_orchestration"
    
    def _define_success_criteria(self, query: PhysicsQuery) -> Dict[str, Any]:
        """Define success criteria for the query"""
        criteria = {
            "minimum_confidence": ConfidenceLevel.MEDIUM,
            "minimum_sources": 3,
            "required_perspectives": 2,
            "coherence_threshold": 0.7,
            "completeness_threshold": 0.8
        }
        
        # Adjust based on complexity
        if query.complexity_level == ComplexityLevel.RESEARCH:
            criteria["minimum_sources"] = 5
            criteria["required_perspectives"] = 3
        
        return criteria
    
    async def _distribute_tasks(self, query: PhysicsQuery, plan: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Distribute tasks to required agents"""
        self.logger.info("Distributing tasks to agents")
        
        required_agents = plan["required_agents"]
        tasks = {}
        
        for agent_name in required_agents:
            if agent_name == "physicist_master":
                tasks[agent_name] = {
                    "type": "orchestration",
                    "query": query,
                    "context": plan,
                    "priority": 1
                }
            elif agent_name == "web_crawler":
                tasks[agent_name] = {
                    "type": "research",
                    "query": query,
                    "context": {"focus": "academic_sources"},
                    "priority": 2
                }
            elif agent_name == "tesla_principles":
                tasks[agent_name] = {
                    "type": "innovation",
                    "query": query,
                    "context": {"approach": "first_principles"},
                    "priority": 3
                }
            elif agent_name == "curious_questioner":
                tasks[agent_name] = {
                    "type": "analysis",
                    "query": query,
                    "context": {"depth": "critical_inquiry"},
                    "priority": 4
                }
        
        return tasks
    
    async def _execute_agent_tasks(self, tasks: Dict[str, Dict[str, Any]]) -> Dict[str, AgentResponse]:
        """Execute tasks across all agents"""
        self.logger.info(f"Executing tasks for {len(tasks)} agents")
        
        responses = {}
        
        # Execute tasks based on strategy
        strategy = tasks.get("physicist_master", {}).get("context", {}).get("execution_strategy", "parallel_moderate")
        
        if strategy == "sequential_simple":
            responses = await self._execute_sequential(tasks)
        elif strategy == "parallel_moderate":
            responses = await self._execute_parallel(tasks)
        elif strategy == "hierarchical_complex":
            responses = await self._execute_hierarchical(tasks)
        else:  # full_orchestration
            responses = await self._execute_full_orchestration(tasks)
        
        return responses
    
    async def _execute_sequential(self, tasks: Dict[str, Dict[str, Any]]) -> Dict[str, AgentResponse]:
        """Execute tasks sequentially"""
        responses = {}
        
        # Sort by priority
        sorted_tasks = sorted(tasks.items(), key=lambda x: x[1]["priority"])
        
        for agent_name, task in sorted_tasks:
            if agent_name in self.agents:
                try:
                    response = await self.agents[agent_name].process_query(task["query"])
                    responses[agent_name] = response
                except Exception as e:
                    self.logger.error(f"Error executing task for {agent_name}: {str(e)}")
        
        return responses
    
    async def _execute_parallel(self, tasks: Dict[str, Dict[str, Any]]) -> Dict[str, AgentResponse]:
        """Execute tasks in parallel"""
        responses = {}
        
        # Create tasks for parallel execution
        async_tasks = []
        agent_names = []
        
        for agent_name, task in tasks.items():
            if agent_name in self.agents and agent_name != "physicist_master":
                async_tasks.append(self.agents[agent_name].process_query(task["query"]))
                agent_names.append(agent_name)
        
        # Execute in parallel
        if async_tasks:
            try:
                results = await asyncio.gather(*async_tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Error in parallel execution for {agent_names[i]}: {str(result)}")
                    else:
                        responses[agent_names[i]] = result
                        
            except Exception as e:
                self.logger.error(f"Error in parallel execution: {str(e)}")
        
        # Execute master agent last
        if "physicist_master" in tasks:
            try:
                master_response = await self.agents["physicist_master"].process_query(tasks["physicist_master"]["query"])
                responses["physicist_master"] = master_response
            except Exception as e:
                self.logger.error(f"Error executing master agent: {str(e)}")
        
        return responses
    
    async def _execute_hierarchical(self, tasks: Dict[str, Dict[str, Any]]) -> Dict[str, AgentResponse]:
        """Execute tasks hierarchically with master coordination"""
        responses = {}
        
        # Phase 1: Research agents
        research_agents = ["web_crawler"]
        for agent_name in research_agents:
            if agent_name in tasks and agent_name in self.agents:
                try:
                    response = await self.agents[agent_name].process_query(tasks[agent_name]["query"])
                    responses[agent_name] = response
                except Exception as e:
                    self.logger.error(f"Error in research phase for {agent_name}: {str(e)}")
        
        # Phase 2: Analysis agents (with research context)
        analysis_agents = ["tesla_principles", "curious_questioner"]
        for agent_name in analysis_agents:
            if agent_name in tasks and agent_name in self.agents:
                try:
                    # Pass research context to analysis agents
                    task_with_context = tasks[agent_name].copy()
                    task_with_context["context"]["research_results"] = responses.get("web_crawler")
                    
                    response = await self.agents[agent_name].process_query(task_with_context["query"])
                    responses[agent_name] = response
                except Exception as e:
                    self.logger.error(f"Error in analysis phase for {agent_name}: {str(e)}")
        
        # Phase 3: Master orchestration
        if "physicist_master" in tasks:
            try:
                master_response = await self.agents["physicist_master"].orchestrate_swarm(
                    tasks["physicist_master"]["query"], 
                    self.agents
                )
                responses["physicist_master"] = master_response.master_response
            except Exception as e:
                self.logger.error(f"Error in master orchestration: {str(e)}")
        
        return responses
    
    async def _execute_full_orchestration(self, tasks: Dict[str, Dict[str, Any]]) -> Dict[str, AgentResponse]:
        """Execute full orchestration using CrewAI"""
        responses = {}
        
        try:
            # Create CrewAI tasks
            crew_tasks = []
            
            for agent_name, task in tasks.items():
                if agent_name in self.agents:
                    crew_task = Task(
                        description=f"Process physics query: {task['query'].question}",
                        agent=self.agents[agent_name].crew_agent,
                        expected_output="Comprehensive physics analysis"
                    )
                    crew_tasks.append(crew_task)
            
            # Execute crew
            if crew_tasks:
                self.crew.tasks = crew_tasks
                crew_results = self.crew.kickoff()
                
                # Process crew results
                for i, result in enumerate(crew_results):
                    agent_name = list(tasks.keys())[i]
                    
                    # Convert crew result to AgentResponse
                    responses[agent_name] = AgentResponse(
                        agent_name=agent_name,
                        content=str(result),
                        confidence=ConfidenceLevel.MEDIUM,
                        sources=[],
                        metadata={"crew_execution": True},
                        timestamp=datetime.now()
                    )
                    
        except Exception as e:
            self.logger.error(f"Error in full orchestration: {str(e)}")
            # Fallback to hierarchical execution
            responses = await self._execute_hierarchical(tasks)
        
        return responses
    
    async def _orchestrate_with_master(self, query: PhysicsQuery, agent_responses: Dict[str, AgentResponse]) -> SwarmResponse:
        """Let master agent orchestrate the final response"""
        self.logger.info("Master agent orchestrating final response")
        
        try:
            # Use master agent to orchestrate
            master_agent = self.agents["physicist_master"]
            swarm_response = await master_agent.orchestrate_swarm(query, self.agents)
            
            return swarm_response
            
        except Exception as e:
            self.logger.error(f"Error in master orchestration: {str(e)}")
            
            # Fallback: create basic orchestration
            return SwarmResponse(
                query=query,
                master_response=AgentResponse(
                    agent_name="Physicist Master Agent",
                    content="Master orchestration failed, providing basic synthesis",
                    confidence=ConfidenceLevel.LOW,
                    sources=[],
                    metadata={"orchestration_error": str(e)},
                    timestamp=datetime.now()
                ),
                agent_responses=agent_responses,
                synthesis={},
                confidence=ConfidenceLevel.LOW,
                processing_time=0,
                timestamp=datetime.now()
            )
    
    async def _synthesize_and_validate(self, query: PhysicsQuery, orchestrated_response: SwarmResponse, 
                                     agent_responses: Dict[str, AgentResponse]) -> SwarmResponse:
        """Synthesize and validate the final response"""
        self.logger.info("Synthesizing and validating final response")
        
        try:
            # Use result synthesizer
            synthesis = self.result_synthesizer.synthesize_responses(
                query, orchestrated_response, agent_responses
            )
            
            # Validate response quality
            validation = self._validate_response_quality(orchestrated_response, synthesis)
            
            # Create final response
            final_response = SwarmResponse(
                query=query,
                master_response=orchestrated_response.master_response,
                agent_responses=agent_responses,
                synthesis=synthesis,
                confidence=validation["confidence"],
                processing_time=orchestrated_response.processing_time,
                timestamp=datetime.now()
            )
            
            return final_response
            
        except Exception as e:
            self.logger.error(f"Error in synthesis and validation: {str(e)}")
            return orchestrated_response
    
    def _validate_response_quality(self, response: SwarmResponse, synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of the response"""
        validation = {
            "confidence": ConfidenceLevel.MEDIUM,
            "quality_score": 0.7,
            "issues": [],
            "strengths": []
        }
        
        # Check agent participation
        if len(response.agent_responses) >= 3:
            validation["strengths"].append("Multiple agent perspectives")
        else:
            validation["issues"].append("Limited agent participation")
        
        # Check source quality
        all_sources = []
        for agent_response in response.agent_responses.values():
            all_sources.extend(agent_response.sources)
        
        if len(all_sources) >= 3:
            validation["strengths"].append("Adequate source coverage")
        else:
            validation["issues"].append("Limited source coverage")
        
        # Adjust confidence based on validation
        if len(validation["issues"]) > len(validation["strengths"]):
            validation["confidence"] = ConfidenceLevel.LOW
        elif len(validation["strengths"]) > len(validation["issues"]):
            validation["confidence"] = ConfidenceLevel.HIGH
        
        return validation
    
    def _generate_query_id(self, query: PhysicsQuery) -> str:
        """Generate unique ID for query"""
        import hashlib
        query_str = f"{query.question}_{datetime.now().isoformat()}"
        return hashlib.md5(query_str.encode()).hexdigest()[:8]
    
    def _record_performance_metrics(self, query: PhysicsQuery, processing_time: float, response: SwarmResponse):
        """Record performance metrics"""
        metrics = {
            "query_complexity": query.complexity_level.value,
            "processing_time": processing_time,
            "agents_used": len(response.agent_responses),
            "sources_found": sum(len(r.sources) for r in response.agent_responses.values()),
            "confidence_level": response.confidence.value,
            "timestamp": datetime.now().isoformat()
        }
        
        self.performance_metrics[self._generate_query_id(query)] = metrics
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get current swarm status"""
        return {
            "agents": {
                name: {
                    "status": "active",
                    "class": agent.__class__.__name__,
                    "config": agent.config.agent_name
                }
                for name, agent in self.agents.items()
            },
            "active_queries": len(self.active_queries),
            "total_queries_processed": len(self.orchestration_history),
            "average_processing_time": self._calculate_average_processing_time(),
            "performance_metrics": self.performance_metrics
        }
    
    def _calculate_average_processing_time(self) -> float:
        """Calculate average processing time"""
        if not self.performance_metrics:
            return 0.0
        
        times = [metrics["processing_time"] for metrics in self.performance_metrics.values()]
        return sum(times) / len(times)
    
    async def shutdown(self):
        """Shutdown the swarm gracefully"""
        self.logger.info("Shutting down physics swarm...")
        
        # Cancel active queries
        for query_id in self.active_queries:
            self.active_queries[query_id]["status"] = "cancelled"
        
        # Clean up agents
        for agent in self.agents.values():
            if hasattr(agent, 'cleanup'):
                await agent.cleanup()
        
        self.logger.info("Physics swarm shutdown complete")


class SwarmManager:
    """
    High-level manager for the physics swarm
    
    Provides a simplified interface for interacting with the swarm
    """
    
    def __init__(self, config: SwarmConfig):
        self.orchestrator = SwarmOrchestrator(config)
        self.logger = SwarmLogger("SwarmManager")
    
    async def ask_physics_question(self, question: str, context: str = "", 
                                 complexity: ComplexityLevel = ComplexityLevel.INTERMEDIATE) -> SwarmResponse:
        """
        Ask a physics question to the swarm
        
        Args:
            question: The physics question
            context: Additional context for the question
            complexity: Complexity level of the question
            
        Returns:
            SwarmResponse with comprehensive analysis
        """
        query = PhysicsQuery(
            question=question,
            context=context,
            complexity_level=complexity,
            timestamp=datetime.now()
        )
        
        return await self.orchestrator.process_physics_query(query)
    
    def get_status(self) -> Dict[str, Any]:
        """Get swarm status"""
        return self.orchestrator.get_swarm_status()
    
    async def shutdown(self):
        """Shutdown the swarm"""
        await self.orchestrator.shutdown() 