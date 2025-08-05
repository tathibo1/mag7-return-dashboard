import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set, Tuple
import logging
import os
from .cache import cache_instance

yf.set_tz_cache_location(os.path.dirname(__file__))

logger = logging.getLogger(__name__)

MAG7_SYMBOLS = ["MSFT", "AAPL", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]


class StockDataService:
    @staticmethod
    def fetch_single_day_return(ticker: str, target_date: str) -> Dict[str, Any]:
        """Fetch return for a single ticker on a specific date"""
        try:
            logger.info(f"Fetching {ticker} for {target_date}")
            
            # Parse target date
            date_obj = datetime.strptime(target_date, "%Y-%m-%d")
            
            # Get a few days of data to calculate return (need previous day)
            start_date = (date_obj - timedelta(days=5)).strftime("%Y-%m-%d")
            end_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
            
            yf_ticker = yf.Ticker(ticker)
            hist = yf_ticker.history(interval='1d', start=start_date, end=end_date)
            
            if hist.empty:
                logger.warning(f"No data for {ticker} around {target_date}")
                return {"ticker": ticker, "date": target_date, "return": None, "error": "No data available"}
            
            # Find the target date and previous trading day
            hist.index = hist.index.tz_localize(None)  # Remove timezone
            target_datetime = datetime.strptime(target_date, "%Y-%m-%d")
            
            # Get all available dates and find closest ones
            available_dates = hist.index.tolist()
            available_dates.sort()
            
            # Find target date or closest trading day
            target_idx = None
            for i, hist_date in enumerate(available_dates):
                if hist_date.date() == target_datetime.date():
                    target_idx = i
                    break
                elif hist_date.date() > target_datetime.date():
                    # Target date is not a trading day, use previous available
                    target_idx = max(0, i - 1) if i > 0 else None
                    break
            
            if target_idx is None or target_idx == 0:
                logger.warning(f"Cannot calculate return for {ticker} on {target_date} - no previous trading day")
                return {"ticker": ticker, "date": target_date, "return": None, "error": "No previous trading day available"}
            
            # Calculate return
            current_price = hist.iloc[target_idx]['Close']
            previous_price = hist.iloc[target_idx - 1]['Close']
            
            if previous_price != 0:
                daily_return = (current_price - previous_price) / previous_price
                return {
                    "ticker": ticker,
                    "date": target_date,
                    "return": round(daily_return, 6),
                    "price": round(current_price, 2),
                    "previous_price": round(previous_price, 2)
                }
            else:
                return {"ticker": ticker, "date": target_date, "return": None, "error": "Previous price is zero"}
                
        except Exception as e:
            logger.error(f"Error fetching {ticker} on {target_date}: {e}")
            return {"ticker": ticker, "date": target_date, "return": None, "error": str(e)}