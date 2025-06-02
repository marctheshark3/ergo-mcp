"""
Node-related API routes for Ergo Explorer MCP.
"""

from mcp.server.fastmcp import Context
from ergo_explorer.logging_config import get_logger
from ergo_explorer.tools.node import get_node_wallet_info_json

# Get module-specific logger
logger = get_logger(__name__)

def register_node_routes(mcp):
    """Register node-related routes with the MCP server."""
    
    @mcp.tool()
    async def get_node_wallet(ctx: Context) -> dict:
        """Get information about the connected node's wallet."""
        logger.info("Getting node wallet information")
        return await get_node_wallet_info_json()
    
    logger.info("Registered node routes") 