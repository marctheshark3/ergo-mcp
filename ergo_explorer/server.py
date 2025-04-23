"""
Ergo Explorer MCP Server implementation.

This file serves as the main entry point for the Ergo Explorer MCP server.
"""

import os
from ergo_explorer.server_config import create_server, run_server
from ergo_explorer.logging_config import get_logger

# Get logger
logger = get_logger(__name__)

def main():
    """Run the MCP server."""
    logger.info("Initializing Ergo Explorer MCP server...")
    run_server()

# If this file is run directly, start the server
if __name__ == "__main__":
    main()

# Export the __all__ list for backwards compatibility
__all__ = [
    # Core blockchain tools
    "blockchain_status",
    "mempool_status",
    
    # Transaction tools
    "get_transaction",
    "get_transaction_by_index",
    
    # Box tools
    "get_box",
    "get_box_by_index",
    
    # Token tools
    "get_token",
    "get_token_holders",
    "search_token",
    
    # Block tools
    "get_block_by_height",
    "get_block_by_hash",
    "get_latest_blocks",
    "get_block_transactions",
    
    # Node tools
    "get_node_wallet",
    
    # Address book tools
    "get_address_book",
    "get_address_book_by_type",
    "search_address_book",
    "get_address_details",
    
    # Deprecated functions - these will be removed in a future version
    "get_address_txs",
    "get_address_balance",
    "get_network_hashrate",
    "get_mining_difficulty",
    "get_info",
    "get_info_raw",
]
