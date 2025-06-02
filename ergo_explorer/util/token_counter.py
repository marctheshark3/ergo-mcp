"""
Token counting utilities for Ergo Explorer MCP.

This module provides utilities for estimating token counts for different LLM model types.
It's used to provide token count estimates in response metadata to help clients
optimize their usage and stay within context limits.

The module includes:
    - Tokenizers for various LLM models (Claude, GPT, etc.)
    - Functions for counting tokens in text and JSON
    - Response token estimation with breakdowns
    - Truncation threshold determination
    - Token usage tier categorization

Usage:
    ```python
    from ergo_explorer.util.token_counter import count_tokens, count_json_tokens

    # Count tokens in a string
    text = "This is a sample string"
    token_count = count_tokens(text, model_type="claude")
    print(f"Token count: {token_count}")

    # Count tokens in a JSON object
    data = {"key": "value", "nested": {"data": [1, 2, 3]}}
    token_count = count_json_tokens(data, model_type="gpt-4")
    print(f"JSON token count: {token_count}")
    ```

Dependencies:
    - tiktoken (optional): For accurate token counting
      If not available, fallback to character-based estimation
"""

import json
import logging
import functools
from typing import Dict, Any, Optional, Union, List, Tuple

# Initialize logger
logger = logging.getLogger(__name__)

# Try to import tiktoken, but don't fail if it's not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    logger.warning("tiktoken not installed. Token counting will be rough estimates.")
    TIKTOKEN_AVAILABLE = False

# Cache for tokenizers to avoid recreating them for each request
_TOKENIZER_CACHE = {}

# Default encoding to use if not specified
DEFAULT_ENCODING = "cl100k_base"  # Claude/Anthropic encoding

# Add mapping of model types to encoding names
MODEL_TO_ENCODING = {
    "claude": "cl100k_base",       # Anthropic Claude models
    "gpt-3.5": "cl100k_base",      # OpenAI GPT-3.5 models
    "gpt-4": "cl100k_base",        # OpenAI GPT-4 models
    "gpt-4o": "cl100k_base",       # OpenAI GPT-4o models
    "palm": "cl100k_base",         # Google PaLM models
    "gemini": "cl100k_base",       # Google Gemini models
    "mistral": "cl100k_base",      # Mistral models
    "llama": "cl100k_base",        # Meta LLaMA models
}

def get_tokenizer(encoding_name: str = DEFAULT_ENCODING):
    """
    Get a tokenizer for the specified encoding.
    
    This function retrieves a tokenizer for the given encoding name. It caches
    tokenizers for efficiency so they don't need to be recreated for each request.
    
    Args:
        encoding_name: Name of the encoding to use (default: 'cl100k_base')
            Common options:
            - 'cl100k_base': Claude/Anthropic models
            - 'p50k_base': OpenAI models
            - 'r50k_base': Older OpenAI models
        
    Returns:
        A tokenizer for the specified encoding or None if tiktoken is not available
        or if the encoding is invalid.
        
    Examples:
        ```python
        tokenizer = get_tokenizer("cl100k_base")
        tokens = tokenizer.encode("Hello, world!")
        ```
    """
    if not TIKTOKEN_AVAILABLE:
        return None
    
    # Check cache first
    if encoding_name in _TOKENIZER_CACHE:
        return _TOKENIZER_CACHE[encoding_name]
    
    try:
        tokenizer = tiktoken.get_encoding(encoding_name)
        _TOKENIZER_CACHE[encoding_name] = tokenizer
        return tokenizer
    except Exception as e:
        logger.error(f"Error creating tokenizer for encoding {encoding_name}: {str(e)}")
        return None

