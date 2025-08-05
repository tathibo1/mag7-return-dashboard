import yfinance as yf
from datetime import datetime
from typing import Dict, List, Any
import logging
import os

yf.set_tz_cache_location(os.path.dirname(__file__))

logger = logging.getLogger(__name__)

MAG7_SYMBOLS = ["MSFT", "AAPL", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]


class StockDataService:
    @staticmethod
    def fetch_returns_batch(start_date: str, end_date: str) -> Dict[str, Any]:
        return StockDataService.fetch_returns(start_date, end_date)
    
    @staticmethod
    def fetch_returns(start_date: str, end_date: str) -> Dict[str, Any]:
        all_data = {}
        summary_stats = {}
        
        for symbol in MAG7_SYMBOLS:
            try:
                logger.info(f"Fetching {symbol}")
                
                ticker = yf.Ticker(symbol)
                hist = ticker.history(interval='1d', start=start_date, end=end_date)
                
                if hist.empty:
                    logger.warning(f"No data for {symbol}")
                    all_data[symbol] = []
                    summary_stats[symbol] = {"min": 0, "max": 0, "mean": 0}
                    continue
                
                # Calculate returns
                close_prices = hist['Close'].tolist()
                dates = [idx.strftime("%Y-%m-%d") for idx in hist.index]
                
                returns = []
                return_data = []
                
                for i in range(1, len(close_prices)):
                    if close_prices[i-1] != 0:
                        pct_return = (close_prices[i] - close_prices[i-1]) / close_prices[i-1]
                        returns.append(pct_return)
                        return_data.append({
                            "date": dates[i],
                            "return": round(pct_return, 6)
                        })
                
                all_data[symbol] = return_data
                
                if returns:
                    summary_stats[symbol] = {
                        "min": round(min(returns), 6),
                        "max": round(max(returns), 6),
                        "mean": round(sum(returns) / len(returns), 6)
                    }
                else:
                    summary_stats[symbol] = {"min": 0, "max": 0, "mean": 0}
                
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                all_data[symbol] = []
                summary_stats[symbol] = {"min": 0, "max": 0, "mean": 0}
        
        return {
            "data": all_data,
            "summary": summary_stats
        }