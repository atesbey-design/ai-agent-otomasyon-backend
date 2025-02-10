from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import asyncio
from phi.agent import Agent
from phi.tools.youtube_tools import YouTubeTools
from phi.model.groq import Groq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/youtube", tags=["youtube"])

# Initialize the YouTube agent
youtube_agent = Agent(
    model=Groq(id="mixtral-8x7b-32768"),
    tools=[YouTubeTools()],
    show_tool_calls=True,
    description="You are a YouTube agent. Obtain the captions of a YouTube video and answer questions.",
)

class VideoRequest(BaseModel):
    video_url: str
    question: Optional[str] = "Summarize this video"

@router.post("/analyze")
async def analyze_video(request: VideoRequest):
    try:
        logger.info(f"Processing video: {request.video_url}")
        
        # Set a timeout for the agent's response
        async def run_agent():
            return youtube_agent.run(
                f"{request.question} {request.video_url}",
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
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )