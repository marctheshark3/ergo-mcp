"""
Ergo Node API client for direct node interaction.
"""
import httpx
import logging
from typing import Dict, List, Any, Optional, Union
from ergo_explorer.config import ERGO_NODE_API, ERGO_NODE_API_KEY, USER_AGENT
from ergo_explorer.logging_config import get_logger

# Configure logger - Ensure DEBUG level to capture detailed logs
logger = get_logger(__name__, log_level='DEBUG')

async def fetch_node_api(endpoint: str, params: Optional[Dict] = None, method: str = "GET", json_data: Optional[Dict] = None) -> Dict:
    """Make a request to the Ergo Node API."""
    url = f"{ERGO_NODE_API}/{endpoint}"
    async with httpx.AsyncClient() as client:
        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json"
        }
        
        # Add API key if available
        if ERGO_NODE_API_KEY:
            headers["api_key"] = ERGO_NODE_API_KEY
            
        # Log request details before sending
        logger.debug(f"Node API Request: Method={method}, URL={url}, Params={params}, JSON={json_data}, Headers={headers}")
        
        response = None
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            elif method == "POST":
                response = await client.post(url, headers=headers, params=params, json=json_data, timeout=30.0)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Log raw response details before processing
            response_text = await response.aread() # Read content efficiently
            logger.debug(f"Node API Response: Status={response.status_code}, Headers={response.headers}, Raw Body='{response_text.decode('utf-8', errors='replace')}'")
            
            response.raise_for_status()
            # Attempt to parse JSON *after* logging raw response and checking status
            return response.json()
        
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
            # Re-raise or handle as appropriate for the application
            raise 
        except httpx.HTTPStatusError as exc:
            logger.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc}")
            # Log the response body that caused the error, which we already captured
            # Re-raise or handle as appropriate
            raise
        except Exception as exc:
            # Catch potential JSONDecodeError or other unexpected errors
            logger.error(f"An unexpected error occurred during Node API call to {url}: {exc}", exc_info=True)
            # Log response details if available
            if response:
                 logger.error(f"Response details on error: Status={response.status_code}, Headers={response.headers}")
                 # Raw body already logged in DEBUG level
            raise

# Blockchain API endpoints

async def get_indexed_height() -> Dict:
    """Get current indexed block height."""
    return await fetch_node_api("blockchain/indexedHeight")

async def get_transaction_by_id(tx_id: str) -> Dict:
    """Get transaction details by ID."""
    logger.info(f"Fetching transaction details for {tx_id}")
    return await fetch_node_api(f"blockchain/transaction/byId/{tx_id}")

async def get_transaction_by_index(tx_index: int) -> Dict:
    """Get transaction by global index number."""
    return await fetch_node_api(f"blockchain/transaction/byIndex/{tx_index}")

async def get_transactions_by_address(address: str, offset: int = 0, limit: int = 20) -> Dict:
    """Get transactions for an address."""
    return await fetch_node_api(
        "blockchain/transaction/byAddress",
        method="POST",
        json_data=address,
        params={"offset": offset, "limit": limit}
    )

async def get_transaction_range(offset: int = 0, limit: int = 20) -> List[str]:
    """Get a range of transaction IDs."""
    return await fetch_node_api(
        "blockchain/transaction/range",
        params={"offset": offset, "limit": limit}
    )

async def get_box_by_id(box_id: str) -> Dict:
    """Get box details by ID."""
    return await fetch_node_api(f"blockchain/box/byId/{box_id}")

async def get_box_by_index(box_index: int) -> Dict:
    """Get box by global index number."""
    return await fetch_node_api(f"blockchain/box/byIndex/{box_index}")

async def get_boxes_by_token_id(token_id: str, offset: int = 0, limit: int = 20) -> Dict:
    """Get boxes containing a specific token."""
    return await fetch_node_api(
        f"blockchain/box/byTokenId/{token_id}",
        params={"offset": offset, "limit": limit}
    )

async def get_unspent_boxes_by_token_id(token_id: str, offset: int = 0, limit: int = 20) -> Dict:
    """Get unspent boxes containing a specific token."""
    return await fetch_node_api(
        f"blockchain/box/unspent/byTokenId/{token_id}",
        params={"offset": offset, "limit": limit}
    )

