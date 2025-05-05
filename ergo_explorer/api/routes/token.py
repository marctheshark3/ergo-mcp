"""
Token-related API routes for Ergo Explorer MCP.
"""

from mcp.server.fastmcp import Context
from ergo_explorer.logging_config import get_logger
from ergo_explorer.tools.token import get_token_info, search_token_info
from ergo_explorer.tools.blockchain import (
    get_token_stats as get_token_stats_from_blockchain,
    get_token_holders as get_token_holders_list_from_blockchain,
    get_histogram_token_stats as get_histogram_token_stats_from_blockchain
)
from ergo_explorer.tools.token_holders.collections import (
    search_collections as search_collections_impl,
    get_collection_holders as get_collection_holders_impl
)
from ergo_explorer.tools.node import search_for_token_from_node

# Get module-specific logger
logger = get_logger(__name__)

def register_token_routes(mcp):
    """Register token-related routes with the MCP server."""
    
    @mcp.tool()
    async def get_token(ctx: Context, token_id: str) -> dict:
        """Get detailed information about a token."""
        logger.info(f"Getting token info for ID: {token_id}")
        return await get_token_info(token_id)

    @mcp.tool()
    async def get_token_stats(ctx: Context, token_id: str) -> dict:
        """
        Get statistical analysis for token holders.
        
        Args:
            token_id: Token ID to analyze
        """
        logger.info(f"Getting token stats for token ID: {token_id}")
        return await get_token_stats_from_blockchain(token_id)

    @mcp.tool()
    async def get_token_holders(ctx: Context, token_id: str, include_raw: bool = False, include_analysis: bool = True) -> dict:
        """
        Get comprehensive token holder information.
        
        Args:
            token_id: Token ID to analyze
            include_raw: Include raw holder data
            include_analysis: Include holder analysis
        """
        logger.info(f"Getting token holder list for token ID: {token_id}")
        return await get_token_holders_list_from_blockchain(token_id, include_raw, include_analysis)
    
    @mcp.tool()
    async def get_histogram_token_stats(ctx: Context, token_id: str, bin_count: int = 10) -> dict:
        """
        Get token holder distribution data suitable for histogram visualization.
        
        Args:
            token_id: Token ID to analyze
            bin_count: Number of bins to divide the holder amounts into
            
        Returns:
            Dictionary containing binned distribution data for token holders
        """
        logger.info(f"Getting token histogram data for token ID: {token_id} with {bin_count} bins")
        return await get_histogram_token_stats_from_blockchain(token_id, bin_count)
    
    @mcp.tool()
    async def get_collection_holders(ctx: Context, token_id: str, include_raw: bool = False, include_analysis: bool = True) -> dict:
        """
        Get comprehensive token holder information for an NFT collection.
        
        Args:
            token_id: Token ID of the collection
            include_raw: Include raw holder data
            include_analysis: Include holder analysis
        
        Returns:
            Formatted text with collection holder details including name, ID, description, and holder information
        """
        logger.info(f"Getting collection holders for collection ID: {token_id}")
        return await get_collection_holders_impl(token_id, include_raw, include_analysis)

    @mcp.tool()
    async def search_token(ctx: Context, query: str) -> dict:
        """Search for tokens by ID or name."""
        logger.info(f"Searching for token with query: {query}")
        return await search_token_info(query)
    
    @mcp.tool()
    async def search_collections(ctx: Context, query: str, limit: int = 10) -> dict:
        """
        Search for NFT collections by name or ID.
        
        This endpoint allows searching for NFT collections that follow the EIP-34 standard.
        It can search by either collection name or directly by collection ID.
        
        Args:
            query: Search query (collection name or ID)
            limit: Maximum number of results to return (default: 10)
            
        Returns:
            Formatted text with collection details including name, ID, description, and category
        """
        logger.info(f"Searching for collections with query: {query}")
        return await search_collections_impl(query, limit)
    
    logger.info("Registered token routes") 