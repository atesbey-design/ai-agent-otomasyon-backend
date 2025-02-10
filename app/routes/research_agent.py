from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import asyncio
from phi.agent import Agent
from phi.model.google import Gemini

from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["research"])

# Initialize the Research agent
research_agent = Agent(
    model=Gemini(id="gemini-1.5-flash"),
    tools=[DuckDuckGo(), Newspaper4k()],
    show_tool_calls=True,
    description="You are a senior NYT researcher writing an article on a topic.",
    instructions=[
        "For a given topic, search for the top 5 links.",
        "Then read each URL and extract the article text, if a URL isn't available, ignore it.",
        "Analyse and prepare an NYT worthy article based on the information.",
    ],
    markdown=True,
    add_datetime_to_instructions=True,
)

class ResearchRequest(BaseModel):
    topic: str
    num_links: Optional[int] = 5

@router.post("/analyze")
async def analyze_topic(request: ResearchRequest):
    try:
        logger.info(f"Processing research topic: {request.topic}")
        
        # Set a timeout for the agent's response
        async def run_agent():
            return research_agent.run(
                f"Research and write an article about: {request.topic}",
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
        logger.error(f"Error processing research: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error processing research: {str(e)}"
        ) 