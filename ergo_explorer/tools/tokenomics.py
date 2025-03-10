"""
MCP tools for token price and liquidity analysis.
"""
from typing import Dict, List, Optional, Any

from ergo_explorer.api import (
    get_token_price,
    get_erg_price_usd,
    get_liquidity_pools,
    get_price_history,
    search_tokens
)


async def get_token_price_info(token_query: str) -> str:
    """Get the current price and basic market information for a token.
    
    Args:
        token_query: Token name or ID to search for
    """
    try:
        # First, search for the token to get the ID
        search_results = await search_tokens(token_query)
        tokens = search_results.get("items", [])
        
        if not tokens:
            return f"No tokens found matching '{token_query}'. Please try a different search term."
        
        # Take the first token from the results
        token = tokens[0]
        token_id = token.get("id")
        token_name = token.get("name", "Unknown Token")
        token_ticker = token.get("tokenType", {}).get("tokenId", token_name[:4].upper())
        
        # Get price information
        price_data = await get_token_price(token_id)
        
        if "error" in price_data:
            return f"Found token {token_name} (ID: {token_id[:8]}...), but {price_data['error'].lower()}"
        
        # Format the response
        erg_price = price_data.get("price_in_erg", 0)
        usd_price = price_data.get("price_in_usd", 0)
        liquidity = price_data.get("liquidity", 0)
        volume = price_data.get("volume_24h", 0)
        
        result = f"Token Price Information for {token_name} ({token_ticker})\n"
        result += f"Token ID: {token_id}\n\n"
        result += f"Current Price: {erg_price:.8f} ERG (${usd_price:.4f})\n"
        result += f"Liquidity: {liquidity:.2f} ERG\n"
        result += f"24h Volume: {volume:.2f} ERG\n"
        result += f"Source: {price_data.get('source', 'ErgoDEX')}\n"
        
        return result
        
    except Exception as e:
        return f"Error fetching token price: {str(e)}"


async def get_token_price_chart(token_query: str, days: int = 7) -> str:
    """Get price chart data for a token.
    
    Args:
        token_query: Token name or ID to search for
        days: Number of days to show history for (default: 7)
    """
    try:
        # Validate days parameter
        if days < 1 or days > 30:
            return "Days parameter must be between 1 and 30."
            
        # First, search for the token to get the ID
        search_results = await search_tokens(token_query)
        tokens = search_results.get("items", [])
        
        if not tokens:
            return f"No tokens found matching '{token_query}'. Please try a different search term."
        
        # Take the first token from the results
        token = tokens[0]
        token_id = token.get("id")
        token_name = token.get("name", "Unknown Token")
        
        # Get price history
        history = await get_price_history(token_id, days)
        
        if history and "error" in history[0]:
            return f"Found token {token_name} (ID: {token_id[:8]}...), but {history[0]['error'].lower()}"
        
        # Format the response
        result = f"Price History for {token_name} (Last {days} days)\n\n"
        result += "Date           | Price (ERG)    | Price (USD)\n"
        result += "---------------|---------------|-------------\n"
        
        for point in history:
            date = point.get("date", "Unknown")
            erg_price = point.get("price_in_erg", 0)
            usd_price = point.get("price_in_usd", 0)
            
            result += f"{date} | {erg_price:.8f} | ${usd_price:.4f}\n"
        
        result += "\nNote: Historical price data is based on available liquidity pool data."
        return result
        
    except Exception as e:
        return f"Error fetching token price history: {str(e)}"


