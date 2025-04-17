"""
Transaction-related API routes for Ergo Explorer MCP.
"""

from mcp.server.fastmcp import Context
from ergo_explorer.logging_config import get_logger
from ergo_explorer.tools.blockchain import get_transaction_info

# Get module-specific logger
logger = get_logger(__name__)

def register_transaction_routes(mcp):
    """Register transaction-related routes with the MCP server."""
    
    @mcp.tool()
    async def get_transaction(ctx: Context, tx_id: str) -> str:
        """Get detailed information about a transaction by its ID."""
        logger.info(f"Getting transaction info for ID: {tx_id}")
        return await get_transaction_info(tx_id)

    @mcp.tool()
    async def get_transaction_by_index(ctx: Context, index: int) -> str:
        """Get detailed information about a transaction by its index."""
        logger.info(f"Getting transaction info for index: {index}")
        return await get_transaction_info(str(index), by_index=True)
    
    logger.info("Registered transaction routes") 