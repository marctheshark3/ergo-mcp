"""
API client for interacting with ErgoDEX for token prices and liquidity information.
"""
import httpx
from typing import Dict, List, Optional, Union, Any
import asyncio
from datetime import datetime, timedelta

# ErgoDEX API endpoints
ERGODEX_API_URL = "https://api.ergodex.io/v1"
SPECTRUM_API_URL = "https://api.spectrum.fi/v1"

async def fetch_ergodex_api(endpoint: str, params: Optional[Dict] = None) -> Dict:
    """Make a request to the ErgoDEX API."""
    url = f"{ERGODEX_API_URL}/{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()

async def fetch_spectrum_api(endpoint: str, params: Optional[Dict] = None) -> Dict:
    """Make a request to the Spectrum Finance API."""
    url = f"{SPECTRUM_API_URL}/{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()

async def get_token_price(token_id: str) -> Dict[str, Any]:
    """Get the current price of a token in ERG.
    
    Args:
        token_id: ID of the token to check
        
    Returns:
        Dictionary with price information
    """
    try:
        # First try ErgoDEX API
        pools = await fetch_ergodex_api("amm/pools")
        
        # Find pools with this token
        relevant_pools = []
        for pool in pools:
            if pool.get("quoteId") == token_id or pool.get("baseId") == token_id:
                relevant_pools.append(pool)
        
        if not relevant_pools:
            return {"error": f"No liquidity pools found for token {token_id}"}
        
        # Calculate price from the pool with highest liquidity
        # Sort pools by liquidity
        sorted_pools = sorted(relevant_pools, key=lambda x: x.get("liquidity", 0), reverse=True)
        best_pool = sorted_pools[0]
        
        # Calculate price based on pool ratio
        is_quote = best_pool.get("quoteId") == token_id
        
        if is_quote:
            price_in_erg = best_pool.get("baseReserves", 0) / best_pool.get("quoteReserves", 0)
            volume = best_pool.get("volume24h", {}).get("quote", 0)
        else:
            price_in_erg = best_pool.get("quoteReserves", 0) / best_pool.get("baseReserves", 0)
            volume = best_pool.get("volume24h", {}).get("base", 0)
        
        return {
            "price_in_erg": price_in_erg,
            "price_in_usd": price_in_erg * await get_erg_price_usd(),
            "liquidity": best_pool.get("liquidity", 0),
            "volume_24h": volume,
            "pool_id": best_pool.get("poolId"),
            "source": "ErgoDEX"
        }
    
    except Exception as e:
        return {"error": f"Error fetching token price: {str(e)}"}

async def get_erg_price_usd() -> float:
    """Get the current price of ERG in USD."""
    try:
        # First try the Spectrum API
        response = await fetch_spectrum_api("price/erg")
        return float(response.get("price", 0))
    except Exception:
        # Fallback to another source like CoinGecko
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "ergo", "vs_currencies": "usd"},
                timeout=30.0
            )
            data = response.json()
            return float(data.get("ergo", {}).get("usd", 0))

async def get_liquidity_pools(token_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get liquidity pools information, optionally filtered by token.
    
    Args:
        token_id: Optional token ID to filter pools
        
    Returns:
        List of liquidity pools with detailed information
    """
    try:
        pools = await fetch_ergodex_api("amm/pools")
        
        # Process and enrich pool data
        enriched_pools = []
        for pool in pools:
            # Skip if we're filtering by token and this pool doesn't contain it
            if token_id and token_id not in [pool.get("quoteId"), pool.get("baseId")]:
                continue
                
            # Calculate additional metrics
            tvl_usd = pool.get("liquidity", 0) * await get_erg_price_usd()
            
            enriched_pool = {
                "pool_id": pool.get("poolId"),
                "base_token": {
                    "id": pool.get("baseId"),
                    "name": pool.get("baseName", "Unknown"),
                    "decimals": pool.get("baseDecimals", 0),
                    "reserves": pool.get("baseReserves", 0)
                },
                "quote_token": {
                    "id": pool.get("quoteId"),
                    "name": pool.get("quoteName", "Unknown"),
                    "decimals": pool.get("quoteDecimals", 0),
                    "reserves": pool.get("quoteReserves", 0)
                },
                "liquidity_erg": pool.get("liquidity", 0),
                "tvl_usd": tvl_usd,
                "volume_24h": pool.get("volume24h", {}),
                "fee_percent": pool.get("fee", 0) * 100,
                "created_at": pool.get("timestamp", 0)
            }
            
            enriched_pools.append(enriched_pool)
        
        # Sort by liquidity (highest first)
        return sorted(enriched_pools, key=lambda x: x.get("liquidity_erg", 0), reverse=True)
    
    except Exception as e:
        return [{"error": f"Error fetching liquidity pools: {str(e)}"}]

async def get_price_history(token_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """Get historical price data for a token.
    
    Args:
        token_id: ID of the token to check
        days: Number of days to fetch history for
        
    Returns:
        List of historical price points
    """
    try:
        # This would ideally come from a time series API endpoint
        # For now, let's create a placeholder implementation with mock data
        # In real implementation, you would query a historical price API
        
        # Get current price as reference
        current_price_data = await get_token_price(token_id)
        if "error" in current_price_data:
            return [{"error": current_price_data["error"]}]
            
        current_price = current_price_data.get("price_in_erg", 0)
        
        # Generate mock historical data
        # In a real implementation, this would be replaced with actual API calls
        history = []
        now = datetime.now()
        
        for i in range(days, -1, -1):
            date = now - timedelta(days=i)
            # Create some random-ish variation for the demo
            variation = (days - i) * 0.01 - 0.05
            price = current_price * (1 + variation)
            
            history.append({
                "timestamp": int(date.timestamp() * 1000),
                "date": date.strftime("%Y-%m-%d"),
                "price_in_erg": price,
                "price_in_usd": price * await get_erg_price_usd()
            })
        
        return history
    
    except Exception as e:
        return [{"error": f"Error fetching price history: {str(e)}"}] 