async def get_liquidity_pool_info(token_query: Optional[str] = None) -> str:
    """Get information about liquidity pools, optionally filtered by token.
    
    Args:
        token_query: Optional token name or ID to filter pools
    """
    try:
        token_id = None
        
        # If token query is provided, search for the token
        if token_query:
            search_results = await search_tokens(token_query)
            tokens = search_results.get("items", [])
            
            if not tokens:
                return f"No tokens found matching '{token_query}'. Please try a different search term."
            
            # Take the first token from the results
            token = tokens[0]
            token_id = token.get("id")
            token_name = token.get("name", "Unknown Token")
        
        # Get liquidity pools
        pools = await get_liquidity_pools(token_id)
        
        if pools and "error" in pools[0]:
            return f"Error: {pools[0]['error']}"
        
        # Format the results
        if token_query:
            result = f"Liquidity Pools for {token_name}\n\n"
        else:
            result = "Top Liquidity Pools on ErgoDEX\n\n"
        
        if not pools:
            return result + "No liquidity pools found."
        
        # Limit to top 10 pools for readability
        display_pools = pools[:10]
        
        result += "Pool                   | Base Token       | Quote Token      | Liquidity (ERG) | TVL (USD)\n"
        result += "-----------------------|------------------|------------------|-----------------|----------\n"
        
        for pool in display_pools:
            pool_id = pool.get("pool_id", "")[:8] + "..."
            base = pool.get("base_token", {})
            quote = pool.get("quote_token", {})
            
            base_name = base.get("name", "Unknown")[:15]
            quote_name = quote.get("name", "Unknown")[:15]
            
            liquidity = pool.get("liquidity_erg", 0)
            tvl = pool.get("tvl_usd", 0)
            
            result += f"{pool_id} | {base_name:<16} | {quote_name:<16} | {liquidity:,.2f} | ${tvl:,.2f}\n"
        
        if len(pools) > 10:
            result += f"\n...and {len(pools) - 10} more pools."
            
        # Add volume information
        total_volume = sum(
            sum(p.get("volume_24h", {}).get(key, 0) for key in ["base", "quote"]) 
            for p in pools
        )
        
        erg_price = await get_erg_price_usd()
        result += f"\n\nTotal 24h Volume: {total_volume:,.2f} ERG (${total_volume * erg_price:,.2f})"
        result += f"\nTotal Value Locked: ${sum(p.get('tvl_usd', 0) for p in pools):,.2f}"
        
        return result
        
    except Exception as e:
        return f"Error fetching liquidity pools: {str(e)}"


