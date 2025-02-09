from fastapi import APIRouter
from .youtube_agent import router as youtube_router
from .web_search_agent import router as websearch_router

api_router = APIRouter()
api_router.include_router(youtube_router)
api_router.include_router(websearch_router) 