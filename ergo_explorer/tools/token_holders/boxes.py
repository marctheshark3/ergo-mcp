"""
Box operations

This module provides functionality for working with Ergo boxes.
"""

from typing import Dict, List
from ergo_explorer.logging_config import get_logger
from .api import fetch_node_api
from .cache import _CACHE

# Get module-specific logger
logger = get_logger("token_holders.boxes")

async def get_box_by_id(box_id: str) -> Dict:
    """
    Get a box by ID with caching support.
    
    Args:
        box_id: Box ID to fetch
        
    Returns:
        Box data
    """
    # Check cache first
    if box_id in _CACHE["boxes"]:
        logger.debug(f"Cache hit for box {box_id}")
        return _CACHE["boxes"][box_id]
    
    result = await fetch_node_api(f"blockchain/box/byId/{box_id}")
    
    # Add result to cache
    if "error" not in result:
        _CACHE["boxes"][box_id] = result
        
    return result

async def get_boxes_by_token_id(token_id: str, offset: int = 0, limit: int = 100) -> List[Dict]:
    """
    Get all boxes (spent and unspent) containing a specific token.
    
    Args:
        token_id: Token ID to search for
        offset: Pagination offset
        limit: Maximum number of boxes to return
        
    Returns:
        List of boxes containing the token
    """
    response = await fetch_node_api(
        f"blockchain/box/byTokenId/{token_id}",
        params={"offset": offset, "limit": limit}
    )
    
    # Handle both array and error responses
    if isinstance(response, dict) and "items" in response:
        return response.get("items", [])
    elif "error" in response:
        logger.error(f"Error fetching boxes: {response.get('error')}")
        return []
    else:
        return response

async def get_unspent_boxes_by_token_id(token_id: str, offset: int = 0, limit: int = 100) -> List[Dict]:
    """
    Get unspent boxes containing a specific token.
    
    Args:
        token_id: Token ID to search for
        offset: Pagination offset
        limit: Maximum number of boxes to return
        
    Returns:
        List of unspent boxes containing the token
    """
    response = await fetch_node_api(
        f"blockchain/box/unspent/byTokenId/{token_id}",
        params={"offset": offset, "limit": limit}
    )
    
    # Handle both array and error responses
    if isinstance(response, list):
        return response
    elif "error" in response:
        logger.error(f"Error fetching unspent boxes: {response.get('error')}")
        return []
    else:
        return response 