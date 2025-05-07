"""
Common utilities for Ergo Explorer tools.

This module contains shared utilities and decorators used across the Ergo Explorer codebase.
"""

import logging
import functools
import inspect
from typing import Any, Dict, Callable, Awaitable

# Get logger
logger = logging.getLogger(__name__)

def standardize_response(func):
    """
    Decorator to standardize the response format of functions.
    
    This ensures that all API responses follow a consistent structure.
    
    Args:
        func: The async function to decorate
        
    Returns:
        Decorated function that standardizes its output
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Call the original function
            result = await func(*args, **kwargs)
            
            # Process the result based on its type
            if isinstance(result, dict):
                # Add standard metadata
                if "success" not in result:
                    result["success"] = True
                if "error" not in result:
                    result["error"] = None
                return result
            else:
                # Non-dict responses are wrapped
                logger.error(f"Unknown response type for standardization.")
                return {
                    "success": True,
                    "error": None,
                    "data": result
                }
                
        except Exception as e:
            # Capture and standardize errors
            logger.exception(f"Error in {func.__name__}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
            
    return wrapper 