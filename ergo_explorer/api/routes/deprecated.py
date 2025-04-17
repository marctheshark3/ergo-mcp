"""
Deprecated API routes for Ergo Explorer MCP.

These are kept temporarily for backward compatibility
and will be removed in a future version.
"""

from mcp.server.fastmcp import Context
from ergo_explorer.logging_config import get_logger

# Get module-specific logger
logger = get_logger(__name__)

def register_deprecated_routes(mcp):
    """Register deprecated routes with the MCP server."""
    
    @mcp.tool()
    async def get_address_txs(ctx: Context, address: str, offset: int = 0, limit: int = 20) -> str:
        """
        DEPRECATED: Use get_block_transactions instead.
        Get transaction history for an address.
        """
        logger.warning("get_address_txs is deprecated; use get_block_transactions instead")
        from ergo_explorer.api.routes.block import get_block_transactions
        return await get_block_transactions(ctx, address, limit)

    @mcp.tool()
    async def get_address_balance(ctx: Context, address: str) -> str:
        """
        DEPRECATED: Use get_token_holders instead.
        Get the confirmed balance for an Ergo address.
        """
        logger.warning("get_address_balance is deprecated; use get_token_holders instead")
        from ergo_explorer.api.routes.token import get_token_holders
        return await get_token_holders(ctx, address, include_raw=False, include_analysis=True)

    @mcp.tool()
    async def get_network_hashrate(ctx: Context) -> str:
        """
        DEPRECATED: Use blockchain_status instead.
        Get the current estimated network hashrate of the Ergo blockchain.
        """
        logger.warning("get_network_hashrate is deprecated; use blockchain_status instead")
        from ergo_explorer.api.routes.blockchain import blockchain_status
        return await blockchain_status(ctx)

    @mcp.tool()
    async def get_mining_difficulty(ctx: Context) -> str:
        """
        DEPRECATED: Use blockchain_status instead.
        Get the current mining difficulty of the Ergo blockchain.
        """
        logger.warning("get_mining_difficulty is deprecated; use blockchain_status instead")
        from ergo_explorer.api.routes.blockchain import blockchain_status
        return await blockchain_status(ctx)

    @mcp.tool()
    async def get_info(ctx: Context) -> str:
        """
        DEPRECATED: Use blockchain_status instead.
        Get comprehensive information about the Ergo node and network status.
        """
        logger.warning("get_info is deprecated; use blockchain_status instead")
        from ergo_explorer.api.routes.blockchain import blockchain_status
        return await blockchain_status(ctx)

    @mcp.tool()
    async def get_info_raw(ctx: Context) -> str:
        """
        DEPRECATED: Use more specific tools instead.
        Get raw JSON data from the Ergo node info endpoint.
        """
        logger.warning("get_info_raw is deprecated; use more specific tools instead")
        return "This function has been deprecated. Please use specific tools instead."
    
    logger.info("Registered deprecated routes") 