async def get_token_swap_info(from_token: str, to_token: str, amount: float) -> str:
    """Get swap information between two tokens.
    
    Args:
        from_token: Source token name or ID
        to_token: Target token name or ID
        amount: Amount of source token to swap
    """
    try:
        # Validate amount
        if amount <= 0:
            return "Amount must be greater than 0."
            
        # Search for source token
        from_search = await search_tokens(from_token)
        from_tokens = from_search.get("items", [])
        
        if not from_tokens:
            return f"No tokens found matching source token '{from_token}'."
            
        from_token_data = from_tokens[0]
        from_id = from_token_data.get("id")
        from_name = from_token_data.get("name", "Unknown Token")
        from_decimals = from_token_data.get("decimals", 0)
        
        # Search for target token
        to_search = await search_tokens(to_token)
        to_tokens = to_search.get("items", [])
        
        if not to_tokens:
            return f"No tokens found matching target token '{to_token}'."
            
        to_token_data = to_tokens[0]
        to_id = to_token_data.get("id")
        to_name = to_token_data.get("name", "Unknown Token")
        
        # Get all liquidity pools
        all_pools = await get_liquidity_pools()
        
        # Find pools that connect these tokens (directly or via ERG)
        direct_pools = []
        for pool in all_pools:
            base_id = pool.get("base_token", {}).get("id", "")
            quote_id = pool.get("quote_token", {}).get("id", "")
            
            # Check for direct path
            if (base_id == from_id and quote_id == to_id) or (base_id == to_id and quote_id == from_id):
                direct_pools.append(pool)
        
        # If no direct pools, look for indirect paths via ERG
        if not direct_pools:
            # Find pools with from_token and ERG
            from_erg_pools = [
                p for p in all_pools if from_id in [
                    p.get("base_token", {}).get("id", ""),
                    p.get("quote_token", {}).get("id", "")
                ]
            ]
            
            # Find pools with to_token and ERG
            to_erg_pools = [
                p for p in all_pools if to_id in [
                    p.get("base_token", {}).get("id", ""),
                    p.get("quote_token", {}).get("id", "")
                ]
            ]
            
            # If we have both, we can do a multi-hop swap
            if from_erg_pools and to_erg_pools:
                # Use the pools with highest liquidity
                from_erg_pool = sorted(from_erg_pools, key=lambda p: p.get("liquidity_erg", 0), reverse=True)[0]
                to_erg_pool = sorted(to_erg_pools, key=lambda p: p.get("liquidity_erg", 0), reverse=True)[0]
                
                # Calculate estimated output
                # For simplicity, we just get the price and multiply
                from_price = await get_token_price(from_id)
                to_price = await get_token_price(to_id)
                
                if "error" in from_price or "error" in to_price:
                    return f"Cannot calculate swap: Price data unavailable for one or both tokens."
                
                # Calculate the swap
                erg_equivalent = amount * from_price.get("price_in_erg", 0)
                to_amount = erg_equivalent / to_price.get("price_in_erg", 0)
                
                # Factor in fees (0.3% per swap typically)
                fee_factor = 0.997 * 0.997  # Two swaps with 0.3% fee each
                to_amount_after_fees = to_amount * fee_factor
                
                # Format the response
                result = f"Swap Estimate: {amount} {from_name} → {to_amount_after_fees:.8f} {to_name}\n\n"
                result += f"Path: {from_name} → ERG → {to_name}\n"
                result += f"Rate: 1 {from_name} ≈ {to_amount_after_fees/amount:.8f} {to_name}\n"
                result += f"Fees: 0.3% per hop (0.6% total)\n\n"
                result += "Note: This is an estimate. Actual swap rates may vary due to slippage and price impact."
                
                return result
            else:
                return f"No liquidity pools found connecting {from_name} and {to_name}."
        else:
            # Use the direct pool with highest liquidity
            pool = sorted(direct_pools, key=lambda p: p.get("liquidity_erg", 0), reverse=True)[0]
            
            # Check if from_token is base or quote
            base_id = pool.get("base_token", {}).get("id", "")
            base_reserves = pool.get("base_token", {}).get("reserves", 0)
            quote_reserves = pool.get("quote_token", {}).get("reserves", 0)
            
            # Calculate the output amount using constant product formula
            # (x * y = k)
            if base_id == from_id:
                # Calculate input amount considering decimals
                input_amount = amount * (10 ** from_decimals)
                
                # Calculate output using constant product formula
                # y_out = y_reserve * x_in / (x_reserve + x_in)
                output_reserves = quote_reserves * input_amount / (base_reserves + input_amount)
                
                # Apply pool fee
                fee_percent = pool.get("fee_percent", 0.3)
                output_after_fees = output_reserves * (100 - fee_percent) / 100
                
                # Format to human-readable
                to_decimals = pool.get("quote_token", {}).get("decimals", 0)
                to_amount = output_after_fees / (10 ** to_decimals)
            else:
                # from_token is quote
                input_amount = amount * (10 ** from_decimals)
                
                # Calculate output using formula
                output_reserves = base_reserves * input_amount / (quote_reserves + input_amount)
                
                # Apply pool fee
                fee_percent = pool.get("fee_percent", 0.3)
                output_after_fees = output_reserves * (100 - fee_percent) / 100
                
                # Format to human-readable
                to_decimals = pool.get("base_token", {}).get("decimals", 0)
                to_amount = output_after_fees / (10 ** to_decimals)
            
            # Format the response
            result = f"Swap Estimate: {amount} {from_name} → {to_amount:.8f} {to_name}\n\n"
            result += f"Direct swap via pool: {pool.get('pool_id', '')[:8]}...\n"
            result += f"Rate: 1 {from_name} ≈ {to_amount/amount:.8f} {to_name}\n"
            result += f"Fee: {pool.get('fee_percent', 0.3)}%\n\n"
            result += "Note: This is an estimate. Actual swap rates may vary due to slippage and price impact."
            
            return result
            
    except Exception as e:
        return f"Error calculating swap: {str(e)}" 