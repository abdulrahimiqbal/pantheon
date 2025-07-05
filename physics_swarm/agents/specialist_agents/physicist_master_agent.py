"""
Physicist Master Agent - Orchestrator and Subject Matter Expert

This agent serves as the master orchestrator for the physics swarm, coordinating
other agents and providing deep physics expertise. It manages the overall research
process and synthesizes findings from all agents.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ...shared.types import (
    DataSource, SourceType, ConfidenceLevel, AgentResponse, 
    PhysicsQuery, ComplexityLevel, AgentRole, SwarmResponse
)
from ...shared.config import AgentConfig
from ...shared.utils import (
    TextProcessor, ConfidenceCalculator, DataFormatter,
    PhysicsAnalyzer, ConceptMapper
)
from ..base_agent import BasePhysicsAgent


class PhysicsKnowledgeBase(BaseTool):
    """Tool for accessing physics knowledge and principles"""
    
    name: str = "physics_knowledge"
    description: str = "Access comprehensive physics knowledge base for analysis and validation"
    knowledge_domains: Dict[str, Any] = {}
    
    def __init__(self):
        super().__init__()
        self.knowledge_domains = {
            "classical_mechanics": {
                "concepts": ["Newton's laws", "energy", "momentum", "oscillations", "gravitation"],
                "equations": ["F=ma", "E=mc²", "p=mv", "F=GMm/r²"],
                "applications": ["projectile motion", "orbital mechanics", "collisions"]
            },
            "quantum_mechanics": {
                "concepts": ["wave-particle duality", "uncertainty principle", "superposition", "entanglement"],
                "equations": ["Schrödinger equation", "Heisenberg uncertainty", "de Broglie wavelength"],
                "applications": ["quantum computing", "atomic structure", "spectroscopy"]
            },
            "thermodynamics": {
                "concepts": ["entropy", "temperature", "heat", "work", "phase transitions"],
                "equations": ["PV=nRT", "ΔS≥0", "dU=δQ-δW"],
                "applications": ["engines", "refrigeration", "statistical mechanics"]
            },
            "electromagnetism": {
                "concepts": ["electric field", "magnetic field", "electromagnetic waves", "induction"],
                "equations": ["Maxwell equations", "Coulomb's law", "Faraday's law"],
                "applications": ["electronics", "optics", "telecommunications"]
            },
            "relativity": {
                "concepts": ["spacetime", "time dilation", "length contraction", "mass-energy equivalence"],
                "equations": ["E=mc²", "Lorentz transformations", "Einstein field equations"],
                "applications": ["GPS", "particle accelerators", "cosmology"]
            },
            "particle_physics": {
                "concepts": ["quarks", "leptons", "bosons", "standard model", "symmetries"],
                "equations": ["Dirac equation", "Yang-Mills theory", "QCD Lagrangian"],
                "applications": ["particle accelerators", "detector physics", "cosmology"]
            },
            "astrophysics": {
                "concepts": ["stellar evolution", "galaxies", "dark matter", "dark energy", "cosmology"],
                "equations": ["Friedmann equations", "Schwarzschild metric", "Chandrasekhar limit"],
                "applications": ["space missions", "observational astronomy", "cosmological models"]
            }
        }
    
    def _run(self, domain: str, concept: str = None) -> Dict[str, Any]:
        """Retrieve physics knowledge for a specific domain and concept"""
        if domain not in self.knowledge_domains:
            return {"error": f"Domain '{domain}' not found in knowledge base"}
        
        domain_knowledge = self.knowledge_domains[domain]
        
        if concept:
            # Search for specific concept
            for category, items in domain_knowledge.items():
                if concept.lower() in [item.lower() for item in items]:
                    return {
                        "domain": domain,
                        "concept": concept,
                        "category": category,
                        "related_items": items,
                        "full_domain": domain_knowledge
                    }
            return {"error": f"Concept '{concept}' not found in domain '{domain}'"}
        
        return {
            "domain": domain,
            "knowledge": domain_knowledge
        }


class PhysicsAnalysisTool(BaseTool):
    """Tool for deep physics analysis and concept mapping"""
    
    name: str = "physics_analysis"
    description: str = "Perform deep physics analysis, concept mapping, and theoretical validation"
    analyzer: Optional[Any] = None
    concept_mapper: Optional[Any] = None
    
    def __init__(self):
        super().__init__()
        # For now, these are placeholder objects
        # In a real implementation, these would be sophisticated NLP/ML models
        self.analyzer = "PhysicsAnalyzer"  # Placeholder
        self.concept_mapper = "ConceptMapper"  # Placeholder
    
    def _run(self, query: str, sources: List[Dict] = None, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Perform physics analysis"""
        analysis_results = {
            "query": query,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Identify physics domains
        domains = self._identify_physics_domains(query)
        analysis_results["domains"] = domains
        
        # Concept mapping
        concepts = self._map_concepts(query, domains)
        analysis_results["concepts"] = concepts
        
        # Theoretical framework
        framework = self._identify_theoretical_framework(query, concepts)
        analysis_results["theoretical_framework"] = framework
        
        # Complexity assessment
        complexity = self._assess_complexity(query, concepts, framework)
        analysis_results["complexity_assessment"] = complexity
        
        return analysis_results
    
    def _identify_physics_domains(self, query: str) -> List[str]:
        """Identify relevant physics domains from query"""
        query_lower = query.lower()
        domains = []
        
        domain_keywords = {
            "classical_mechanics": ["force", "motion", "velocity", "acceleration", "momentum", "energy", "newton"],
            "quantum_mechanics": ["quantum", "wave", "particle", "uncertainty", "superposition", "entanglement"],
            "thermodynamics": ["heat", "temperature", "entropy", "thermal", "gas", "pressure"],
            "electromagnetism": ["electric", "magnetic", "electromagnetic", "field", "charge", "current"],
            "relativity": ["relativity", "spacetime", "einstein", "lorentz", "time dilation"],
            "particle_physics": ["particle", "quark", "lepton", "boson", "standard model", "higgs"],
            "astrophysics": ["star", "galaxy", "universe", "cosmic", "black hole", "dark matter"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                domains.append(domain)
        
        return domains if domains else ["general_physics"]
    
    def _map_concepts(self, query: str, domains: List[str]) -> List[str]:
        """Map key physics concepts in the query"""
        # This would use more sophisticated NLP in a real implementation
        query_lower = query.lower()
        concepts = []
        
        # Basic concept extraction
        concept_patterns = [
            "law", "principle", "theory", "equation", "force", "energy", "field",
            "wave", "particle", "momentum", "acceleration", "velocity", "mass"
        ]
        
        for pattern in concept_patterns:
            if pattern in query_lower:
                concepts.append(pattern)
        
        return concepts
    
    def _identify_theoretical_framework(self, query: str, concepts: List[str]) -> str:
        """Identify the theoretical framework needed"""
        if any(concept in ["quantum", "wave", "particle"] for concept in concepts):
            return "quantum_mechanics"
        elif any(concept in ["relativity", "spacetime"] for concept in concepts):
            return "relativity"
        elif any(concept in ["force", "motion", "newton"] for concept in concepts):
            return "classical_mechanics"
        else:
            return "general_physics"
    
    def _assess_complexity(self, query: str, concepts: List[str], framework: str) -> Dict[str, Any]:
        """Assess the complexity of the physics query"""
        complexity_indicators = {
            "mathematical_complexity": len([c for c in concepts if c in ["equation", "integral", "derivative"]]),
            "conceptual_depth": len(concepts),
            "theoretical_framework": framework,
            "interdisciplinary": len(self._identify_physics_domains(query)) > 1
        }
        
        # Calculate overall complexity score
        score = (
            complexity_indicators["mathematical_complexity"] * 0.3 +
            complexity_indicators["conceptual_depth"] * 0.3 +
            (1 if complexity_indicators["interdisciplinary"] else 0) * 0.4
        )
        
        if score >= 2.0:
            level = "advanced"
        elif score >= 1.0:
            level = "intermediate"
        else:
            level = "basic"
        
        complexity_indicators["overall_score"] = score
        complexity_indicators["level"] = level
        
        return complexity_indicators


class PhysicistMasterAgent(BasePhysicsAgent):
    """
    Physicist Master Agent - Orchestrator and Subject Matter Expert
    
    Responsibilities:
    - Coordinate all other agents in the swarm
    - Provide deep physics expertise and validation
    - Synthesize findings from multiple agents
    - Ensure scientific accuracy and coherence
    - Manage the overall research process
    """
    
    def __init__(self, config: AgentConfig):
        # Initialize tools BEFORE calling super().__init__
        self.knowledge_base = PhysicsKnowledgeBase()
        self.analysis_tool = PhysicsAnalysisTool()
        
        # Initialize utilities
        self.text_processor = TextProcessor()
        self.confidence_calculator = ConfidenceCalculator()
        self.data_formatter = DataFormatter()
        
        # Now call super().__init__ which will call _get_tools()
        super().__init__(config)
        
        # Agent-specific configuration
        self.agent_config = {
            "role": "Physics Master Orchestrator",
            "goal": "Coordinate physics research and provide expert analysis",
            "backstory": """You are a distinguished physics professor with decades of 
            experience in theoretical and experimental physics. You have published 
            extensively in quantum mechanics, relativity, and particle physics. 
            You excel at coordinating research teams, validating scientific claims, 
            and synthesizing complex physics concepts for different audiences.""",
            "temperature": 0.5,  # Balanced for analysis and creativity
            "max_iterations": 5,
            "validation_threshold": 0.8
        }
        
        # Track agent coordination
        self.agent_responses = {}
        self.coordination_history = []
    
    async def orchestrate_swarm(self, query: PhysicsQuery, agent_pool: Dict[str, Any]) -> SwarmResponse:
        """Orchestrate the entire physics swarm to answer a query"""
        self.logger.info(f"Orchestrating swarm for query: {query.question}")
        
        start_time = datetime.now()
        
        # Phase 1: Initial Analysis
        initial_analysis = await self._perform_initial_analysis(query)
        
        # Phase 2: Coordinate Agent Tasks
        agent_tasks = self._plan_agent_tasks(query, initial_analysis)
        
        # Phase 3: Execute Agent Tasks
        agent_responses = await self._execute_agent_tasks(agent_tasks, agent_pool)
        
        # Phase 4: Synthesize Results
        synthesis = await self._synthesize_results(query, agent_responses, initial_analysis)
        
        # Phase 5: Validation and Quality Control
        final_response = await self._validate_and_finalize(query, synthesis)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return SwarmResponse(
            query=query,
            master_response=final_response,
            agent_responses=agent_responses,
            synthesis=synthesis,
            confidence=self._calculate_swarm_confidence(agent_responses),
            processing_time=processing_time,
            timestamp=datetime.now()
        )
    
    async def _perform_initial_analysis(self, query: PhysicsQuery) -> Dict[str, Any]:
        """Perform initial analysis of the physics query"""
        self.logger.info("Performing initial physics analysis")
        
        # Use physics analysis tool
        analysis = self.analysis_tool._run(query.question, analysis_type="initial")
        
        # Enhance with knowledge base
        domains = analysis.get("domains", [])
        knowledge_context = {}
        
        for domain in domains:
            domain_knowledge = self.knowledge_base._run(domain)
            if "error" not in domain_knowledge:
                knowledge_context[domain] = domain_knowledge
        
        analysis["knowledge_context"] = knowledge_context
        analysis["query_classification"] = self._classify_query(query)
        
        return analysis
    
    def _classify_query(self, query: PhysicsQuery) -> Dict[str, Any]:
        """Classify the physics query for appropriate handling"""
        classification = {
            "type": "unknown",
            "complexity": query.complexity_level,
            "requires_calculation": False,
            "requires_research": False,
            "requires_creativity": False,
            "requires_validation": True
        }
        
        query_lower = query.question.lower()
        
        # Determine query type
        if any(word in query_lower for word in ["what is", "define", "explain"]):
            classification["type"] = "explanation"
        elif any(word in query_lower for word in ["how", "why", "mechanism"]):
            classification["type"] = "mechanism"
        elif any(word in query_lower for word in ["calculate", "solve", "find"]):
            classification["type"] = "calculation"
            classification["requires_calculation"] = True
        elif any(word in query_lower for word in ["hypothesis", "theory", "propose"]):
            classification["type"] = "hypothesis"
            classification["requires_creativity"] = True
        elif any(word in query_lower for word in ["research", "latest", "current"]):
            classification["type"] = "research"
            classification["requires_research"] = True
        
        return classification
    
    def _plan_agent_tasks(self, query: PhysicsQuery, analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Plan tasks for each agent based on query analysis"""
        self.logger.info("Planning agent tasks")
        
        query_classification = analysis.get("query_classification", {})
        
        tasks = {}
        
        # Web Crawler Agent - Always needed for research
        tasks["web_crawler"] = {
            "priority": 1,
            "task_type": "research",
            "instructions": f"Search for high-quality physics sources related to: {query.question}",
            "expected_output": "List of validated physics sources with credibility scores"
        }
        
        # Tesla Principles Agent - For creative/hypothesis queries
        if query_classification.get("requires_creativity") or query_classification.get("type") == "hypothesis":
            tasks["tesla_principles"] = {
                "priority": 2,
                "task_type": "innovation",
                "instructions": f"Apply first-principles thinking to: {query.question}",
                "expected_output": "Novel insights and first-principles analysis"
            }
        
        # Curious Questioner Agent - For deep analysis
        if query.complexity_level in [ComplexityLevel.ADVANCED, ComplexityLevel.RESEARCH]:
            tasks["curious_questioner"] = {
                "priority": 3,
                "task_type": "analysis",
                "instructions": f"Generate probing questions about: {query.question}",
                "expected_output": "List of insightful questions to deepen understanding"
            }
        
        return tasks
    
    async def _execute_agent_tasks(self, tasks: Dict[str, Dict[str, Any]], agent_pool: Dict[str, Any]) -> Dict[str, AgentResponse]:
        """Execute tasks across the agent pool"""
        self.logger.info(f"Executing tasks for {len(tasks)} agents")
        
        responses = {}
        
        # Execute tasks in priority order
        sorted_tasks = sorted(tasks.items(), key=lambda x: x[1]["priority"])
        
        for agent_name, task_config in sorted_tasks:
            if agent_name in agent_pool:
                agent = agent_pool[agent_name]
                
                try:
                    # Execute agent task
                    response = await agent.process_query(task_config.get("query", None))
                    responses[agent_name] = response
                    
                    # Log coordination
                    self.coordination_history.append({
                        "agent": agent_name,
                        "task": task_config["task_type"],
                        "timestamp": datetime.now(),
                        "success": True
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error executing task for {agent_name}: {str(e)}")
                    
                    # Create error response
                    responses[agent_name] = AgentResponse(
                        agent_name=agent_name,
                        content=f"Error processing task: {str(e)}",
                        confidence=ConfidenceLevel.LOW,
                        sources=[],
                        metadata={"error": str(e)},
                        timestamp=datetime.now()
                    )
                    
                    # Log coordination failure
                    self.coordination_history.append({
                        "agent": agent_name,
                        "task": task_config["task_type"],
                        "timestamp": datetime.now(),
                        "success": False,
                        "error": str(e)
                    })
        
        return responses
    
    async def _synthesize_results(self, query: PhysicsQuery, agent_responses: Dict[str, AgentResponse], 
                                 initial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from all agents"""
        self.logger.info("Synthesizing agent responses")
        
        synthesis = {
            "query": query.question,
            "analysis": initial_analysis,
            "agent_contributions": {},
            "unified_sources": [],
            "confidence_assessment": {},
            "key_insights": [],
            "contradictions": [],
            "gaps": []
        }
        
        # Process each agent response
        all_sources = []
        for agent_name, response in agent_responses.items():
            synthesis["agent_contributions"][agent_name] = {
                "content": response.content,
                "confidence": response.confidence,
                "sources_count": len(response.sources),
                "key_points": self._extract_key_points(response.content)
            }
            
            all_sources.extend(response.sources)
        
        # Unify and deduplicate sources
        synthesis["unified_sources"] = self._unify_sources(all_sources)
        
        # Identify key insights
        synthesis["key_insights"] = self._identify_key_insights(agent_responses)
        
        # Check for contradictions
        synthesis["contradictions"] = self._identify_contradictions(agent_responses)
        
        # Identify knowledge gaps
        synthesis["gaps"] = self._identify_knowledge_gaps(query, agent_responses)
        
        return synthesis
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from agent response content"""
        # Simple implementation - would use more sophisticated NLP in practice
        sentences = content.split('.')
        key_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(keyword in sentence.lower() for keyword in 
                                        ["important", "key", "significant", "crucial", "fundamental"]):
                key_points.append(sentence)
        
        return key_points[:5]  # Top 5 key points
    
    def _unify_sources(self, sources: List[DataSource]) -> List[DataSource]:
        """Unify and deduplicate sources from multiple agents"""
        unified = {}
        
        for source in sources:
            # Use URL as unique identifier
            if source.url not in unified:
                unified[source.url] = source
            else:
                # Merge metadata if same source found multiple times
                existing = unified[source.url]
                if source.credibility_score > existing.credibility_score:
                    unified[source.url] = source
        
        # Sort by credibility score
        return sorted(unified.values(), key=lambda x: x.credibility_score, reverse=True)
    
    def _identify_key_insights(self, agent_responses: Dict[str, AgentResponse]) -> List[str]:
        """Identify key insights across all agent responses"""
        insights = []
        
        for agent_name, response in agent_responses.items():
            # Extract insights based on agent type
            if agent_name == "tesla_principles":
                insights.extend(self._extract_innovative_insights(response.content))
            elif agent_name == "curious_questioner":
                insights.extend(self._extract_analytical_insights(response.content))
            elif agent_name == "web_crawler":
                insights.extend(self._extract_research_insights(response.content))
        
        return insights
    
    def _extract_innovative_insights(self, content: str) -> List[str]:
        """Extract innovative insights from Tesla Principles agent"""
        # Look for creative or novel ideas
        insights = []
        sentences = content.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in 
                  ["novel", "innovative", "breakthrough", "paradigm", "revolutionary"]):
                insights.append(sentence.strip())
        
        return insights
    
    def _extract_analytical_insights(self, content: str) -> List[str]:
        """Extract analytical insights from Curious Questioner agent"""
        # Look for deep questions and analysis
        insights = []
        sentences = content.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in 
                  ["question", "analysis", "implication", "consequence", "deeper"]):
                insights.append(sentence.strip())
        
        return insights
    
    def _extract_research_insights(self, content: str) -> List[str]:
        """Extract research insights from Web Crawler agent"""
        # Look for research findings and source-based insights
        insights = []
        sentences = content.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in 
                  ["research", "study", "findings", "evidence", "data"]):
                insights.append(sentence.strip())
        
        return insights
    
    def _identify_contradictions(self, agent_responses: Dict[str, AgentResponse]) -> List[str]:
        """Identify contradictions between agent responses"""
        # Simple implementation - would use more sophisticated analysis in practice
        contradictions = []
        
        # Compare responses for conflicting information
        response_contents = [response.content.lower() for response in agent_responses.values()]
        
        # Look for contradictory statements (basic implementation)
        contradiction_pairs = [
            ("true", "false"),
            ("correct", "incorrect"),
            ("possible", "impossible"),
            ("proven", "unproven")
        ]
        
        for pair in contradiction_pairs:
            if any(pair[0] in content for content in response_contents) and \
               any(pair[1] in content for content in response_contents):
                contradictions.append(f"Potential contradiction found regarding {pair[0]}/{pair[1]}")
        
        return contradictions
    
    def _identify_knowledge_gaps(self, query: PhysicsQuery, agent_responses: Dict[str, AgentResponse]) -> List[str]:
        """Identify knowledge gaps in the collective response"""
        gaps = []
        
        # Check if all expected aspects were covered
        query_lower = query.question.lower()
        
        expected_aspects = []
        if "how" in query_lower:
            expected_aspects.append("mechanism")
        if "why" in query_lower:
            expected_aspects.append("causation")
        if "what" in query_lower:
            expected_aspects.append("definition")
        
        # Check if aspects were covered
        all_content = " ".join([response.content.lower() for response in agent_responses.values()])
        
        for aspect in expected_aspects:
            if aspect not in all_content:
                gaps.append(f"Missing {aspect} explanation")
        
        return gaps
    
    async def _validate_and_finalize(self, query: PhysicsQuery, synthesis: Dict[str, Any]) -> AgentResponse:
        """Validate synthesis and create final response"""
        self.logger.info("Validating and finalizing response")
        
        # Calculate overall confidence
        confidence = self._calculate_synthesis_confidence(synthesis)
        
        # Create comprehensive response
        final_content = self._create_final_response(query, synthesis)
        
        return AgentResponse(
            agent_name="Physicist Master Agent",
            content=final_content,
            confidence=confidence,
            sources=synthesis["unified_sources"],
            metadata={
                "synthesis": synthesis,
                "coordination_history": self.coordination_history,
                "agents_involved": list(synthesis["agent_contributions"].keys()),
                "total_sources": len(synthesis["unified_sources"]),
                "insights_count": len(synthesis["key_insights"]),
                "contradictions_count": len(synthesis["contradictions"]),
                "gaps_count": len(synthesis["gaps"])
            },
            timestamp=datetime.now()
        )
    
    def _calculate_synthesis_confidence(self, synthesis: Dict[str, Any]) -> ConfidenceLevel:
        """Calculate confidence level for the synthesis"""
        factors = {
            "source_quality": 0.3,
            "agent_agreement": 0.3,
            "knowledge_coverage": 0.2,
            "contradiction_penalty": 0.2
        }
        
        # Source quality score
        sources = synthesis["unified_sources"]
        source_score = sum(source.credibility_score for source in sources) / len(sources) if sources else 0
        
        # Agent agreement score (simplified)
        agent_confidences = [
            contrib["confidence"] for contrib in synthesis["agent_contributions"].values()
        ]
        agreement_score = len([c for c in agent_confidences if c in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]]) / len(agent_confidences) if agent_confidences else 0
        
        # Knowledge coverage score
        coverage_score = 1.0 - (len(synthesis["gaps"]) * 0.2)  # Penalty for gaps
        
        # Contradiction penalty
        contradiction_penalty = len(synthesis["contradictions"]) * 0.1
        
        # Calculate weighted score
        total_score = (
            source_score * factors["source_quality"] +
            agreement_score * factors["agent_agreement"] +
            coverage_score * factors["knowledge_coverage"] -
            contradiction_penalty * factors["contradiction_penalty"]
        )
        
        if total_score >= 0.8:
            return ConfidenceLevel.HIGH
        elif total_score >= 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _create_final_response(self, query: PhysicsQuery, synthesis: Dict[str, Any]) -> str:
        """Create the final comprehensive response"""
        response = f"# Physics Analysis: {query.question}\n\n"
        
        # Executive Summary
        response += "## Executive Summary\n"
        response += f"Based on collaborative analysis from {len(synthesis['agent_contributions'])} specialized agents, "
        response += f"we found {len(synthesis['unified_sources'])} high-quality sources and identified "
        response += f"{len(synthesis['key_insights'])} key insights.\n\n"
        
        # Key Insights
        if synthesis["key_insights"]:
            response += "## Key Insights\n"
            for i, insight in enumerate(synthesis["key_insights"], 1):
                response += f"{i}. {insight}\n"
            response += "\n"
        
        # Agent Contributions
        response += "## Agent Contributions\n"
        for agent_name, contribution in synthesis["agent_contributions"].items():
            response += f"### {agent_name.replace('_', ' ').title()}\n"
            response += f"**Confidence:** {contribution['confidence'].value}\n"
            response += f"**Sources:** {contribution['sources_count']}\n"
            response += f"**Analysis:** {contribution['content'][:300]}...\n\n"
        
        # Source Summary
        if synthesis["unified_sources"]:
            response += "## Source Summary\n"
            response += f"Found {len(synthesis['unified_sources'])} validated sources:\n"
            for i, source in enumerate(synthesis["unified_sources"][:5], 1):
                response += f"{i}. **{source.title}** ({source.source_type.value}) - Credibility: {source.credibility_score:.2f}\n"
            response += "\n"
        
        # Quality Assessment
        response += "## Quality Assessment\n"
        if synthesis["contradictions"]:
            response += f"⚠️ **Contradictions Found:** {len(synthesis['contradictions'])}\n"
            for contradiction in synthesis["contradictions"]:
                response += f"- {contradiction}\n"
        
        if synthesis["gaps"]:
            response += f"🔍 **Knowledge Gaps:** {len(synthesis['gaps'])}\n"
            for gap in synthesis["gaps"]:
                response += f"- {gap}\n"
        
        response += "\n---\n"
        response += "*This analysis was coordinated by the Physicist Master Agent with contributions from specialized physics research agents.*"
        
        return response
    
    def _calculate_swarm_confidence(self, agent_responses: Dict[str, AgentResponse]) -> ConfidenceLevel:
        """Calculate overall swarm confidence"""
        if not agent_responses:
            return ConfidenceLevel.LOW
        
        confidences = [response.confidence for response in agent_responses.values()]
        
        high_count = sum(1 for c in confidences if c == ConfidenceLevel.HIGH)
        medium_count = sum(1 for c in confidences if c == ConfidenceLevel.MEDIUM)
        
        if high_count >= len(confidences) * 0.7:
            return ConfidenceLevel.HIGH
        elif (high_count + medium_count) >= len(confidences) * 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    async def process_query(self, query: PhysicsQuery) -> AgentResponse:
        """Process a physics query as the master agent"""
        self.logger.info(f"Processing query as master agent: {query.question}")
        
        # Perform deep physics analysis
        analysis = await self._perform_initial_analysis(query)
        
        # Create response based on analysis
        content = self._create_master_analysis(query, analysis)
        
        # Calculate confidence
        confidence = self._calculate_master_confidence(analysis)
        
        return AgentResponse(
            agent_name="Physicist Master Agent",
            content=content,
            confidence=confidence,
            sources=[],  # Master agent doesn't directly provide sources
            metadata={"analysis": analysis},
            timestamp=datetime.now()
        )
    
    def _create_master_analysis(self, query: PhysicsQuery, analysis: Dict[str, Any]) -> str:
        """Create master analysis response"""
        response = f"# Physics Expert Analysis\n\n"
        
        # Domain Analysis
        domains = analysis.get("domains", [])
        response += f"**Physics Domains:** {', '.join(domains)}\n\n"
        
        # Complexity Assessment
        complexity = analysis.get("complexity_assessment", {})
        response += f"**Complexity Level:** {complexity.get('level', 'unknown')}\n"
        response += f"**Theoretical Framework:** {complexity.get('theoretical_framework', 'general')}\n\n"
        
        # Conceptual Analysis
        concepts = analysis.get("concepts", [])
        response += f"**Key Concepts:** {', '.join(concepts)}\n\n"
        
        # Expert Recommendations
        response += "## Expert Recommendations\n"
        query_classification = analysis.get("query_classification", {})
        
        if query_classification.get("requires_research"):
            response += "- Recommend comprehensive literature review\n"
        if query_classification.get("requires_calculation"):
            response += "- Mathematical analysis required\n"
        if query_classification.get("requires_creativity"):
            response += "- First-principles thinking approach recommended\n"
        
        return response
    
    def _calculate_master_confidence(self, analysis: Dict[str, Any]) -> ConfidenceLevel:
        """Calculate confidence for master analysis"""
        complexity = analysis.get("complexity_assessment", {})
        domains = analysis.get("domains", [])
        
        # High confidence for well-understood domains
        if len(domains) == 1 and domains[0] in ["classical_mechanics", "thermodynamics"]:
            return ConfidenceLevel.HIGH
        elif len(domains) <= 2:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    # Abstract method implementations required by BasePhysicsAgent
    def _get_role_description(self) -> str:
        """Get the role description for CrewAI."""
        return "Physics Master Orchestrator"
    
    def _get_goal_description(self) -> str:
        """Get the goal description for CrewAI."""
        return "Coordinate physics research and provide expert analysis"
    
    def _get_backstory(self) -> str:
        """Get the backstory for CrewAI."""
        return """You are a distinguished physics professor with decades of 
        experience in theoretical and experimental physics. You have published 
        extensively in quantum mechanics, relativity, and particle physics. 
        You excel at coordinating research teams, validating scientific claims, 
        and synthesizing complex physics concepts for different audiences."""
    
    def _get_tools(self) -> List:
        """Get the tools available to this agent."""
        return [self.knowledge_base, self.analysis_tool]
    
    def _create_task_description(self, query: PhysicsQuery) -> str:
        """Create a task description for CrewAI based on the query."""
        return f"""Provide expert physics analysis for: {query.question}
        
        Requirements:
        - Apply deep physics knowledge and expertise
        - Identify key physics domains and concepts
        - Assess theoretical frameworks and complexity
        - Provide authoritative analysis appropriate for {query.complexity_level.value} level
        
        Deliver comprehensive physics expert analysis."""
    
    def _get_expected_output_format(self) -> str:
        """Get the expected output format for CrewAI."""
        return """Expert physics analysis containing:
        - Domain identification and classification
        - Complexity assessment
        - Theoretical framework analysis
        - Key concepts and principles
        - Expert recommendations and insights"""
    
    async def _process_result(self, query: PhysicsQuery, result: Any) -> AgentResponse:
        """Process the result from CrewAI and create an AgentResponse."""
        try:
            # Perform initial analysis
            analysis = await self._perform_initial_analysis(query)
            
            # Create master analysis
            content = self._create_master_analysis(query, analysis)
            
            # Calculate confidence
            confidence = self._calculate_master_confidence(analysis)
            
            return AgentResponse(
                agent_name="physicist_master",
                content=content,
                confidence=confidence,
                sources=[],
                reasoning="Expert physics analysis based on comprehensive knowledge base",
                questions_raised=self._generate_expert_questions(query, analysis),
                metadata={
                    "analysis": analysis,
                    "domains": analysis.get("domains", []),
                    "complexity": analysis.get("complexity_assessment", {}),
                    "theoretical_framework": analysis.get("theoretical_framework", "general")
                },
                processing_time=0.0,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return AgentResponse(
                agent_name="physicist_master",
                content=f"Error in physics master analysis: {str(e)}",
                confidence=ConfidenceLevel.LOW,
                sources=[],
                reasoning=f"Master agent error: {str(e)}",
                questions_raised=[],
                metadata={"error": str(e)},
                processing_time=0.0,
                timestamp=datetime.utcnow()
            )
    
    def _generate_expert_questions(self, query: PhysicsQuery, analysis: Dict[str, Any]) -> List[str]:
        """Generate expert-level questions to deepen understanding"""
        questions = []
        
        domains = analysis.get("domains", [])
        complexity = analysis.get("complexity_assessment", {})
        
        # Domain-specific questions
        if "quantum_mechanics" in domains:
            questions.append("What are the quantum mechanical implications of this phenomenon?")
        if "relativity" in domains:
            questions.append("How do relativistic effects influence the outcome?")
        if "thermodynamics" in domains:
            questions.append("What are the thermodynamic constraints and considerations?")
        
        # Complexity-based questions
        if complexity.get("level") == "advanced":
            questions.append("What are the mathematical formulations underlying this concept?")
            questions.append("How does this relate to current research frontiers?")
        
        return questions[:5]  # Limit to 5 questions 