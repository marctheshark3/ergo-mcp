"""
Response format standardization for the Ergo Explorer MCP.
This module provides consistent response structures for all MCP endpoints.

The module implements:
- A standard response format with status, data, and metadata sections
- Response metadata with timing, sizing, and token estimation
- Decorator for automatic response standardization
- Token estimation based on model type (Claude, GPT, etc.)
- Response truncation capabilities based on token thresholds

Token estimation features:
- Each response includes an estimate of its token count for various LLM models
- Breakdown of tokens by response section (data, metadata, status)
- Support for model-specific token counting (claude, gpt-4, etc.)
- Configurable truncation thresholds to limit response size
- Graceful fallback if tiktoken library is not available
"""

import time
import json
from typing import Any, Dict, List, Optional, Union
import logging
from functools import wraps

# Import the token counter
try:
    from ergo_explorer.util.token_counter import count_json_tokens, estimate_response_tokens
    TOKEN_COUNTER_AVAILABLE = True
except ImportError:
    TOKEN_COUNTER_AVAILABLE = False

logger = logging.getLogger(__name__)

class ResponseMetadata:
    """
    Metadata for MCP responses including timing, sizing, and token estimation.
    
    This class tracks:
    - Execution time of endpoint processing
    - Result size in bytes for the response
    - Whether the response was truncated to fit within limits
    - Token estimate for the response (for LLM consumption)
    - Breakdown of tokens by response section
    
    Token estimation is performed for the chosen model type, with Claude
    as the default model. Token estimation helps AI assistants optimize
    their context window usage when consuming API responses.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.execution_time_ms: Optional[float] = None
        self.result_count: Optional[int] = None
        self.result_size_bytes: Optional[int] = None
        self.is_truncated: bool = False
        self.token_estimate: Optional[int] = None
        self.token_breakdown: Optional[Dict[str, int]] = None
        self.model_type: str = "claude"  # Default model for token estimation
    
    def finish(self):
        """
        Complete the timing measurement for the response.
        
        This calculates the execution time in milliseconds based on the
        elapsed time since initialization.
        """
        self.end_time = time.time()
        self.execution_time_ms = round((self.end_time - self.start_time) * 1000, 2)
    
    def set_result_metrics(self, data: Any, is_truncated: bool = False, size_bytes: Optional[int] = None, model_type: Optional[str] = None):
        """
        Set metrics related to the response data size and token estimation.
        
        This method:
        - Sets the result size in bytes (calculated if not provided)
        - Records if the response was truncated
        - Estimates token count for the data
        - Calculates a breakdown of tokens by section
        
        Args:
            data: The response data to analyze
            is_truncated: Whether the response was truncated
            size_bytes: Size of the response in bytes (calculated if None)
            model_type: LLM model type to use for token estimation (e.g., "claude", "gpt-4")
                If None, uses the model_type set in the instance
        """
        # Set truncation flag
        self.is_truncated = is_truncated
        
        # Use provided model type or instance default
        model = model_type or self.model_type
        
        # Calculate size if not provided
        if size_bytes is None:
            try:
                size_bytes = len(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            except Exception:
                size_bytes = 0
        
        self.result_size_bytes = size_bytes
        
        # If data is a collection, record the count
        if isinstance(data, list):
            self.result_count = len(data)
        elif isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            self.result_count = len(data["items"])
        
        # Estimate token count if token counter is available
        if TOKEN_COUNTER_AVAILABLE:
            try:
                self.token_estimate, self.token_breakdown = estimate_response_tokens(
                    {"data": data}, model_type=model
                )
            except Exception as e:
                logger.error(f"Error estimating tokens: {str(e)}")
                self.token_estimate = 0
                self.token_breakdown = {"data": 0, "metadata": 0, "status": 0}
        else:
            # Fallback to rough estimate based on size
            self.token_estimate = size_bytes // 4  # Rough approximation
            self.token_breakdown = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to a dictionary for inclusion in the response.
        
        Returns:
            A dictionary containing execution time, result size, truncation status,
            token estimate, and token breakdown (if available).
        """
        result = {}
        
        if self.execution_time_ms is not None:
            result["execution_time_ms"] = self.execution_time_ms
        
        if self.result_count is not None:
            result["result_count"] = self.result_count
            
        if self.result_size_bytes is not None:
            result["result_size_bytes"] = self.result_size_bytes
            
        result["is_truncated"] = self.is_truncated
        
        # Add token estimation if available
        if self.token_estimate is not None:
            result["token_estimate"] = self.token_estimate
            
            # Add token breakdown if available
            if self.token_breakdown:
                result["token_breakdown"] = self.token_breakdown
                
        return result

