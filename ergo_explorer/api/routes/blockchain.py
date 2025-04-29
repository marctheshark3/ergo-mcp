"""
Blockchain-related API routes for Ergo Explorer MCP.
"""

from mcp.server.fastmcp import Context, FastMCP
from ergo_explorer.logging_config import get_logger
from ergo_explorer.tools.blockchain import (
    get_blockchain_height, 
    get_address_full_balance,
    get_address_transaction_history,
    blockchain_status as blockchain_status_tool
)

# Get module-specific logger
logger = get_logger(__name__)

def register_blockchain_routes(mcp: FastMCP):
    """Register blockchain-related routes with the MCP server."""
    
    @mcp.tool()
    async def blockchain_status(ctx: Context) -> dict:
        """
        Get comprehensive blockchain status including height, difficulty metrics,
        network hashrate, and recent adjustments.
        
        Returns:
            Dictionary containing blockchain status information including height,
            mining metrics, and network state.
        """
        logger.info("Getting blockchain status")
        return await blockchain_status_tool()

    @mcp.tool()
    async def blockchain_height(ctx: Context) -> dict:
        """
        Get current blockchain height information including indexed height
        and full blockchain height.
        """
        logger.info("Getting blockchain height")
        return await get_blockchain_height()

    @mcp.tool()
    async def blockchain_address_balance(ctx: Context, address: str) -> dict:
        """
        Get comprehensive address balance information including ERG and tokens.
        
        Args:
            address: Ergo blockchain address to analyze
        
        Returns:
            Dictionary containing:
            - address: The queried address
            - confirmed: Dictionary with confirmed balance info (ERG and tokens)
            - unconfirmed: Dictionary with unconfirmed balance info (ERG and tokens)
        """
        logger.info(f"Getting balance information for {address}")
        return await get_address_full_balance(address=address)

    @mcp.tool()
    async def blockchain_address_transactions(ctx: Context, address: str, offset: int = 0, limit: int = 20) -> dict:
        """
        Get transaction history for an address.
        
        Args:
            address: Ergo blockchain address to analyze
            offset: Number of transactions to skip
            limit: Maximum number of transactions to return
        
        Returns:
            Dictionary containing:
            - address: The queried address
            - total_transactions: Total number of transactions found
            - transactions: List of transaction details
            - offset: Current offset
            - limit: Current limit
        """
        logger.info(f"Getting transaction history for {address}")
        return await get_address_transaction_history(
            address=address,
            offset=offset,
            limit=limit
        )
    
    logger.info("Registered blockchain routes") 