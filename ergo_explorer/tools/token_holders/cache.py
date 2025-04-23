"""
Cache management for token holder data

This module provides caching functionality to improve performance for
token holder analysis operations.
"""

# Cache structure
_CACHE = {
    "collections": {},  # Cache for collection metadata
    "nfts": {},         # Cache for collection NFTs
    "holders": {},      # Cache for holder data
    "tokens": {},       # Cache for token info
    "boxes": {}         # Cache for box data
}

def clear_cache():
    """Clear all cached data."""
    for cache_type in _CACHE:
        _CACHE[cache_type].clear()

def get_cache_stats():
    """Get statistics about the cache usage."""
    return {cache_type: len(items) for cache_type, items in _CACHE.items()} 