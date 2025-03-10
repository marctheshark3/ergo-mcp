"""
API client for interacting with the Ergo Explorer API.
"""

import httpx
from typing import Dict, Optional

from ergo_explorer.config import ERGO_EXPLORER_API, USER_AGENT

async def fetch_api(endpoint: str, params: Optional[Dict] = None) -> Dict:
    """Make a request to the Ergo Explorer API."""
    url = f"{ERGO_EXPLORER_API}/{endpoint}"
    async with httpx.AsyncClient() as client:
        headers = {"User-Agent": USER_AGENT}
        response = await client.get(url, headers=headers, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()

async def fetch_balance(address: str) -> Dict:
    """Fetch the confirmed balance for an address."""
    return await fetch_api(f"addresses/{address}/balance/confirmed")

async def fetch_address_transactions(address: str, limit: int = 20, offset: int = 0) -> Dict:
    """Fetch transactions for an address."""
    params = {"limit": limit, "offset": offset}
    return await fetch_api(f"addresses/{address}/transactions", params=params)

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

async def search_tokens(query: str) -> Dict:
    """Search for tokens by ID or symbol."""
    params = {"query": query}
    return await fetch_api("tokens/search", params=params)

"""
API functions for the Ergo Explorer MCP server.
"""

# Explorer API functions
from ergo_explorer.api.explorer import (
    fetch_api,
    fetch_balance,
    fetch_address_transactions,
    fetch_transaction,
    fetch_block,
    fetch_network_state,
    fetch_box,
    search_tokens
)

# Node API functions
from ergo_explorer.api.node import (
    get_address_balance_node,
    get_transaction_node,
    get_transaction_by_address_node,
    submit_transaction_node,
    get_box_by_id_node,
    get_box_by_address_node,
    get_unspent_boxes_by_address_node,
    get_token_by_id_node,
    search_for_token_node,
    get_network_info_node
)

# ErgoDEX API functions
from ergo_explorer.api.ergodex import (
    get_token_price,
    get_erg_price_usd,
    get_liquidity_pools,
    get_price_history
)

__all__ = [
    # Explorer API
    'fetch_api',
    'fetch_balance',
    'fetch_address_transactions',
    'fetch_transaction',
    'fetch_block',
    'fetch_network_state',
    'fetch_box',
    'search_tokens',
    
    # Node API
    'get_address_balance_node',
    'get_transaction_node',
    'get_transaction_by_address_node',
    'submit_transaction_node',
    'get_box_by_id_node',
    'get_box_by_address_node',
    'get_unspent_boxes_by_address_node',
    'get_token_by_id_node',
    'search_for_token_node',
    'get_network_info_node',
    
    # ErgoDEX API
    'get_token_price',
    'get_erg_price_usd',
    'get_liquidity_pools',
    'get_price_history'
]
