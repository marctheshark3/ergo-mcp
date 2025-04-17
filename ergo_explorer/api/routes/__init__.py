"""
API routes package for Ergo Explorer MCP.

This package contains all the API route definitions grouped by domain.
"""

from ergo_explorer.api.routes.blockchain import register_blockchain_routes
from ergo_explorer.api.routes.transaction import register_transaction_routes
from ergo_explorer.api.routes.box import register_box_routes
from ergo_explorer.api.routes.token import register_token_routes
from ergo_explorer.api.routes.block import register_block_routes
from ergo_explorer.api.routes.node import register_node_routes
from ergo_explorer.api.routes.deprecated import register_deprecated_routes
from ergo_explorer.api.routes.eip import register_eip_routes

__all__ = [
    "register_all_routes",
]

def register_all_routes(mcp):
    """Register all API routes with the MCP server."""
    register_blockchain_routes(mcp)
    register_transaction_routes(mcp)
    register_box_routes(mcp)
    register_token_routes(mcp)
    register_block_routes(mcp)
    register_node_routes(mcp)
    register_deprecated_routes(mcp)
    register_eip_routes(mcp) 