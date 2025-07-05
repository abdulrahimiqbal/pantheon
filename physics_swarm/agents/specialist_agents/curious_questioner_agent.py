"""
Curious Questioner Agent - Probing Questions and Deep Analysis

This agent specializes in generating insightful questions that deepen understanding,
reveal hidden assumptions, and guide deeper exploration of physics concepts.
It acts as the critical thinking catalyst for the swarm.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import random

from ...shared.types import (
    DataSource, SourceType, ConfidenceLevel, AgentResponse, 
    PhysicsQuery, ComplexityLevel, AgentRole
)
from ...shared.config import AgentConfig
from ...shared.utils import (
    TextProcessor, ConfidenceCalculator, DataFormatter,
    QuestionGenerator, AnalysisDeepener
)
from ..base_agent import BasePhysicsAgent


class SocraticQuestioningTool(BaseTool):
    """Tool for generating Socratic questions to deepen understanding"""
    
    name: str = "socratic_questioning"
    description: str = "Generate probing questions using Socratic method to reveal deeper understanding"
    
    def __init__(self):
        super().__init__()
        self.question_categories = {
            "clarification": [
                "What do you mean by...?",
                "Can you give me an example of...?",
                "How does this relate to...?",
                "What is the significance of...?",
                "Could you explain this in simpler terms?"
            ],
            "assumptions": [
                "What assumptions are we making here?",
                "What if we assumed the opposite?",
                "What evidence supports this assumption?",
                "How do we know this assumption is valid?",
                "What are the implications if this assumption is wrong?"
            ],
            "evidence": [
                "What evidence supports this claim?",
                "How reliable is this evidence?",
                "What might contradict this evidence?",
                "What additional evidence would strengthen this?",
                "How was this evidence obtained?"
            ],
            "implications": [
                "What are the consequences of this?",
                "How does this affect...?",
                "What are the broader implications?",
                "What would happen if this is true?",
                "What does this tell us about...?"
            ],
            "perspectives": [
                "What are alternative ways to look at this?",
                "How might someone disagree with this?",
                "What are the strengths and weaknesses of this view?",
                "What would [specific physicist] say about this?",
                "How does this compare to other theories?"
            ],
            "meta_questions": [
                "Why is this question important?",
                "What does this question assume?",
                "How does this question relate to the bigger picture?",
                "What would happen if we asked a different question?",
                "What questions are we not asking?"
            ]
        }
    
    def _run(self, topic: str, context: str = "", question_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate Socratic questions for a given topic"""
        questions = {
            "topic": topic,
            "context": context,
            "question_type": question_type,
            "generated_questions": {},
            "follow_up_paths": [],
            "depth_levels": {}
        }
        
        # Generate questions for each category
        for category, templates in self.question_categories.items():
            category_questions = self._generate_category_questions(topic, templates, context)
            questions["generated_questions"][category] = category_questions
        
        # Generate follow-up paths
        questions["follow_up_paths"] = self._generate_follow_up_paths(topic, context)
        
        # Organize by depth levels
        questions["depth_levels"] = self._organize_by_depth(questions["generated_questions"])
        
        return questions
    
    def _generate_category_questions(self, topic: str, templates: List[str], context: str) -> List[str]:
        """Generate questions for a specific category"""
        questions = []
        
        for template in templates:
            # Customize template for the topic
            if "..." in template:
                customized = template.replace("...", topic)
            else:
                customized = f"{template} (regarding {topic})"
            
            questions.append(customized)
        
        return questions[:3]  # Return top 3 questions per category
    
    def _generate_follow_up_paths(self, topic: str, context: str) -> List[Dict[str, Any]]:
        """Generate follow-up question paths"""
        paths = [
            {
                "path_name": "Fundamental Understanding",
                "questions": [
                    f"What is the most basic principle underlying {topic}?",
                    f"How does {topic} emerge from more fundamental concepts?",
                    f"What would happen if we removed one key component of {topic}?"
                ]
            },
            {
                "path_name": "Practical Applications",
                "questions": [
                    f"How is {topic} used in real-world applications?",
                    f"What problems does {topic} solve?",
                    f"What new applications might be possible?"
                ]
            },
            {
                "path_name": "Limitations and Boundaries",
                "questions": [
                    f"Where does {topic} break down or become invalid?",
                    f"What are the limits of our understanding of {topic}?",
                    f"What questions about {topic} remain unanswered?"
                ]
            },
            {
                "path_name": "Connections and Relationships",
                "questions": [
                    f"How does {topic} connect to other areas of physics?",
                    f"What analogies help us understand {topic}?",
                    f"How does {topic} fit into the bigger picture?"
                ]
            }
        ]
        
        return paths
    
    def _organize_by_depth(self, questions_by_category: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Organize questions by depth level"""
        depth_levels = {
            "surface": [],
            "intermediate": [],
            "deep": []
        }
        
        # Categorize questions by depth
        surface_categories = ["clarification"]
        intermediate_categories = ["evidence", "implications"]
        deep_categories = ["assumptions", "perspectives", "meta_questions"]
        
        for category, questions in questions_by_category.items():
            if category in surface_categories:
                depth_levels["surface"].extend(questions)
            elif category in intermediate_categories:
                depth_levels["intermediate"].extend(questions)
            elif category in deep_categories:
                depth_levels["deep"].extend(questions)
        
        return depth_levels


class CriticalAnalysisTool(BaseTool):
    """Tool for critical analysis and identifying gaps in reasoning"""
    
    name: str = "critical_analysis"
    description: str = "Perform critical analysis to identify gaps, inconsistencies, and areas for deeper investigation"
    
    def __init__(self):
        super().__init__()
        self.analysis_frameworks = {
            "logical_consistency": {
                "description": "Check for logical consistency and coherence",
                "checks": [
                    "Are the premises logically sound?",
                    "Do the conclusions follow from the premises?",
                    "Are there any logical fallacies?",
                    "Are the arguments internally consistent?"
                ]
            },
            "empirical_support": {
                "description": "Evaluate empirical evidence and support",
                "checks": [
                    "What experimental evidence supports this?",
                    "Are there reproducible results?",
                    "What is the quality of the data?",
                    "Are there conflicting experimental results?"
                ]
            },
            "theoretical_framework": {
                "description": "Assess theoretical foundations",
                "checks": [
                    "What theoretical principles underlie this?",
                    "Are the theoretical foundations solid?",
                    "How does this fit with established theory?",
                    "Are there theoretical predictions that can be tested?"
                ]
            },
            "scope_and_limitations": {
                "description": "Identify scope and limitations",
                "checks": [
                    "What are the boundaries of applicability?",
                    "What assumptions limit the scope?",
                    "Where might this approach fail?",
                    "What cases are not covered?"
                ]
            },
            "alternative_explanations": {
                "description": "Consider alternative explanations",
                "checks": [
                    "What other explanations are possible?",
                    "How do we rule out alternatives?",
                    "What would change our conclusions?",
                    "Are there simpler explanations?"
                ]
            }
        }
    
    def _run(self, content: str, focus_area: str = "comprehensive") -> Dict[str, Any]:
        """Perform critical analysis of given content"""
        analysis = {
            "content": content,
            "focus_area": focus_area,
            "framework_analyses": {},
            "identified_gaps": [],
            "inconsistencies": [],
            "areas_for_investigation": [],
            "critical_questions": []
        }
        
        # Apply each analysis framework
        for framework_name, framework in self.analysis_frameworks.items():
            framework_analysis = self._apply_framework(content, framework)
            analysis["framework_analyses"][framework_name] = framework_analysis
        
        # Identify gaps and inconsistencies
        analysis["identified_gaps"] = self._identify_gaps(content, analysis["framework_analyses"])
        analysis["inconsistencies"] = self._identify_inconsistencies(content, analysis["framework_analyses"])
        
        # Suggest areas for further investigation
        analysis["areas_for_investigation"] = self._suggest_investigation_areas(content, analysis)
        
        # Generate critical questions
        analysis["critical_questions"] = self._generate_critical_questions(content, analysis)
        
        return analysis
    
    def _apply_framework(self, content: str, framework: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a specific analysis framework"""
        framework_result = {
            "description": framework["description"],
            "checks_performed": [],
            "findings": [],
            "score": 0.0
        }
        
        content_lower = content.lower()
        
        # Perform checks
        for check in framework["checks"]:
            check_result = self._perform_check(content_lower, check)
            framework_result["checks_performed"].append({
                "check": check,
                "result": check_result
            })
            
            if check_result["passed"]:
                framework_result["score"] += 1.0
        
        # Normalize score
        framework_result["score"] /= len(framework["checks"])
        
        return framework_result
    
    def _perform_check(self, content: str, check: str) -> Dict[str, Any]:
        """Perform a specific check"""
        # Simple heuristic-based checking
        check_lower = check.lower()
        
        result = {
            "passed": False,
            "confidence": 0.5,
            "evidence": [],
            "concerns": []
        }
        
        # Check for evidence-related content
        if "evidence" in check_lower:
            evidence_indicators = ["experiment", "data", "measurement", "observation", "study"]
            if any(indicator in content for indicator in evidence_indicators):
                result["passed"] = True
                result["confidence"] = 0.7
                result["evidence"] = ["Found evidence indicators in content"]
            else:
                result["concerns"] = ["Limited evidence discussed"]
        
        # Check for theoretical content
        elif "theoretical" in check_lower:
            theory_indicators = ["theory", "principle", "law", "equation", "model"]
            if any(indicator in content for indicator in theory_indicators):
                result["passed"] = True
                result["confidence"] = 0.7
                result["evidence"] = ["Found theoretical framework indicators"]
            else:
                result["concerns"] = ["Limited theoretical foundation discussed"]
        
        # Check for logical consistency
        elif "logical" in check_lower:
            # Simple check for logical connectors
            logical_indicators = ["therefore", "because", "thus", "hence", "consequently"]
            if any(indicator in content for indicator in logical_indicators):
                result["passed"] = True
                result["confidence"] = 0.6
                result["evidence"] = ["Found logical connectors"]
            else:
                result["concerns"] = ["Limited logical structure evident"]
        
        # Default case
        else:
            result["passed"] = True
            result["confidence"] = 0.5
            result["evidence"] = ["General content analysis"]
        
        return result
    
    def _identify_gaps(self, content: str, framework_analyses: Dict[str, Any]) -> List[str]:
        """Identify gaps in the analysis"""
        gaps = []
        
        # Check for low-scoring frameworks
        for framework_name, analysis in framework_analyses.items():
            if analysis["score"] < 0.5:
                gaps.append(f"Weak {framework_name.replace('_', ' ')}")
        
        # Content-specific gaps
        content_lower = content.lower()
        
        if "quantum" in content_lower and "classical" not in content_lower:
            gaps.append("Missing classical physics perspective")
        
        if "theory" in content_lower and "experiment" not in content_lower:
            gaps.append("Missing experimental validation")
        
        if "energy" in content_lower and "conservation" not in content_lower:
            gaps.append("Missing conservation law discussion")
        
        return gaps
    
    def _identify_inconsistencies(self, content: str, framework_analyses: Dict[str, Any]) -> List[str]:
        """Identify potential inconsistencies"""
        inconsistencies = []
        
        # Look for contradictory statements
        content_lower = content.lower()
        
        contradiction_pairs = [
            ("always", "never"),
            ("certain", "uncertain"),
            ("proven", "unproven"),
            ("possible", "impossible")
        ]
        
        for pair in contradiction_pairs:
            if pair[0] in content_lower and pair[1] in content_lower:
                inconsistencies.append(f"Potential contradiction: {pair[0]} vs {pair[1]}")
        
        return inconsistencies
    
    def _suggest_investigation_areas(self, content: str, analysis: Dict[str, Any]) -> List[str]:
        """Suggest areas for further investigation"""
        areas = []
        
        # Based on identified gaps
        gaps = analysis["identified_gaps"]
        for gap in gaps:
            areas.append(f"Investigate {gap.lower()}")
        
        # Based on content
        content_lower = content.lower()
        
        if "hypothesis" in content_lower:
            areas.append("Design experiments to test hypothesis")
        
        if "mechanism" in content_lower:
            areas.append("Explore underlying mechanisms in detail")
        
        if "application" in content_lower:
            areas.append("Investigate practical applications")
        
        return areas[:5]  # Return top 5 areas
    
    def _generate_critical_questions(self, content: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate critical questions based on analysis"""
        questions = []
        
        # Questions based on gaps
        for gap in analysis["identified_gaps"]:
            questions.append(f"How can we address the gap in {gap.lower()}?")
        
        # Questions based on inconsistencies
        for inconsistency in analysis["inconsistencies"]:
            questions.append(f"How do we resolve the {inconsistency.lower()}?")
        
        # General critical questions
        general_questions = [
            "What are the strongest and weakest aspects of this analysis?",
            "What additional information would strengthen this conclusion?",
            "How might this analysis be wrong?",
            "What are the most important follow-up questions?",
            "What assumptions should we test first?"
        ]
        
        questions.extend(general_questions[:3])
        
        return questions


class QuestionPrioritizationTool(BaseTool):
    """Tool for prioritizing questions based on importance and impact"""
    
    name: str = "question_prioritization"
    description: str = "Prioritize questions based on their importance, impact, and potential for insight"
    
    def __init__(self):
        super().__init__()
        self.prioritization_criteria = {
            "fundamental_importance": 0.3,
            "practical_impact": 0.25,
            "insight_potential": 0.25,
            "investigability": 0.2
        }
    
    def _run(self, questions: List[str], context: str = "") -> Dict[str, Any]:
        """Prioritize a list of questions"""
        prioritization = {
            "questions": questions,
            "context": context,
            "prioritized_questions": [],
            "criteria_scores": {},
            "recommendations": []
        }
        
        # Score each question
        question_scores = []
        for question in questions:
            scores = self._score_question(question, context)
            total_score = sum(scores[criterion] * weight 
                            for criterion, weight in self.prioritization_criteria.items())
            
            question_scores.append({
                "question": question,
                "total_score": total_score,
                "criteria_scores": scores
            })
        
        # Sort by total score
        question_scores.sort(key=lambda x: x["total_score"], reverse=True)
        
        prioritization["prioritized_questions"] = question_scores
        prioritization["criteria_scores"] = {
            q["question"]: q["criteria_scores"] for q in question_scores
        }
        
        # Generate recommendations
        prioritization["recommendations"] = self._generate_recommendations(question_scores)
        
        return prioritization
    
    def _score_question(self, question: str, context: str) -> Dict[str, float]:
        """Score a question based on prioritization criteria"""
        scores = {
            "fundamental_importance": 0.5,
            "practical_impact": 0.5,
            "insight_potential": 0.5,
            "investigability": 0.5
        }
        
        question_lower = question.lower()
        
        # Fundamental importance
        fundamental_keywords = ["why", "how", "what", "principle", "law", "fundamental"]
        if any(keyword in question_lower for keyword in fundamental_keywords):
            scores["fundamental_importance"] += 0.3
        
        # Practical impact
        practical_keywords = ["application", "use", "technology", "problem", "solution"]
        if any(keyword in question_lower for keyword in practical_keywords):
            scores["practical_impact"] += 0.3
        
        # Insight potential
        insight_keywords = ["assumption", "perspective", "alternative", "deeper", "underlying"]
        if any(keyword in question_lower for keyword in insight_keywords):
            scores["insight_potential"] += 0.3
        
        # Investigability
        if "?" in question:
            scores["investigability"] += 0.2
        if len(question.split()) < 20:  # Shorter questions often more focused
            scores["investigability"] += 0.2
        
        # Normalize scores
        for key in scores:
            scores[key] = min(scores[key], 1.0)
        
        return scores
    
    def _generate_recommendations(self, question_scores: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on question prioritization"""
        recommendations = []
        
        if not question_scores:
            return ["No questions to prioritize"]
        
        top_question = question_scores[0]
        recommendations.append(f"Start with: {top_question['question']}")
        
        # Identify question types
        fundamental_questions = [q for q in question_scores 
                               if q["criteria_scores"]["fundamental_importance"] > 0.7]
        practical_questions = [q for q in question_scores 
                             if q["criteria_scores"]["practical_impact"] > 0.7]
        
        if fundamental_questions:
            recommendations.append(f"Focus on fundamental questions: {len(fundamental_questions)} identified")
        
        if practical_questions:
            recommendations.append(f"Consider practical applications: {len(practical_questions)} questions")
        
        # Investigation strategy
        if len(question_scores) > 5:
            recommendations.append("Consider investigating top 5 questions in parallel")
        else:
            recommendations.append("Investigate all questions systematically")
        
        return recommendations


class CuriousQuestionerAgent(BasePhysicsAgent):
    """
    Curious Questioner Agent - Probing Questions and Deep Analysis
    
    Specializes in:
    - Generating insightful questions
    - Critical analysis and gap identification
    - Deepening understanding through inquiry
    - Challenging assumptions and perspectives
    - Guiding investigation priorities
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        
        # Initialize specialized tools
        self.socratic_tool = SocraticQuestioningTool()
        self.critical_analysis_tool = CriticalAnalysisTool()
        self.prioritization_tool = QuestionPrioritizationTool()
        
        # Initialize utilities
        self.text_processor = TextProcessor()
        self.confidence_calculator = ConfidenceCalculator()
        self.data_formatter = DataFormatter()
        
        # Agent-specific configuration
        self.agent_config = {
            "role": "Curious Physics Questioner",
            "goal": "Generate insightful questions and deepen understanding through critical inquiry",
            "backstory": """You are an insatiably curious physicist with a gift for asking 
            the right questions at the right time. You have studied under great mentors who 
            taught you that the quality of questions determines the quality of understanding. 
            You excel at identifying assumptions, finding gaps in reasoning, and guiding 
            others toward deeper insights. You believe that every answer should lead to 
            better questions, and that true understanding comes from questioning everything.""",
            "temperature": 0.7,  # Balanced for analytical creativity
            "max_questions_per_category": 5,
            "depth_focus": True
        }
        
        # Create CrewAI agent
        self.crew_agent = Agent(
            role=self.agent_config["role"],
            goal=self.agent_config["goal"],
            backstory=self.agent_config["backstory"],
            tools=[self.socratic_tool, self.critical_analysis_tool, self.prioritization_tool],
            llm=self.llm,
            verbose=True
        )
        
        # Famous questioning quotes for inspiration
        self.questioning_quotes = [
            "The important thing is not to stop questioning. - Albert Einstein",
            "Judge a man by his questions rather than his answers. - Voltaire",
            "The art and science of asking questions is the source of all knowledge. - Thomas Berger",
            "Quality questions create a quality life. - Anthony Robbins",
            "Questions are the creative acts of intelligence. - Frank Kingdon"
        ]
    
    async def generate_socratic_questions(self, query: PhysicsQuery, context: str = "") -> Dict[str, Any]:
        """Generate Socratic questions to deepen understanding"""
        self.logger.info(f"Generating Socratic questions for: {query.question}")
        
        # Use Socratic questioning tool
        socratic_analysis = self.socratic_tool._run(query.question, context)
        
        # Enhance with physics-specific questions
        physics_questions = self._generate_physics_specific_questions(query)
        socratic_analysis["physics_specific"] = physics_questions
        
        return socratic_analysis
    
    def _generate_physics_specific_questions(self, query: PhysicsQuery) -> List[str]:
        """Generate physics-specific probing questions"""
        questions = []
        query_lower = query.question.lower()
        
        # Conservation law questions
        questions.append("What conservation laws apply to this system?")
        
        # Scale questions
        questions.append("How does this phenomenon change at different scales?")
        
        # Symmetry questions
        questions.append("What symmetries are present in this system?")
        
        # Interaction questions
        questions.append("What fundamental interactions are involved?")
        
        # Measurement questions
        questions.append("How would we measure or detect this phenomenon?")
        
        # Limit questions
        questions.append("What happens in the limiting cases?")
        
        # Quantum vs classical
        if "quantum" not in query_lower:
            questions.append("Are there quantum effects we should consider?")
        if "classical" not in query_lower:
            questions.append("What is the classical analog of this phenomenon?")
        
        # Energy questions
        questions.append("How does energy flow through this system?")
        
        # Information questions
        questions.append("What information is preserved or lost in this process?")
        
        # Emergence questions
        questions.append("Could this be an emergent property of simpler phenomena?")
        
        return questions
    
    async def perform_critical_analysis(self, content: str, sources: List[DataSource] = None) -> Dict[str, Any]:
        """Perform critical analysis of content and sources"""
        self.logger.info("Performing critical analysis")
        
        # Use critical analysis tool
        analysis = self.critical_analysis_tool._run(content)
        
        # Analyze sources if provided
        if sources:
            source_analysis = self._analyze_sources_critically(sources)
            analysis["source_analysis"] = source_analysis
        
        # Generate follow-up questions
        follow_up_questions = self._generate_follow_up_questions(analysis)
        analysis["follow_up_questions"] = follow_up_questions
        
        return analysis
    
    def _analyze_sources_critically(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Critically analyze the quality and reliability of sources"""
        analysis = {
            "total_sources": len(sources),
            "source_diversity": {},
            "credibility_assessment": {},
            "bias_indicators": [],
            "gaps_in_coverage": [],
            "quality_questions": []
        }
        
        if not sources:
            return analysis
        
        # Analyze source diversity
        source_types = {}
        for source in sources:
            source_type = source.source_type.value
            source_types[source_type] = source_types.get(source_type, 0) + 1
        
        analysis["source_diversity"] = source_types
        
        # Credibility assessment
        avg_credibility = sum(source.credibility_score for source in sources) / len(sources)
        analysis["credibility_assessment"] = {
            "average_credibility": avg_credibility,
            "high_credibility_count": sum(1 for s in sources if s.credibility_score >= 0.8),
            "low_credibility_count": sum(1 for s in sources if s.credibility_score < 0.6)
        }
        
        # Identify potential biases
        if len(source_types) == 1:
            analysis["bias_indicators"].append("Single source type - potential bias")
        
        if "WEB_ARTICLE" in source_types and source_types["WEB_ARTICLE"] > len(sources) * 0.7:
            analysis["bias_indicators"].append("Over-reliance on web articles")
        
        # Identify gaps
        expected_types = ["PEER_REVIEWED_JOURNAL", "ACADEMIC_PAPER", "RESEARCH_INSTITUTION"]
        missing_types = [t for t in expected_types if t not in source_types]
        
        if missing_types:
            analysis["gaps_in_coverage"] = [f"Missing {t.replace('_', ' ').lower()}" for t in missing_types]
        
        # Generate quality questions
        analysis["quality_questions"] = [
            "Are the sources recent enough for this topic?",
            "Do the sources represent diverse perspectives?",
            "Are there any conflicts of interest in the sources?",
            "What sources might we be missing?",
            "How do we validate the credibility of these sources?"
        ]
        
        return analysis
    
    def _generate_follow_up_questions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate follow-up questions based on critical analysis"""
        questions = []
        
        # Questions based on gaps
        for gap in analysis.get("identified_gaps", []):
            questions.append(f"How can we address the gap in {gap.lower()}?")
        
        # Questions based on inconsistencies
        for inconsistency in analysis.get("inconsistencies", []):
            questions.append(f"How do we resolve: {inconsistency}?")
        
        # Questions based on investigation areas
        for area in analysis.get("areas_for_investigation", []):
            questions.append(f"What specific approach should we take to {area.lower()}?")
        
        return questions
    
    async def prioritize_questions(self, questions: List[str], context: str = "") -> Dict[str, Any]:
        """Prioritize questions based on importance and impact"""
        self.logger.info(f"Prioritizing {len(questions)} questions")
        
        # Use prioritization tool
        prioritization = self.prioritization_tool._run(questions, context)
        
        # Add investigation strategy
        strategy = self._develop_investigation_strategy(prioritization)
        prioritization["investigation_strategy"] = strategy
        
        return prioritization
    
    def _develop_investigation_strategy(self, prioritization: Dict[str, Any]) -> Dict[str, Any]:
        """Develop a strategy for investigating prioritized questions"""
        strategy = {
            "approach": "systematic_inquiry",
            "phases": [],
            "parallel_tracks": [],
            "dependencies": [],
            "timeline": "iterative"
        }
        
        prioritized_questions = prioritization.get("prioritized_questions", [])
        
        if not prioritized_questions:
            return strategy
        
        # Phase 1: Fundamental questions
        fundamental_questions = [q for q in prioritized_questions 
                               if q["criteria_scores"]["fundamental_importance"] > 0.7]
        
        if fundamental_questions:
            strategy["phases"].append({
                "phase": "fundamental_inquiry",
                "questions": [q["question"] for q in fundamental_questions[:3]],
                "goal": "Establish foundational understanding"
            })
        
        # Phase 2: Practical applications
        practical_questions = [q for q in prioritized_questions 
                             if q["criteria_scores"]["practical_impact"] > 0.7]
        
        if practical_questions:
            strategy["phases"].append({
                "phase": "practical_exploration",
                "questions": [q["question"] for q in practical_questions[:3]],
                "goal": "Explore applications and implications"
            })
        
        # Phase 3: Deep insights
        insight_questions = [q for q in prioritized_questions 
                           if q["criteria_scores"]["insight_potential"] > 0.7]
        
        if insight_questions:
            strategy["phases"].append({
                "phase": "deep_investigation",
                "questions": [q["question"] for q in insight_questions[:3]],
                "goal": "Generate breakthrough insights"
            })
        
        # Parallel tracks for highly investigable questions
        investigable_questions = [q for q in prioritized_questions 
                                if q["criteria_scores"]["investigability"] > 0.8]
        
        if len(investigable_questions) > 1:
            strategy["parallel_tracks"] = [q["question"] for q in investigable_questions[:3]]
        
        return strategy
    
    async def guide_deeper_inquiry(self, topic: str, current_understanding: str) -> Dict[str, Any]:
        """Guide deeper inquiry into a physics topic"""
        self.logger.info(f"Guiding deeper inquiry into: {topic}")
        
        guidance = {
            "topic": topic,
            "current_understanding": current_understanding,
            "deeper_questions": [],
            "unexplored_angles": [],
            "connection_opportunities": [],
            "breakthrough_potential": {}
        }
        
        # Generate deeper questions
        guidance["deeper_questions"] = self._generate_deeper_questions(topic, current_understanding)
        
        # Identify unexplored angles
        guidance["unexplored_angles"] = self._identify_unexplored_angles(topic, current_understanding)
        
        # Find connection opportunities
        guidance["connection_opportunities"] = self._find_connection_opportunities(topic)
        
        # Assess breakthrough potential
        guidance["breakthrough_potential"] = self._assess_inquiry_breakthrough_potential(topic, guidance)
        
        return guidance
    
    def _generate_deeper_questions(self, topic: str, understanding: str) -> List[str]:
        """Generate questions that go deeper than current understanding"""
        questions = []
        
        # Meta-questions about the topic
        questions.extend([
            f"What are we assuming about {topic} that might not be true?",
            f"What would {topic} look like from a completely different perspective?",
            f"What is the simplest possible explanation for {topic}?",
            f"What would happen if {topic} didn't exist?",
            f"How does {topic} connect to the deepest principles of physics?"
        ])
        
        # Questions about mechanisms
        questions.extend([
            f"What is the underlying mechanism that produces {topic}?",
            f"How does {topic} emerge from more fundamental processes?",
            f"What information is encoded in {topic}?",
            f"How does {topic} relate to spacetime structure?"
        ])
        
        # Questions about boundaries and limits
        questions.extend([
            f"Where does our understanding of {topic} break down?",
            f"What are the extreme cases of {topic}?",
            f"How does {topic} behave at the quantum level?",
            f"What happens to {topic} at cosmological scales?"
        ])
        
        return questions[:10]  # Return top 10 deeper questions
    
    def _identify_unexplored_angles(self, topic: str, understanding: str) -> List[str]:
        """Identify unexplored angles and perspectives"""
        angles = []
        
        # Different physics perspectives
        perspectives = [
            "Information theory perspective",
            "Thermodynamic perspective",
            "Quantum field theory perspective",
            "Geometric perspective",
            "Symmetry perspective",
            "Emergent phenomena perspective",
            "Computational perspective",
            "Topological perspective"
        ]
        
        # Check which perspectives might be missing
        understanding_lower = understanding.lower()
        
        for perspective in perspectives:
            key_terms = perspective.lower().split()
            if not any(term in understanding_lower for term in key_terms):
                angles.append(perspective)
        
        # Add creative angles
        creative_angles = [
            "Historical development perspective",
            "Philosophical implications",
            "Technological applications",
            "Educational approaches",
            "Cross-disciplinary connections"
        ]
        
        angles.extend(creative_angles[:3])
        
        return angles[:7]  # Return top 7 unexplored angles
    
    def _find_connection_opportunities(self, topic: str) -> List[str]:
        """Find opportunities to connect with other physics areas"""
        connections = []
        
        # Standard physics connections
        physics_areas = [
            "quantum mechanics",
            "relativity",
            "thermodynamics",
            "electromagnetism",
            "particle physics",
            "condensed matter",
            "astrophysics",
            "biophysics"
        ]
        
        for area in physics_areas:
            connections.append(f"How does {topic} connect to {area}?")
        
        # Interdisciplinary connections
        other_fields = [
            "mathematics",
            "chemistry",
            "biology",
            "computer science",
            "philosophy",
            "engineering"
        ]
        
        for field in other_fields[:3]:
            connections.append(f"What connections exist between {topic} and {field}?")
        
        return connections[:8]  # Return top 8 connection opportunities
    
    def _assess_inquiry_breakthrough_potential(self, topic: str, guidance: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the breakthrough potential of deeper inquiry"""
        potential = {
            "score": 0.0,
            "factors": [],
            "high_potential_questions": [],
            "research_directions": []
        }
        
        # Factors that indicate breakthrough potential
        num_unexplored = len(guidance["unexplored_angles"])
        num_connections = len(guidance["connection_opportunities"])
        num_deep_questions = len(guidance["deeper_questions"])
        
        score = 0.0
        
        if num_unexplored > 5:
            score += 0.3
            potential["factors"].append("Many unexplored angles")
        
        if num_connections > 6:
            score += 0.3
            potential["factors"].append("Rich connection opportunities")
        
        if num_deep_questions > 8:
            score += 0.4
            potential["factors"].append("Deep questioning potential")
        
        potential["score"] = score
        
        # Identify high-potential questions
        deep_questions = guidance["deeper_questions"]
        potential["high_potential_questions"] = deep_questions[:3]
        
        # Suggest research directions
        potential["research_directions"] = [
            "Fundamental mechanism investigation",
            "Cross-disciplinary collaboration",
            "Novel experimental approaches",
            "Theoretical framework development"
        ]
        
        return potential
    
    async def process_query(self, query: PhysicsQuery) -> AgentResponse:
        """Process a physics query by generating insightful questions"""
        start_time = datetime.now()
        
        try:
            # Generate Socratic questions
            socratic_analysis = await self.generate_socratic_questions(query)
            
            # Perform critical analysis
            critical_analysis = await self.perform_critical_analysis(query.question)
            
            # Collect all generated questions
            all_questions = []
            
            # Add questions from Socratic analysis
            for category, questions in socratic_analysis["generated_questions"].items():
                all_questions.extend(questions)
            
            # Add critical questions
            all_questions.extend(critical_analysis["critical_questions"])
            
            # Add physics-specific questions
            all_questions.extend(socratic_analysis["physics_specific"])
            
            # Prioritize questions
            prioritization = await self.prioritize_questions(all_questions, query.question)
            
            # Guide deeper inquiry
            deeper_inquiry = await self.guide_deeper_inquiry(query.question, "")
            
            # Calculate confidence
            confidence = self._calculate_questioner_confidence(socratic_analysis, critical_analysis)
            
            # Format response
            content = self._format_questioner_response(
                query, socratic_analysis, critical_analysis, prioritization, deeper_inquiry
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResponse(
                agent_name="Curious Questioner Agent",
                content=content,
                confidence=confidence,
                sources=[],  # Questioner generates questions rather than sources
                metadata={
                    "socratic_analysis": socratic_analysis,
                    "critical_analysis": critical_analysis,
                    "prioritization": prioritization,
                    "deeper_inquiry": deeper_inquiry,
                    "total_questions_generated": len(all_questions),
                    "processing_time": processing_time,
                    "questioning_quote": random.choice(self.questioning_quotes)
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in curious questioner processing: {str(e)}")
            return AgentResponse(
                agent_name="Curious Questioner Agent",
                content=f"Error in question generation: {str(e)}",
                confidence=ConfidenceLevel.LOW,
                sources=[],
                metadata={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def _calculate_questioner_confidence(self, socratic_analysis: Dict[str, Any], 
                                       critical_analysis: Dict[str, Any]) -> ConfidenceLevel:
        """Calculate confidence based on question quality and depth"""
        factors = {
            "question_diversity": len(socratic_analysis["generated_questions"]),
            "depth_levels": len(socratic_analysis["depth_levels"]),
            "critical_insights": len(critical_analysis["identified_gaps"]),
            "follow_up_paths": len(socratic_analysis["follow_up_paths"])
        }
        
        # Calculate score
        score = (
            min(factors["question_diversity"] / 6, 1.0) * 0.3 +
            min(factors["depth_levels"] / 3, 1.0) * 0.3 +
            min(factors["critical_insights"] / 3, 1.0) * 0.2 +
            min(factors["follow_up_paths"] / 4, 1.0) * 0.2
        )
        
        if score >= 0.8:
            return ConfidenceLevel.HIGH
        elif score >= 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _format_questioner_response(self, query: PhysicsQuery, socratic_analysis: Dict[str, Any],
                                   critical_analysis: Dict[str, Any], prioritization: Dict[str, Any],
                                   deeper_inquiry: Dict[str, Any]) -> str:
        """Format the curious questioner response"""
        response = f"# Curious Inquiry: {query.question}\n\n"
        
        # Inspiring quote
        quote = random.choice(self.questioning_quotes)
        response += f"*{quote}*\n\n"
        
        # Executive summary
        total_questions = sum(len(questions) for questions in socratic_analysis["generated_questions"].values())
        response += f"Generated {total_questions} probing questions across {len(socratic_analysis['generated_questions'])} categories "
        response += f"to deepen understanding and guide investigation.\n\n"
        
        # Priority questions
        response += "## Priority Questions to Investigate\n"
        prioritized = prioritization.get("prioritized_questions", [])
        for i, q_data in enumerate(prioritized[:5], 1):
            response += f"{i}. **{q_data['question']}** (Score: {q_data['total_score']:.2f})\n"
        response += "\n"
        
        # Socratic questioning by category
        response += "## Socratic Questioning Framework\n"
        for category, questions in socratic_analysis["generated_questions"].items():
            if questions:
                response += f"### {category.replace('_', ' ').title()}\n"
                for question in questions[:3]:
                    response += f"- {question}\n"
                response += "\n"
        
        # Critical analysis insights
        response += "## Critical Analysis Insights\n"
        gaps = critical_analysis.get("identified_gaps", [])
        if gaps:
            response += "**Identified Gaps:**\n"
            for gap in gaps:
                response += f"- {gap}\n"
            response += "\n"
        
        inconsistencies = critical_analysis.get("inconsistencies", [])
        if inconsistencies:
            response += "**Potential Inconsistencies:**\n"
            for inconsistency in inconsistencies:
                response += f"- {inconsistency}\n"
            response += "\n"
        
        # Deeper inquiry guidance
        response += "## Deeper Inquiry Opportunities\n"
        deeper_questions = deeper_inquiry.get("deeper_questions", [])
        if deeper_questions:
            response += "**Questions for Deeper Understanding:**\n"
            for question in deeper_questions[:5]:
                response += f"- {question}\n"
            response += "\n"
        
        unexplored = deeper_inquiry.get("unexplored_angles", [])
        if unexplored:
            response += "**Unexplored Perspectives:**\n"
            for angle in unexplored[:5]:
                response += f"- {angle}\n"
            response += "\n"
        
        # Investigation strategy
        response += "## Recommended Investigation Strategy\n"
        strategy = prioritization.get("investigation_strategy", {})
        phases = strategy.get("phases", [])
        
        if phases:
            for i, phase in enumerate(phases, 1):
                response += f"**Phase {i}: {phase['phase'].replace('_', ' ').title()}**\n"
                response += f"Goal: {phase['goal']}\n"
                response += "Key Questions:\n"
                for question in phase['questions']:
                    response += f"- {question}\n"
                response += "\n"
        
        # Breakthrough potential
        breakthrough = deeper_inquiry.get("breakthrough_potential", {})
        if breakthrough.get("score", 0) > 0.5:
            response += "## Breakthrough Potential\n"
            response += f"**Score:** {breakthrough['score']:.2f}/1.0\n"
            response += f"**Factors:** {', '.join(breakthrough.get('factors', []))}\n"
            response += "**High-Potential Questions:**\n"
            for question in breakthrough.get("high_potential_questions", []):
                response += f"- {question}\n"
            response += "\n"
        
        response += "---\n"
        response += "*This analysis uses Socratic questioning and critical thinking to guide deeper "
        response += "exploration and understanding of physics concepts.*"
        
        return response 