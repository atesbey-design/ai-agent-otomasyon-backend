from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import asyncio
from phi.agent import Agent
from phi.tools.tavily import TavilySearch
from phi.model.google import Gemini

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tavily", tags=["tavily"])

# Initialize the Tavily agent
tavily_agent = Agent(
    model=Gemini(id="gemini-1.5-flash"),
    tools=[TavilySearch()],
    show_tool_calls=True,
    description="You are a specialized search agent using Tavily's AI-powered search engine.",
    instructions=[
        "Use Tavily's search capabilities to find accurate and relevant information.",
        "Focus on providing high-quality, fact-checked results.",
        "Include both general web content and news articles when relevant.",
        "Prioritize recent and authoritative sources.",
    ],
)

class TavilyRequest(BaseModel):
    query: str
    search_depth: Optional[str] = "basic"  # "basic" or "deep"
    include_images: Optional[bool] = False
    include_raw_content: Optional[bool] = False

@router.post("/search")
async def tavily_search(request: TavilyRequest):
    try:
        logger.info(f"Processing Tavily search query: {request.query}")
        
        # Construct the search instruction
        instruction = f"""Search for information about: {request.query}
        Search depth: {request.search_depth}
        Include images: {request.include_images}
        Include raw content: {request.include_raw_content}"""
        
        # Set a timeout for the agent's response
        async def run_agent():
            return tavily_agent.run(
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
        logger.error(f"Error processing search: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error processing search: {str(e)}"
        ) 