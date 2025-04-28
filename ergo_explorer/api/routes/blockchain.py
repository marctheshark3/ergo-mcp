"""
Blockchain-related API routes for Ergo Explorer MCP.
"""

from mcp.server.fastmcp import Context, FastMCP
from ergo_explorer.logging_config import get_logger
from ergo_explorer.tools.blockchain import get_blockchain_height, blockchain_status as blockchain_status_tool

# Import our new comprehensive address info utility
from ergo_explorer.tools.blockchain_address_info import (
    blockchain_address_info as blockchain_address_info_func,
    blockchain_address_info_markdown as blockchain_address_info_markdown_func
)

# Get module-specific logger
logger = get_logger(__name__)

def register_blockchain_routes(mcp: FastMCP):
    """Register blockchain-related routes with the MCP server."""
    
    @mcp.tool()
    async def blockchain_status(ctx: Context, random_string: str = None) -> str:
        """
        Get comprehensive blockchain status including height, difficulty metrics,
        network hashrate, and recent adjustments.
        """
        logger.info("Getting blockchain status")
        return blockchain_status_tool()

    @mcp.tool()
    async def blockchain_height(ctx: Context) -> str:
        """
        Get current blockchain height information including indexed height
        and full blockchain height.
        """
        logger.info("Getting blockchain height")
        return get_blockchain_height()

    @mcp.tool()
    async def blockchain_address_info(ctx: Context, address: str, include_transactions: bool = True, tx_limit: int = 10) -> dict:
        """
        Get comprehensive address information including balance, tokens, and recent transactions.
        
        Args:
            address: Ergo blockchain address to analyze
            include_transactions: Whether to include transaction history
            tx_limit: Maximum number of transactions to include in the response
        
        Returns:
            Comprehensive information about the address including balance and transaction history
        """
        logger.info(f"Getting comprehensive address information for {address}")
        return blockchain_address_info_func(
            address=address,
            include_transactions=include_transactions,
            tx_limit=tx_limit
        )

    # Only for backwards compatibility - will be deprecated in favor of the JSON format
    @mcp.tool()
    async def blockchain_address_info_markdown(ctx: Context, address: str, include_transactions: bool = True, tx_limit: int = 10) -> str:
        """
        Get comprehensive address information formatted as markdown.
        
        Args:
            address: Ergo blockchain address to analyze
            include_transactions: Whether to include transaction history
            tx_limit: Maximum number of transactions to include in the response
        
        Returns:
            Markdown-formatted information about the address
        """
        logger.info(f"Getting comprehensive address information (markdown) for {address}")
        return blockchain_address_info_markdown_func(
            address=address,
            include_transactions=include_transactions,
            tx_limit=tx_limit
        )
        
    # Deprecated tools with notices
    @mcp.tool()
    async def get_network_hashrate(ctx: Context, random_string: str = None) -> str:
        """
        DEPRECATED: Use blockchain_status instead.
        Get the current estimated network hashrate of the Ergo blockchain.
        """
        logger.info("Getting network hashrate (deprecated)")
        blockchain_data = blockchain_status_tool()
        return "DEPRECATED: Use blockchain_status instead.\n\n" + blockchain_data

    @mcp.tool()
    async def get_mining_difficulty(ctx: Context, random_string: str = None) -> str:
        """
        DEPRECATED: Use blockchain_status instead.
        Get the current mining difficulty of the Ergo blockchain.
        """
        logger.info("Getting mining difficulty (deprecated)")
        blockchain_data = blockchain_status_tool()
        return "DEPRECATED: Use blockchain_status instead.\n\n" + blockchain_data

    @mcp.tool()
    async def get_info(ctx: Context, random_string: str = None) -> str:
        """
        DEPRECATED: Use blockchain_status instead.
        Get comprehensive information about the Ergo node and network status.
        """
        logger.info("Getting comprehensive info (deprecated)")
        blockchain_data = blockchain_status_tool()
        return "DEPRECATED: Use blockchain_status instead.\n\n" + blockchain_data

    @mcp.tool()
    async def get_info_raw(ctx: Context, random_string: str = None) -> str:
        """
        DEPRECATED: Use more specific tools instead.
        Get raw JSON data from the Ergo node info endpoint.
        """
        logger.info("Getting raw info (deprecated)")
        blockchain_data = blockchain_status_tool()
        return "DEPRECATED: Use blockchain_status instead.\n\n" + blockchain_data
    
    logger.info("Registered blockchain routes") 