class MCPResponse:
    """
    Standard response format for Ergo Explorer MCP endpoints.
    
    This class implements the standard response structure with:
    - status: "success" or "error"
    - data: The main response payload
    - metadata: Timing, sizing, and token estimation information
    
    Token estimation is performed automatically when the response is finished,
    providing both a total token count and a breakdown by section. This helps
    AI assistants optimize their context window usage when consuming API responses.
    
    The response can be automatically converted to a dictionary or JSON string.
    """
    
    def __init__(self, data: Any = None, error: Optional[Dict[str, Any]] = None, status: str = "success", model_type: str = "claude"):
        """
        Initialize a standardized MCP response.
        
        Args:
            data: The response payload (None for error responses)
            error: Error information (None for successful responses)
            status: Response status ("success" or "error")
            model_type: LLM model type to use for token estimation
        """
        self.status = status
        self.data = data
        self.error = error
        self.metadata = ResponseMetadata()
        self.metadata.model_type = model_type
        self.model_type = model_type
    
    def finish(self):
        """
        Complete the response by finalizing metadata.
        
        This method:
        - Completes timing information
        - Calculates response size metrics
        - Estimates token count for the response
        """
        self.metadata.finish()
        
        # For successful responses, set metrics based on data
        if self.status == "success" and self.data is not None:
            self.metadata.set_result_metrics(self.data, model_type=self.model_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the response to a dictionary.
        
        Returns:
            A dictionary with status, data/error, and metadata.
        """
        result = {
            "status": self.status,
            "metadata": self.metadata.to_dict()
        }
        
        if self.status == "success":
            result["data"] = self.data
        else:
            result["error"] = self.error
            
        return result
    
    def to_json(self, **kwargs) -> str:
        """
        Convert the response to a JSON string.
        
        Args:
            **kwargs: Additional arguments for json.dumps
            
        Returns:
            A JSON string representation of the response
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, **kwargs)

def standardize_response(func):
    """
    Decorator for standardizing endpoint responses.
    
    This decorator wraps endpoint functions to:
    - Automatically format responses in the standard structure
    - Track execution time
    - Calculate response size metrics
    - Estimate token count for the response
    - Extract model_type parameter if provided
    
    The model_type parameter is used for token estimation and helps
    AI assistants optimize their context window usage based on the
    specific LLM they're using.
    
    Args:
        func: The endpoint function to wrap
        
    Returns:
        A wrapped function that returns standardized responses
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract model_type if provided for token estimation
        model_type = kwargs.pop("model_type", "claude") if "model_type" in kwargs else "claude"
        
        # Create response object
        response = MCPResponse(model_type=model_type)
        
        try:
            # Call the original function
            result = func(*args, **kwargs)
            
            # Handle different return types
            if isinstance(result, dict) and "error" in result:
                response.status = "error"
                response.error = result["error"]
            elif isinstance(result, Exception):
                response.status = "error"
                response.error = {"message": str(result)}
            else:
                response.data = result
            
            # Finalize the response
            response.finish()
            return response
            
        except Exception as e:
            # Handle exceptions
            logger.exception(f"Error in {func.__name__}: {str(e)}")
            response.status = "error"
            response.error = {"message": str(e)}
            response.finish()
            return response
    
    return wrapper

def format_response(data: Any, verbose: bool = True, model_type: str = "claude") -> Dict[str, Any]:
    """
    Format data in the standard response structure.
    
    This is a utility function that:
    - Creates a standard response with status, data, and metadata
    - Calculates timing and sizing metrics
    - Estimates token count for the response
    - Returns a simplified version if verbose=False
    
    Args:
        data: The data to include in the response
        verbose: Whether to include metadata (default: True)
        model_type: LLM model type for token estimation (default: "claude")
            Supported model types include: "claude", "gpt-4", "gpt-3.5", etc.
            
    Returns:
        A dictionary with the standardized response format
    """
    # Create and finalize response
    response = MCPResponse(data=data, model_type=model_type)
    response.finish()
    
    # Return full or minimal response based on verbose flag
    if verbose:
        return response.to_dict()
    else:
        return {"status": "success", "data": data}

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