"""
Response format standardization for the Ergo Explorer MCP.
This module provides consistent response structures for all MCP endpoints.
"""

import time
import json
from typing import Any, Dict, List, Optional, Union
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class ResponseMetadata:
    """Metadata for MCP responses including timing and sizing information."""
    
    def __init__(self):
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.execution_time_ms: Optional[float] = None
        self.result_count: Optional[int] = None
        self.result_size_bytes: Optional[int] = None
        self.is_truncated: bool = False
        self.original_count: Optional[int] = None
        self.token_estimate: Optional[int] = None
    
    def finish(self):
        """Mark the end of processing and calculate execution time."""
        self.end_time = time.time()
        self.execution_time_ms = round((self.end_time - self.start_time) * 1000, 2)
    
    def set_result_metrics(self, result: Any, is_truncated: bool = False, 
                           original_count: Optional[int] = None):
        """Set metrics about the result size."""
        if isinstance(result, list):
            self.result_count = len(result)
        
        # Estimate result size in bytes
        try:
            result_json = json.dumps(result)
            self.result_size_bytes = len(result_json.encode('utf-8'))
            # Very rough token estimate: ~4 chars per token
            self.token_estimate = len(result_json) // 4
        except (TypeError, ValueError) as e:
            logger.warning(f"Could not calculate result size: {e}")
        
        self.is_truncated = is_truncated
        self.original_count = original_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "execution_time_ms": self.execution_time_ms,
            "result_count": self.result_count,
            "result_size_bytes": self.result_size_bytes,
            "is_truncated": self.is_truncated,
            "original_count": self.original_count if self.is_truncated else None,
            "token_estimate": self.token_estimate
        }


class MCPResponse:
    """Standard response format for MCP endpoints."""
    
    def __init__(self, data: Any = None, status: str = "success", 
                 message: Optional[str] = None):
        self.status = status
        self.data = data
        self.message = message
        self.metadata = ResponseMetadata()
    
    def finish(self, is_truncated: bool = False, original_count: Optional[int] = None):
        """Finalize the response by setting metadata."""
        self.metadata.finish()
        self.metadata.set_result_metrics(self.data, is_truncated, original_count)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format."""
        return {
            "status": self.status,
            "data": self.data,
            "message": self.message,
            "metadata": self.metadata.to_dict()
        }
    
    def to_minimal_dict(self) -> Dict[str, Any]:
        """Convert to minimal dictionary format (without metadata)."""
        return {
            "status": self.status,
            "data": self.data,
            "message": self.message
        }


def standardize_response(func):
    """Decorator to standardize function responses."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = MCPResponse()
        
        try:
            # Extract limit parameter if provided
            limit = kwargs.get('limit', None)
            
            # Call the original function
            result = func(*args, **kwargs)
            
            # If result is already an MCPResponse, return it
            if isinstance(result, MCPResponse):
                return result
            
            # Handle different return types
            if isinstance(result, tuple) and len(result) == 2:
                # Assuming (data, is_truncated) format
                data, is_truncated = result
                response.data = data
                response.finish(is_truncated=is_truncated)
            else:
                # Standard data return
                response.data = result
                response.finish()
            
            return response
            
        except Exception as e:
            logger.exception(f"Error in {func.__name__}: {str(e)}")
            response.status = "error"
            response.message = str(e)
            response.finish()
            return response
    
    return wrapper


def smart_limit(data: List[Any], limit: Optional[int] = None) -> tuple[List[Any], bool]:
    """Apply smart limiting to result data.
    
    Args:
        data: The list data to potentially limit
        limit: Maximum number of items to return
        
    Returns:
        Tuple of (limited_data, is_truncated)
    """
    if limit is None or not isinstance(data, list):
        return data, False
    
    if len(data) <= limit:
        return data, False
    
    return data[:limit], True


def format_response(response: Union[MCPResponse, Dict, Any], 
                    verbose: bool = True) -> Dict[str, Any]:
    """Format a response based on verbosity settings.
    
    Args:
        response: The response object or data
        verbose: Whether to include metadata
        
    Returns:
        Formatted response dictionary
    """
    if isinstance(response, MCPResponse):
        return response.to_dict() if verbose else response.to_minimal_dict()
    
    if isinstance(response, dict) and "status" in response and "data" in response:
        # Already formatted as a response dict
        return response
    
    # Create a new response with the provided data
    mcp_response = MCPResponse(data=response)
    mcp_response.finish()
    
    return mcp_response.to_dict() if verbose else mcp_response.to_minimal_dict() 