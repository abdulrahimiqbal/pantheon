"""
Utility functions for the Physics AI Agent Swarm.

This module contains helper functions for validation, formatting,
data processing, and other common operations.
"""

import re
import time
import hashlib
import logging
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import json

from .types import (
    DataSource, SourceType, ValidationResult, ConfidenceLevel,
    ComplexityLevel, PhysicsQuery, AgentResponse
)


class Logger:
    """Centralized logging utility."""
    
    @staticmethod
    def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
        """Set up a logger with consistent formatting."""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger


class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.logger = Logger.setup_logger(self.__class__.__name__)
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        self.logger.info(f"Completed {self.name} in {duration:.2f} seconds")
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time."""
        if self.start_time is None:
            return 0.0
        end_time = self.end_time or time.time()
        return end_time - self.start_time


class URLValidator:
    """Utility for validating URLs."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def is_academic_domain(url: str) -> bool:
        """Check if URL is from an academic domain."""
        academic_domains = [
            '.edu', '.ac.uk', '.ac.', 'arxiv.org', 'scholar.google',
            'pubmed.ncbi.nlm.nih.gov', 'ieeexplore.ieee.org',
            'link.springer.com', 'nature.com', 'science.org',
            'aps.org', 'iop.org', 'elsevier.com'
        ]
        return any(domain in url.lower() for domain in academic_domains)


class SourceValidator:
    """Utility for validating data sources."""
    
    @staticmethod
    def validate_source(source: DataSource) -> ValidationResult:
        """Validate a data source."""
        validation_notes = []
        credibility_score = 0.0
        
        # Check URL validity
        if not URLValidator.is_valid_url(source.url):
            validation_notes.append("Invalid URL")
            return ValidationResult(
                is_valid=False,
                credibility_score=0.0,
                validation_notes=validation_notes
            )
        
        # Base credibility
        credibility_score = 0.3
        
        # Academic domain bonus
        if URLValidator.is_academic_domain(source.url):
            credibility_score += 0.3
            validation_notes.append("Academic domain")
        
        # Source type bonus
        if source.source_type == SourceType.PEER_REVIEWED:
            credibility_score += 0.4
            validation_notes.append("Peer reviewed")
        elif source.source_type == SourceType.PREPRINT:
            credibility_score += 0.2
            validation_notes.append("Preprint")
        elif source.source_type == SourceType.EXPERIMENTAL:
            credibility_score += 0.3
            validation_notes.append("Experimental data")
        
        # Recent publication bonus
        recent = False
        if source.publication_date:
            days_old = (datetime.now() - source.publication_date).days
            if days_old < 365:
                credibility_score += 0.1
                recent = True
                validation_notes.append("Recent publication")
        
        # Authors bonus
        if source.authors:
            credibility_score += min(0.1, len(source.authors) * 0.02)
            validation_notes.append(f"{len(source.authors)} authors")
        
        # Ensure score doesn't exceed 1.0
        credibility_score = min(1.0, credibility_score)
        
        return ValidationResult(
            is_valid=credibility_score >= 0.4,
            credibility_score=credibility_score,
            validation_notes=validation_notes,
            peer_reviewed=(source.source_type == SourceType.PEER_REVIEWED),
            recent=recent,
            authoritative=URLValidator.is_academic_domain(source.url)
        )


