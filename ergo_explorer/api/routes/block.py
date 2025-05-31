"""
Block-related API routes for Ergo Explorer MCP.
"""

from mcp.server.fastmcp import Context
from ergo_explorer.logging_config import get_logger
# from ergo_explorer.tools.blockchain import get_box_info
from ergo_explorer.tools.block import (
    get_block_by_height as fetch_block_by_height,
    get_block_by_hash as fetch_block_by_hash,
    get_latest_blocks as fetch_latest_blocks,
    get_block_transactions as fetch_block_transactions,
    get_block_by_block_id as fetch_block_by_block_id
)

# Get module-specific logger
logger = get_logger(__name__)

def register_block_routes(mcp):
    """Register block-related routes with the MCP server."""
    
    @mcp.tool()
    async def get_block(ctx: Context, block_id: str) -> dict:
        """Get block data by block id."""
        logger.info(f"Getting block by block id: {block_id}")
        return await fetch_block_by_block_id(block_id)

    @mcp.tool()
    async def get_latest_blocks(ctx: Context, limit: int = 10) -> dict:
        """Get most recent blocks."""
        logger.info(f"Getting latest blocks with limit: {limit}")
        return await fetch_latest_blocks(limit)

    @mcp.tool()
    async def get_block_transactions(ctx: Context, block_id: str, limit: int = 100) -> dict:
        """Get transactions in a block."""
        logger.info(f"Getting transactions for block ID: {block_id} with limit: {limit}")
        return await fetch_block_transactions(block_id, limit)
    
    logger.info("Registered block routes") 