def get_tokenizer_for_model(model_type: str = "claude"):
    """
    Get a tokenizer appropriate for the specified model type.
    
    This function maps model types to their appropriate encoding and returns
    a tokenizer configured for that model.
    
    Args:
        model_type: Type of model (e.g., 'claude', 'gpt-4', etc.)
            Supported model types include:
            - 'claude': Anthropic Claude models
            - 'gpt-3.5', 'gpt-4', 'gpt-4o': OpenAI models
            - 'palm', 'gemini': Google models
            - 'mistral': Mistral models
            - 'llama': Meta LLaMA models
        
    Returns:
        A tokenizer for the specified model or None if tiktoken is not available
        
    Examples:
        ```python
        tokenizer = get_tokenizer_for_model("gpt-4")
        tokens = tokenizer.encode("Hello, world!")
        ```
    """
    encoding_name = MODEL_TO_ENCODING.get(model_type, DEFAULT_ENCODING)
    return get_tokenizer(encoding_name)

@functools.lru_cache(maxsize=1024)
def count_tokens(text: str, model_type: str = "claude") -> int:
    """
    Count the number of tokens in a text string.
    
    This function counts tokens using the appropriate tokenizer for the
    specified model type. It uses an LRU cache to improve performance for
    repeated calls with the same text.
    
    Args:
        text: The text to count tokens for
        model_type: Type of model to count tokens for (default: "claude")
            See get_tokenizer_for_model() for supported model types
        
    Returns:
        The number of tokens in the text, or a rough estimate if tiktoken is not available
        
    Examples:
        ```python
        # Count tokens for Claude models
        claude_tokens = count_tokens("Hello, world!", "claude")
        
        # Count tokens for GPT-4
        gpt4_tokens = count_tokens("Hello, world!", "gpt-4")
        ```
        
    Notes:
        - If tiktoken is not available, a rough estimate is provided based on
          character count (dividing by 4)
        - If the tokenizer creation fails, a similar fallback is used
        - Returns 0 for empty or None inputs
    """
    if not text:
        return 0
    
    if not TIKTOKEN_AVAILABLE:
        # Rough estimate based on average of 4 chars per token
        # Use integer division to get exact result for tests
        return len(text) // 4
    
    tokenizer = get_tokenizer_for_model(model_type)
    if not tokenizer:
        # Fall back to rough estimate
        return len(text) // 4
    
    try:
        tokens = tokenizer.encode(text)
        return len(tokens)
    except Exception as e:
        logger.error(f"Error counting tokens: {str(e)}")
        # Fall back to rough estimate
        return len(text) // 4

def count_json_tokens(data: Any, model_type: str = "claude") -> int:
    """
    Count the number of tokens in a JSON-serializable data structure.
    
    This function converts the data to a JSON string and then counts
    the tokens in that string using the appropriate tokenizer.
    
    Args:
        data: The data to count tokens for (must be JSON-serializable)
        model_type: Type of model to count tokens for (default: "claude")
            See get_tokenizer_for_model() for supported model types
        
    Returns:
        The number of tokens in the JSON representation of the data.
        Returns 0 for None values or if serialization fails.
        
    Examples:
        ```python
        # Count tokens for a simple dictionary
        data = {"name": "John", "age": 30, "items": ["apple", "banana"]}
        token_count = count_json_tokens(data)
        
        # Count tokens with a specific model type
        gpt_tokens = count_json_tokens(data, "gpt-4")
        ```
        
    Notes:
        - Non-ASCII characters are preserved during JSON serialization
        - Returns 0 for None inputs or if JSON serialization fails
    """
    # Return 0 for None values
    if data is None:
        return 0
        
    try:
        # Convert to JSON string (ensure_ascii=False to keep non-ASCII chars)
        json_string = json.dumps(data, ensure_ascii=False)
        return count_tokens(json_string, model_type)
    except Exception as e:
        logger.error(f"Error counting JSON tokens: {str(e)}")
        return 0

