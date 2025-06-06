"""
API routes package for Ergo Explorer MCP.

This package contains all the API route definitions grouped by domain.
"""

from mcp.server.fastmcp import FastMCP

from ergo_explorer.api.routes.blockchain import register_blockchain_routes
from ergo_explorer.api.routes.transaction import register_transaction_routes
from ergo_explorer.api.routes.box import register_box_routes
from ergo_explorer.api.routes.token import register_token_routes
from ergo_explorer.api.routes.block import register_block_routes
# from ergo_explorer.api.routes.node import register_node_routes
# from ergo_explorer.api.routes.eip import register_eip_routes
from ergo_explorer.api.routes.address_book import register_address_book_routes
from ergo_explorer.api.routes.address_clustering import register_address_clustering_routes

__all__ = [
    "register_all_routes",
]

def register_all_routes(mcp: FastMCP):
    """Register all API routes with the MCP server."""
    register_blockchain_routes(mcp)
    register_transaction_routes(mcp)
    register_box_routes(mcp)
    register_token_routes(mcp)
    register_block_routes(mcp)
    # register_node_routes(mcp)
    # register_eip_routes(mcp)
    register_address_book_routes(mcp)
    register_address_clustering_routes(mcp) 