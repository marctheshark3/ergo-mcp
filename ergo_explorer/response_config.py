"""
Configuration settings for response formatting in the Ergo Explorer MCP.
"""

import os
from typing import Dict, Any, Optional

# Default response verbosity
DEFAULT_VERBOSITY = os.environ.get("RESPONSE_VERBOSITY", "normal").lower()

# Default result limits for different endpoint types
DEFAULT_LIMITS = {
    # Blockchain data endpoints
    "blocks": 10,
    "transactions": 20,
    "box": 50,
    
    # Token related endpoints
    "tokens": 20,
    "token_holders": 100,
    "collections": 10,
    
    # Address related endpoints
    "address_transactions": 20,
    "address_tokens": 50,
    
    # Search endpoints
    "search_results": 15,
    
    # Custom analytics
    "analytics": 25,
    
    # Default for any unspecified endpoint type
    "default": 50
}

# Environment variable override for limits
def _get_env_limits() -> Dict[str, int]:
    """Get limit overrides from environment variables."""
    env_limits = {}
    
    for key in DEFAULT_LIMITS.keys():
        env_var = f"LIMIT_{key.upper()}"
        if env_var in os.environ:
            try:
                env_limits[key] = int(os.environ[env_var])
            except ValueError:
                pass
    
    return env_limits

# Merge environment limits with defaults
RESULT_LIMITS = {**DEFAULT_LIMITS, **_get_env_limits()}

# Maximum response size in bytes before compression is applied
MAX_RESPONSE_SIZE = int(os.environ.get("MAX_RESPONSE_SIZE", "1000000"))  # 1MB default

# Maximum token estimate before truncation warning
MAX_TOKEN_ESTIMATE = int(os.environ.get("MAX_TOKEN_ESTIMATE", "4000"))  # ~16K chars

# Response format configuration
class ResponseConfig:
    """Configuration for response formatting."""
    
    @staticmethod
    def is_verbose() -> bool:
        """Check if verbose responses are enabled."""
        return DEFAULT_VERBOSITY == "normal"
    
    @staticmethod
    def get_limit(endpoint_type: str) -> int:
        """Get the result limit for a specific endpoint type."""
        return RESULT_LIMITS.get(endpoint_type, RESULT_LIMITS["default"])
    
    @staticmethod
    def should_compress(size_bytes: Optional[int]) -> bool:
        """Determine if response should be compressed."""
        if size_bytes is None:
            return False
        return size_bytes > MAX_RESPONSE_SIZE
    
    @staticmethod
    def exceeds_token_limit(token_estimate: Optional[int]) -> bool:
        """Check if the response exceeds the token limit."""
        if token_estimate is None:
            return False
        return token_estimate > MAX_TOKEN_ESTIMATE 