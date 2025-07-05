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
    """Utility for validating and processing URLs."""
    
    TRUSTED_DOMAINS = [
        'arxiv.org',
        'nature.com',
        'science.org',
        'aaas.org',
        'aps.org',
        'iop.org',
        'springer.com',
        'elsevier.com',
        'wiley.com',
        'mit.edu',
        'stanford.edu',
        'caltech.edu',
        'cern.ch',
        'nasa.gov',
        'nist.gov',
        'doe.gov',
        'nsf.gov',
        'wikipedia.org',
        'britannica.com'
    ]
    
    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @classmethod
    def is_trusted_domain(cls, url: str) -> bool:
        """Check if URL is from a trusted domain."""
        try:
            domain = urlparse(url).netloc.lower()
            return any(trusted in domain for trusted in cls.TRUSTED_DOMAINS)
        except Exception:
            return False
    
    @classmethod
    def get_domain_credibility(cls, url: str) -> float:
        """Get credibility score based on domain."""
        if not cls.is_valid_url(url):
            return 0.0
        
        domain = urlparse(url).netloc.lower()
        
        # Academic and research institutions
        if any(domain.endswith(suffix) for suffix in ['.edu', '.gov']):
            return 0.9
        
        # Trusted scientific publishers
        scientific_domains = ['arxiv.org', 'nature.com', 'science.org', 'aps.org']
        if any(trusted in domain for trusted in scientific_domains):
            return 0.95
        
        # Other trusted domains
        if cls.is_trusted_domain(url):
            return 0.8
        
        # Default for unknown domains
        return 0.5


class SourceValidator:
    """Utility for validating data sources."""
    
    @staticmethod
    def validate_source(source: DataSource) -> ValidationResult:
        """Validate a data source and calculate credibility."""
        validation_notes = []
        credibility_factors = []
        
        # URL validation
        if not URLValidator.is_valid_url(source.url):
            validation_notes.append("Invalid URL format")
            return ValidationResult(
                is_valid=False,
                credibility_score=0.0,
                validation_notes=validation_notes
            )
        
        # Domain credibility
        domain_credibility = URLValidator.get_domain_credibility(source.url)
        credibility_factors.append(domain_credibility)
        
        # Source type credibility
        type_credibility = {
            SourceType.PEER_REVIEWED: 0.95,
            SourceType.GOVERNMENT: 0.9,
            SourceType.EXPERIMENTAL: 0.85,
            SourceType.THEORETICAL: 0.8,
            SourceType.PREPRINT: 0.7,
            SourceType.CONFERENCE: 0.75,
            SourceType.BOOK: 0.7,
            SourceType.EDUCATIONAL: 0.6,
            SourceType.NEWS: 0.4
        }.get(source.source_type, 0.5)
        
        credibility_factors.append(type_credibility)
        
        # Author credibility (if available)
        if source.authors:
            author_credibility = min(0.8, 0.5 + 0.1 * len(source.authors))
            credibility_factors.append(author_credibility)
            validation_notes.append(f"Has {len(source.authors)} author(s)")
        
        # Citation credibility (if available)
        if source.citation_count is not None:
            citation_credibility = min(0.9, 0.5 + 0.01 * source.citation_count)
            credibility_factors.append(citation_credibility)
            validation_notes.append(f"Has {source.citation_count} citations")
        
        # DOI credibility (if available)
        if source.doi:
            credibility_factors.append(0.8)
            validation_notes.append("Has DOI")
        
        # Calculate overall credibility
        overall_credibility = sum(credibility_factors) / len(credibility_factors)
        
        # Determine if source is valid
        is_valid = overall_credibility >= 0.4
        
        return ValidationResult(
            is_valid=is_valid,
            credibility_score=overall_credibility,
            validation_notes=validation_notes,
            peer_reviewed=(source.source_type == SourceType.PEER_REVIEWED),
            recent=SourceValidator._is_recent(source.publication_date),
            authoritative=URLValidator.is_trusted_domain(source.url)
        )
    
    @staticmethod
    def _is_recent(publication_date: Optional[str]) -> bool:
        """Check if publication is recent (within 5 years)."""
        if not publication_date:
            return False
        
        try:
            # Try to parse common date formats
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y', '%m/%d/%Y']:
                try:
                    pub_date = datetime.strptime(publication_date, fmt)
                    cutoff_date = datetime.now() - timedelta(days=5*365)
                    return pub_date >= cutoff_date
                except ValueError:
                    continue
        except Exception:
            pass
        
        return False


