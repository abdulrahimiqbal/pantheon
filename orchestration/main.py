"""
FastAPI backend for the Pantheon Physics Swarm platform.
This serves as the main API entry point for Vercel deployment.
Build Version: 1.1.0 - RESET BUILD TEST
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "physics_swarm"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pantheon Physics Swarm API",
    description="AI Agent Swarm for Physics Research and Analysis",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PhysicsQuery(BaseModel):
    question: str
    complexity: Optional[str] = "intermediate"
    include_sources: Optional[bool] = True
    agent_preferences: Optional[List[str]] = None

class SwarmResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "pantheon-physics-swarm"}

# Root endpoint
@app.get("/")
async def root():
    """Root API endpoint."""
    return {
        "message": "Pantheon Physics Swarm API",
        "version": "1.1.0",
        "docs": "/docs",
        "build_test": "RESET BUILD TEST - Framework: Other",
        "timestamp": "2024-12-19T15:00:00Z",
        "trigger_id": "TRIGGER-005-RESET",
        "status": "Testing complete deployment pipeline"
    }

# Note: Frontend is served by static files in /public directory

# Physics query endpoint
@app.post("/physics/query", response_model=SwarmResponse)
async def physics_query(query: PhysicsQuery, background_tasks: BackgroundTasks):
    """
    Process a physics query using the AI agent swarm.
    """
    try:
        # Import here to avoid circular imports and handle missing dependencies
        try:
            from physics_swarm.orchestration.swarm_orchestrator import SwarmOrchestrator
            from physics_swarm.shared.types import PhysicsQuery as SwarmPhysicsQuery
            
            # Initialize the swarm orchestrator
            orchestrator = SwarmOrchestrator()
            
            # Convert request to internal format
            swarm_query = SwarmPhysicsQuery(
                question=query.question,
                complexity=query.complexity or "intermediate",
                include_sources=query.include_sources,
                metadata={"agent_preferences": query.agent_preferences or []}
            )
            
            # Process the query
            result = await orchestrator.process_query(swarm_query)
            
            return SwarmResponse(
                success=True,
                data=result.dict() if hasattr(result, 'dict') else result,
                execution_time=getattr(result, 'execution_time', None)
            )
            
        except ImportError as e:
            logger.warning(f"Physics swarm not available: {e}")
            # Return a mock response for demonstration
            return SwarmResponse(
                success=True,
                data={
                    "answer": f"Mock response for: {query.question}",
                    "confidence": 0.8,
                    "sources": ["Mock source for demonstration"],
                    "agents_used": ["physicist_master", "web_crawler"],
                    "note": "This is a mock response. Full physics swarm not available in this deployment."
                },
                execution_time=0.1
            )
            
    except Exception as e:
        logger.error(f"Error processing physics query: {e}")
        return SwarmResponse(
            success=False,
            error=str(e)
        )

# Agent status endpoint
@app.get("/agents/status")
async def get_agent_status():
    """Get the status of all physics agents."""
    try:
        # Try to import and get actual status
        try:
            from physics_swarm.orchestration.swarm_orchestrator import SwarmOrchestrator
            orchestrator = SwarmOrchestrator()
            status = orchestrator.get_agent_status()
            return {"success": True, "agents": status}
        except ImportError:
            # Return mock status
            return {
                "success": True,
                "agents": {
                    "physicist_master": {"status": "ready", "last_used": None},
                    "web_crawler": {"status": "ready", "last_used": None},
                    "tesla_principles": {"status": "ready", "last_used": None},
                    "curious_questioner": {"status": "ready", "last_used": None}
                },
                "note": "Mock status - full physics swarm not available"
            }
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoint
@app.get("/config")
async def get_config():
    """Get API configuration and available features."""
    return {
        "features": {
            "physics_queries": True,
            "agent_orchestration": True,
            "source_validation": True,
            "complexity_levels": ["basic", "intermediate", "advanced", "research"]
        },
        "agents": [
            "physicist_master",
            "web_crawler", 
            "tesla_principles",
            "curious_questioner"
        ],
        "version": "1.0.0"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# For Vercel deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 