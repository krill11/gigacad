"""
FastAPI web interface for CoralMaker AI CAD Agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
from .ai_agent import CADAgent
from .config import config

app = FastAPI(
    title="CoralMaker - AI CAD Agent",
    description="AI-powered CAD generation using Onshape API",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[CADAgent] = None

class PartRequest(BaseModel):
    description: str
    llm_type: str = "groq"

class StatusResponse(BaseModel):
    document_id: Optional[str]
    workspace_id: Optional[str]
    part_studio_id: Optional[str]
    assembly_id: Optional[str]
    tools_available: list

@app.on_event("startup")
async def startup_event():
    """Initialize the AI agent on startup"""
    global agent
    try:
        if not config.validate():
            raise Exception("Configuration validation failed")
        agent = CADAgent(llm_type="groq")
        print("AI CAD Agent initialized successfully")
    except Exception as e:
        print(f"Failed to initialize AI CAD Agent: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CoralMaker AI CAD Agent",
        "version": "0.1.0",
        "status": "running",
        "capabilities": [
            "Full CAD operations (sketches, extrusions, revolves, sweeps, lofts)",
            "Advanced features (patterns, fillets, holes)",
            "Assembly creation and management",
            "Natural language part generation"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/create-part")
async def create_part(request: PartRequest):
    """Create a CAD part from natural language description"""
    global agent
    
    if not agent:
        raise HTTPException(status_code=500, detail="AI Agent not initialized")
    
    try:
        # Update agent LLM type if specified
        if request.llm_type != "groq":
            agent = CADAgent(llm_type=request.llm_type)
        
        # Create the part
        result = await agent.create_part_from_description(request.description)
        
        return {
            "success": True,
            "message": result,
            "status": await agent.get_status()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current CAD session status"""
    global agent
    
    if not agent:
        raise HTTPException(status_code=500, detail="AI Agent not initialized")
    
    try:
        status = await agent.get_status()
        return StatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    """List available Onshape documents"""
    global agent
    
    if not agent:
        raise HTTPException(status_code=500, detail="AI Agent not initialized")
    
    try:
        documents = await agent.list_documents()
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_session():
    """Reset the current CAD session"""
    global agent
    
    if not agent:
        raise HTTPException(status_code=500, detail="AI Agent not initialized")
    
    try:
        await agent.reset_session()
        return {"message": "Session reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def get_available_tools():
    """Get list of available CAD tools"""
    global agent
    
    if not agent:
        raise HTTPException(status_code=500, detail="AI Agent not initialized")
    
    try:
        status = await agent.get_status()
        return {
            "tools": status["tools_available"],
            "count": len(status["tools_available"]),
            "description": "Available CAD operations for the AI agent",
            "categories": {
                "Document Management": ["create_document", "select_document"],
                "Sketch Operations": ["create_sketch", "create_rectangle_sketch", "create_circle_sketch"],
                "3D Features": ["extrude_sketch", "revolve_sketch", "sweep_sketch", "loft_sketches"],
                "Basic Shapes": ["create_box", "create_cylinder", "create_sphere"],
                "Modifications": ["create_hole", "fillet_edges"],
                "Patterns": ["linear_pattern", "circular_pattern"],
                "Assembly": ["create_assembly"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 