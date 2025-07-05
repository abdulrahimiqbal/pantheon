"""
FastAPI backend for the Pantheon Physics Swarm platform.
This serves as the main API entry point for Vercel deployment.
Build Version: 2.0.0 - REAL PHYSICS SWARM INTEGRATION
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
import asyncio
from datetime import datetime

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
    version="2.0.0",
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

# Global variables for orchestration
swarm_orchestrator = None
swarm_status = {"initialized": False, "error": None}

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

def initialize_swarm():
    """Initialize the physics swarm orchestrator."""
    global swarm_orchestrator, swarm_status
    
    try:
        logger.info("Initializing Physics Swarm...")
        
        # Import physics swarm components
        from physics_swarm.shared import settings, swarm_config, PhysicsQuery as SwarmPhysicsQuery, ComplexityLevel
        from physics_swarm.orchestration.swarm_orchestrator import SwarmOrchestrator
        
        # Create orchestrator instance
        swarm_orchestrator = SwarmOrchestrator(swarm_config)
        
        swarm_status["initialized"] = True
        swarm_status["error"] = None
        logger.info("✅ Physics Swarm initialized successfully")
        
    except Exception as e:
        error_msg = f"Failed to initialize Physics Swarm: {str(e)}"
        logger.error(error_msg)
        swarm_status["initialized"] = False
        swarm_status["error"] = error_msg
        swarm_orchestrator = None

# Initialize swarm on startup
@app.on_event("startup")
async def startup_event():
    """Initialize swarm on app startup."""
    initialize_swarm()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy", 
        "service": "pantheon-physics-swarm",
        "swarm_initialized": swarm_status["initialized"],
        "swarm_error": swarm_status["error"]
    }

# Root endpoint
@app.get("/")
async def root():
    """Root API endpoint."""
    return {
        "message": "Pantheon Physics Swarm API",
        "version": "2.0.0",
        "docs": "/docs",
        "build_test": "REAL PHYSICS SWARM INTEGRATION",
        "timestamp": datetime.now().isoformat(),
        "trigger_id": "PHASE-4-IMPLEMENTATION",
        "status": "Physics swarm ready for queries",
        "swarm_initialized": swarm_status["initialized"]
    }

# Physics query endpoint
@app.post("/physics/query", response_model=SwarmResponse)
async def physics_query(query: PhysicsQuery, background_tasks: BackgroundTasks):
    """
    Process a physics query using the AI agent swarm.
    """
    start_time = datetime.now()
    
    try:
        # Check if swarm is initialized
        if not swarm_orchestrator or not swarm_status["initialized"]:
            # Try to reinitialize
            initialize_swarm()
            
            if not swarm_orchestrator or not swarm_status["initialized"]:
                return SwarmResponse(
                    success=False,
                    error=f"Physics swarm not available: {swarm_status['error']}",
                    execution_time=0.0
                )
        
        # Import required types
        from physics_swarm.shared import PhysicsQuery as SwarmPhysicsQuery, ComplexityLevel
        
        # Convert complexity level
        complexity_mapping = {
            "basic": ComplexityLevel.BASIC,
            "intermediate": ComplexityLevel.INTERMEDIATE,
            "advanced": ComplexityLevel.ADVANCED,
            "research": ComplexityLevel.RESEARCH
        }
        
        complexity_level = complexity_mapping.get(query.complexity.lower(), ComplexityLevel.INTERMEDIATE)
        
        # Create swarm query
        swarm_query = SwarmPhysicsQuery(
            question=query.question,
            context="User query via API",
            complexity_level=complexity_level,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Processing physics query: {query.question}")
        
        # Process the query through the swarm
        swarm_response = await swarm_orchestrator.process_physics_query(swarm_query)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Format response
        response_data = {
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
            "agent_details": {
                agent_name: {
                    "content": response.content,
                    "confidence": response.confidence.value,
                    "sources_count": len(response.sources),
                    "questions_raised": response.questions_raised,
                    "processing_time": response.processing_time
                }
                for agent_name, response in swarm_response.agent_responses.items()
            },
            "total_sources": len(swarm_response.master_response.sources),
            "processing_time": execution_time,
            "query_complexity": complexity_level.value,
            "timestamp": swarm_response.timestamp.isoformat()
        }
        
        logger.info(f"✅ Query processed successfully in {execution_time:.2f}s")
        
        return SwarmResponse(
            success=True,
            data=response_data,
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        error_msg = f"Error processing physics query: {str(e)}"
        logger.error(error_msg)
        
        return SwarmResponse(
            success=False,
            error=error_msg,
            execution_time=execution_time
        )

# Agent status endpoint
@app.get("/agents/status")
async def get_agent_status():
    """Get the status of all physics agents."""
    try:
        if not swarm_orchestrator or not swarm_status["initialized"]:
            return {
                "success": False,
                "error": "Physics swarm not initialized",
                "agents": {}
            }
        
        # Get swarm status
        status = swarm_orchestrator.get_swarm_status()
        
        return {
            "success": True,
            "agents": status.get("agents", {}),
            "active_queries": status.get("active_queries", 0),
            "total_queries_processed": status.get("total_queries_processed", 0),
            "average_processing_time": status.get("average_processing_time", 0.0),
            "swarm_initialized": swarm_status["initialized"]
        }
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return {
            "success": False,
            "error": str(e),
            "agents": {}
        }

# Configuration endpoint
@app.get("/config")
async def get_config():
    """Get API configuration and available features."""
    try:
        from physics_swarm.shared import settings
        
        return {
            "features": {
                "physics_queries": True,
                "agent_orchestration": True,
                "source_validation": True,
                "complexity_levels": ["basic", "intermediate", "advanced", "research"],
                "real_time_processing": True,
                "multi_agent_synthesis": True
            },
            "agents": [
                "physicist_master",
                "web_crawler", 
                "tesla_principles",
                "curious_questioner"
            ],
            "version": "2.0.0",
            "swarm_initialized": swarm_status["initialized"],
            "environment": settings.environment,
            "max_parallel_agents": settings.max_parallel_agents
        }
        
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return {
            "features": {"physics_queries": False},
            "agents": [],
            "version": "2.0.0",
            "error": str(e)
        }

# Swarm management endpoints
@app.post("/swarm/reinitialize")
async def reinitialize_swarm():
    """Reinitialize the physics swarm."""
    try:
        initialize_swarm()
        return {
            "success": swarm_status["initialized"],
            "message": "Swarm reinitialized" if swarm_status["initialized"] else "Swarm initialization failed",
            "error": swarm_status["error"]
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to reinitialize swarm",
            "error": str(e)
        }

@app.get("/swarm/performance")
async def get_swarm_performance():
    """Get swarm performance metrics."""
    try:
        if not swarm_orchestrator or not swarm_status["initialized"]:
            return {
                "success": False,
                "error": "Physics swarm not initialized"
            }
        
        status = swarm_orchestrator.get_swarm_status()
        return {
            "success": True,
            "metrics": status.get("performance_metrics", {}),
            "average_processing_time": status.get("average_processing_time", 0.0),
            "total_queries": status.get("total_queries_processed", 0)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
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
    """Handle internal server errors."""
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Export the app for Vercel
# Vercel will use this as the ASGI application
asgi_app = app

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 