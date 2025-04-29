"""
Response standardization utilities for the Ergo Explorer MCP.

This module provides utilities to standardize response formats across endpoints.
It helps convert existing responses to structured JSON data.
"""

import logging
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)

def standardize_response(response: Any, response_format: str = "json") -> Union[Dict[str, Any], None]:
    """
    Standardize a response to JSON format.
    Args:
        response: The response data to standardize
        response_format: The desired format ("json")
    Returns:
        Formatted response in JSON format
    """
    if isinstance(response, dict):
        return response
    # If response is a string, wrap it in a JSON structure
    if isinstance(response, str):
        logger.warning("Received string response, wrapping in JSON structure.")
        return {"message": response, "format": "plain_text"}
    # If response is None or unknown, return None
    logger.error("Unknown response type for standardization.")
    return None 