"""
Blockchain-related API routes for Ergo Explorer MCP.
"""

from mcp.server.fastmcp import Context
from ergo_explorer.logging_config import get_logger
from ergo_explorer.tools.blockchain import get_blockchain_height
from ergo_explorer.tools.network import (
    format_network_hashrate,
    format_mining_difficulty,
)

# Get module-specific logger
logger = get_logger(__name__)

def register_blockchain_routes(mcp):
    """Register blockchain-related routes with the MCP server."""
    
    @mcp.tool()
    async def blockchain_status(ctx: Context) -> str:
        """
        Get comprehensive blockchain status including height, difficulty metrics,
        network hashrate, and recent adjustments.
        """
        logger.info("Getting comprehensive blockchain status")
        
        # Gather all relevant data
        height_data = await get_blockchain_height()
        difficulty_data = await fetch_mining_difficulty()
        hashrate_data = await fetch_network_hashrate()
        
        # Format the data
        difficulty_info = await format_mining_difficulty(difficulty_data)
        hashrate_info = await format_network_hashrate(hashrate_data)
        
        # Combine into comprehensive status
        return f"""# Ergo Blockchain Status

    ## Current State
    {height_data}

    ## Network Metrics
    {difficulty_info}

    ## Performance
    {hashrate_info}
    """

    @mcp.tool()
    async def blockchain_address_info(ctx: Context, address: str, include_transactions: bool = True, tx_limit: int = 10) -> str:
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
        
        # Import these inside the function to avoid circular imports
        from ergo_explorer.tools.address import get_address_balance, get_transaction_history
        
        # Get balance information
        balance_info = await get_address_balance(address)
        
        # If transactions are requested, get transaction history
        if include_transactions:
            tx_history = await get_transaction_history(address, limit=tx_limit)
            result = f"{balance_info}\n\n## Recent Transactions\n{tx_history}"
        else:
            result = balance_info
            
        return result

    # @mcp.tool()
    # async def mempool_status(ctx: Context) -> str:
    #     \"\"\"
    #     Get current mempool state including pending transactions,
    #     memory usage, and size statistics.
    #     \"\"\"
    #     logger.info(\"Getting mempool status\")
    #     mempool_data = await fetch_mempool_info()
    #     return await format_mempool_info(mempool_data)

    # These functions need to be imported locally since they're 
    # defined in the same function scope as their use
    async def fetch_mining_difficulty():
        """Get mining difficulty data."""
        try:
            from ergo_explorer.tools.node import get_network_status_from_node
            status = await get_network_status_from_node()
            return status
        except Exception as e:
            logger.error(f"Error fetching mining difficulty: {str(e)}")
            return {"error": str(e)}

    async def fetch_network_hashrate():
        """Get network hashrate data."""
        try:
            from ergo_explorer.tools.node import get_network_status_from_node
            status = await get_network_status_from_node()
            return status
        except Exception as e:
            logger.error(f"Error fetching network hashrate: {str(e)}")
            return {"error": str(e)}

    logger.info("Registered blockchain routes") 