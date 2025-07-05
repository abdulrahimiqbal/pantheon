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

# Test basic import first
try:
    import fastapi
    print("FastAPI import successful")
except ImportError as e:
    print(f"FastAPI import failed: {e}")
    # Create a minimal fallback
    async def app(scope, receive, send):
        """Minimal ASGI app fallback"""
        import json
        
        if scope["type"] == "http":
            response_body = json.dumps({
                "error": "FastAPI not available", 
                "message": "Dependencies not installed properly",
                "python_path": sys.path,
                "working_dir": os.getcwd(),
                "files": os.listdir("/var/task") if os.path.exists("/var/task") else "no /var/task"
            }).encode()
            
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [[b"content-type", b"application/json"]],
            })
            await send({
                "type": "http.response.body",
                "body": response_body,
            })

# Try to import the main FastAPI app
try:
    from main import app
    print("Main app import successful")
except ImportError as e:
    print(f"Main app import failed: {e}")
    # Try to create a simple FastAPI app
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Pantheon Physics Swarm - Fallback", version="1.0.0")
        
        @app.get("/")
        async def root():
            return {
                "status": "fallback_mode",
                "message": "Main application import failed",
                "error": str(e),
                "python_path": sys.path,
                "working_dir": os.getcwd()
            }
            
        @app.get("/api/")
        async def api_root():
            return {
                "status": "fallback_mode", 
                "service": "pantheon-physics-swarm-fallback",
                "error": str(e)
            }
            
    except ImportError as fallback_error:
        print(f"Fallback FastAPI import also failed: {fallback_error}")
        # Use the minimal ASGI fallback defined above
        pass 