class TextProcessor:
    """Utility for processing text content."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction - in production, use more sophisticated NLP
        words = re.findall(r'\b\w{4,}\b', text.lower())
        # Remove common words
        stop_words = {
            'that', 'this', 'with', 'from', 'they', 'been', 'have', 'were',
            'said', 'each', 'which', 'their', 'time', 'will', 'about', 'would',
            'there', 'could', 'other', 'more', 'very', 'what', 'know', 'just',
            'first', 'into', 'over', 'think', 'also', 'your', 'work', 'life'
        }
        keywords = [word for word in words if word not in stop_words]
        
        # Count frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    @staticmethod
    def summarize_text(text: str, max_sentences: int = 3) -> str:
        """Create a simple summary of text."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) <= max_sentences:
            return '. '.join(sentences) + '.'
        
        # Simple approach: take first, middle, and last sentences
        if max_sentences == 3:
            selected = [sentences[0], sentences[len(sentences)//2], sentences[-1]]
        else:
            # Distribute evenly
            indices = [i * len(sentences) // max_sentences for i in range(max_sentences)]
            selected = [sentences[i] for i in indices]
        
        return '. '.join(selected) + '.'


class ConfidenceCalculator:
    """Utility for calculating confidence levels."""
    
    @staticmethod
    def calculate_response_confidence(sources: List[DataSource], **kwargs) -> ConfidenceLevel:
        """Calculate confidence level based on sources and other factors."""
        if not sources:
            return ConfidenceLevel.LOW
        
        # Calculate average credibility
        avg_credibility = sum(source.credibility_score for source in sources) / len(sources)
        
        # Number of sources factor
        source_count_factor = min(1.0, len(sources) / 3)  # Optimal around 3 sources
        
        # Source diversity factor
        source_types = set(source.source_type for source in sources)
        diversity_factor = min(1.0, len(source_types) / 2)  # Bonus for diverse sources
        
        # Combined confidence score
        confidence_score = (avg_credibility * 0.6 + 
                          source_count_factor * 0.3 + 
                          diversity_factor * 0.1)
        
        # Convert to confidence level
        if confidence_score >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.SPECULATION
    
    @staticmethod
    def combine_confidences(confidences: List[ConfidenceLevel]) -> ConfidenceLevel:
        """Combine multiple confidence levels."""
        if not confidences:
            return ConfidenceLevel.LOW
        
        # Map to numeric values
        confidence_values = {
            ConfidenceLevel.HIGH: 0.9,
            ConfidenceLevel.MEDIUM: 0.7,
            ConfidenceLevel.LOW: 0.5,
            ConfidenceLevel.SPECULATION: 0.3
        }
        
        # Calculate weighted average (give more weight to higher confidences)
        values = [confidence_values[c] for c in confidences]
        weights = [v ** 2 for v in values]  # Square for more weight on higher values
        
        if sum(weights) == 0:
            return ConfidenceLevel.LOW
        
        weighted_avg = sum(v * w for v, w in zip(values, weights)) / sum(weights)
        
        # Convert back to confidence level
        if weighted_avg >= 0.8:
            return ConfidenceLevel.HIGH
        elif weighted_avg >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif weighted_avg >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.SPECULATION


class DataFormatter:
    """Utility for formatting data for display."""
    
    @staticmethod
    def format_source_list(sources: List[DataSource]) -> str:
        """Format a list of sources for display."""
        if not sources:
            return "No sources available"
        
        formatted = []
        for i, source in enumerate(sources, 1):
            formatted.append(f"{i}. {source.title} ({source.url})")
        
        return "\n".join(formatted)
    
    @staticmethod
    def format_agent_response(response: AgentResponse) -> str:
        """Format an agent response for display."""
        formatted = f"**{response.agent_name}**\n"
        formatted += f"Content: {response.content}\n"
        formatted += f"Confidence: {response.confidence.value}\n"
        
        if response.sources:
            formatted += f"Sources: {len(response.sources)} found\n"
        
        if response.questions_raised:
            formatted += f"Questions: {len(response.questions_raised)} raised\n"
        
        return formatted


class HashGenerator:
    """Utility for generating hashes and IDs."""
    
    @staticmethod
    def generate_query_hash(query: PhysicsQuery) -> str:
        """Generate a hash for a physics query."""
        content = f"{query.question}_{query.context}_{query.complexity_level.value}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    @staticmethod
    def generate_source_hash(source: DataSource) -> str:
        """Generate a hash for a data source."""
        content = f"{source.url}_{source.title}"
        return hashlib.md5(content.encode()).hexdigest()[:8]


class JSONEncoder:
    """Utility for JSON encoding of complex objects."""
    
    @staticmethod
    def encode_datetime(obj: datetime) -> str:
        """Encode datetime to ISO format."""
        return obj.isoformat()
    
    @staticmethod
    def encode_enum(obj: Any) -> str:
        """Encode enum to its value."""
        return obj.value if hasattr(obj, 'value') else str(obj)


# Additional utility classes for specific physics operations
class PhysicsAnalyzer:
    """Utility for analyzing physics content."""
    
    @staticmethod
    def identify_physics_domains(text: str) -> List[str]:
        """Identify physics domains mentioned in text."""
        domains = {
            'quantum_mechanics': ['quantum', 'wave function', 'superposition', 'entanglement', 'uncertainty'],
            'relativity': ['relativity', 'spacetime', 'lorentz', 'einstein', 'time dilation'],
            'thermodynamics': ['entropy', 'temperature', 'heat', 'thermal', 'gas laws'],
            'electromagnetism': ['electric', 'magnetic', 'electromagnetic', 'maxwell', 'field'],
            'mechanics': ['force', 'motion', 'velocity', 'acceleration', 'newton'],
            'optics': ['light', 'photon', 'reflection', 'refraction', 'interference'],
            'nuclear': ['nuclear', 'radioactive', 'isotope', 'fission', 'fusion'],
            'particle': ['particle', 'quark', 'lepton', 'boson', 'standard model'],
            'astrophysics': ['star', 'galaxy', 'universe', 'cosmic', 'black hole']
        }
        
        text_lower = text.lower()
        identified_domains = []
        
        for domain, keywords in domains.items():
            if any(keyword in text_lower for keyword in keywords):
                identified_domains.append(domain)
        
        return identified_domains


class ConceptMapper:
    """Utility for mapping physics concepts."""
    
    @staticmethod
    def map_related_concepts(concept: str) -> List[str]:
        """Map a physics concept to related concepts."""
        concept_map = {
            'quantum mechanics': ['wave-particle duality', 'uncertainty principle', 'superposition'],
            'relativity': ['time dilation', 'length contraction', 'mass-energy equivalence'],
            'thermodynamics': ['entropy', 'temperature', 'heat engines', 'phase transitions'],
            'electromagnetism': ['electric field', 'magnetic field', 'electromagnetic waves'],
            'mechanics': ['kinematics', 'dynamics', 'energy', 'momentum']
        }
        
        concept_lower = concept.lower()
        for key, related in concept_map.items():
            if key in concept_lower:
                return related
        
        return []


# Convenience functions
def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Set up a logger - convenience function."""
    return Logger.setup_logger(name, level)


def validate_source(source: DataSource) -> ValidationResult:
    """Validate a source - convenience function."""
    return SourceValidator.validate_source(source)


def calculate_confidence(sources: List[DataSource], **kwargs) -> ConfidenceLevel:
    """Calculate confidence - convenience function."""
    return ConfidenceCalculator.calculate_response_confidence(sources, **kwargs)


# Additional utilities for swarm orchestration
class SwarmLogger:
    """Specialized logger for swarm operations."""
    
    def __init__(self, name: str):
        self.logger = setup_logger(name)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)


class PerformanceMonitor:
    """Monitor performance of swarm operations."""
    
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, name: str, value: float):
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
    
    def get_average(self, name: str) -> float:
        if name not in self.metrics or not self.metrics[name]:
            return 0.0
        return sum(self.metrics[name]) / len(self.metrics[name])


class ResultSynthesizer:
    """Synthesize results from multiple agents."""
    
    def synthesize_responses(self, query: PhysicsQuery, orchestrated_response: Any, 
                           agent_responses: Dict[str, AgentResponse]) -> Dict[str, Any]:
        """Synthesize responses from multiple agents."""
        synthesis = {
            "unified_answer": "",
            "unified_sources": [],
            "unified_questions": [],
            "agent_contributions": {},
            "gaps": [],
            "contradictions": []
        }
        
        # Combine all sources
        all_sources = []
        for response in agent_responses.values():
            all_sources.extend(response.sources)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_sources = []
        for source in all_sources:
            if source.url not in seen_urls:
                unique_sources.append(source)
                seen_urls.add(source.url)
        
        synthesis["unified_sources"] = unique_sources
        
        # Combine all questions
        all_questions = []
        for response in agent_responses.values():
            all_questions.extend(response.questions_raised)
        
        synthesis["unified_questions"] = list(set(all_questions))  # Remove duplicates
        
        # Record agent contributions
        for agent_name, response in agent_responses.items():
            synthesis["agent_contributions"][agent_name] = {
                "content_length": len(response.content),
                "source_count": len(response.sources),
                "confidence": response.confidence,
                "processing_time": response.processing_time
            }
        
        return synthesis


class InnovationAnalyzer:
    """Utility for analyzing innovation potential and breakthrough opportunities."""
    
    def __init__(self):
        self.innovation_indicators = {
            "novel_approach": ["novel", "new", "innovative", "breakthrough", "revolutionary"],
            "cross_disciplinary": ["interdisciplinary", "cross-field", "multi-domain"],
            "paradigm_shift": ["paradigm", "fundamental", "revolutionary", "transformative"],
            "practical_impact": ["application", "practical", "useful", "implementation"]
        }
    
    def analyze_innovation_potential(self, text: str) -> Dict[str, Any]:
        """Analyze the innovation potential of given text."""
        analysis = {
            "innovation_score": 0.0,
            "indicators": {},
            "breakthrough_potential": "low",
            "innovation_areas": [],
            "recommendations": []
        }
        
        text_lower = text.lower()
        
        # Check for innovation indicators
        for category, keywords in self.innovation_indicators.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            analysis["indicators"][category] = score
            analysis["innovation_score"] += score * 0.25
        
        # Normalize score
        analysis["innovation_score"] = min(1.0, analysis["innovation_score"])
        
        # Determine breakthrough potential
        if analysis["innovation_score"] >= 0.8:
            analysis["breakthrough_potential"] = "high"
        elif analysis["innovation_score"] >= 0.5:
            analysis["breakthrough_potential"] = "medium"
        else:
            analysis["breakthrough_potential"] = "low"
        
        # Identify innovation areas
        for category, score in analysis["indicators"].items():
            if score > 0:
                analysis["innovation_areas"].append(category.replace("_", " "))
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_innovation_recommendations(analysis)
        
        return analysis
    
    def _generate_innovation_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for innovation enhancement."""
        recommendations = []
        
        if analysis["innovation_score"] < 0.3:
            recommendations.append("Consider more creative approaches")
            recommendations.append("Explore interdisciplinary connections")
        
        if "novel_approach" not in analysis["innovation_areas"]:
            recommendations.append("Look for novel methodologies")
        
        if "practical_impact" not in analysis["innovation_areas"]:
            recommendations.append("Consider practical applications")
        
        return recommendations
    
    def assess_breakthrough_factors(self, problem: str, solution: str) -> Dict[str, Any]:
        """Assess factors that contribute to breakthrough potential."""
        assessment = {
            "problem_novelty": self._assess_problem_novelty(problem),
            "solution_creativity": self._assess_solution_creativity(solution),
            "theoretical_impact": self._assess_theoretical_impact(solution),
            "practical_feasibility": self._assess_practical_feasibility(solution),
            "overall_breakthrough_score": 0.0
        }
        
        # Calculate overall score
        weights = {
            "problem_novelty": 0.25,
            "solution_creativity": 0.35,
            "theoretical_impact": 0.25,
            "practical_feasibility": 0.15
        }
        
        assessment["overall_breakthrough_score"] = sum(
            assessment[factor] * weight 
            for factor, weight in weights.items()
        )
        
        return assessment
    
    def _assess_problem_novelty(self, problem: str) -> float:
        """Assess how novel the problem is."""
        novelty_indicators = ["unsolved", "mystery", "unexplained", "paradox", "unknown"]
        problem_lower = problem.lower()
        
        score = sum(0.2 for indicator in novelty_indicators if indicator in problem_lower)
        return min(1.0, score)
    
    def _assess_solution_creativity(self, solution: str) -> float:
        """Assess the creativity of the solution."""
        creativity_indicators = ["innovative", "creative", "novel", "unique", "original"]
        solution_lower = solution.lower()
        
        score = sum(0.2 for indicator in creativity_indicators if indicator in solution_lower)
        return min(1.0, score)
    
    def _assess_theoretical_impact(self, solution: str) -> float:
        """Assess the theoretical impact of the solution."""
        impact_indicators = ["theory", "principle", "law", "fundamental", "framework"]
        solution_lower = solution.lower()
        
        score = sum(0.2 for indicator in impact_indicators if indicator in solution_lower)
        return min(1.0, score)
    
    def _assess_practical_feasibility(self, solution: str) -> float:
        """Assess the practical feasibility of the solution."""
        feasibility_indicators = ["feasible", "practical", "implementable", "realistic", "achievable"]
        solution_lower = solution.lower()
        
        score = sum(0.2 for indicator in feasibility_indicators if indicator in solution_lower)
        return min(1.0, score)


class QuestionGenerator:
    """Utility for generating physics-related questions."""
    
    def __init__(self):
        self.question_templates = {
            "mechanism": [
                "What is the underlying mechanism of {}?",
                "How does {} work at the fundamental level?",
                "What causes {} to occur?"
            ],
            "implications": [
                "What are the implications of {} for {}?",
                "How does {} affect {}?",
                "What would happen if {} were different?"
            ],
            "relationships": [
                "How is {} related to {}?",
                "What is the connection between {} and {}?",
                "How do {} and {} interact?"
            ],
            "applications": [
                "How could {} be applied to {}?",
                "What are the practical applications of {}?",
                "Where else might we see {} in action?"
            ],
            "limitations": [
                "What are the limitations of {}?",
                "Under what conditions does {} break down?",
                "What assumptions underlie {}?"
            ]
        }
    
    def generate_questions(self, topic: str, context: str = "", question_types: List[str] = None) -> List[str]:
        """Generate questions about a physics topic."""
        if question_types is None:
            question_types = list(self.question_templates.keys())
        
        questions = []
        
        for question_type in question_types:
            if question_type in self.question_templates:
                templates = self.question_templates[question_type]
                for template in templates[:2]:  # Limit to 2 per type
                    try:
                        question = template.format(topic)
                        questions.append(question)
                    except:
                        # Skip if template doesn't format properly
                        continue
        
        return questions
    
    def generate_socratic_questions(self, statement: str) -> List[str]:
        """Generate Socratic questions to probe deeper into a statement."""
        questions = [
            f"What evidence supports the claim that {statement}?",
            f"What assumptions are we making about {statement}?",
            f"What are the implications if {statement} is true?",
            f"What are the implications if {statement} is false?",
            f"How does {statement} relate to what we already know?",
            f"What questions does {statement} raise?",
            f"What would someone who disagrees with {statement} say?",
            f"How could we test whether {statement} is true?"
        ]
        
        return questions
    
    def generate_critical_questions(self, analysis: str) -> List[str]:
        """Generate critical questions about an analysis."""
        questions = [
            "What are the strongest points in this analysis?",
            "What are the weakest points in this analysis?",
            "What evidence is missing?",
            "What alternative explanations exist?",
            "What biases might be present?",
            "How could this analysis be improved?",
            "What are the practical implications?",
            "What questions remain unanswered?"
        ]
        
        return questions


class AnalysisDeepener:
    """Utility for deepening analysis through systematic questioning."""
    
    def __init__(self):
        self.deepening_strategies = {
            "causal_analysis": {
                "description": "Explore cause-and-effect relationships",
                "questions": [
                    "What causes this phenomenon?",
                    "What are the contributing factors?",
                    "What would happen if we changed each factor?",
                    "Are there feedback loops involved?"
                ]
            },
            "systems_thinking": {
                "description": "Consider the broader system context",
                "questions": [
                    "How does this fit into the larger system?",
                    "What are the system boundaries?",
                    "How do different parts interact?",
                    "What emergent properties arise?"
                ]
            },
            "multiple_perspectives": {
                "description": "Consider different viewpoints",
                "questions": [
                    "How would different experts view this?",
                    "What would the opposing view be?",
                    "How might this look from a different scale?",
                    "What historical perspectives exist?"
                ]
            },
            "temporal_analysis": {
                "description": "Consider time-related aspects",
                "questions": [
                    "How has this changed over time?",
                    "What are the short-term vs long-term effects?",
                    "What trends are emerging?",
                    "How might this evolve in the future?"
                ]
            }
        }
    
    def deepen_analysis(self, topic: str, current_analysis: str, strategy: str = "comprehensive") -> Dict[str, Any]:
        """Deepen analysis using systematic questioning."""
        deepening = {
            "topic": topic,
            "strategy": strategy,
            "deeper_questions": [],
            "analysis_gaps": [],
            "new_perspectives": [],
            "recommendations": []
        }
        
        if strategy == "comprehensive":
            # Apply all strategies
            for strategy_name, strategy_info in self.deepening_strategies.items():
                questions = self._apply_strategy(topic, current_analysis, strategy_name)
                deepening["deeper_questions"].extend(questions)
        else:
            # Apply specific strategy
            if strategy in self.deepening_strategies:
                questions = self._apply_strategy(topic, current_analysis, strategy)
                deepening["deeper_questions"].extend(questions)
        
        # Identify gaps
        deepening["analysis_gaps"] = self._identify_gaps(current_analysis)
        
        # Suggest new perspectives
        deepening["new_perspectives"] = self._suggest_perspectives(topic, current_analysis)
        
        # Generate recommendations
        deepening["recommendations"] = self._generate_recommendations(deepening)
        
        return deepening
    
    def _apply_strategy(self, topic: str, analysis: str, strategy: str) -> List[str]:
        """Apply a specific deepening strategy."""
        if strategy not in self.deepening_strategies:
            return []
        
        strategy_info = self.deepening_strategies[strategy]
        questions = []
        
        for question_template in strategy_info["questions"]:
            try:
                question = question_template.format(topic=topic)
                questions.append(question)
            except:
                questions.append(question_template)
        
        return questions
    
    def _identify_gaps(self, analysis: str) -> List[str]:
        """Identify gaps in the current analysis."""
        gaps = []
        analysis_lower = analysis.lower()
        
        # Check for missing elements
        missing_elements = {
            "quantitative_data": ["data", "measurement", "quantitative"],
            "mechanisms": ["mechanism", "how", "process"],
            "evidence": ["evidence", "proof", "validation"],
            "implications": ["implications", "consequences", "effects"],
            "limitations": ["limitations", "constraints", "boundaries"]
        }
        
        for element, keywords in missing_elements.items():
            if not any(keyword in analysis_lower for keyword in keywords):
                gaps.append(f"Missing {element.replace('_', ' ')}")
        
        return gaps
    
    def _suggest_perspectives(self, topic: str, analysis: str) -> List[str]:
        """Suggest new perspectives to consider."""
        perspectives = [
            "Mathematical/quantitative perspective",
            "Experimental/empirical perspective",
            "Theoretical/conceptual perspective",
            "Historical/evolutionary perspective",
            "Interdisciplinary perspective",
            "Scale-dependent perspective",
            "Practical/applied perspective",
            "Philosophical/foundational perspective"
        ]
        
        return perspectives
    
    def _generate_recommendations(self, deepening: Dict[str, Any]) -> List[str]:
        """Generate recommendations for deeper analysis."""
        recommendations = []
        
        if deepening["analysis_gaps"]:
            recommendations.append("Address identified gaps in the analysis")
        
        if len(deepening["deeper_questions"]) > 10:
            recommendations.append("Prioritize the most important questions")
        
        recommendations.extend([
            "Seek additional expert perspectives",
            "Look for quantitative data to support claims",
            "Consider conducting experiments or simulations",
            "Explore connections to other fields"
        ])
        
        return recommendations[:5] 