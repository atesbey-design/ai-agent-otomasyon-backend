from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
import asyncio
from phi.agent import Agent
from phi.tools.github import GithubTools
from phi.model.google import Gemini

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["github"])

# Initialize the Github agent
github_agent = Agent(
    model=Gemini(id="gemini-1.5-flash"),
    tools=[GithubTools()],
    show_tool_calls=True,
    description="You are a Github agent that can interact with repositories and perform various operations.",
    instructions=[
        "Help users interact with Github repositories.",
        "Search repositories and analyze code.",
        "Get repository information and statistics.",
        "List issues, pull requests, and other repository data.",
    ],
)

class GithubRequest(BaseModel):
    action: str  # "search", "analyze", "info"
    repo: Optional[str] = None
    query: Optional[str] = None
    owner: Optional[str] = None
    include_code: Optional[bool] = False
    include_issues: Optional[bool] = False

@router.post("/interact")
async def github_interact(request: GithubRequest):
    try:
        logger.info(f"Processing Github {request.action} request for: {request.repo or request.query}")
        
        # Construct the instruction based on action
        if request.action == "search":
            instruction = f"Search Github repositories for: {request.query}"
        elif request.action == "analyze":
            instruction = f"Analyze the repository {request.owner}/{request.repo}"
            if request.include_code:
                instruction += " including code analysis"
            if request.include_issues:
                instruction += " and issues analysis"
        elif request.action == "info":
            instruction = f"Get information about the repository {request.owner}/{request.repo}"
        else:
            raise HTTPException(status_code=400, detail="Invalid action specified")
        
        # Set a timeout for the agent's response
        async def run_agent():
            return github_agent.run(
                instruction,
                markdown=True
            )
        
        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(run_agent(), timeout=60.0)  # 60 seconds timeout
            return {"response": response.content}
        except asyncio.TimeoutError:
            logger.error("Request timed out after 60 seconds")
            raise HTTPException(
                status_code=504,
                detail="Request timed out. Please try again."
            )
            
    except Exception as e:
        logger.error(f"Error processing Github request: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error processing Github request: {str(e)}"
        ) 