from cachetools import TTLCache
from typing import Any, Optional


class InMemoryCache:
    def __init__(self, ttl_seconds: int = 3600, maxsize: int = 1000):
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl_seconds)  # eviction strategy: LRU + TTL
    
    def _generate_key(self, ticker: str, date: str) -> str:
        return f"ticker:{ticker}:{date}"
    
    def get(self, ticker: str, date: str) -> Optional[Any]:
        key = self._generate_key(ticker, date)
        return self._cache.get(key)
    
    def set(self, ticker: str, date: str, data: Any) -> None:
        key = self._generate_key(ticker, date)
        self._cache[key] = data
    
    def clear(self) -> None:
        self._cache.clear()


cache_instance = InMemoryCache()