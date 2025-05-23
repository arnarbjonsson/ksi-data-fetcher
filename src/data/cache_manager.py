from diskcache import Cache
from datetime import datetime, timedelta
import os
import json
from typing import Any, Optional

class CacheManager:
    """Manages caching of API responses and web scraping results."""
    
    def __init__(self, cache_dir: str = "cache", ttl_days: int = 1):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_days: Number of days before cache entries expire
        """
        self.cache = Cache(cache_dir)
        self.ttl = ttl_days * 24 * 60 * 60  # Convert days to seconds
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        try:
            return self.cache.get(key)
        except Exception as e:
            print(f"Error reading from cache: {str(e)}")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Store a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        try:
            self.cache.set(key, value, expire=self.ttl)
        except Exception as e:
            print(f"Error writing to cache: {str(e)}")
    
    def build_key(self, *args: Any, **kwargs: Any) -> str:
        """
        Build a cache key from arguments.
        
        Example:
            >>> cache.build_key("tournaments", age_group=420, year=2024)
            "tournaments_age_group_420_year_2024"
        """
        # Start with positional arguments
        key_parts = [str(arg) for arg in args]
        
        # Add keyword arguments in sorted order
        for k, v in sorted(kwargs.items()):
            key_parts.extend([str(k), str(v)])
        
        return "_".join(key_parts)
    
    def clear(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
    
    def clear_expired(self) -> None:
        """Remove expired entries from cache."""
        self.cache.expire()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cache.close() 