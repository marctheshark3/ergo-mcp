"""
Ergo Explorer API client.
"""
import httpx
from typing import Dict, List, Any, Optional
from ergo_explorer.config import ERGO_EXPLORER_API, USER_AGENT
import logging
import os
import json

async def fetch_api(endpoint: str, params: Optional[Dict] = None) -> Dict:
    """Make a request to the Ergo Explorer API."""
    try:
        url = f"{ERGO_EXPLORER_API}/{endpoint}"
        logging.info(f"Making API request to: {url}")
        
        async with httpx.AsyncClient() as client:
            headers = {"User-Agent": USER_AGENT}
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            
            # Log response status
            logging.info(f"API response status: {response.status_code}")
            
            # Check for error status codes
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                data = response.json()
                if isinstance(data, dict):
                    return data
                else:
                    logging.error(f"Unexpected response format: {data}")
                    return {"items": [], "error": "Invalid response format"}
            except ValueError as e:
                logging.error(f"Failed to parse JSON response: {str(e)}")
                return {"items": [], "error": "Invalid JSON response"}
                
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error occurred: {str(e)}")
        return {"items": [], "error": f"HTTP error: {e.response.status_code}"}
    except httpx.RequestError as e:
        logging.error(f"Request error occurred: {str(e)}")
        return {"items": [], "error": f"Request failed: {str(e)}"}
    except Exception as e:
        logging.error(f"Unexpected error in fetch_api: {str(e)}", exc_info=True)
        return {"items": [], "error": f"Unexpected error: {str(e)}"}

async def fetch_balance(address: str) -> Dict:
    """Fetch the confirmed balance for an address."""
    return await fetch_api(f"addresses/{address}/balance/confirmed")

async def fetch_address_transactions(address: str, limit: int = 20, offset: int = 0) -> Dict:
    """Fetch transactions for an address."""
    try:
        url = f"{ERGO_EXPLORER_API}/addresses/{address}/transactions"
        logging.info(f"Making API request to: {url}")
        
        params = {"limit": limit, "offset": offset}
        
        async with httpx.AsyncClient() as client:
            headers = {"User-Agent": USER_AGENT}
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            
            # Log request details
            logging.info(f"HTTP Request: {response.request.method} {response.request.url}")
            logging.info(f"HTTP Response: {response.status_code}")
            
            # Check for error status codes
            if response.status_code != 200:
                logging.error(f"HTTP error received: {response.status_code} for address {address}")
                return {
                    "items": [],
                    "total": 0,
                    "error": f"HTTP error: {response.status_code}",
                    "address": address
                }
            
            # Try to parse JSON response
            try:
                data = response.json()
                # Validate the response structure
                if not isinstance(data, dict):
                    logging.error(f"Invalid response format: expected dict, got {type(data)}")
                    return {
                        "items": [],
                        "total": 0,
                        "error": "Invalid response format",
                        "address": address
                    }
                
                # Ensure the expected structure exists
                if "items" not in data:
                    logging.warning(f"No 'items' field in response for address {address}. Keys: {list(data.keys())}")
                    data["items"] = []
                
                if "total" not in data:
                    data["total"] = len(data.get("items", []))
                    
                # Log some information about the results    
                logging.info(f"Retrieved {len(data.get('items', []))} transactions for address {address} (total: {data.get('total', 0)})")
                
                # Add the address to the response for reference
                data["address"] = address
                
                return data
            except ValueError as e:
                logging.error(f"Failed to parse JSON response from address transactions: {str(e)}")
                return {
                    "items": [],
                    "total": 0,
                    "error": "Invalid JSON response",
                    "address": address
                }
                
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error occurred in fetch_address_transactions: {str(e)}")
        return {
            "items": [],
            "total": 0,
            "error": f"HTTP error: {e.response.status_code}",
            "address": address
        }
    except httpx.RequestError as e:
        logging.error(f"Request error occurred in fetch_address_transactions: {str(e)}")
        return {
            "items": [],
            "total": 0,
            "error": f"Request failed: {str(e)}",
            "address": address
        }
    except Exception as e:
        logging.error(f"Unexpected error in fetch_address_transactions: {str(e)}", exc_info=True)
        return {
            "items": [],
            "total": 0,
            "error": f"Unexpected error: {str(e)}",
            "address": address
        }

async def fetch_transaction(tx_id: str) -> Dict:
    """Fetch details for a specific transaction."""
    return await fetch_api(f"transactions/{tx_id}")

async def fetch_block(block_id: str) -> Dict:
    """Fetch details for a specific block."""
    return await fetch_api(f"blocks/{block_id}")

async def fetch_network_state() -> Dict:
    """Fetch the current network state."""
    return await fetch_api("networkState")

async def fetch_box(box_id: str) -> Dict:
    """Fetch details for a specific box (UTXO)."""
    return await fetch_api(f"boxes/{box_id}")

async def get_token_by_id(token_id: str) -> Dict:
    """Fetch details for a specific token by ID."""
    return await fetch_api(f"tokens/{token_id}")

