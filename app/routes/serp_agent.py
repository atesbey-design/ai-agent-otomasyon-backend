from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
import asyncio
from phi.agent import Agent
from phi.tools.serpapi import SerpApi
from phi.model.google import Gemini

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/serp", tags=["serp"])

# Initialize the SerpApi agent
serp_agent = Agent(
    model=Gemini(id="gemini-1.5-flash"),
    tools=[SerpApi()],
    show_tool_calls=True,
    description="You are a search agent that can perform advanced Google and YouTube searches.",
    instructions=[
        "Given a query, search using Google or YouTube and return relevant results.",
        "For YouTube queries, focus on finding video details like title, description, and statistics.",
        "For Google queries, provide comprehensive search results with snippets and metadata.",
        "Handle both general web searches and specific YouTube video searches.",
    ],
)

class SerpRequest(BaseModel):
    query: str
    search_type: Optional[str] = "google"  # "google" or "youtube"
    num_results: Optional[int] = 5
    language: Optional[str] = "en"

@router.post("/search")
async def serp_search(request: SerpRequest):
    try:
        logger.info(f"Processing {request.search_type} search query: {request.query}")
        
        # Construct the search instruction
        instruction = f"""Perform a {request.search_type} search for: {request.query}
        Number of results: {request.num_results}
        Language: {request.language}"""
        
        # Set a timeout for the agent's response
        async def run_agent():
            return serp_agent.run(
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