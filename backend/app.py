from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from services.stock_data import StockDataService
from services.cache import cache_instance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MAG7 Stock Returns API", version="1.0.0")

# Thread pool for CPU-bound tasks
executor = ThreadPoolExecutor(max_workers=4)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/returns")
async def get_returns(
    start: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end: str = Query(..., description="End date in YYYY-MM-DD format")
):
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if end_date > date.today():
        raise HTTPException(status_code=400, detail="End date cannot be in the future")
    
    logger.info(f"Fetching data for {start} to {end}")
    
    try:
        # Run yfinance in thread pool to avoid blocking the event loop
        # This isolates yfinance's synchronous HTTP calls from uvicorn's async event loop
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            executor, 
            StockDataService.fetch_returns_batch, 
            start, 
            end
        )
        return data
    except Exception as e:
        logger.error(f"Error fetching returns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)