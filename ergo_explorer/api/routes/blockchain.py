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
from ergo_explorer.tools.address import (
    get_transaction_history_json,
    analyze_address,
    get_common_interactions
)
from ergo_explorer.visualization.address_viz import (
    process_interaction_data_for_viz,
    generate_interaction_viz_html
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

    @mcp.tool()
    async def blockchain_address_interactions(ctx: Context, address: str, limit: int = 20, min_interactions: int = 2, verbose: bool = True) -> dict:
        """
        Analyze common address interactions to identify patterns.
        
        Args:
            address: Ergo blockchain address to analyze
            limit: Maximum number of transactions to analyze
            min_interactions: Minimum number of interactions to consider an address as "common"
            verbose: Whether to return detailed information or a condensed version
        
        Returns:
            Dictionary containing analysis of common address interactions
        """
        try:
            # Ensure verbose is properly cast to bool
            verbose_bool = verbose
            if isinstance(verbose, str):
                if verbose.lower() in ("true", "yes", "1"):
                    verbose_bool = True
                elif verbose.lower() in ("false", "no", "0"):
                    verbose_bool = False
                    
            result = await get_common_interactions(address, limit=limit, min_interactions=min_interactions, verbose=verbose_bool)
            return {
                "result": result,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error analyzing address interactions: {str(e)}")
            return {
                "result": None,
                "status": "error",
                "error": str(e)
            }

    @mcp.tool()
    async def blockchain_address_interaction_viz(ctx: Context, address: str, limit: int = 20, min_interactions: int = 2, format: str = "html") -> dict:
        """
        Generate a visualization of common address interactions.
        
        Args:
            address: Ergo blockchain address to analyze
            limit: Maximum number of transactions to analyze
            min_interactions: Minimum number of interactions to consider an address as "common"
            format: Output format - 'html' (default) or 'json'
        
        Returns:
            Dictionary containing the visualization data or HTML content
        """
        try:
            logger.info(f"Generating address interaction visualization for {address}")
            
            # Ensure format is valid
            if format not in ["html", "json"]:
                format = "html"  # Default to HTML if invalid format
            
            # Get the interaction data (using verbose=True to get complete data)
            interaction_data = await get_common_interactions(address, limit=limit, min_interactions=min_interactions, verbose=True)
            
            if format == "html":
                # Generate HTML visualization
                html_content = generate_interaction_viz_html(interaction_data)
                return {
                    "format": "html",
                    "content": html_content,
                    "status": "success"
                }
            else:
                # For JSON format, return the structured data that can be used for visualization on the client side
                # Process the data for visualization
                viz_data = process_interaction_data_for_viz(interaction_data)
                return {
                    "format": "json",
                    "data": viz_data,
                    "status": "success"
                }
        except Exception as e:
            logger.error(f"Error generating address interaction visualization: {str(e)}")
            return {
                "format": format,
                "status": "error",
                "error": str(e)
            }
        
    logger.info("Registered blockchain routes") 