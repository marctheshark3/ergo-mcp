"""
Address-related MCP resources for Ergo blockchain.
"""

from ergo_explorer.api import fetch_balance

async def get_address_balance_resource(address: str) -> dict:
    """Get the confirmed balance for an Ergo address.
    
    Args:
        address: Ergo blockchain address
    """
    try:
        balance = await fetch_balance(address)
        
        # Format ERG amount
        erg_amount = balance.get("nanoErgs", 0) / 1_000_000_000
        
        formatted_tokens = []
        for token in balance.get("tokens", []):
            formatted_tokens.append({
                "tokenId": token.get("tokenId", ""),
                "name": token.get("name", "Unknown Token"),
                "amount": token.get("amount", 0),
                "decimals": token.get("decimals", 0),
                "formatted": token.get("amount", 0) / (10 ** token.get("decimals", 0)) if token.get("decimals", 0) > 0 else token.get("amount", 0)
            })
            
        return {
            "address": address,
            "confirmedBalance": {
                "nanoErgs": balance.get("nanoErgs", 0),
                "ergs": erg_amount,
                "tokens": formatted_tokens
            }
        }
    except Exception as e:
        return {"error": str(e)} 