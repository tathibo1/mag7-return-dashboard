from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import hashlib
import json


class InMemoryCache:
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)
    
    def _generate_key(self, start_date: str, end_date: str) -> str:
        key_string = f"returns:{start_date}:{end_date}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        key = self._generate_key(start_date, end_date)
        
        if key in self._cache:
            entry = self._cache[key]
            if datetime.now() < entry["expires_at"]:
                return entry["data"]
            else:
                del self._cache[key]
        
        return None
    
    def set(self, start_date: str, end_date: str, data: Dict[str, Any]) -> None:
        key = self._generate_key(start_date, end_date)
        self._cache[key] = {
            "data": data,
            "expires_at": datetime.now() + self._ttl
        }
    
    def clear(self) -> None:
        self._cache.clear()


cache_instance = InMemoryCache()