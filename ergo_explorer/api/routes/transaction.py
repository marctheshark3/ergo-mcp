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
    async def get_transaction(ctx: Context, tx_id: str) -> dict:
        """Get detailed information about a transaction by its ID."""
        try:
            logger.info(f"Starting get_transaction request for ID: {tx_id}")
            result = await get_transaction_info(identifier=tx_id)
            logger.info(f"Successfully retrieved transaction info for ID: {tx_id}")
            return result
        except Exception as e:
            logger.error(f"Error in get_transaction for ID {tx_id}: {str(e)}", exc_info=True)
            return {"error": f"Failed to retrieve transaction: {str(e)}"}

    # @mcp.tool()
    # async def get_transaction_by_index(ctx: Context, index: int) -> dict:
    #     """Get detailed information about a transaction by its index."""
    #     logger.info(f"Getting transaction info for index: {index}")
    #     return await get_transaction_info(identifier=index, by_index=True)
    
    logger.info("Registered transaction routes") 