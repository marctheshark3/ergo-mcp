"""
Token-related API routes for Ergo Explorer MCP.
"""

from mcp.server.fastmcp import Context
from ergo_explorer.logging_config import get_logger
from ergo_explorer.tools.token import get_token_info, search_token_info
from ergo_explorer.tools.blockchain import (
    get_token_stats as get_token_stats_from_blockchain,
    get_token_holders as get_token_holders_list_from_blockchain,
    get_histogram_token_stats as get_histogram_token_stats_from_blockchain,
    get_historical_token_holder_data
)
from ergo_explorer.tools.token_holders.collections import (
    search_collections as search_collections_impl,
    get_collection_holders as get_collection_holders_impl
)
# The constants are defined in history.py, not __init__.py
from ergo_explorer.tools.token_holders.history import (
    PERIOD_DAILY,
    PERIOD_WEEKLY,
    PERIOD_MONTHLY,
    PERIOD_QUARTERLY,
    PERIOD_YEARLY
)
from ergo_explorer.tools.node import search_for_token_from_node
import asyncio
import time

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
    async def get_historical_token_holders(ctx: Context, 
                                          token_id: str, 
                                          max_transactions: int = 1000000,  # Set to a very high value essentially removing the limit
                                          offset: int = 0,
                                          limit: int = 100,
                                          include_transfers: bool = False) -> dict:
        """
        Get historical token holder distribution showing how ownership has changed over time.
        
        This endpoint uses the box-based approach to analyze token history by examining
        all boxes that have ever contained the token. This provides comprehensive information
        about token transfers, including block heights when tokens were in user wallets.
        
        Args:
            token_id: Token ID to analyze
            max_transactions: Maximum number of transactions to analyze (default very high to process all)
            offset: Number of transfers to skip for pagination
            limit: Maximum number of transfers to return
            include_transfers: Whether to include transfer details in the response (defaults to False)
            
        Returns:
            Historical token holder data including:
            - Token distribution snapshots over time
            - Concentration metrics (Gini coefficient)
            - Recent token transfers with block heights (if include_transfers=True)
        """
        try:
            logger.info(f"Processing historical token holder request for {token_id}")
            
            # Get the node URL from context or use default
            node_url = getattr(ctx, 'node_url', None)
            if not node_url:
                # Use default node URL if not available in context
                node_url = "http://localhost:9053"
                logger.warning(f"Context missing node_url, using default: {node_url}")
            
            # Validate token_id is not empty
            if not token_id or token_id.strip() == "":
                return {
                    "error": "Token ID is required",
                    "status": "error"
                }
                
            # Validate max_transactions if provided - allow very large values
            try:
                max_transactions = int(max_transactions)
                if max_transactions <= 0:
                    max_transactions = 1000000  # Default to very high value to process all
            except (ValueError, TypeError):
                max_transactions = 1000000  # Default to very high value if conversion fails
            
            # Validate offset and limit for pagination
            try:
                offset = max(0, int(offset))  # Ensure non-negative
            except (ValueError, TypeError):
                offset = 0
                
            try:
                limit = max(1, min(500, int(limit)))  # Between 1 and 500
            except (ValueError, TypeError):
                limit = 100
            
            # Check cache first (implement caching in the future if needed)
            cache_key = f"token_holders:{token_id}:{max_transactions}"
            cached_data = None  # ctx.cache.get(cache_key) if hasattr(ctx, 'cache') else None
            
            if cached_data:
                logger.info(f"Returning cached holder data for token {token_id}")
                # Handle include_transfers parameter for cached data
                if include_transfers:
                    # Pagination for cached transfers data if it exists
                    if "transfers" in cached_data:
                        transfers = cached_data.get("transfers", [])[offset:offset+limit]
                        cached_data["transfers"] = transfers
                else:
                    # Remove transfers data if it exists but is not requested
                    if "transfers" in cached_data:
                        transfers = cached_data.pop("transfers")
                        cached_data["transferCount"] = len(transfers) if len(transfers) <= limit else f"{limit}+ (limited by response)"
                
                return cached_data
            
            # Base URL for box queries
            api_url = f"{node_url}/blockchain/box/byTokenId/{token_id}"
            
            # First fetch to determine how many boxes to process
            box_limit = 100  # Fixed batch size for all requests
            try:
                # Check if http_client exists in context
                if not hasattr(ctx, 'http_client'):
                    logger.warning("Context missing http_client, using requests library")
                    import requests
                    # Create a synchronous HTTP request
                    response = requests.get(f"{api_url}", params={"offset": 0, "limit": 1})
                    response.raise_for_status()
                    data = response.json()
                else:
                    # Use the context's HTTP client
                    response = await ctx.http_client.get(api_url, params={"offset": 0, "limit": 1})
                    response.raise_for_status()
                    data = response.json()
                
                logger.info(f"Successfully connected to node API for token {token_id}")
            except Exception as e:
                logger.error(f"Failed initial connection to node API: {str(e)}")
                return {
                    "error": f"Failed to connect to node API: {str(e)}",
                    "status": "error"
                }
            
            # We'll track address to height mapping for holder analysis
            address_to_height = {}
            current_offset = 0
            processed_boxes = 0
            transfers = []
            
            # Also fetch some block info for timestamp conversions
            height_to_timestamp = {}
            
            # Process boxes in batches - continue until we run out of boxes
            while True:
                # Fetch a batch of boxes
                params = {"offset": current_offset, "limit": box_limit}
                try:
                    # Use the appropriate HTTP client
                    if not hasattr(ctx, 'http_client'):
                        import requests
                        response = requests.get(api_url, params=params)
                        response.raise_for_status()
                        data = response.json()
                    else:
                        response = await ctx.http_client.get(api_url, params=params)
                        response.raise_for_status()
                        data = response.json()
                    
                    logger.debug(f"Fetched {len(data.get('items', []))} boxes at offset {current_offset}")
                except Exception as e:
                    logger.error(f"Error fetching boxes at offset {current_offset}: {str(e)}")
                    # We'll return what we've got so far instead of failing completely
                    break
                
                items = data.get("items", [])
                if not items:
                    logger.info("No more boxes found. Finished processing.")
                    break  # No more boxes
                
                # Process this batch of boxes
                for item in items:
                    address = item.get("address")
                    height = item.get("inclusionHeight")
                    box_id = item.get("boxId")
                    value = item.get("value", 0)
                    spent_tx_id = item.get("spentTransactionId")
                    
                    # Add the height to our set of heights to fetch timestamps for
                    if height and height not in height_to_timestamp:
                        height_to_timestamp[height] = None
                    
                    # Get token amount
                    token_amount = 0
                    for asset in item.get("assets", []):
                        if asset.get("tokenId") == token_id:
                            token_amount = asset.get("amount", 0)
                            break
                    
                    # Record transfer data for the response (but only up to the limit)
                    # This logic is separate from the holder mapping - we want ALL holders
                    # Only collect transfer data if requested to save memory and processing time
                    if include_transfers and len(transfers) < limit and processed_boxes >= offset:
                        transfers.append({
                            "boxId": box_id,
                            "address": address,
                            "inclusionHeight": height,
                            "spentTransactionId": spent_tx_id,
                            "value": value,
                            "tokenAmount": token_amount,
                            "timestamp": None  # Will be filled in later
                        })
                    
                    # Update address to height mapping - this needs to process ALL boxes
                    if address:
                        # Store the latest blockheight for each address
                        if address not in address_to_height or height > address_to_height[address]["height"]:
                            address_to_height[address] = {
                                "height": height,
                                "amount": token_amount
                            }
                
                # Update for next iteration
                processed_boxes += len(items)
                
                # Check if we've reached max_transactions - as a safety valve
                if processed_boxes >= max_transactions:
                    logger.warning(f"Reached max_transactions limit: {max_transactions}. Consider increasing this value if you need more data.")
                    break
                
                # If we received fewer items than requested, we've reached the end
                if len(items) < box_limit:
                    logger.info("Received fewer boxes than requested. Finished processing.")
                    break
                
                # Move to the next batch
                current_offset += box_limit
                
                # Small delay to avoid hammering the node API
                if hasattr(ctx, 'http_client'):
                    # Use asyncio.sleep in async mode
                    await asyncio.sleep(0.1)
                else:
                    # Use time.sleep in sync mode
                    time.sleep(0.1)
            
            # Log the total number of boxes processed and unique addresses found
            logger.info(f"Processed {processed_boxes} boxes and found {len(address_to_height)} unique addresses")
            
            # Try to fetch timestamps for the heights we've collected
            # Only do this if transfers are requested to save processing time
            if include_transfers and transfers:
                # This is optional and can be expanded in the future
                heights_list = list(height_to_timestamp.keys())[:10]  # Limit to avoid too many requests
                for height in heights_list:
                    try:
                        # Get the header info for this height
                        header_url = f"{node_url}/blocks/at/{height}"
                        
                        # Use the appropriate HTTP client
                        if not hasattr(ctx, 'http_client'):
                            import requests
                            header_response = requests.get(header_url)
                            header_response.raise_for_status()
                            header_data = header_response.json()
                        else:
                            header_response = await ctx.http_client.get(header_url)
                            header_data = header_response.json()
                            
                        if header_data and len(header_data) > 0:
                            # Extract timestamp from the first block at this height
                            timestamp = header_data[0].get("timestamp")
                            if timestamp:
                                height_to_timestamp[height] = timestamp
                    except Exception as e:
                        logger.warning(f"Could not fetch timestamp for height {height}: {str(e)}")
                
                # Populate timestamps in the transfers data
                for transfer in transfers:
                    height = transfer.get("inclusionHeight")
                    if height in height_to_timestamp and height_to_timestamp[height]:
                        transfer["timestamp"] = height_to_timestamp[height]
            
            # Calculate distribution metrics
            holder_count = len(address_to_height)
            
            # Even if we don't fetch transfer timestamps, we should still try to get timestamps
            # for the most recent holder heights to provide useful data
            if not include_transfers and holder_count > 0:
                # Get unique heights from all holders
                holder_heights = {data["height"] for address, data in address_to_height.items()}
                heights_list = list(holder_heights)[:10]  # Limit to 10 most important heights
                
                for height in heights_list:
                    if height not in height_to_timestamp or height_to_timestamp[height] is None:
                        try:
                            # Get the header info for this height
                            header_url = f"{node_url}/blocks/at/{height}"
                            
                            # Use the appropriate HTTP client
                            if not hasattr(ctx, 'http_client'):
                                import requests
                                header_response = requests.get(header_url)
                                header_response.raise_for_status()
                                header_data = header_response.json()
                            else:
                                header_response = await ctx.http_client.get(header_url)
                                header_data = header_response.json()
                                
                            if header_data and len(header_data) > 0:
                                # Extract timestamp from the first block at this height
                                timestamp = header_data[0].get("timestamp")
                                if timestamp:
                                    height_to_timestamp[height] = timestamp
                        except Exception as e:
                            logger.warning(f"Could not fetch timestamp for height {height}: {str(e)}")
            
            # Convert address_to_height to a sorted list of holders
            holders = [
                {
                    "address": address, 
                    "lastHeight": data["height"], 
                    "amount": data["amount"],
                    "timestamp": height_to_timestamp.get(data["height"])
                } 
                for address, data in address_to_height.items()
            ]
            
            # Sort by token amount (descending)
            holders.sort(key=lambda x: x["amount"], reverse=True)
            
            # Calculate simple Gini coefficient if we have enough holders
            gini = 0
            if holder_count > 1:
                amounts = [holder["amount"] for holder in holders]
                total = sum(amounts)
                if total > 0:
                    # Calculate Gini coefficient
                    n = len(amounts)
                    s1 = 0
                    for i, xi in enumerate(sorted(amounts)):
                        s1 += xi * (n - i)
                    gini = 1 - 2 * (s1 / (n * sum(amounts)))
            
            # Prepare response object
            response_data = {
                "tokenId": token_id,
                "holderCount": holder_count,
                "holders": holders[:100],  # Return top 100 holders
                "concentration": {
                    "gini": gini,
                    "top10Percent": sum(h["amount"] for h in holders[:max(1, holder_count // 10)]) / sum(h["amount"] for h in holders) if holders else 0
                },
                "processedBoxes": processed_boxes,
                "status": "success"
            }
            
            # Only include transfers data if explicitly requested
            if include_transfers:
                response_data["transfers"] = transfers
            else:
                # Include just a count of available transfers to indicate data was processed
                response_data["transferCount"] = len(transfers) if len(transfers) <= limit else f"{limit}+ (limited by response)"
            
            # Store in cache for future use if caching is available
            # if hasattr(ctx, 'cache'):
            #     ctx.cache.set(cache_key, response_data, ttl=300)  # Cache for 5 minutes
            
            return response_data
        except Exception as e:
            logger.error(f"Error in get_historical_token_holders: {str(e)}")
            return {
                "error": str(e),
                "status": "error"
            }
    
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