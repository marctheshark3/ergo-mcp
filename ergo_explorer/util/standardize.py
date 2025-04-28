"""
Response standardization decorator and related utilities.

This module provides functionality for standardizing API responses
across the entire Ergo Explorer MCP project.
"""

import time
import functools
import logging
from typing import Dict, Any, Callable, TypeVar, cast

logger = logging.getLogger(__name__)

# Type variable for function annotations
F = TypeVar('F', bound=Callable[..., Dict[str, Any]])

def standardize_response(func: F) -> F:
    """
    Decorator to ensure all API responses follow the standard format.
    
    The standard format is:
    {
        "status": "success" | "error",
        "data": {...},  # The actual response data
        "metadata": {
            "execution_time": float,  # Time in seconds
            "result_size": int,       # Size of the result
            "timestamp": str,         # ISO timestamp
            ...                       # Any additional metadata
        }
    }
    
    If the decorated function already returns data in this format,
    this decorator will not modify it.
    
    Args:
        func: The function to decorate
        
    Returns:
        A decorated function that ensures standardized response format
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # If the result is already in the standard format, return it
            if (isinstance(result, dict) and 
                "status" in result and 
                "data" in result and 
                "metadata" in result):
                
                # Ensure execution_time is included in metadata if not already
                if "execution_time" not in result["metadata"]:
                    result["metadata"]["execution_time"] = execution_time
                
                # Ensure timestamp is included in metadata
                if "timestamp" not in result["metadata"]:
                    result["metadata"]["timestamp"] = timestamp
                    
                return result
            
            # Otherwise, wrap the result in the standard format
            result_size = len(str(result)) if result is not None else 0
            
            standardized_result = {
                "status": "success",
                "data": result,
                "metadata": {
                    "execution_time": execution_time,
                    "result_size": result_size,
                    "timestamp": timestamp
                }
            }
            
            return standardized_result
            
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            execution_time = time.time() - start_time
            
            error_response = {
                "status": "error",
                "data": {
                    "message": str(e),
                    "error_type": e.__class__.__name__
                },
                "metadata": {
                    "execution_time": execution_time,
                    "result_size": 0,
                    "timestamp": timestamp
                }
            }
            
            return error_response
    
    return cast(F, wrapper)

def format_error_response(message: str, error_type: str = "GeneralError") -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        error_type: Type of error
        
    Returns:
        Standardized error response dictionary
    """
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    return {
        "status": "error",
        "data": {
            "message": message,
            "error_type": error_type
        },
        "metadata": {
            "execution_time": 0,  # This will be 0 since we're not timing anything
            "result_size": 0,
            "timestamp": timestamp
        }
    }

def format_success_response(data: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        metadata: Additional metadata (optional)
        
    Returns:
        Standardized success response dictionary
    """
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # Default metadata
    default_metadata = {
        "execution_time": 0,  # This will be 0 since we're not timing anything
        "result_size": len(str(data)),
        "timestamp": timestamp
    }
    
    # Merge with custom metadata if provided
    if metadata:
        default_metadata.update(metadata)
    
    return {
        "status": "success",
        "data": data,
        "metadata": default_metadata
    }

class StandardizationError(Exception):
    """
    Exception raised for errors in response standardization.
    """
    pass 