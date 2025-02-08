from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from phi.agent import Agent
from phi.tools.youtube_tools import YouTubeTools
from phi.model.google import Gemini

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/youtube", tags=["youtube"])

# Initialize the YouTube agent
youtube_agent = Agent(
   model=Gemini(id="gemini-1.5-flash"),
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
        # Get response from agent
        response = youtube_agent.run(
            f"{request.question} {request.video_url}",
            markdown=True
        )
        return {"response": response.content}
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )