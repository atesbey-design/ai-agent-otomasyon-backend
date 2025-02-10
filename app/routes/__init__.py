from fastapi import APIRouter
from .youtube_agent import router as youtube_router
from .web_search_agent import router as websearch_router
from .research_agent import router as research_router
from .serp_agent import router as serp_router
# from .tavily_agent import router as tavily_router
# from .github_agent import router as github_router
from .duckdb_agent import router as duckdb_router

api_router = APIRouter()
api_router.include_router(youtube_router)
api_router.include_router(websearch_router)
api_router.include_router(research_router)
api_router.include_router(serp_router)
# api_router.include_router(tavily_router)
# api_router.include_router(github_router)
api_router.include_router(duckdb_router) 