"""
Token Holders Implementation - Compatibility Layer

This module is maintained for backward compatibility and redirects to 
the new modular implementation in the token_holders package.

DEPRECATED: Use the new package structure at ergo_explorer.tools.token_holders.* instead.
"""

import warnings

# Show deprecation warning
warnings.warn(
    "The monolithic token_holders.py module is deprecated. "
    "Please update your imports to use the new package structure: "
    "from ergo_explorer.tools.token_holders import ...",
    DeprecationWarning,
    stacklevel=2
)

# Re-export all public functions from the package
from ergo_explorer.tools.token_holders import (
    # API functions
    fetch_node_api,
    fetch_explorer_api,
    
    # Cache management
    clear_cache,
    get_cache_stats,
    
    # Token functions
    get_token_by_id,
    
    # Box functions
    get_unspent_boxes_by_token_id,
    get_box_by_id,
    
    # Holder analysis
    get_token_holders,
    
    # Collection functions
    get_collection_metadata,
    get_collection_nfts,
    get_collection_holders,
    search_collections
)

__all__ = [
    # API functions
    "fetch_node_api",
    "fetch_explorer_api",
    
    # Cache management
    "clear_cache",
    "get_cache_stats",
    
    # Token functions
    "get_token_by_id",
    
    # Box functions
    "get_unspent_boxes_by_token_id",
    "get_box_by_id",
    
    # Holder analysis
    "get_token_holders",
    
    # Collection functions
    "get_collection_metadata",
    "get_collection_nfts",
    "get_collection_holders",
    "search_collections"
] 