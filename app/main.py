from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from app.routes import api_router
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Agent System API",
    description="REST API for AI Agent System",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# In-memory storage
agents = [
    
]

class Agent(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    status: str = "inactive"

@app.get("/")
async def root():
    return {"message": "Welcome to AI Agent System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/agents/", response_model=Agent)
async def create_agent(agent: Agent):
    agent.id = len(agents) + 1
    agents.append(agent)
    return agent

@app.get("/agents/", response_model=List[Agent])
async def get_agents():
    return agents

@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: int):
    if agent_id <= 0 or agent_id > len(agents):
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents[agent_id - 1]

@app.put("/agents/{agent_id}/status")
async def update_agent_status(agent_id: int, status: str):
    if agent_id <= 0 or agent_id > len(agents):
        raise HTTPException(status_code=404, detail="Agent not found")
    agents[agent_id - 1].status = status
    return {"message": f"Agent {agent_id} status updated to {status}"} 