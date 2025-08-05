"""
Integration tests that test multiple components working together
"""
import pytest
from unittest.mock import patch
import pandas as pd
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from app import app
from services.stock_data import StockDataService
from services.cache import cache_instance


class TestIntegration:
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_yfinance_data(self):
        """Create realistic yfinance data"""
        dates = pd.date_range('2024-01-01', '2024-01-05', freq='D')
        data = {
            'Close': [150.0, 155.0, 153.0, 158.0, 160.0],
            'Open': [149.0, 151.0, 155.0, 152.0, 158.0],
            'High': [152.0, 156.0, 156.0, 159.0, 162.0],
            'Low': [148.0, 150.0, 152.0, 151.0, 157.0],
            'Volume': [1000000, 1100000, 950000, 1200000, 1050000]
        }
        df = pd.DataFrame(data, index=dates)
        df.index.name = 'Date'
        return df

    @pytest.mark.integration
    @patch('services.stock_data.yf.Ticker')
    def test_end_to_end_api_call(self, mock_yf_ticker, client, sample_yfinance_data, clean_cache):
        """Test complete flow from API call to response with caching"""
        # Setup mock
        mock_ticker_instance = mock_yf_ticker.return_value
        mock_ticker_instance.history.return_value = sample_yfinance_data
        
        # First API call - should hit yfinance and cache result
        response1 = client.get("/ticker-return?ticker=AAPL&date=2024-01-02")
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["ticker"] == "AAPL"
        assert data1["date"] == "2024-01-02"
        assert abs(data1["return"] - ((155.0 - 150.0) / 150.0)) < 0.001
        
        # Verify yfinance was called
        mock_ticker_instance.history.assert_called_once()
        
        # Second API call - should hit cache
        mock_ticker_instance.history.reset_mock()
        response2 = client.get("/ticker-return?ticker=AAPL&date=2024-01-02")
        
        assert response2.status_code == 200
        assert response2.json() == data1
        
        # Verify yfinance was NOT called again (cache hit)
        mock_ticker_instance.history.assert_not_called()

    @pytest.mark.integration
    @patch('services.stock_data.yf.Ticker')
    def test_cache_and_stock_service_integration(self, mock_yf_ticker, sample_yfinance_data, clean_cache):
        """Test cache and stock service working together"""
        # Setup mock
        mock_ticker_instance = mock_yf_ticker.return_value
        mock_ticker_instance.history.return_value = sample_yfinance_data
        
        # Call service directly
        result1 = StockDataService.fetch_single_day_return("AAPL", "2024-01-02")
        
        # Verify result
        assert result1["ticker"] == "AAPL"
        assert result1["return"] is not None
        
        # Cache the result manually
        clean_cache.set("AAPL", "2024-01-02", result1)
        
        # Verify cache contains the data
        cached_result = clean_cache.get("AAPL", "2024-01-02")
        assert cached_result == result1

    @pytest.mark.integration
    @patch('services.stock_data.yf.Ticker')
    def test_multiple_tickers_same_date(self, mock_yf_ticker, client, sample_yfinance_data, clean_cache):
        """Test fetching multiple tickers for the same date"""
        # Setup mock to return data for any ticker
        mock_ticker_instance = mock_yf_ticker.return_value
        mock_ticker_instance.history.return_value = sample_yfinance_data
        
        tickers = ["AAPL", "MSFT", "GOOGL"]
        results = []
        
        for ticker in tickers:
            response = client.get(f"/ticker-return?ticker={ticker}&date=2024-01-02")
            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == ticker
            assert data["date"] == "2024-01-02"
            results.append(data)
        
        # All should have the same return (using same mock data)
        returns = [r["return"] for r in results]
        assert all(abs(r - returns[0]) < 0.001 for r in returns)

    @pytest.mark.integration
    @patch('services.stock_data.yf.Ticker')
    def test_api_error_handling_integration(self, mock_yf_ticker, client, clean_cache):
        """Test error handling through the entire stack"""
        # Setup mock to raise exception
        mock_ticker_instance = mock_yf_ticker.return_value
        mock_ticker_instance.history.side_effect = Exception("Network error")
        
        # API call should handle the exception gracefully
        response = client.get("/ticker-return?ticker=AAPL&date=2024-01-02")
        
        # The service catches exceptions and returns error data with 200 status
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "AAPL"
        assert data["date"] == "2024-01-02"
        assert data["return"] is None
        assert "Network error" in data["error"]

    @pytest.mark.integration
    def test_app_configuration_and_metadata(self, client):
        """Test that app is properly configured with correct metadata"""
        # Test that app metadata is correct
        response = client.get("/openapi.json")
        assert response.status_code == 200
        spec = response.json()
        assert spec["info"]["title"] == "MAG7 Stock Returns API"
        assert spec["info"]["version"] == "1.0.0"

    @pytest.mark.integration
    @patch('services.stock_data.yf.Ticker')
    def test_date_edge_cases_integration(self, mock_yf_ticker, client, sample_yfinance_data, clean_cache):
        """Test various date edge cases through the API"""
        mock_ticker_instance = mock_yf_ticker.return_value
        mock_ticker_instance.history.return_value = sample_yfinance_data
        
        # Test weekend date (should work with available data)
        response = client.get("/ticker-return?ticker=AAPL&date=2024-01-06")  # Saturday
        assert response.status_code == 200
        
        # Test holiday (depends on mock data)
        response = client.get("/ticker-return?ticker=AAPL&date=2024-01-01")  # New Year's Day
        assert response.status_code == 200

    @pytest.mark.integration
    def test_health_and_docs_integration(self, client):
        """Test that all standard endpoints work together"""
        # Health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # OpenAPI spec
        openapi_response = client.get("/openapi.json")
        assert openapi_response.status_code == 200
        
        # Swagger UI (docs)
        docs_response = client.get("/docs")
        assert docs_response.status_code == 200
        
        # ReDoc
        redoc_response = client.get("/redoc")
        assert redoc_response.status_code == 200

    @pytest.mark.integration
    @patch('services.stock_data.yf.Ticker')
    def test_concurrent_api_calls_integration(self, mock_yf_ticker, client, sample_yfinance_data, clean_cache):
        """Test concurrent API calls with caching"""
        import threading
        import time
        
        # Setup mock with a small delay to simulate real API
        mock_ticker_instance = mock_yf_ticker.return_value
        
        def slow_history(*args, **kwargs):
            time.sleep(0.1)  # Small delay
            return sample_yfinance_data
        
        mock_ticker_instance.history.side_effect = slow_history
        
        results = []
        errors = []
        
        def make_request(ticker, date):
            try:
                response = client.get(f"/ticker-return?ticker={ticker}&date={date}")
                results.append(response)
            except Exception as e:
                errors.append(e)
        
        # Make concurrent requests
        threads = []
        for i in range(5):
            t = threading.Thread(target=make_request, args=("AAPL", "2024-01-02"))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 5
        for response in results:
            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == "AAPL"
            assert data["date"] == "2024-01-02"