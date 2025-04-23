"""
Miscellaneous MCP tools for Ergo blockchain.
"""

from ergo_explorer.api import search_tokens, fetch_network_state


async def search_for_token(query: str) -> str:
    """Search for tokens on the Ergo blockchain by name or ID.
    
    Args:
        query: Token name or ID (minimum 3 characters)
    """
    try:
        # Basic validation
        if len(query) < 3:
            return "Search query must be at least 3 characters long."
            
        # Search for tokens
        results = await search_tokens(query)
        items = results.get("items", [])
        
        if not items:
            return f"No tokens found matching '{query}'."
            
        # Format results
        result = f"Token Search Results for '{query}'\n"
        result += f"Found {len(items)} tokens\n\n"
        
        for i, token in enumerate(items, 1):
            token_id = token.get("id", "Unknown")
            token_name = token.get("name", "Unknown Token")
            token_description = token.get("description", "No description available")
            
            # Get token stats
            emission_amount = token.get("emissionAmount", 0)
            decimals = token.get("decimals", 0)
            
            # Format emission amount with decimals if applicable
            if decimals > 0:
                formatted_emission = emission_amount / (10 ** decimals)
                supply_str = f"{formatted_emission:.{decimals}f}"
            else:
                supply_str = str(emission_amount)
                
            # Format result
            result += f"{i}. {token_name}\n"
            result += f"   ID: {token_id}\n"
            result += f"   Supply: {supply_str}\n"
            if token_description and token_description != "null":
                # Truncate long descriptions
                if len(token_description) > 100:
                    token_description = token_description[:97] + "..."
                result += f"   Description: {token_description}\n"
            result += "\n"
            
        return result
    except Exception as e:
        return f"Error searching for token: {str(e)}"

# The get_network_status function is removed as it's redundant with get_info 