from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
import asyncio
from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.model.google import Gemini

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/websearch", tags=["websearch"])

# Initialize the Web Search agent
web_search_agent = Agent(
    model=Gemini(id="gemini-1.5-flash"),
    tools=[DuckDuckGo()],
    show_tool_calls=True,
    description="You are a web search agent that helps users find relevant information.",
    instructions=[
        "Given a topic by the user, respond with relevant search results about that topic.",
        "Search for multiple results and select the most relevant unique items.",
        "Search in multiple languages when specified.",
        "Provide structured and well-formatted responses.",
        "if query about youtube, search for youtube videos and return the only the youtube video links."
    ],
)

class SearchRequest(BaseModel):
    query: str
    num_results: Optional[int] = 4
    languages: Optional[List[str]] = ["en"]

@router.post("/search")
async def search_web(request: SearchRequest):
    try:
        logger.info(f"Processing search query: {request.query}")
        
        # Construct the search instruction
        instruction = f"""Search for {request.num_results} relevant results about: {request.query}
        Languages to search in: {', '.join(request.languages)}"""
        
        # Set a timeout for the agent's response
        async def run_agent():
            return web_search_agent.run(
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