async def get_boxes_by_address(address: str, offset: int = 0, limit: int = 20) -> Dict:
    """Get boxes for an address."""
    return await fetch_node_api(
        "blockchain/box/byAddress",
        method="POST",
        json_data=address,
        params={"offset": offset, "limit": limit}
    )

async def get_unspent_boxes_by_address(address: str, offset: int = 0, limit: int = 20) -> Dict:
    """Get unspent boxes for an address."""
    return await fetch_node_api(
        "blockchain/box/unspent/byAddress",
        method="POST",
        json_data=address,
        params={"offset": offset, "limit": limit}
    )

async def get_box_range(offset: int = 0, limit: int = 20) -> List[str]:
    """Get a range of box IDs."""
    return await fetch_node_api(
        "blockchain/box/range",
        params={"offset": offset, "limit": limit}
    )

async def get_boxes_by_ergo_tree(ergo_tree: str, offset: int = 0, limit: int = 20) -> Dict:
    """Get boxes by ErgoTree."""
    return await fetch_node_api(
        "blockchain/box/byErgoTree",
        method="POST",
        json_data=ergo_tree,
        params={"offset": offset, "limit": limit}
    )

async def get_unspent_boxes_by_ergo_tree(ergo_tree: str, offset: int = 0, limit: int = 20) -> Dict:
    """Get unspent boxes by ErgoTree."""
    return await fetch_node_api(
        "blockchain/box/unspent/byErgoTree",
        method="POST",
        json_data=ergo_tree,
        params={"offset": offset, "limit": limit}
    )

async def get_token_by_id(token_id: str) -> Dict:
    """Get token information by ID."""
    return await fetch_node_api(f"blockchain/token/byId/{token_id}")

async def get_tokens() -> Dict:
    """Get list of tokens."""
    return await fetch_node_api("blockchain/tokens", method="POST")

async def get_address_balance(address: str) -> Dict:
    """Get confirmed and unconfirmed balance for an address."""
    return await fetch_node_api("blockchain/balance", method="POST", json_data=address)

# Legacy API functions maintained for backward compatibility
async def get_address_balance_node(address: str) -> Dict:
    """Legacy function for getting address balance."""
    return await get_address_balance(address)

async def get_transaction_node(tx_id: str) -> Dict:
    """Legacy function for getting transaction details."""
    return await get_transaction_by_id(tx_id)

async def get_transaction_by_address_node(address: str, offset: int = 0, limit: int = 20) -> Dict:
    """Legacy function for getting address transactions."""
    return await get_transactions_by_address(address, offset, limit)

async def get_box_by_id_node(box_id: str) -> Dict:
    """Legacy function for getting box details."""
    return await get_box_by_id(box_id)

async def get_unspent_boxes_by_address_node(address: str, offset: int = 0, limit: int = 20) -> Dict:
    """Legacy function for getting unspent boxes."""
    return await get_unspent_boxes_by_address(address, offset, limit)

async def get_token_by_id_node(token_id: str) -> Dict:
    """Legacy function for getting token details."""
    return await get_token_by_id(token_id)

async def search_for_token_node(query: str) -> Dict:
    """Legacy function for token search."""
    # Note: This is a placeholder as the node API doesn't have a direct token search endpoint
    raise NotImplementedError("Token search is not available through the node API")

async def get_network_info_node() -> Dict:
    """Legacy function for getting network info."""
    return await fetch_node_api("info")


async def submit_transaction_node(tx_data: Dict) -> Dict:
    """Submit a transaction to the node."""
    return await fetch_node_api("transactions", method="POST", json_data=tx_data)

async def get_node_wallet_addresses() -> List[str]:
    """Get all wallet addresses from the node wallet."""
    return await fetch_node_api("wallet/addresses")

