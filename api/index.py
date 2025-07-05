"""
Vercel serverless function entry point for Pantheon Physics Swarm.
This file serves as the handler for all HTTP requests in the Vercel environment.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "orchestration"))

# Import the FastAPI app
try:
    from main import app
    # Export the FastAPI app for Vercel ASGI
    # Vercel will automatically detect this as an ASGI application
except ImportError:
    # Fallback if import fails
    from fastapi import FastAPI
    app = FastAPI(title="Pantheon Physics Swarm - Error", version="1.0.0")
    
    @app.get("/")
    async def error_handler():
        return {
            "error": "Failed to import main application",
            "status": "error",
            "message": "Please check the application configuration"
        } 