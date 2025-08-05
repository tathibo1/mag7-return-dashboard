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

@app.get("/ticker-return")
async def get_ticker_return(
    ticker: str = Query(..., description="Stock ticker symbol (e.g., MSFT, AAPL)"),
    date: str = Query(..., description="Date in YYYY-MM-DD format")
):
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if target_date > date.today():
        raise HTTPException(status_code=400, detail="Date cannot be in the future")
    
    ticker = ticker.upper()
    
    # Check cache first
    cached_data = cache_instance.get(ticker, date)
    if cached_data:
        logger.info(f"Cache hit for {ticker}:{date}")
        return cached_data
    
    logger.info(f"Cache miss for {ticker}:{date}, fetching data...")
    
    try:
        # Run yfinance call in thread pool
        loop = asyncio.get_event_loop()
        return_data = await loop.run_in_executor(
            executor, 
            StockDataService.fetch_single_day_return, 
            ticker, 
            date
        )
        
        # Cache the result
        cache_instance.set(ticker, date, return_data)
        
        return return_data
    except Exception as e:
        logger.error(f"Error fetching return for {ticker} on {date}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)