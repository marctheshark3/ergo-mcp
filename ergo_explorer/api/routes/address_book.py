"""
Address Book API routes.

This module contains routes for accessing the Ergo address book,
which provides information about known addresses in the Ergo ecosystem.
"""

import logging
from typing import Dict, Any, Optional
from ergo_explorer.api import fetch_address_book

# Get logger
logger = logging.getLogger(__name__)

async def get_address_book() -> Dict[str, Any]:
    """
    Get a comprehensive list of known addresses in the Ergo ecosystem.
    
    This endpoint fetches data from the ergexplorer.com address book API,
    which includes information about services, exchanges, mining pools, 
    and other notable addresses.
    
    Returns:
        A dictionary containing address book entries and token information
    """
    logger.info("Getting address book data")
    return await fetch_address_book()

async def filter_address_book_by_type(type_filter: str) -> Dict[str, Any]:
    """
    Get address book entries filtered by type.
    
    Args:
        type_filter: The type to filter by (e.g., "Service", "Mining pool", "Exchange")
        
    Returns:
        A dictionary containing filtered address book entries
    """
    logger.info(f"Getting address book data filtered by type: {type_filter}")
    
    # Fetch the full address book
    address_book = await fetch_address_book()
    
    if "items" not in address_book:
        return {"items": [], "total": 0, "tokens": [], "error": "Failed to fetch address book"}
    
    # Filter items by type
    filtered_items = [item for item in address_book["items"] if item.get("type") == type_filter]
    
    # Return filtered results
    return {
        "items": filtered_items,
        "total": len(filtered_items),
        "tokens": address_book.get("tokens", [])
    }

async def search_address_book(query: str) -> Dict[str, Any]:
    """
    Search the address book for entries matching the query.
    
    Args:
        query: The search query to match against address names, URLs, or addresses
        
    Returns:
        A dictionary containing matching address book entries
    """
    logger.info(f"Searching address book with query: {query}")
    
    # Fetch the full address book
    address_book = await fetch_address_book()
    
    if "items" not in address_book:
        return {"items": [], "total": 0, "tokens": [], "error": "Failed to fetch address book"}
    
    query = query.lower()
    
    # Filter items by query
    filtered_items = [
        item for item in address_book["items"] 
        if (query in item.get("name", "").lower() or 
            query in item.get("url", "").lower() or 
            query in item.get("address", "").lower() or
            query in item.get("type", "").lower())
    ]
    
    # Return filtered results
    return {
        "items": filtered_items,
        "total": len(filtered_items),
        "tokens": address_book.get("tokens", [])
    }

async def get_address_details(address: str) -> Dict[str, Any]:
    """
    Get details for a specific address from the address book.
    
    Args:
        address: The address to look up
        
    Returns:
        A dictionary containing information about the address if found,
        or an empty result if not found
    """
    logger.info(f"Looking up address in address book: {address}")
    
    # Fetch the address book
    address_book = await fetch_address_book()
    
    if "items" not in address_book:
        return {"found": False, "error": "Failed to fetch address book"}
    
    # Find the address in the book
    for item in address_book["items"]:
        if item.get("address") == address:
            logger.info(f"Found address in address book: {item.get('name')}")
            return {
                "found": True,
                "details": item
            }
    
    # If we get here, the address wasn't found
    logger.info(f"Address not found in address book: {address}")
    return {
        "found": False,
        "message": "Address not found in the address book"
    }

def register_address_book_routes(mcp):
    """Register address book routes with the MCP server."""
    
    @mcp.tool(name="get_address_book")
    async def address_book() -> Dict[str, Any]:
        """
        Get comprehensive address book data from ergexplorer.com.
        
        Returns information about known addresses in the Ergo ecosystem
        including services, exchanges, mining pools, and other notable addresses.
        """
        return await get_address_book()
    
    @mcp.tool(name="get_address_book_by_type")
    async def address_book_by_type(type_filter: str) -> Dict[str, Any]:
        """
        Get address book entries filtered by type.
        
        Args:
            type_filter: The type to filter by (e.g., "Service", "Mining pool", "Exchange")
        """
        return await filter_address_book_by_type(type_filter)
    
    @mcp.tool(name="search_address_book")
    async def search_address_book_endpoint(query: str) -> Dict[str, Any]:
        """
        Search the address book for entries matching the query.
        
        Args:
            query: The search query to match against address names, URLs, or addresses
        """
        return await search_address_book(query)
    
    @mcp.tool(name="get_address_details")
    async def address_details_endpoint(address: str) -> Dict[str, Any]:
        """
        Get details for a specific address from the address book.
        
        Args:
            address: The address to look up in the address book
        """
        return await get_address_details(address) 