"""
Web Crawler Agent for Physics Research

This agent specializes in searching for and validating physics-related sources
using the Tavily API. It focuses on academic sources, credibility scoring,
and comprehensive research gathering.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ...shared.types import (
    DataSource, SourceType, ConfidenceLevel, AgentResponse, 
    PhysicsQuery, ComplexityLevel
)
from ...shared.config import AgentConfig
from ...shared.utils import (
    URLValidator, SourceValidator, TextProcessor, 
    ConfidenceCalculator, DataFormatter
)
from ..base_agent import BasePhysicsAgent


class TavilySearchTool(BaseTool):
    """Custom tool for Tavily API integration"""
    
    name: str = "tavily_search"
    description: str = "Search for physics-related academic sources using Tavily API"
    api_key: str = ""
    base_url: str = "https://api.tavily.com/search"
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        
    def _run(self, query: str, max_results: int = 10, include_domains: List[str] = None) -> Dict[str, Any]:
        """Execute Tavily search"""
        headers = {
            "Content-Type": "application/json"
        }
        
        # Physics-focused domains for academic sources
        physics_domains = [
            "arxiv.org",
            "journals.aps.org",  # American Physical Society
            "nature.com",
            "science.org",
            "iop.org",  # Institute of Physics
            "springer.com",
            "wiley.com",
            "elsevier.com",
            "cern.ch",
            "fermilab.gov",
            "nasa.gov",
            "mit.edu",
            "stanford.edu",
            "harvard.edu",
            "princeton.edu"
        ]
        
        if include_domains:
            physics_domains.extend(include_domains)
        
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": True,
            "max_results": max_results,
            "include_domains": physics_domains[:10],  # Limit to top 10 domains
            "exclude_domains": [
                "wikipedia.org",  # Exclude for academic focus
                "reddit.com",
                "quora.com",
                "yahoo.com"
            ]
        }
        
        # Check if we're in demo mode
        if self.api_key == "demo_key":
            return {
                "query": query,
                "max_results": max_results,
                "results": [
                    {
                        "title": f"Physics Research: {query}",
                        "url": "https://arxiv.org/abs/demo1",
                        "content": f"Comprehensive research on {query} from academic sources.",
                        "score": 0.95,
                        "published_date": "2024-01-01"
                    },
                    {
                        "title": f"Academic Paper: {query}",
                        "url": "https://journals.aps.org/demo2",
                        "content": f"Peer-reviewed academic paper discussing {query}.",
                        "score": 0.92,
                        "published_date": "2024-01-15"
                    },
                    {
                        "title": f"University Research: {query}",
                        "url": "https://mit.edu/research/demo3",
                        "content": f"University research findings related to {query}.",
                        "score": 0.88,
                        "published_date": "2024-02-01"
                    }
                ]
            }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Tavily API error: {str(e)}"}


class BrightDataTool(BaseTool):
    """Optional tool for BrightData API integration"""
    
    name: str = "brightdata_search"
    description: str = "Enhanced web scraping for physics sources using BrightData API"
    api_key: str = ""
    enabled: bool = False
    
    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or ""
        self.enabled = api_key is not None
        
    def _run(self, urls: List[str]) -> Dict[str, Any]:
        """Execute BrightData scraping"""
        if not self.enabled:
            return {"error": "BrightData API key not provided"}
            
        # Implementation would go here
        # For now, return a placeholder
        return {"message": "BrightData integration placeholder"}


class WebCrawlerAgent(BasePhysicsAgent):
    """
    Web Crawler Agent for Physics Research
    
    Specializes in:
    - Academic source discovery
    - Credibility assessment
    - Comprehensive research gathering
    - Source validation and ranking
    """
    
    def __init__(self, config: AgentConfig):
        # Initialize tools BEFORE calling super().__init__
        self.tavily_tool = TavilySearchTool(config.tavily_api_key or "demo_key")
        self.brightdata_tool = BrightDataTool(config.brightdata_api_key)
        
        # Initialize utilities
        self.url_validator = URLValidator()
        self.source_validator = SourceValidator()
        self.text_processor = TextProcessor()
        self.confidence_calculator = ConfidenceCalculator()
        self.data_formatter = DataFormatter()
        
        # Now call super().__init__ which will call _get_tools()
        super().__init__(config)
        
        # Agent-specific configuration
        self.agent_config = {
            "role": "Physics Research Crawler",
            "goal": "Find and validate high-quality physics sources",
            "backstory": """You are an expert research assistant specializing in physics 
            literature. You excel at finding academic sources, assessing credibility, 
            and gathering comprehensive research materials. You prioritize peer-reviewed 
            journals, academic institutions, and authoritative physics organizations.""",
            "temperature": 0.3,  # Low temperature for factual accuracy
            "max_search_results": 15,
            "source_quality_threshold": 0.7
        }
        
        # Note: CrewAI agent will be created by base class
    
    def _get_role_description(self) -> str:
        """Get the role description for CrewAI."""
        return "Physics Research Crawler"
    
    def _get_goal_description(self) -> str:
        """Get the goal description for CrewAI."""
        return "Find and validate high-quality physics sources from academic and research institutions"
    
    def _get_backstory(self) -> str:
        """Get the backstory for CrewAI."""
        return """You are an expert research assistant specializing in physics literature. 
        You excel at finding academic sources, assessing credibility, and gathering comprehensive 
        research materials. You prioritize peer-reviewed journals, academic institutions, 
        and authoritative physics organizations."""
    
    def _get_tools(self) -> List:
        """Get the tools available to this agent."""
        return [self.tavily_tool, self.brightdata_tool]
    
    def _create_task_description(self, query: PhysicsQuery) -> str:
        """Create a task description for CrewAI based on the query."""
        return f"""Search for high-quality physics sources related to: {query.question}
        
        Requirements:
        - Focus on academic and research sources
        - Prioritize peer-reviewed journals
        - Assess source credibility
        - Find sources appropriate for {query.complexity_level.value} level
        
        Return a comprehensive list of validated sources."""
    
    def _get_expected_output_format(self) -> str:
        """Get the expected output format for CrewAI."""
        return """A list of validated physics sources with:
        - Source title and URL
        - Credibility assessment
        - Relevance to query
        - Source type classification
        - Brief summary of content"""
    
    async def _process_result(self, query: PhysicsQuery, result: Any) -> AgentResponse:
        """Process the result from CrewAI and create an AgentResponse."""
        try:
            # Search for sources
            sources = await self.search_physics_sources(query)
            
            # Calculate confidence
            confidence = self._calculate_response_confidence(sources)
            
            # Format response
            content = self._format_crawler_response(sources, query)
            
            return AgentResponse(
                agent_name="web_crawler",
                content=content,
                confidence=confidence,
                sources=sources,
                reasoning=f"Found {len(sources)} validated physics sources",
                questions_raised=[],
                metadata={
                    "search_strategy": self._get_search_strategy(query),
                    "total_sources_found": len(sources),
                    "avg_credibility": sum(s.credibility_score for s in sources) / len(sources) if sources else 0
                },
                processing_time=0.0,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return AgentResponse(
                agent_name="web_crawler",
                content=f"Error in web crawler: {str(e)}",
                confidence=ConfidenceLevel.LOW,
                sources=[],
                reasoning=f"Crawler error: {str(e)}",
                questions_raised=[],
                metadata={"error": str(e)},
                processing_time=0.0,
                timestamp=datetime.utcnow()
            )
    
    async def search_physics_sources(self, query: PhysicsQuery) -> List[DataSource]:
        """Search for physics sources based on query"""
        self.logger.info(f"Searching physics sources for: {query.question}")
        
        # Enhance query for physics-specific search
        enhanced_query = self._enhance_physics_query(query)
        
        # Execute Tavily search
        search_results = self.tavily_tool._run(
            enhanced_query,
            max_results=self.agent_config["max_search_results"]
        )
        
        if "error" in search_results:
            self.logger.error(f"Search error: {search_results['error']}")
            return []
        
        # Process and validate sources
        sources = []
        for result in search_results.get("results", []):
            source = self._process_search_result(result, query)
            if source and source.credibility_score >= self.agent_config["source_quality_threshold"]:
                sources.append(source)
        
        # Sort by credibility score
        sources.sort(key=lambda x: x.credibility_score, reverse=True)
        
        self.logger.info(f"Found {len(sources)} high-quality sources")
        return sources
    
    def _enhance_physics_query(self, query: PhysicsQuery) -> str:
        """Enhance query with physics-specific terms"""
        enhanced_terms = []
        
        # Add physics context
        if query.complexity_level == ComplexityLevel.BASIC:
            enhanced_terms.append("physics education")
        elif query.complexity_level == ComplexityLevel.INTERMEDIATE:
            enhanced_terms.append("undergraduate physics")
        elif query.complexity_level == ComplexityLevel.ADVANCED:
            enhanced_terms.append("graduate physics research")
        elif query.complexity_level == ComplexityLevel.RESEARCH:
            enhanced_terms.append("physics research paper")
        
        # Add domain-specific terms
        physics_domains = [
            "quantum mechanics", "relativity", "thermodynamics", 
            "electromagnetism", "particle physics", "astrophysics",
            "condensed matter", "nuclear physics", "optics"
        ]
        
        # Check if query relates to specific domains
        query_lower = query.question.lower()
        for domain in physics_domains:
            if any(term in query_lower for term in domain.split()):
                enhanced_terms.append(domain)
                break
        
        # Combine original query with enhancements
        enhanced_query = query.question
        if enhanced_terms:
            enhanced_query += " " + " ".join(enhanced_terms)
        
        return enhanced_query
    
    def _process_search_result(self, result: Dict[str, Any], query: PhysicsQuery) -> Optional[DataSource]:
        """Process a single search result into a DataSource"""
        try:
            url = result.get("url", "")
            title = result.get("title", "")
            content = result.get("content", "")
            
            # Validate URL
            if not self.url_validator.is_valid_url(url):
                return None
            
            # Determine source type
            source_type = self._determine_source_type(url)
            
            # Calculate credibility score
            credibility_score = self._calculate_credibility_score(result, source_type)
            
            # Extract metadata
            metadata = self._extract_metadata(result)
            
            return DataSource(
                title=title,
                url=url,
                content=content,
                source_type=source_type,
                credibility_score=credibility_score,
                metadata=metadata,
                timestamp=datetime.now(),
                relevance_score=self._calculate_relevance_score(result, query)
            )
            
        except Exception as e:
            self.logger.error(f"Error processing search result: {str(e)}")
            return None
    
    def _determine_source_type(self, url: str) -> SourceType:
        """Determine the type of source based on URL"""
        url_lower = url.lower()
        
        if "arxiv.org" in url_lower:
            return SourceType.ACADEMIC_PAPER
        elif any(domain in url_lower for domain in ["journals.aps.org", "nature.com", "science.org"]):
            return SourceType.PEER_REVIEWED_JOURNAL
        elif any(domain in url_lower for domain in [".edu", "university", "institute"]):
            return SourceType.ACADEMIC_INSTITUTION
        elif any(domain in url_lower for domain in ["cern.ch", "fermilab.gov", "nasa.gov"]):
            return SourceType.RESEARCH_INSTITUTION
        elif "wikipedia.org" in url_lower:
            return SourceType.ENCYCLOPEDIA
        else:
            return SourceType.WEB_ARTICLE
    
    def _calculate_credibility_score(self, result: Dict[str, Any], source_type: SourceType) -> float:
        """Calculate credibility score for a source"""
        base_scores = {
            SourceType.PEER_REVIEWED_JOURNAL: 0.95,
            SourceType.ACADEMIC_PAPER: 0.90,
            SourceType.RESEARCH_INSTITUTION: 0.85,
            SourceType.ACADEMIC_INSTITUTION: 0.80,
            SourceType.TEXTBOOK: 0.75,
            SourceType.ENCYCLOPEDIA: 0.60,
            SourceType.WEB_ARTICLE: 0.40
        }
        
        score = base_scores.get(source_type, 0.30)
        
        # Adjust based on additional factors
        url = result.get("url", "").lower()
        
        # Boost for high-quality domains
        if any(domain in url for domain in ["arxiv.org", "nature.com", "science.org"]):
            score += 0.05
        
        # Boost for recent content
        if "published_date" in result:
            # Implementation for date-based scoring
            pass
        
        return min(score, 1.0)
    
    def _calculate_relevance_score(self, result: Dict[str, Any], query: PhysicsQuery) -> float:
        """Calculate relevance score based on query match"""
        title = result.get("title", "").lower()
        content = result.get("content", "").lower()
        query_terms = query.question.lower().split()
        
        # Simple relevance scoring
        title_matches = sum(1 for term in query_terms if term in title)
        content_matches = sum(1 for term in query_terms if term in content)
        
        title_score = title_matches / len(query_terms) if query_terms else 0
        content_score = content_matches / len(query_terms) if query_terms else 0
        
        # Weight title matches more heavily
        return (title_score * 0.7 + content_score * 0.3)
    
    def _extract_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from search result"""
        metadata = {
            "search_score": result.get("score", 0),
            "published_date": result.get("published_date"),
            "domain": self.url_validator.extract_domain(result.get("url", "")),
            "raw_content_length": len(result.get("raw_content", "")),
            "snippet": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", "")
        }
        
        return metadata
    
    async def validate_sources(self, sources: List[DataSource]) -> List[DataSource]:
        """Validate and re-rank sources"""
        validated_sources = []
        
        for source in sources:
            # Additional validation
            if self.source_validator.validate_physics_source(source):
                validated_sources.append(source)
        
        return validated_sources
    
    async def process_query(self, query: PhysicsQuery) -> AgentResponse:
        """Main processing method for the Web Crawler Agent"""
        start_time = datetime.now()
        
        try:
            # Search for sources
            sources = await self.search_physics_sources(query)
            
            # Validate sources
            validated_sources = await self.validate_sources(sources)
            
            # Calculate confidence
            confidence = self._calculate_response_confidence(validated_sources)
            
            # Format response
            response_data = {
                "sources_found": len(validated_sources),
                "top_sources": validated_sources[:5],  # Top 5 sources
                "search_strategy": self._get_search_strategy(query),
                "credibility_assessment": self._assess_overall_credibility(validated_sources)
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResponse(
                agent_name="Web Crawler Agent",
                content=self._format_crawler_response(validated_sources, query),
                confidence=confidence,
                sources=validated_sources,
                metadata={
                    "processing_time": processing_time,
                    "sources_found": len(validated_sources),
                    "search_enhanced": True
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in web crawler processing: {str(e)}")
            return AgentResponse(
                agent_name="Web Crawler Agent",
                content=f"Error during research: {str(e)}",
                confidence=ConfidenceLevel.LOW,
                sources=[],
                metadata={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def _calculate_response_confidence(self, sources: List[DataSource]) -> ConfidenceLevel:
        """Calculate confidence based on source quality"""
        if not sources:
            return ConfidenceLevel.LOW
        
        avg_credibility = sum(source.credibility_score for source in sources) / len(sources)
        
        if avg_credibility >= 0.85:
            return ConfidenceLevel.HIGH
        elif avg_credibility >= 0.70:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _get_search_strategy(self, query: PhysicsQuery) -> str:
        """Get search strategy description"""
        strategies = []
        
        if query.complexity_level == ComplexityLevel.RESEARCH:
            strategies.append("Academic paper focus")
        
        strategies.append("Physics domain filtering")
        strategies.append("Credibility scoring")
        strategies.append("Source validation")
        
        return ", ".join(strategies)
    
    def _assess_overall_credibility(self, sources: List[DataSource]) -> str:
        """Assess overall credibility of found sources"""
        if not sources:
            return "No sources found"
        
        high_credibility = sum(1 for s in sources if s.credibility_score >= 0.8)
        medium_credibility = sum(1 for s in sources if 0.6 <= s.credibility_score < 0.8)
        low_credibility = len(sources) - high_credibility - medium_credibility
        
        return f"High: {high_credibility}, Medium: {medium_credibility}, Low: {low_credibility}"
    
    def _format_crawler_response(self, sources: List[DataSource], query: PhysicsQuery) -> str:
        """Format the crawler response"""
        if not sources:
            return "No reliable physics sources found for this query. Consider refining the search terms or checking for alternative phrasings."
        
        response = f"Found {len(sources)} high-quality physics sources for your query.\n\n"
        
        response += "**Top Sources:**\n"
        for i, source in enumerate(sources[:3], 1):
            response += f"{i}. **{source.title}**\n"
            response += f"   - URL: {source.url}\n"
            response += f"   - Type: {source.source_type.value}\n"
            response += f"   - Credibility: {source.credibility_score:.2f}\n"
            response += f"   - Relevance: {source.relevance_score:.2f}\n\n"
        
        if len(sources) > 3:
            response += f"... and {len(sources) - 3} more sources available.\n\n"
        
        response += "**Research Summary:**\n"
        response += f"- Search focused on {query.complexity_level.value} level content\n"
        response += f"- Average source credibility: {sum(s.credibility_score for s in sources) / len(sources):.2f}\n"
        response += f"- Primary source types: {', '.join(set(s.source_type.value for s in sources[:5]))}\n"
        
        return response 