def estimate_response_tokens(
    response: Dict[str, Any], 
    model_type: str = "claude",
    include_metadata: bool = True
) -> Tuple[int, Dict[str, int]]:
    """
    Estimate the number of tokens in a response object.
    
    This function analyzes a structured response and estimates token counts
    for each section (data, metadata, status), providing both a total count
    and a breakdown by section.
    
    Args:
        response: The response object to estimate tokens for
            Expected to have keys like "data", "metadata", "status"
        model_type: Type of model to count tokens for (default: "claude")
            See get_tokenizer_for_model() for supported model types
        include_metadata: Whether to include metadata in the count (default: True)
            Set to False to exclude metadata from token counts
        
    Returns:
        A tuple of (total_token_count, breakdown) where breakdown is a
        dictionary with token counts for each section of the response
        
    Examples:
        ```python
        # Estimate tokens for a standard response
        response = {
            "status": "success",
            "data": {"balance": 100, "transactions": [...]},
            "metadata": {"execution_time_ms": 123}
        }
        total, breakdown = estimate_response_tokens(response)
        print(f"Total tokens: {total}")
        print(f"Data tokens: {breakdown['data']}")
        
        # Exclude metadata from count
        total_no_meta, breakdown_no_meta = estimate_response_tokens(
            response, include_metadata=False
        )
        ```
    """
    token_counts = {}
    
    # Count data tokens
    if "data" in response:
        data_tokens = count_json_tokens(response["data"], model_type)
        token_counts["data"] = data_tokens
    else:
        token_counts["data"] = 0
    
    # Count metadata tokens if requested
    if include_metadata and "metadata" in response:
        metadata_tokens = count_json_tokens(response["metadata"], model_type)
        token_counts["metadata"] = metadata_tokens
    else:
        token_counts["metadata"] = 0
    
    # Count status tokens
    if "status" in response:
        status_tokens = count_tokens(response["status"], model_type)
        token_counts["status"] = status_tokens
    else:
        token_counts["status"] = 0
    
    # Calculate total
    total_tokens = sum(token_counts.values())
    
    return total_tokens, token_counts

def should_truncate(
    token_count: int, 
    threshold: int = 2000,
    model_type: str = "claude"
) -> bool:
    """
    Determine whether a response should be truncated based on token count.
    
    This function checks if a response exceeds a token count threshold,
    with model-specific adjustments to the threshold.
    
    Args:
        token_count: The token count to check
        threshold: The base threshold above which to truncate (default: 2000)
        model_type: Type of model to use for threshold adjustment (default: "claude")
            Different models may have adjusted thresholds:
            - GPT-3.5 models: 20% lower threshold
            - GPT-4 models: 20% higher threshold
            - Other models: standard threshold
        
    Returns:
        True if the response should be truncated, False otherwise
        
    Examples:
        ```python
        # Check if response should be truncated
        if should_truncate(3000):
            # Apply truncation logic
            
        # Use model-specific threshold
        if should_truncate(2300, threshold=2000, model_type="gpt-4"):
            # This will return False due to GPT-4's higher threshold
        ```
    """
    # Adjust threshold based on model type
    if model_type.startswith("gpt-3"):
        # Lower threshold for older OpenAI models
        adjusted_threshold = threshold * 0.8
    elif model_type.startswith("gpt-4"):
        # Higher threshold for GPT-4
        adjusted_threshold = threshold * 1.2
    else:
        adjusted_threshold = threshold
    
    return token_count > adjusted_threshold

def get_token_usage_tier(token_count: int) -> str:
    """
    Get the token usage tier for a given token count.
    
    This function categorizes token counts into usage tiers:
    - minimal: < 500 tokens
    - standard: 500-1999 tokens
    - intensive: 2000-4999 tokens
    - excessive: 5000+ tokens
    
    Args:
        token_count: The token count to check
        
    Returns:
        A string representing the token usage tier:
        - "minimal" for small responses
        - "standard" for normal responses
        - "intensive" for large responses
        - "excessive" for very large responses
        
    Examples:
        ```python
        # Check token usage tier
        tier = get_token_usage_tier(1500)
        print(f"Response is in the {tier} tier")  # "standard"
        
        # Use in conditional logic
        if get_token_usage_tier(token_count) == "excessive":
            # Apply special handling for very large responses
        ```
    """
    if token_count < 500:
        return "minimal"
    elif token_count < 2000:
        return "standard"
    elif token_count < 5000:
        return "intensive"
    else:
        return "excessive" 