async def get_all_token_holders(token_id: str) -> List[Dict]:
    """
    Get all addresses holding a specific token by fetching all unspent boxes.
    
    Args:
        token_id: Token ID to search for
        
    Returns:
        List of dictionaries containing address and amount information
    """
    all_boxes = []
    offset = 0
    limit = 100  # Max items per request
    
    while True:
        try:
            response = await fetch_node_api(
                f"blockchain/box/unspent/byTokenId/{token_id}",
                params={"offset": offset, "limit": limit}
            )
            
            # For this endpoint, the response is just the array of boxes
            boxes = response if isinstance(response, list) else []
            if not boxes:
                break
                
            all_boxes.extend(boxes)
            
            # If we got fewer boxes than the limit, we've reached the end
            if len(boxes) < limit:
                break
                
            offset += limit
            
        except Exception as e:
            logger.error(f"Error fetching token holders at offset {offset}: {str(e)}")
            break
    
    # Process boxes to get address holdings
    address_holdings = {}
    for box in all_boxes:
        address = box.get("address")
        if not address:
            continue
            
        # Find the specific token in the box's assets
        for asset in box.get("assets", []):
            if asset.get("tokenId") == token_id:
                amount = asset.get("amount", 0)
                if address in address_holdings:
                    address_holdings[address] += amount
                else:
                    address_holdings[address] = amount
    
    # Convert to list of dictionaries
    return [
        {"address": addr, "amount": amount}
        for addr, amount in address_holdings.items()
    ]

async def get_token_holders_json(token_id: str) -> Dict:
    """
    Get all addresses holding a specific token with detailed JSON output.
    
    This function fetches all unspent boxes containing the specified token,
    aggregates holdings by address, and returns structured JSON with token
    information and holder details.
    
    Args:
        token_id: Token ID to search for
        
    Returns:
        Dictionary containing token info and holder details suitable for JSON serialization
    """
    try:
        logger.info(f"Fetching token information for {token_id}")
        token_info = await get_token_by_id(token_id)
        
        if isinstance(token_info, dict) and "error" in token_info:
            logger.error(f"Error fetching token info: {token_info.get('error')}")
            return {"error": token_info.get("error"), "token_id": token_id}
            
        logger.info(f"Fetching unspent boxes for token {token_id}")
        all_boxes = []
        offset = 0
        limit = 100  # Max items per request
        
        while True:
            logger.debug(f"Fetching boxes at offset={offset}, limit={limit}")
            boxes = await get_unspent_boxes_by_token_id(token_id, offset, limit)
            
            if not boxes:
                break
                
            # If boxes is a dict with error, break the loop
            if isinstance(boxes, dict) and "error" in boxes:
                logger.error(f"Error fetching boxes: {boxes.get('error')}")
                break
                
            all_boxes.extend(boxes)
            logger.debug(f"Retrieved {len(boxes)} boxes, total now: {len(all_boxes)}")
            
            # If we got fewer boxes than the limit, we've reached the end
            if len(boxes) < limit:
                break
                
            offset += limit
        
        # Process boxes to get address holdings
        logger.info(f"Processing {len(all_boxes)} boxes to extract holder information")
        address_holdings = {}
        for box in all_boxes:
            address = box.get("address")
            if not address:
                continue
                
            # Find the specific token in the box's assets
            for asset in box.get("assets", []):
                if asset.get("tokenId") == token_id:
                    amount = int(asset.get("amount", 0))
                    if address in address_holdings:
                        address_holdings[address] += amount
                    else:
                        address_holdings[address] = amount
        
        # Calculate total supply and percentages
        total_supply = sum(address_holdings.values())
        logger.info(f"Found {len(address_holdings)} unique holders with total supply of {total_supply}")
        
        # Extract token metadata
        token_name = token_info.get("name", "Unknown Token")
        token_decimals = token_info.get("decimals", 0)
        
        # Build the result
        result = {
            "token_id": token_id,
            "token_name": token_name,
            "decimals": token_decimals,
            "total_supply": total_supply,
            "total_holders": len(address_holdings),
            "holders": []
        }
        
        # Add holder information
        for address, amount in address_holdings.items():
            percentage = (amount / total_supply * 100) if total_supply > 0 else 0
            holder_info = {
                "address": address,
                "amount": amount,
                "percentage": round(percentage, 6)
            }
            result["holders"].append(holder_info)
        
        # Sort holders by amount in descending order
        result["holders"].sort(key=lambda x: x["amount"], reverse=True)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting token holders: {str(e)}")
        return {"error": str(e), "token_id": token_id} 