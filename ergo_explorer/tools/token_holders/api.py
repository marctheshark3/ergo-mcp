"""
API access functions

This module provides functionality to interact with the Ergo Node API and Explorer API.
"""

import os
import asyncio
import httpx
import functools
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from ergo_explorer.logging_config import get_logger

# Get module-specific logger
logger = get_logger("token_holders.api")

# Default configuration
NODE_API = os.environ.get("ERGO_NODE_API", "http://localhost:9053")
NODE_API_KEY = os.environ.get("ERGO_NODE_API_KEY", "")
EXPLORER_API = os.environ.get("ERGO_EXPLORER_API", "https://api.ergoplatform.com/api/v1")
USER_AGENT = "ErgoExplorerMCP/1.0"

def with_retry(max_retries=3, delay=1):
    """
    Decorator for API calls that implements exponential backoff and retries.
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e) or "rate limit" in str(e).lower():
                        # Rate limited - implement backoff
                        retries += 1
                        if retries < max_retries:
                            logger.warning(f"Rate limited, retrying in {current_delay}s... ({retries}/{max_retries})")
                            await asyncio.sleep(current_delay)
                            current_delay *= 2  # Exponential backoff
                        else:
                            logger.error(f"Max retries reached for API call")
                            raise
                    else:
                        # Different error, don't retry
                        raise
        return wrapper
    return decorator

async def fetch_node_api(endpoint: str, params: Optional[Dict] = None, method: str = "GET", json_data: Optional[Dict] = None) -> Dict:
    """Make a request to the Ergo Node API."""
    url = f"{NODE_API}/{endpoint}"
    logger.debug(f"Requesting: {url} with method={method}, params={params}")
    
    async with httpx.AsyncClient() as client:
        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json"
        }
        
        # Add API key if available
        if NODE_API_KEY:
            headers["api_key"] = NODE_API_KEY
            
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            elif method == "POST":
                response = await client.post(url, headers=headers, params=params, json=json_data, timeout=30.0)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            # Log response status
            logger.debug(f"Response status: {response.status_code}")
            
            # Check for error status codes
            response.raise_for_status()
            
            # Parse JSON response
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            logger.error(f"Error in fetch_node_api: {str(e)}")
            return {"error": str(e)}

@with_retry(max_retries=3, delay=1)
async def fetch_explorer_api(endpoint: str, params: Optional[Dict] = None) -> Dict:
    """Make a request to the Ergo Explorer API."""
    url = f"{EXPLORER_API}/{endpoint}"
    logger.debug(f"Requesting Explorer API: {url} with params={params}")
    
    async with httpx.AsyncClient() as client:
        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json"
        }
            
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
                
            # Log response status
            logger.debug(f"Explorer API response status: {response.status_code}")
            
            # Check for error status codes
            response.raise_for_status()
            
            # Parse JSON response
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Explorer API: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            logger.error(f"Error in fetch_explorer_api: {str(e)}")
            return {"error": str(e)} 