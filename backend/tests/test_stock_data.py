import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from services.stock_data import StockDataService


class TestStockDataService:
    
    @pytest.fixture
    def sample_yfinance_data(self):
        """Create sample yfinance historical data"""
        dates = pd.date_range('2024-01-01', '2024-01-05', freq='D')
        data = {
            'Close': [100.0, 105.0, 103.0, 108.0, 110.0],
            'Open': [99.0, 101.0, 105.0, 102.0, 108.0],
            'High': [102.0, 106.0, 106.0, 109.0, 112.0],
            'Low': [98.0, 100.0, 102.0, 101.0, 107.0],
            'Volume': [1000000, 1100000, 950000, 1200000, 1050000]
        }
        df = pd.DataFrame(data, index=dates)
        df.index.name = 'Date'
        return df

    @pytest.fixture
    def empty_yfinance_data(self):
        """Create empty yfinance data"""
        return pd.DataFrame()

    @pytest.mark.unit
    @patch('services.stock_data.yf.Ticker')
    def test_fetch_single_day_return_success(self, mock_yf_ticker, sample_yfinance_data):
        """Test successful single day return calculation"""
        # Setup
        mock_ticker_instance = Mock()
        mock_yf_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = sample_yfinance_data
        
        # Execute
        result = StockDataService.fetch_single_day_return("AAPL", "2024-01-02")
        
        # Assert
        assert result["ticker"] == "AAPL"
        assert result["date"] == "2024-01-02"
        assert result["return"] == 0.05  # (105-100)/100 = 0.05
        assert result["price"] == 105.0
        assert result["previous_price"] == 100.0
        assert "error" not in result

    @pytest.mark.unit
    @patch('services.stock_data.yf.Ticker')
    def test_fetch_single_day_return_no_data(self, mock_yf_ticker, empty_yfinance_data):
        """Test handling of empty yfinance data"""
        # Setup
        mock_ticker_instance = Mock()
        mock_yf_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = empty_yfinance_data
        
        # Execute
        result = StockDataService.fetch_single_day_return("INVALID", "2024-01-02")
        
        # Assert
        assert result["ticker"] == "INVALID"
        assert result["date"] == "2024-01-02"
        assert result["return"] is None
        assert result["error"] == "No data available"

    @pytest.mark.unit
    @patch('services.stock_data.yf.Ticker')
    def test_fetch_single_day_return_no_previous_day(self, mock_yf_ticker):
        """Test handling when no previous trading day is available"""
        # Setup - only one day of data
        dates = pd.date_range('2024-01-02', '2024-01-02', freq='D')
        single_day_data = pd.DataFrame({
            'Close': [100.0],
            'Open': [99.0],
            'High': [102.0],
            'Low': [98.0],
            'Volume': [1000000]
        }, index=dates)
        
        mock_ticker_instance = Mock()
        mock_yf_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = single_day_data
        
        # Execute
        result = StockDataService.fetch_single_day_return("AAPL", "2024-01-02")
        
        # Assert
        assert result["ticker"] == "AAPL"
        assert result["date"] == "2024-01-02"
        assert result["return"] is None
        assert "No previous trading day available" in result["error"]

    @pytest.mark.unit
    @patch('services.stock_data.yf.Ticker')
    def test_fetch_single_day_return_zero_previous_price(self, mock_yf_ticker):
        """Test handling when previous price is zero"""
        # Setup - data with zero previous price
        dates = pd.date_range('2024-01-01', '2024-01-02', freq='D')
        zero_price_data = pd.DataFrame({
            'Close': [0.0, 100.0],
            'Open': [0.0, 99.0],
            'High': [0.0, 102.0],
            'Low': [0.0, 98.0],
            'Volume': [1000000, 1100000]
        }, index=dates)
        
        mock_ticker_instance = Mock()
        mock_yf_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = zero_price_data
        
        # Execute
        result = StockDataService.fetch_single_day_return("AAPL", "2024-01-02")
        
        # Assert
        assert result["ticker"] == "AAPL"
        assert result["date"] == "2024-01-02"
        assert result["return"] is None
        assert result["error"] == "Previous price is zero"

    @pytest.mark.unit
    @patch('services.stock_data.yf.Ticker')
    def test_fetch_single_day_return_weekend_date(self, mock_yf_ticker, sample_yfinance_data):
        """Test requesting data for a weekend date (should use previous trading day)"""
        # Setup - sample data for weekdays only
        mock_ticker_instance = Mock()
        mock_yf_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = sample_yfinance_data
        
        # Execute - request Saturday data (should use Friday's data)
        result = StockDataService.fetch_single_day_return("AAPL", "2024-01-06")  # Saturday
        
        # Assert - should use the latest available trading day
        assert result["ticker"] == "AAPL"
        assert result["date"] == "2024-01-06"
        # Should calculate return using the last two available trading days
        assert "return" in result

    @pytest.mark.unit
    @patch('services.stock_data.yf.Ticker')
    def test_fetch_single_day_return_yfinance_exception(self, mock_yf_ticker):
        """Test handling of yfinance API exceptions"""
        # Setup
        mock_ticker_instance = Mock()
        mock_yf_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.side_effect = Exception("API Error")
        
        # Execute
        result = StockDataService.fetch_single_day_return("AAPL", "2024-01-02")
        
        # Assert
        assert result["ticker"] == "AAPL"
        assert result["date"] == "2024-01-02"
        assert result["return"] is None
        assert "API Error" in result["error"]

    @pytest.mark.unit
    def test_fetch_single_day_return_invalid_date_format(self):
        """Test handling of invalid date format"""
        # Execute
        result = StockDataService.fetch_single_day_return("AAPL", "invalid-date")
        
        # Assert
        assert result["ticker"] == "AAPL"
        assert result["date"] == "invalid-date"
        assert result["return"] is None
        assert "error" in result
        assert "does not match format" in result["error"]

    @pytest.mark.unit
    @patch('services.stock_data.yf.Ticker')
    def test_fetch_single_day_return_precision(self, mock_yf_ticker):
        """Test return calculation precision and rounding"""
        # Setup - precise price data
        dates = pd.date_range('2024-01-01', '2024-01-02', freq='D')
        precise_data = pd.DataFrame({
            'Close': [100.123456, 105.789012],
            'Open': [99.0, 101.0],
            'High': [102.0, 106.0],
            'Low': [98.0, 100.0],
            'Volume': [1000000, 1100000]
        }, index=dates)
        
        mock_ticker_instance = Mock()
        mock_yf_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = precise_data
        
        # Execute
        result = StockDataService.fetch_single_day_return("AAPL", "2024-01-02")
        
        # Assert precision
        expected_return = (105.789012 - 100.123456) / 100.123456
        assert result["return"] == round(expected_return, 6)
        assert result["price"] == 105.79  # rounded to 2 decimal places
        assert result["previous_price"] == 100.12  # rounded to 2 decimal places

    @pytest.mark.unit
    @patch('services.stock_data.yf.Ticker')
    def test_fetch_single_day_return_timezone_handling(self, mock_yf_ticker):
        """Test that timezone information is properly handled"""
        # Setup - data with timezone
        dates = pd.date_range('2024-01-01', '2024-01-02', freq='D', tz='US/Eastern')
        tz_data = pd.DataFrame({
            'Close': [100.0, 105.0],
            'Open': [99.0, 101.0],
            'High': [102.0, 106.0],
            'Low': [98.0, 100.0],
            'Volume': [1000000, 1100000]
        }, index=dates)
        
        mock_ticker_instance = Mock()
        mock_yf_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = tz_data
        
        # Execute
        result = StockDataService.fetch_single_day_return("AAPL", "2024-01-02")
        
        # Assert - should work despite timezone
        assert result["ticker"] == "AAPL"
        assert result["return"] == 0.05
        assert "error" not in result

    @pytest.mark.unit
    def test_mag7_symbols_constant(self):
        """Test that MAG7_SYMBOLS constant is properly defined"""
        from services.stock_data import MAG7_SYMBOLS
        
        expected_symbols = ["MSFT", "AAPL", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
        assert MAG7_SYMBOLS == expected_symbols
        assert len(MAG7_SYMBOLS) == 7

    @pytest.mark.integration
    @pytest.mark.slow
    def test_fetch_single_day_return_real_api(self):
        """Integration test with real yfinance API (marked as slow)"""
        # Use a date that should have data
        result = StockDataService.fetch_single_day_return("AAPL", "2024-01-03")
        
        # Assert basic structure (don't assert specific values as they're real data)
        assert result["ticker"] == "AAPL"
        assert result["date"] == "2024-01-03"
        assert isinstance(result.get("return"), (float, type(None)))
        
        if result["return"] is not None:
            assert "price" in result
            assert "previous_price" in result
            assert isinstance(result["price"], float)
            assert isinstance(result["previous_price"], float)