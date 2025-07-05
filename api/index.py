"""
Vercel serverless function entry point for Pantheon Physics Swarm.
This file serves as the handler for all HTTP requests to /api/* in the Vercel environment.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import time
from pathlib import Path
import logging
from typing import Dict, Any
from pydantic import BaseModel

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "physics_swarm"))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a new FastAPI app specifically for Vercel
app = FastAPI(
    title="Pantheon Physics Swarm API", 
    version="1.1.0",
    description="AI-powered physics query system with multi-agent orchestration"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to import the Physics Swarm
physics_swarm = None
swarm_error = None

try:
    from physics_swarm.shared import settings, swarm_config
    from physics_swarm.orchestration.swarm_orchestrator import SwarmOrchestrator
    physics_swarm = SwarmOrchestrator(swarm_config)
    logger.info("✅ Physics Swarm initialized successfully")
except Exception as e:
    swarm_error = str(e)
    logger.error(f"❌ Failed to initialize Physics Swarm: {e}")

# Pydantic models for request/response
class PhysicsQueryRequest(BaseModel):
    question: str

class PhysicsQueryResponse(BaseModel):
    success: bool
    data: Dict[str, Any] = None
    error: str = None
    execution_time: float = 0.0

@app.get("/")
async def root():
    """Root API endpoint."""
    return {
        "message": "Pantheon Physics Swarm API",
        "version": "1.1.0",
        "docs": "/api/docs",
        "status": "running",
        "trigger_id": "TRIGGER-024-REAL-SWARM",
        "swarm_available": physics_swarm is not None,
        "swarm_error": swarm_error
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy" if physics_swarm is not None else "degraded",
        "service": "pantheon-physics-swarm",
        "swarm_initialized": physics_swarm is not None,
        "swarm_error": swarm_error
    }

@app.post("/physics/query")
async def physics_query(request: PhysicsQueryRequest) -> PhysicsQueryResponse:
    """Handle physics queries using the real Physics Swarm."""
    import time
    start_time = time.time()
    
    try:
        if physics_swarm is None:
            return PhysicsQueryResponse(
                success=False,
                error=f"Physics Swarm not available: {swarm_error}",
                execution_time=time.time() - start_time
            )
        
        # Process the query using the real Physics Swarm
        logger.info(f"Processing physics query: {request.question}")
        
        # Import required types
        from physics_swarm.shared import PhysicsQuery as SwarmPhysicsQuery, ComplexityLevel
        from datetime import datetime
        
        # Create swarm query
        swarm_query = SwarmPhysicsQuery(
            question=request.question,
            context="User query via API",
            complexity_level=ComplexityLevel.INTERMEDIATE,
            timestamp=datetime.utcnow()
        )
        
        # Process the query through the swarm
        swarm_response = await physics_swarm.process_physics_query(swarm_query)
        
        # Format response
        result = {
            "answer": swarm_response.master_response.content,
            "confidence": swarm_response.confidence.value,
            "sources": [
                {
                    "title": source.title,
                    "url": source.url,
                    "credibility": source.credibility_score,
                    "type": source.source_type.value
                }
                for source in swarm_response.master_response.sources
            ],
            "agents_used": list(swarm_response.agent_responses.keys()),
            "total_sources": len(swarm_response.master_response.sources),
            "timestamp": swarm_response.timestamp.isoformat()
        }
        
        return PhysicsQueryResponse(
            success=True,
            data=result,
            execution_time=time.time() - start_time
        )
        
    except Exception as e:
        logger.error(f"Error processing physics query: {str(e)}")
        return PhysicsQueryResponse(
            success=False,
            error=f"Query processing failed: {str(e)}",
            execution_time=time.time() - start_time
        )

@app.get("/agents/status")
async def get_agent_status():
    """Get the status of all agents."""
    try:
        if physics_swarm is None:
            return {
                "success": False,
                "error": f"Physics Swarm not available: {swarm_error}",
                "agents": {}
            }
        
        # Get real agent status
        status = physics_swarm.get_agent_status()
        return {
            "success": True,
            "agents": status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to get agent status: {str(e)}",
            "agents": {}
        }

@app.get("/config")
async def get_config():
    """Get API configuration."""
    return {
        "features": {
            "physics_queries": True,
            "agent_orchestration": True,
            "source_validation": True,
            "complexity_levels": ["basic", "intermediate", "advanced", "research"]
        },
        "agents": ["physicist_master", "web_crawler", "tesla_principles", "curious_questioner"],
        "version": "1.1.0",
        "swarm_available": physics_swarm is not None
    }

# Debug info
logger.info(f"✅ Vercel-specific FastAPI app created with {len(app.routes)} routes")
logger.info(f"✅ Available routes: {[route.path for route in app.routes]}")

# This is the ASGI application that Vercel will use 