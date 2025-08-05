"""
Pytest configuration and shared fixtures
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_yfinance_ticker():
    """Mock yfinance Ticker for consistent testing"""
    with patch('services.stock_data.yf.Ticker') as mock_ticker_class:
        mock_ticker_instance = Mock()
        mock_ticker_class.return_value = mock_ticker_instance
        yield mock_ticker_instance


@pytest.fixture
def clean_cache():
    """Ensure cache is clean before each test"""
    from services.cache import cache_instance
    cache_instance.clear()
    yield cache_instance
    cache_instance.clear()


@pytest.fixture
def sample_return_data():
    """Standard sample return data for testing"""
    return {
        "ticker": "AAPL",
        "date": "2024-01-02",
        "return": 0.05,
        "price": 150.0,
        "previous_price": 142.86
    }


@pytest.fixture
def mag7_symbols():
    """MAG7 stock symbols for testing"""
    return ["MSFT", "AAPL", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]


# Pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (makes external API calls)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test patterns"""
    for item in items:
        # Add unit marker to all tests by default
        if not any(marker.name in ['integration', 'slow'] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to tests that likely make external calls
        if 'real_api' in item.name or 'external' in item.name:
            item.add_marker(pytest.mark.slow)


# Skip slow tests by default unless explicitly requested
def pytest_runtest_setup(item):
    """Skip slow tests unless --slow option is provided"""
    if 'slow' in [marker.name for marker in item.iter_markers()]:
        if not item.config.getoption('--slow', default=False):
            pytest.skip('Slow test skipped (use --slow to run)')


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--slow",
        action="store_true",
        default=False,
        help="Run slow tests that make external API calls"
    )