"""ErgoWatch API client for Ergo blockchain analytics."""
import httpx
from typing import Dict, List, Optional, Union
from ..config import ERGOWATCH_API_URL

async def fetch_api(endpoint: str, params: Optional[Dict] = None) -> Dict:
    """Make a request to the ErgoWatch API."""
    url = f"{ERGOWATCH_API_URL}/{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()

# Address Analytics
async def get_address_balance(address: str, token_id: Optional[str] = None) -> Dict:
    """Get current balance for an address.
    
    Args:
        address: The Ergo address to check
        token_id: Optional token ID to get balance for specific token
    """
    params = {"token_id": token_id} if token_id else None
    return await fetch_api(f"addresses/{address}/balance", params=params)

async def get_address_balance_at_height(address: str, height: int, token_id: Optional[str] = None) -> Dict:
    """Get address balance at specific height.
    
    Args:
        address: The Ergo address to check
        height: Block height to check balance at
        token_id: Optional token ID to get balance for specific token
    """
    params = {"token_id": token_id} if token_id else None
    return await fetch_api(f"addresses/{address}/balance/at/height/{height}", params=params)

async def get_address_balance_history(address: str, token_id: Optional[str] = None) -> Dict:
    """Get balance history for an address.
    
    Args:
        address: The Ergo address to check
        token_id: Optional token ID to get history for specific token
    """
    params = {"token_id": token_id} if token_id else None
    return await fetch_api(f"addresses/{address}/balance/history", params=params)

# P2PK Address Stats
async def get_p2pk_address_count() -> Dict:
    """Get the total number of P2PK addresses."""
    return await fetch_api("p2pk/count")

# Contract Statistics
async def get_contract_address_count() -> Dict:
    """Get the total number of contract addresses (P2S & P2SH)."""
    return await fetch_api("contracts/count")

async def get_contracts_supply() -> Dict:
    """Get the total supply held in contract addresses."""
    return await fetch_api("contracts/supply")

# Exchange Monitoring
async def get_exchange_addresses() -> List[Dict]:
    """Get list of tracked exchange addresses."""
    return await fetch_api("exchanges/tracklist")

# Rich Lists
async def get_rich_list(limit: int = 100, offset: int = 0, token_id: Optional[str] = None) -> Dict:
    """Get rich list of addresses sorted by balance.
    
    Args:
        limit: Number of addresses to return
        offset: Offset for pagination
        token_id: Optional token ID to get rich list for specific token
    """
    params = {
        "limit": limit,
        "offset": offset
    }
    if token_id:
        params["token_id"] = token_id
    return await fetch_api("lists/addresses/by/balance", params=params)

# Utility Functions
async def height_to_timestamp(height: int) -> Dict:
    """Convert block height to timestamp.
    
    Args:
        height: Block height to convert
    """
    return await fetch_api(f"utils/height2timestamp/{height}")

async def timestamp_to_height(timestamp: int) -> Dict:
    """Convert timestamp to nearest block height.
    
    Args:
        timestamp: Timestamp in milliseconds since unix epoch
    """
    return await fetch_api(f"utils/timestamp2height/{timestamp}")

# Misc
async def get_p2pk_address_rank(address: str) -> Dict:
    """Get rank of a P2PK address in terms of balance.
    
    Args:
        address: The P2PK address to check
    """
    return await fetch_api(f"ranking/{address}")

async def get_sigmausd_state() -> Dict:
    """Get current state of the SigmaUSD protocol."""
    return await fetch_api("sigmausd/state") 