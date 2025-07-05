"""
Vercel serverless function entry point for Pantheon Physics Swarm.
This file serves as the handler for all HTTP requests to /api/* in the Vercel environment.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "orchestration"))

# Create a new FastAPI app specifically for Vercel
app = FastAPI(title="Pantheon Physics Swarm API", version="1.1.0")

# Try to import the main app for fallback data
try:
    from main import app as main_app
    print("✅ Successfully imported main FastAPI app")
    HAS_MAIN_APP = True
except ImportError as e:
    print(f"❌ Failed to import main app: {e}")
    HAS_MAIN_APP = False

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "pantheon-physics-swarm"}

@app.get("/")
async def root():
    """Root API endpoint."""
    return {
        "message": "Pantheon Physics Swarm API",
        "version": "1.1.0",
        "docs": "/api/docs",
        "status": "running",
        "trigger_id": "TRIGGER-023-DIRECT-ROUTES",
        "has_main_app": HAS_MAIN_APP
    }

@app.post("/physics/query")
async def physics_query(query_data: dict):
    """Handle physics queries."""
    if HAS_MAIN_APP:
        try:
            # Try to use the main app's logic
            from main import physics_query as main_physics_query
            # This is a simplified version - in a real deployment you'd call the actual function
            pass
        except:
            pass
    
    # Return mock response for now
    return {
        "success": True,
        "data": {
            "answer": f"Mock response for: {query_data.get('question', 'No question provided')}",
            "confidence": 0.8,
            "sources": ["Mock source for demonstration"],
            "agents_used": ["physicist_master", "web_crawler"],
            "note": "This is a mock response. Full physics swarm not available in this deployment."
        },
        "error": None,
        "execution_time": 0.1
    }

@app.get("/agents/status")
async def get_agent_status():
    """Get the status of all agents."""
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
        "version": "1.0.0"
    }

# Debug info
print(f"✅ Vercel-specific FastAPI app created with {len(app.routes)} routes")
print(f"✅ Available routes: {[route.path for route in app.routes]}")

# This is the ASGI application that Vercel will use 