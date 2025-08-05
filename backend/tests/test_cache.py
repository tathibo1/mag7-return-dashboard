import pytest
import time
from unittest.mock import patch

from services.cache import InMemoryCache


class TestInMemoryCache:
    
    @pytest.fixture
    def cache(self):
        """Create a fresh cache instance for each test"""
        return InMemoryCache(ttl_seconds=1, maxsize=5)  # Short TTL for testing
    
    @pytest.fixture
    def long_ttl_cache(self):
        """Create a cache with longer TTL for tests that don't need expiration"""
        return InMemoryCache(ttl_seconds=3600, maxsize=10)

    @pytest.mark.unit
    def test_cache_initialization_defaults(self):
        """Test cache initializes with default values"""
        cache = InMemoryCache()
        assert cache._cache.maxsize == 1000
        assert cache._cache.ttl == 3600

    @pytest.mark.unit
    def test_cache_initialization_custom(self):
        """Test cache initializes with custom values"""
        cache = InMemoryCache(ttl_seconds=1800, maxsize=500)
        assert cache._cache.maxsize == 500
        assert cache._cache.ttl == 1800

    @pytest.mark.unit
    def test_generate_key(self, cache):
        """Test key generation for ticker and date"""
        key = cache._generate_key("AAPL", "2024-01-01")
        assert key == "ticker:AAPL:2024-01-01"
        
        # Test with different inputs
        key2 = cache._generate_key("MSFT", "2024-12-31")
        assert key2 == "ticker:MSFT:2024-12-31"

    @pytest.mark.unit
    def test_set_and_get_basic(self, cache):
        """Test basic set and get operations"""
        # Set data
        test_data = {"return": 0.05, "price": 150.0}
        cache.set("AAPL", "2024-01-01", test_data)
        
        # Get data
        retrieved = cache.get("AAPL", "2024-01-01")
        assert retrieved == test_data

    @pytest.mark.unit
    def test_get_nonexistent_key(self, cache):
        """Test getting a key that doesn't exist"""
        result = cache.get("NONEXISTENT", "2024-01-01")
        assert result is None

    @pytest.mark.unit
    def test_cache_overwrite(self, cache):
        """Test overwriting existing cache entry"""
        # Set initial data
        initial_data = {"return": 0.05, "price": 150.0}
        cache.set("AAPL", "2024-01-01", initial_data)
        
        # Overwrite with new data
        new_data = {"return": 0.03, "price": 155.0}
        cache.set("AAPL", "2024-01-01", new_data)
        
        # Should return new data
        retrieved = cache.get("AAPL", "2024-01-01")
        assert retrieved == new_data

    @pytest.mark.unit
    def test_multiple_tickers_and_dates(self, long_ttl_cache):
        """Test storing multiple tickers and dates"""
        # Set data for multiple combinations
        cache = long_ttl_cache
        
        data1 = {"return": 0.05, "price": 150.0}
        data2 = {"return": 0.03, "price": 200.0}
        data3 = {"return": -0.02, "price": 145.0}
        
        cache.set("AAPL", "2024-01-01", data1)
        cache.set("MSFT", "2024-01-01", data2)
        cache.set("AAPL", "2024-01-02", data3)
        
        # Retrieve and verify
        assert cache.get("AAPL", "2024-01-01") == data1
        assert cache.get("MSFT", "2024-01-01") == data2
        assert cache.get("AAPL", "2024-01-02") == data3
        assert cache.get("MSFT", "2024-01-02") is None

    @pytest.mark.unit
    def test_cache_ttl_expiration(self, cache):
        """Test that cache entries expire after TTL"""
        # Set data with short TTL (1 second)
        test_data = {"return": 0.05, "price": 150.0}
        cache.set("AAPL", "2024-01-01", test_data)
        
        # Should be available immediately
        assert cache.get("AAPL", "2024-01-01") == test_data
        
        # Wait for expiration
        time.sleep(1.1)  # Wait slightly longer than TTL
        
        # Should be expired
        assert cache.get("AAPL", "2024-01-01") is None

    @pytest.mark.unit
    def test_cache_maxsize_eviction(self):
        """Test LRU eviction when cache exceeds maxsize"""
        # Create cache with small maxsize
        cache = InMemoryCache(ttl_seconds=3600, maxsize=3)
        
        # Fill cache to capacity
        cache.set("AAPL", "2024-01-01", {"data": "1"})
        cache.set("MSFT", "2024-01-01", {"data": "2"})
        cache.set("GOOGL", "2024-01-01", {"data": "3"})
        
        # All should be present
        assert cache.get("AAPL", "2024-01-01") == {"data": "1"}
        assert cache.get("MSFT", "2024-01-01") == {"data": "2"}
        assert cache.get("GOOGL", "2024-01-01") == {"data": "3"}
        
        # Add one more item (should evict least recently used)
        cache.set("AMZN", "2024-01-01", {"data": "4"})
        
        # AAPL should be evicted (least recently used)
        assert cache.get("AAPL", "2024-01-01") is None
        assert cache.get("MSFT", "2024-01-01") == {"data": "2"}
        assert cache.get("GOOGL", "2024-01-01") == {"data": "3"}
        assert cache.get("AMZN", "2024-01-01") == {"data": "4"}

    @pytest.mark.unit
    def test_cache_lru_behavior(self):
        """Test LRU (Least Recently Used) behavior"""
        cache = InMemoryCache(ttl_seconds=3600, maxsize=3)
        
        # Fill cache
        cache.set("AAPL", "2024-01-01", {"data": "1"})
        cache.set("MSFT", "2024-01-01", {"data": "2"})
        cache.set("GOOGL", "2024-01-01", {"data": "3"})
        
        # Access AAPL to make it recently used
        cache.get("AAPL", "2024-01-01")
        
        # Add new item (should evict MSFT, not AAPL)
        cache.set("AMZN", "2024-01-01", {"data": "4"})
        
        # AAPL should still be present, MSFT should be evicted
        assert cache.get("AAPL", "2024-01-01") == {"data": "1"}
        assert cache.get("MSFT", "2024-01-01") is None
        assert cache.get("GOOGL", "2024-01-01") == {"data": "3"}
        assert cache.get("AMZN", "2024-01-01") == {"data": "4"}

    @pytest.mark.unit
    def test_cache_clear(self, long_ttl_cache):
        """Test clearing the entire cache"""
        cache = long_ttl_cache
        
        # Add some data
        cache.set("AAPL", "2024-01-01", {"data": "1"})
        cache.set("MSFT", "2024-01-01", {"data": "2"})
        cache.set("GOOGL", "2024-01-01", {"data": "3"})
        
        # Verify data is present
        assert cache.get("AAPL", "2024-01-01") is not None
        assert cache.get("MSFT", "2024-01-01") is not None
        assert cache.get("GOOGL", "2024-01-01") is not None
        
        # Clear cache
        cache.clear()
        
        # All data should be gone
        assert cache.get("AAPL", "2024-01-01") is None
        assert cache.get("MSFT", "2024-01-01") is None
        assert cache.get("GOOGL", "2024-01-01") is None

    @pytest.mark.unit
    def test_cache_with_complex_data(self, long_ttl_cache):
        """Test caching complex data structures"""
        cache = long_ttl_cache
        
        complex_data = {
            "ticker": "AAPL",
            "date": "2024-01-01",
            "return": 0.05,
            "price": 150.75,
            "previous_price": 143.57,
            "metadata": {
                "volume": 1500000,
                "high": 152.0,
                "low": 149.0
            },
            "tags": ["tech", "large-cap", "dividend"]
        }
        
        cache.set("AAPL", "2024-01-01", complex_data)
        retrieved = cache.get("AAPL", "2024-01-01")
        
        assert retrieved == complex_data
        assert retrieved["metadata"]["volume"] == 1500000
        assert "tech" in retrieved["tags"]

    @pytest.mark.unit
    def test_cache_none_values(self, long_ttl_cache):
        """Test caching None values"""
        cache = long_ttl_cache
        
        # Cache None value (valid for errors/no data)
        cache.set("INVALID", "2024-01-01", None)
        
        # Should return None, not indicate missing key
        retrieved = cache.get("INVALID", "2024-01-01")
        assert retrieved is None
        
        # But it should be different from a truly missing key
        # (This test shows the limitation - both return None)
        # In practice, you'd cache error objects instead of None

    @pytest.mark.unit
    def test_cache_thread_safety_basic(self, long_ttl_cache):
        """Basic test for cache operations (cachetools.TTLCache is thread-safe)"""
        cache = long_ttl_cache
        
        # This is a basic test - for full thread safety testing,
        # you'd need concurrent thread operations
        import threading
        
        def worker(thread_id):
            for i in range(10):
                cache.set(f"THREAD{thread_id}", f"2024-01-{i:02d}", {"thread": thread_id, "data": i})
        
        threads = []
        for i in range(3):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify some data made it through
        found_data = 0
        for thread_id in range(3):
            for day in range(10):
                if cache.get(f"THREAD{thread_id}", f"2024-01-{day:02d}") is not None:
                    found_data += 1
        
        assert found_data > 0  # At least some operations succeeded

    @pytest.mark.unit
    def test_cache_instance_singleton(self):
        """Test that the cache_instance is properly imported"""
        from services.cache import cache_instance
        
        # Should be an InMemoryCache instance
        assert isinstance(cache_instance, InMemoryCache)
        
        # Should have default configuration
        assert cache_instance._cache.ttl == 3600
        assert cache_instance._cache.maxsize == 1000