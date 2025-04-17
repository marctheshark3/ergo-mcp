"""
Token operations

This module provides functionality for working with Ergo tokens.
"""

from typing import Dict
from ergo_explorer.logging_config import get_logger
from .api import fetch_node_api
from .cache import _CACHE

# Get module-specific logger
logger = get_logger("token_holders.tokens")

async def get_token_by_id(token_id: str) -> Dict:
    """
    Get token information by ID with caching support.
    
    Args:
        token_id: Token ID to fetch
        
    Returns:
        Token information
    """
    # Check cache first
    if token_id in _CACHE["tokens"]:
        logger.debug(f"Cache hit for token {token_id}")
        return _CACHE["tokens"][token_id]
    
    result = await fetch_node_api(f"blockchain/token/byId/{token_id}")
    
    # Add result to cache
    if "error" not in result:
        _CACHE["tokens"][token_id] = result
        
    return result 