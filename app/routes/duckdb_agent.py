from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Union
import logging
import asyncio
from phi.agent import Agent
from phi.tools.duckdb import DuckDbTools
from phi.model.google import Gemini

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/duckdb", tags=["duckdb"])

# Initialize the DuckDB agent
duckdb_agent = Agent(
    model=Gemini(id="gemini-1.5-flash"),
    tools=[DuckDbTools()],
    show_tool_calls=True,
    description="You are a data analysis agent that can execute SQL queries and analyze data using DuckDB.",
    instructions=[
        "Help users analyze data using SQL queries.",
        "Execute queries and return formatted results.",
        "Provide data insights and visualizations when requested.",
        "Handle various data formats including CSV, JSON, and Parquet.",
    ],
)

class DuckDBRequest(BaseModel):
    query: str
    data_source: Optional[str] = None
    format: Optional[str] = "table"  # "table", "json", "csv"
    include_stats: Optional[bool] = False
    include_viz: Optional[bool] = False

@router.post("/query")
async def execute_query(request: DuckDBRequest):
    try:
        logger.info(f"Processing DuckDB query: {request.query}")
        
        # Construct the instruction
        instruction = f"""Execute the following SQL query: {request.query}
        Data source: {request.data_source or 'default'}
        Output format: {request.format}
        Include statistics: {request.include_stats}
        Include visualization: {request.include_viz}"""
        
        # Set a timeout for the agent's response
        async def run_agent():
            return duckdb_agent.run(
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
        logger.error(f"Error processing DuckDB query: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error processing DuckDB query: {str(e)}"
        ) 