async def fetch_token_info(token_id: str) -> Dict:
    """
    Fetch detailed information about a token by its ID.
    
    Args:
        token_id: The token ID to look up
        
    Returns:
        A dictionary containing token details including name, description, and metadata
    """
    try:
        response = await fetch_api(f"tokens/{token_id}")
        logging.info(f"Successfully fetched token info for {token_id}")
        return response
    except Exception as e:
        logging.error(f"Error fetching token info for {token_id}: {str(e)}")
        return {"error": str(e)}

async def search_tokens(query: str) -> Dict:
    """Search for tokens by ID or symbol."""
    try:
        params = {"query": query}
        response = await fetch_api("tokens/search", params=params)
        
        # Ensure we have a valid response
        if not isinstance(response, dict):
            logging.error(f"Invalid response type from API: {type(response)}")
            return {"items": [], "error": "Invalid response from API"}
            
        # If response is empty or doesn't contain items, return empty result
        if not response or "items" not in response:
            return {"items": []}
            
        return response
    except Exception as e:
        logging.error(f"Error in search_tokens: {str(e)}", exc_info=True)
        return {"items": [], "error": str(e)}

async def fetch_blocks_at_height(height: int) -> List[Dict]:
    """
    Fetch blocks at a specific height.
    
    Args:
        height: The block height to fetch
        
    Returns:
        A list of blocks at the specified height
    """
    return await fetch_api(f"blocks/at/{height}")

async def fetch_latest_blocks(limit: int = 10, offset: int = 0) -> Dict:
    """
    Fetch the latest blocks from the blockchain.
    
    Args:
        limit: Maximum number of blocks to retrieve
        offset: Number of blocks to skip
        
    Returns:
        A dictionary containing the latest blocks
    """
    params = {"limit": limit, "offset": offset}
    return await fetch_api("blocks", params=params)

async def fetch_block_transactions(block_id: str, limit: int = 100, offset: int = 0) -> Dict:
    """
    Fetch transactions for a specific block.
    
    Args:
        block_id: The ID of the block
        limit: Maximum number of transactions to retrieve
        offset: Number of transactions to skip
        
    Returns:
        A dictionary containing the block's transactions
    """
    params = {"limit": limit, "offset": offset}
    return await fetch_api(f"blocks/{block_id}/transactions", params=params)

async def fetch_address_book() -> Dict:
    """
    Fetch address book data from ergexplorer.com.
    
    This function retrieves a comprehensive list of known addresses
    including services, exchanges, mining pools, and other notable addresses
    in the Ergo ecosystem.
    
    Returns:
        A dictionary containing address book entries and token information
    """
    try:
        # This API is from a different domain than the standard explorer API
        url = "https://api.ergexplorer.com/addressbook/getAddresses"
        
        logging.info(f"Fetching address book data from: {url}")
        
        async with httpx.AsyncClient() as client:
            headers = {"User-Agent": USER_AGENT}
            # Add longer timeout and more retries for external API
            response = await client.get(url, headers=headers, timeout=60.0)
            
            # Log response status
            logging.info(f"Address book API response status: {response.status_code}")
            
            # Check for error status codes
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                data = response.json()
                # Log success
                logging.info(f"Successfully fetched address book data: {len(data.get('items', []))} items found")
                return data
            except ValueError as e:
                logging.error(f"Failed to parse address book JSON response: {str(e)}")
                return _load_fallback_address_book()
                
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error occurred in address book request: {str(e)}")
        return _load_fallback_address_book()
    except httpx.RequestError as e:
        logging.error(f"Request error occurred in address book request: {str(e)}")
        # Provide a more detailed error message and suggestions
        error_message = str(e)
        if "No address associated with hostname" in error_message:
            logging.error("DNS resolution failed for api.ergexplorer.com. Check network connectivity or DNS settings.")
            error_message = "Cannot resolve api.ergexplorer.com. Check network connectivity or DNS settings."
        
        # Use fallback data
        logging.info("Using fallback address book data")
        return _load_fallback_address_book()
    except Exception as e:
        logging.error(f"Unexpected error in fetch_address_book: {str(e)}", exc_info=True)
        return _load_fallback_address_book()

def _load_fallback_address_book() -> Dict:
    """
    Load fallback address book data from a local JSON file.
    
    This is used when the API is not reachable.
    
    Returns:
        A dictionary containing the fallback address book data
    """
    try:
        # Get the path to the fallback file
        fallback_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "resources",
            "address_book_fallback.json"
        )
        
        logging.info(f"Loading fallback address book data from: {fallback_path}")
        
        with open(fallback_path, 'r') as f:
            data = json.load(f)
            
        logging.info(f"Successfully loaded fallback address book data: {len(data.get('items', []))} items found")
        
        # Add a note that this is fallback data
        data["note"] = "This is fallback data. The actual API could not be reached."
        
        return data
    except Exception as e:
        logging.error(f"Error loading fallback address book data: {str(e)}", exc_info=True)
        return {
            "items": [],
            "total": 0,
            "tokens": [],
            "error": "Could not reach API and fallback data could not be loaded."
        } 