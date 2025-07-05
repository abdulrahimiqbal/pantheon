"""
Vercel serverless function entry point for Pantheon Physics Swarm.
This file serves as the handler for all HTTP requests to /api/* in the Vercel environment.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "orchestration"))

# Import the main FastAPI app
try:
    from main import app
except ImportError as e:
    # Create a minimal FastAPI app if main import fails
    from fastapi import FastAPI
    
    app = FastAPI(title="Pantheon Physics Swarm - Minimal", version="1.0.0")
    
    @app.get("/api/health")
    async def health_check():
        return {"status": "minimal_mode", "error": str(e)}
    
    @app.get("/api/")
    async def root():
        return {
            "status": "minimal_mode",
            "message": "Main application import failed",
            "error": str(e)
        }

# Export the app for Vercel
# Vercel expects the ASGI app to be available as 'app' or a callable
handler = app 