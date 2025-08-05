#!/usr/bin/env python3
import yfinance as yf
import sys
from datetime import datetime, timedelta

def test_yfinance():
    print("Testing yfinance connection...")
    
    # Test with a single ticker
    ticker = "MSFT"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"\nFetching data for {ticker} from {start_date.date()} to {end_date.date()}")
    
    try:
        # Method 1: Using Ticker object
        print("\nMethod 1: Using Ticker object")
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        print(f"Data shape: {hist.shape}")
        if not hist.empty:
            print(f"Latest close price: {hist['Close'].iloc[-1]:.2f}")
            print("✓ Method 1 successful")
        else:
            print("✗ Method 1 returned empty data")
        
        # Method 2: Using download function
        print("\nMethod 2: Using download function")
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        print(f"Data shape: {data.shape}")
        if not data.empty:
            print(f"Latest close price: {data['Close'].iloc[-1]:.2f}")
            print("✓ Method 2 successful")
        else:
            print("✗ Method 2 returned empty data")
            
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        print("\nPossible issues:")
        print("1. Network connectivity problems")
        print("2. Firewall blocking Yahoo Finance")
        print("3. Yahoo Finance API changes")
        print("4. Rate limiting")
        return False
    
    return True

if __name__ == "__main__":
    success = test_yfinance()
    sys.exit(0 if success else 1)