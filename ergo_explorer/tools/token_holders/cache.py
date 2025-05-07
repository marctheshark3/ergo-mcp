"""
Cache management for token holder data

This module provides caching functionality to improve performance for
token holder analysis operations.
"""
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path
from ergo_explorer.logging_config import get_logger
from ergo_explorer.config import CACHE_TIMEOUT

# Get module-specific logger
logger = get_logger("token_holders.cache")

# Cache structure
_CACHE = {
    "collections": {},  # Cache for collection metadata
    "nfts": {},         # Cache for collection NFTs
    "holders": {},      # Cache for holder data
    "tokens": {},       # Cache for token info
    "boxes": {},        # Cache for box data
    "history": {}       # Cache for historical token holder data
}

def clear_cache():
    """Clear all cached data."""
    for cache_type in _CACHE:
        _CACHE[cache_type].clear()

def get_cache_stats():
    """Get statistics about the cache usage."""
    return {cache_type: len(items) for cache_type, items in _CACHE.items()}

def get_cache_dir() -> Path:
    """
    Get the directory for persistent cache files.
    
    Returns:
        Path to the cache directory
    """
    cache_dir = Path("cache/token_holders")
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def get_history_cache_dir() -> Path:
    """
    Get the directory for historical token holder data.
    
    Returns:
        Path to the history cache directory
    """
    history_dir = get_cache_dir() / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    return history_dir

def save_token_history_to_disk(token_id: str, history_data: Dict[str, Any]) -> bool:
    """
    Save token history data to a persistent cache file.
    
    Args:
        token_id: The token ID
        history_data: The token history data to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create cache directory if it doesn't exist
        cache_dir = get_history_cache_dir()
        
        # Create a file path for this token's history
        file_path = cache_dir / f"{token_id}.json"
        
        # Write the data to disk with pretty formatting
        with open(file_path, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        logger.debug(f"Successfully saved token history for {token_id} to disk")
        return True
    
    except Exception as e:
        logger.error(f"Error saving token history for {token_id} to disk: {str(e)}")
        return False

def load_token_history_from_disk(token_id: str) -> Optional[Dict[str, Any]]:
    """
    Load token history data from a persistent cache file.
    
    Args:
        token_id: The token ID
        
    Returns:
        The token history data if found, None otherwise
    """
    try:
        # Get the file path for this token's history
        cache_dir = get_history_cache_dir()
        file_path = cache_dir / f"{token_id}.json"
        
        # Check if the file exists
        if not file_path.exists():
            logger.debug(f"No token history file found for {token_id}")
            return None
        
        # Read the data from disk
        with open(file_path, 'r') as f:
            history_data = json.load(f)
        
        logger.debug(f"Successfully loaded token history for {token_id} from disk")
        return history_data
    
    except Exception as e:
        logger.error(f"Error loading token history for {token_id} from disk: {str(e)}")
        return None

def get_historical_data_size() -> Dict[str, Any]:
    """
    Get statistics about the historical data storage.
    
    Returns:
        A dictionary with statistics about stored historical data
    """
    try:
        # Get the history cache directory
        history_dir = get_history_cache_dir()
        
        # Find all the history files
        history_files = list(history_dir.glob("*.json"))
        
        # Calculate sizes
        total_size = sum(f.stat().st_size for f in history_files)
        
        # Get details about each file
        file_details = []
        for f in history_files:
            file_details.append({
                "token_id": f.stem,
                "size_bytes": f.stat().st_size,
                "last_modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
        
        # Sort by size (largest first)
        file_details.sort(key=lambda x: x["size_bytes"], reverse=True)
        
        return {
            "total_files": len(history_files),
            "total_size_bytes": total_size,
            "files": file_details
        }
    
    except Exception as e:
        logger.error(f"Error getting historical data size: {str(e)}")
        return {
            "error": str(e),
            "total_files": 0,
            "total_size_bytes": 0,
            "files": []
        } 