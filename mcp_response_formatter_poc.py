#!/usr/bin/env python
"""
Proof of Concept - MCP Response Formatter

This script demonstrates how to transform the current MCP markdown responses
into standardized JSON format with status, data, and metadata fields.
"""

import time
import json
from typing import Dict, Any, Union, Optional


class ResponseMetadata:
    """Standardized metadata for MCP responses."""
    
    def __init__(self):
        self.start_time = time.time()
        self.execution_time_ms = None
        self.result_size_bytes = None
        self.is_truncated = False
        self.token_estimate = None
    
    def finish(self):
        """Complete timing metrics when response is ready."""
        self.execution_time_ms = round((time.time() - self.start_time) * 1000, 2)
    
    def set_result_metrics(self, result: Any, is_truncated: bool = False):
        """Set size and token metrics based on the result data."""
        # Calculate size in bytes of the result
        if isinstance(result, str):
            self.result_size_bytes = len(result.encode('utf-8'))
            # Rough estimate: ~4 chars per token
            self.token_estimate = len(result) // 4
        else:
            try:
                result_json = json.dumps(result)
                self.result_size_bytes = len(result_json.encode('utf-8'))
                self.token_estimate = len(result_json) // 4
            except (TypeError, ValueError):
                # If we can't properly measure, make a rough estimate
                self.result_size_bytes = 1000  # Default fallback
                self.token_estimate = 250
        
        self.is_truncated = is_truncated
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for JSON serialization."""
        return {
            "execution_time_ms": self.execution_time_ms,
            "result_size_bytes": self.result_size_bytes,
            "is_truncated": self.is_truncated,
            "token_estimate": self.token_estimate
        }


def standardize_response(markdown_response: str, 
                         status: str = "success", 
                         message: Optional[str] = None,
                         is_truncated: bool = False,
                         verbose: bool = True) -> Dict[str, Any]:
    """
    Transform a markdown response into a standardized JSON response.
    
    Args:
        markdown_response: Original markdown response text
        status: Response status (success, error, etc.)
        message: Optional status message
        is_truncated: Whether the response was truncated
        verbose: Whether to include metadata
        
    Returns:
        Standardized JSON response with status, data, and metadata
    """
    metadata = ResponseMetadata()
    
    # Wrap the markdown in the data field
    response = {
        "status": status,
        "data": markdown_response,
        "message": message
    }
    
    # Set metadata metrics
    metadata.set_result_metrics(markdown_response, is_truncated)
    metadata.finish()
    
    if verbose:
        response["metadata"] = metadata.to_dict()
    
    return response


# Example usage - demonstrate with actual endpoint responses

# Example 1: Blockchain Status
blockchain_status_md = """# Ergo Blockchain Status

    ## Current State
    Blockchain Height Information:
• Indexed Height: 1,510,691
• Full Height: 1,510,691
• Blocks Behind: 0

    ## Network Metrics
  name 'logger' is not defined

    ## Performance
    name 'logger' is not defined
"""

# Example 2: List EIPs
list_eips_md = """# Ergo Improvement Proposals (EIPs)

## EIP-22: Auction contract
Status: Unknown

## EIP-19: Cold Wallet: an interaction protocol between Hot and Cold mobile wallets
Status: Unknown

## EIP-5: EIP-0005: Contract Template
Status: Unknown
"""

# Example 3: Error response
error_response_md = """Error getting token info: Client error '404 Not Found' for url 'http://localhost:9053/blockchain/token/byId/d71693c49a84fbbecd4908c94813b46514b18b67a99952dc1e6e4791556de413'
For more information check: https://httpstatuses.com/404"""


def main():
    """Demonstrate the formatter with examples."""
    # Example 1: Format blockchain status response
    blockchain_json = standardize_response(blockchain_status_md)
    
    # Example 2: Format list EIPs response
    eips_json = standardize_response(list_eips_md)
    
    # Example 3: Format error response
    error_json = standardize_response(
        error_response_md, 
        status="error",
        message="Token not found"
    )
    
    # Example 4: Minimal response (no metadata)
    minimal_json = standardize_response(
        blockchain_status_md,
        verbose=False
    )
    
    # Print examples
    print("\n== Example 1: Blockchain Status (Standard) ==")
    print(json.dumps(blockchain_json, indent=2))
    
    print("\n== Example 2: List EIPs (Standard) ==")
    print(json.dumps(eips_json, indent=2))
    
    print("\n== Example 3: Error Response ==")
    print(json.dumps(error_json, indent=2))
    
    print("\n== Example 4: Minimal Response (No Metadata) ==")
    print(json.dumps(minimal_json, indent=2))


if __name__ == "__main__":
    main() 