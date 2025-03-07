"""ErgoWatch integration tools for the Ergo Explorer MCP."""
from typing import Dict, List, Optional
from ..api import ergowatch

async def get_address_balance_history(address: str, token_id: Optional[str] = None) -> str:
    """Get balance history for an address.
    
    Args:
        address: The Ergo address to check
        token_id: Optional token ID to get history for specific token
    """
    history = await ergowatch.get_address_balance_history(address, token_id)
    
    if not history:
        return f"No balance history found for address {address}"
    
    result = f"Balance History for {address}:\n"
    for entry in history:
        timestamp = entry.get("timestamp", 0)
        balance = entry.get("balance", 0)
        height = entry.get("height", 0)
        result += f"• Height {height}: {balance} ERG (Timestamp: {timestamp})\n"
    
    return result

async def get_address_balance_at_height(address: str, height: int, token_id: Optional[str] = None) -> str:
    """Get address balance at a specific height.
    
    Args:
        address: The Ergo address to check
        height: Block height to check balance at
        token_id: Optional token ID to get balance for specific token
    """
    balance = await ergowatch.get_address_balance_at_height(address, height, token_id)
    
    if not balance:
        return f"No balance found for address {address} at height {height}"
    
    amount = balance.get("amount", 0)
    token_name = "ERG" if not token_id else balance.get("token_name", "Unknown Token")
    
    # Convert nanoERG to ERG if token is ERG
    if token_name == "ERG":
        amount = amount / 1_000_000_000
        # Format as integer if whole number, otherwise keep decimal places
        amount = int(amount) if amount.is_integer() else amount
    
    return f"Balance for {address} at height {height}:\n• {amount} {token_name}"

async def get_contract_stats() -> str:
    """Get statistics about contract addresses."""
    count = await ergowatch.get_contract_address_count()
    supply = await ergowatch.get_contracts_supply()
    
    result = "Contract Address Statistics:\n"
    result += f"• Total Contract Addresses: {count.get('count', 0)}\n"
    result += f"• Total ERG in Contracts: {supply.get('amount', 0) / 1_000_000_000:.2f} ERG\n"
    result += f"• Percentage of Supply: {supply.get('percentage', 0):.2f}%\n"
    
    return result

async def get_p2pk_stats() -> str:
    """Get statistics about P2PK addresses."""
    count = await ergowatch.get_p2pk_address_count()
    
    result = "P2PK Address Statistics:\n"
    result += f"• Total P2PK Addresses: {count.get('count', 0)}\n"
    
    return result

async def get_exchange_addresses() -> str:
    """Get list of tracked exchange addresses."""
    exchanges = await ergowatch.get_exchange_addresses()
    
    if not exchanges:
        return "No exchange addresses found"
    
    result = "Tracked Exchange Addresses:\n"
    for exchange in exchanges:
        name = exchange.get("name", "Unknown Exchange")
        address = exchange.get("address", "")
        balance = exchange.get("balance", 0) / 1_000_000_000
        result += f"• {name}:\n  Address: {address}\n  Balance: {balance:.2f} ERG\n"
    
    return result

async def get_rich_list(limit: int = 10, token_id: Optional[str] = None) -> str:
    """Get rich list of addresses sorted by balance.
    
    Args:
        limit: Number of addresses to return (default: 10)
        token_id: Optional token ID to get rich list for specific token
    """
    rich_list = await ergowatch.get_rich_list(limit=limit, token_id=token_id)
    
    if not rich_list:
        return "No addresses found"
    
    token_name = "ERG" if not token_id else rich_list.get("token_name", "Unknown Token")
    addresses = rich_list.get("addresses", [])
    
    result = f"Top {limit} Addresses by {token_name} Balance:\n"
    for i, addr in enumerate(addresses, 1):
        address = addr.get("address", "Unknown")
        balance = addr.get("balance", 0)
        if token_name == "ERG":
            balance = balance / 1_000_000_000
        result += f"{i}. {address}: {balance:.2f} {token_name}\n"
    
    return result

async def get_address_rank(address: str) -> str:
    """Get rank of a P2PK address in terms of balance.
    
    Args:
        address: The P2PK address to check
    """
    rank_info = await ergowatch.get_p2pk_address_rank(address)
    
    if not rank_info:
        return f"No ranking found for address {address}"
    
    rank = rank_info.get("rank", 0)
    total = rank_info.get("total", 0)
    balance = rank_info.get("balance", 0) / 1_000_000_000
    
    return f"Address Ranking for {address}:\n• Rank: {rank} of {total}\n• Balance: {balance:.2f} ERG" 