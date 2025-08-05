import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import date, datetime
import asyncio

from fastapi.testclient import TestClient
import httpx

from app import app


class TestFastAPIEndpoints:
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app"""
        return TestClient(app)

    @pytest.fixture
    def sample_stock_data(self):
        """Sample stock return data"""
        return {
            "ticker": "AAPL",
            "date": "2024-01-02",
            "return": 0.05,
            "price": 150.0,
            "previous_price": 142.86
        }

    @pytest.fixture
    def error_stock_data(self):
        """Sample error response from stock service"""
        return {
            "ticker": "INVALID",
            "date": "2024-01-02",
            "return": None,
            "error": "No data available"
        }

    @pytest.mark.unit
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    @pytest.mark.unit
    @patch('app.cache_instance.get')
    @patch('app.StockDataService.fetch_single_day_return')
    @patch('app.cache_instance.set')
    def test_get_ticker_return_success(self, mock_cache_set, mock_fetch, mock_cache_get, client, sample_stock_data):
        """Test successful ticker return endpoint"""
        # Setup mocks
        mock_cache_get.return_value = None  # Cache miss
        mock_fetch.return_value = sample_stock_data
        
        # Make request
        response = client.get("/ticker-return?ticker=AAPL&date=2024-01-02")
        
        # Assert response
        assert response.status_code == 200
        assert response.json() == sample_stock_data
        
        # Verify cache interactions
        mock_cache_get.assert_called_once_with("AAPL", "2024-01-02")
        mock_fetch.assert_called_once_with("AAPL", "2024-01-02")
        mock_cache_set.assert_called_once_with("AAPL", "2024-01-02", sample_stock_data)

    @pytest.mark.unit
    @patch('app.cache_instance.get')
    def test_get_ticker_return_cache_hit(self, mock_cache_get, client, sample_stock_data):
        """Test ticker return endpoint with cache hit"""
        # Setup cache hit
        mock_cache_get.return_value = sample_stock_data
        
        with patch('app.StockDataService.fetch_single_day_return') as mock_fetch:
            # Make request
            response = client.get("/ticker-return?ticker=AAPL&date=2024-01-02")
            
            # Assert response
            assert response.status_code == 200
            assert response.json() == sample_stock_data
            
            # Verify cache hit (no fetch called)
            mock_cache_get.assert_called_once_with("AAPL", "2024-01-02")
            mock_fetch.assert_not_called()

    @pytest.mark.unit
    def test_get_ticker_return_missing_ticker(self, client):
        """Test ticker return endpoint with missing ticker parameter"""
        response = client.get("/ticker-return?date=2024-01-02")
        
        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"]
        assert any("ticker" in str(error).lower() for error in error_detail)

    @pytest.mark.unit
    def test_get_ticker_return_missing_date(self, client):
        """Test ticker return endpoint with missing date parameter"""
        response = client.get("/ticker-return?ticker=AAPL")
        
        assert response.status_code == 422  # Validation error
        error_detail = response.json()["detail"]
        assert any("date" in str(error).lower() for error in error_detail)

    @pytest.mark.unit
    def test_get_ticker_return_invalid_date_format(self, client):
        """Test ticker return endpoint with invalid date format"""
        response = client.get("/ticker-return?ticker=AAPL&date=invalid-date")
        
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]

    @pytest.mark.unit
    def test_get_ticker_return_future_date(self, client):
        """Test ticker return endpoint with future date"""
        future_date = "2030-01-01"
        response = client.get(f"/ticker-return?ticker=AAPL&date={future_date}")
        
        assert response.status_code == 400
        assert "Date cannot be in the future" in response.json()["detail"]

    @pytest.mark.unit
    @patch('app.cache_instance.get')
    @patch('app.StockDataService.fetch_single_day_return')
    def test_get_ticker_return_service_exception(self, mock_fetch, mock_cache_get, client):
        """Test ticker return endpoint when service raises exception"""
        # Setup mocks
        mock_cache_get.return_value = None
        mock_fetch.side_effect = Exception("Service error")
        
        # Make request
        response = client.get("/ticker-return?ticker=AAPL&date=2024-01-02")
        
        # Assert error response
        assert response.status_code == 500
        assert "Error fetching stock data: Service error" in response.json()["detail"]

    @pytest.mark.unit
    @patch('app.cache_instance.get')
    @patch('app.StockDataService.fetch_single_day_return')
    @patch('app.cache_instance.set')
    def test_get_ticker_return_ticker_case_insensitive(self, mock_cache_set, mock_fetch, mock_cache_get, client, sample_stock_data):
        """Test that ticker is converted to uppercase"""
        # Setup mocks
        mock_cache_get.return_value = None
        mock_fetch.return_value = sample_stock_data
        
        # Make request with lowercase ticker
        response = client.get("/ticker-return?ticker=aapl&date=2024-01-02")
        
        # Assert response
        assert response.status_code == 200
        
        # Verify uppercase conversion
        mock_cache_get.assert_called_once_with("AAPL", "2024-01-02")
        mock_fetch.assert_called_once_with("AAPL", "2024-01-02")

    @pytest.mark.unit
    @patch('app.cache_instance.get')
    @patch('app.StockDataService.fetch_single_day_return')
    def test_get_ticker_return_with_error_data(self, mock_fetch, mock_cache_get, client, error_stock_data):
        """Test ticker return endpoint when service returns error data"""
        # Setup mocks
        mock_cache_get.return_value = None
        mock_fetch.return_value = error_stock_data
        
        # Make request
        response = client.get("/ticker-return?ticker=INVALID&date=2024-01-02")
        
        # Should still return 200 with error data (not HTTP error)
        assert response.status_code == 200
        assert response.json() == error_stock_data
        assert response.json()["return"] is None
        assert "error" in response.json()

    @pytest.mark.unit
    def test_get_ticker_return_date_boundary_today(self, client):
        """Test ticker return endpoint with today's date"""
        today = date.today().strftime("%Y-%m-%d")
        
        with patch('app.cache_instance.get') as mock_cache_get, \
             patch('app.StockDataService.fetch_single_day_return') as mock_fetch:
            
            mock_cache_get.return_value = None
            mock_fetch.return_value = {"ticker": "AAPL", "date": today, "return": 0.01}
            
            response = client.get(f"/ticker-return?ticker=AAPL&date={today}")
            
            # Should be allowed (today is not in the future)
            assert response.status_code == 200


    @pytest.mark.unit
    @patch('app.cache_instance.get')
    @patch('app.StockDataService.fetch_single_day_return')
    def test_concurrent_requests(self, mock_fetch, mock_cache_get, client, sample_stock_data):
        """Test handling of concurrent requests to the same endpoint"""
        # Setup mocks
        mock_cache_get.return_value = None
        mock_fetch.return_value = sample_stock_data
        
        # Make multiple concurrent requests
        import threading
        results = []
        
        def make_request():
            response = client.get("/ticker-return?ticker=AAPL&date=2024-01-02")
            results.append(response)
        
        threads = []
        for _ in range(5):
            t = threading.Thread(target=make_request)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All requests should succeed
        assert len(results) == 5
        for response in results:
            assert response.status_code == 200
            assert response.json() == sample_stock_data

    @pytest.mark.unit
    def test_special_characters_in_ticker(self, client):
        """Test handling of special characters in ticker parameter"""
        # Test with some edge cases
        test_cases = [
            "BRK.A",  # Common format with dot
            "BRK-A",  # Format with dash
        ]
        
        with patch('app.cache_instance.get') as mock_cache_get, \
             patch('app.StockDataService.fetch_single_day_return') as mock_fetch:
            
            mock_cache_get.return_value = None
            mock_fetch.return_value = {"ticker": "TEST", "date": "2024-01-02", "return": 0.01}
            
            for ticker in test_cases:
                response = client.get(f"/ticker-return?ticker={ticker}&date=2024-01-02")
                # Should not crash, though specific behavior depends on yfinance
                assert response.status_code in [200, 500]  # Either works or service error

    @pytest.mark.integration
    def test_app_startup_and_shutdown(self, client):
        """Test that the app can start up and shut down properly"""
        # This is tested implicitly by other tests, but we can add explicit checks
        response = client.get("/health")
        assert response.status_code == 200
        
        # Test that we can make multiple requests
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200

    @pytest.mark.unit
    def test_endpoint_documentation(self, client):
        """Test that OpenAPI documentation is available"""
        # FastAPI automatically provides these endpoints
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        # Check that our endpoint is documented
        openapi_spec = response.json()
        assert "/ticker-return" in openapi_spec["paths"]
        assert "get" in openapi_spec["paths"]["/ticker-return"]

    @pytest.mark.unit
    def test_request_validation_comprehensive(self, client):
        """Comprehensive test of request parameter validation"""
        test_cases = [
            # Missing both parameters
            {"url": "/ticker-return", "expected_status": 422},
            # Invalid date formats
            {"url": "/ticker-return?ticker=AAPL&date=2024/01/02", "expected_status": 400},
            {"url": "/ticker-return?ticker=AAPL&date=01-02-2024", "expected_status": 400},
            {"url": "/ticker-return?ticker=AAPL&date=2024-13-01", "expected_status": 400},
            {"url": "/ticker-return?ticker=AAPL&date=2024-01-32", "expected_status": 400},
            # Empty ticker parameter - FastAPI treats this as valid but service returns error
            {"url": "/ticker-return?ticker=&date=2024-01-02", "expected_status": 200},
            # Empty date parameter - FastAPI validation returns 400 for invalid date format
            {"url": "/ticker-return?ticker=AAPL&date=", "expected_status": 400},
        ]
        
        for case in test_cases:
            response = client.get(case["url"])
            assert response.status_code == case["expected_status"], f"Failed for URL: {case['url']}"
            
            # For empty ticker, verify it returns error data but 200 status
            if "ticker=&" in case["url"]:
                data = response.json()
                assert data["return"] is None
                assert "error" in data