class TextProcessor:
    """Utility for processing and cleaning text."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]]', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_equations(text: str) -> List[str]:
        """Extract mathematical equations from text."""
        equations = []
        
        # LaTeX equations
        latex_patterns = [
            r'\$\$([^$]+)\$\$',  # Display math
            r'\$([^$]+)\$',      # Inline math
            r'\\begin\{equation\}(.*?)\\end\{equation\}',
            r'\\begin\{align\}(.*?)\\end\{align\}'
        ]
        
        for pattern in latex_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            equations.extend(matches)
        
        return [eq.strip() for eq in equations if eq.strip()]
    
    @staticmethod
    def extract_key_terms(text: str) -> List[str]:
        """Extract key physics terms from text."""
        # Common physics terms
        physics_terms = [
            'quantum', 'relativity', 'energy', 'momentum', 'force', 'mass',
            'acceleration', 'velocity', 'wave', 'particle', 'field', 'charge',
            'magnetic', 'electric', 'gravitational', 'nuclear', 'atomic',
            'photon', 'electron', 'proton', 'neutron', 'boson', 'fermion',
            'entropy', 'enthalpy', 'temperature', 'pressure', 'volume',
            'frequency', 'wavelength', 'amplitude', 'phase', 'interference'
        ]
        
        text_lower = text.lower()
        found_terms = []
        
        for term in physics_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms


class ConfidenceCalculator:
    """Utility for calculating confidence scores."""
    
    @staticmethod
    def calculate_response_confidence(
        sources: List[DataSource],
        source_agreement: float = 0.8,
        content_quality: float = 0.7,
        reasoning_strength: float = 0.6
    ) -> float:
        """Calculate confidence score for an agent response."""
        if not sources:
            return 0.3  # Low confidence without sources
        
        # Source credibility factor
        source_credibility = sum(s.credibility_score for s in sources) / len(sources)
        
        # Number of sources factor
        source_count_factor = min(1.0, len(sources) / 5)  # Optimal around 5 sources
        
        # Combined confidence
        confidence = (
            source_credibility * 0.4 +
            source_agreement * 0.3 +
            content_quality * 0.2 +
            reasoning_strength * 0.1
        ) * source_count_factor
        
        return min(1.0, max(0.0, confidence))
    
    @staticmethod
    def get_confidence_level(score: float) -> ConfidenceLevel:
        """Convert numerical confidence to confidence level."""
        if score >= 0.9:
            return ConfidenceLevel.HIGH
        elif score >= 0.7:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.5:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.SPECULATION


class DataFormatter:
    """Utility for formatting data for display."""
    
    @staticmethod
    def format_response_for_display(response: AgentResponse) -> Dict[str, Any]:
        """Format agent response for display."""
        return {
            "agent": response.agent_name.value,
            "content": response.content,
            "confidence": f"{response.confidence:.1%}",
            "confidence_level": ConfidenceCalculator.get_confidence_level(response.confidence).value,
            "sources_count": len(response.sources),
            "processing_time": f"{response.processing_time:.2f}s",
            "questions_raised": len(response.questions_raised),
            "timestamp": response.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def format_sources_for_display(sources: List[DataSource]) -> List[Dict[str, Any]]:
        """Format sources for display."""
        formatted_sources = []
        
        for source in sources:
            formatted_sources.append({
                "title": source.title,
                "url": source.url,
                "type": source.source_type.value,
                "credibility": f"{source.credibility_score:.1%}",
                "authors": ", ".join(source.authors) if source.authors else "Unknown",
                "publication_date": source.publication_date or "Unknown",
                "citations": source.citation_count or 0,
                "journal": source.journal or "Unknown"
            })
        
        return formatted_sources


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
    """Custom JSON encoder for complex types."""
    
    @staticmethod
    def encode_datetime(obj: datetime) -> str:
        """Encode datetime to ISO format."""
        return obj.isoformat()
    
    @staticmethod
    def encode_enum(obj: Any) -> str:
        """Encode enum to string value."""
        return obj.value if hasattr(obj, 'value') else str(obj)
    
    @staticmethod
    def safe_json_encode(obj: Any) -> str:
        """Safely encode object to JSON."""
        def default_serializer(o):
            if isinstance(o, datetime):
                return JSONEncoder.encode_datetime(o)
            elif hasattr(o, 'value'):  # Enum
                return JSONEncoder.encode_enum(o)
            elif hasattr(o, 'dict'):  # Pydantic model
                return o.dict()
            else:
                return str(o)
        
        return json.dumps(obj, default=default_serializer, indent=2)


# Convenience functions
def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Set up a logger - convenience function."""
    return Logger.setup_logger(name, level)


def validate_source(source: DataSource) -> ValidationResult:
    """Validate a source - convenience function."""
    return SourceValidator.validate_source(source)


def calculate_confidence(sources: List[DataSource], **kwargs) -> float:
    """Calculate confidence - convenience function."""
    return ConfidenceCalculator.calculate_response_confidence(sources, **kwargs) 