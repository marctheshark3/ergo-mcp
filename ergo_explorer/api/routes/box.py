"""
Box-related API routes for Ergo Explorer MCP.
"""

from mcp.server.fastmcp import Context
from ergo_explorer.logging_config import get_logger
from ergo_explorer.tools.blockchain import get_box_info

# Get module-specific logger
logger = get_logger(__name__)

def register_box_routes(mcp):
    """Register box-related routes with the MCP server."""
    
    @mcp.tool()
    async def get_box(ctx: Context, box_id: str) -> str:
        """Get detailed information about a box by its ID."""
        logger.info(f"Getting box info for ID: {box_id}")
        return await get_box_info(box_id)

    @mcp.tool()
    async def get_box_by_index(ctx: Context, index: int) -> str:
        """Get detailed information about a box by its index."""
        logger.info(f"Getting box info for index: {index}")
        return await get_box_info(index, by_index=True)
    
    logger.info("Registered box routes") 