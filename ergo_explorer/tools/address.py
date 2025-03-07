"""
MCP tools for working with Ergo blockchain addresses.
"""

from typing import Dict, Set, List, Any
from datetime import datetime

from ergo_explorer.api import fetch_balance, fetch_address_transactions


async def get_address_balance(address: str) -> str:
    """Get the confirmed balance for an Ergo address.
    
    Args:
        address: Ergo blockchain address
    """
    try:
        balance = await fetch_balance(address)
        
        # Format ERG amount
        erg_amount = balance.get("nanoErgs", 0) / 1_000_000_000
        
        result = f"Balance for {address}:\n"
        result += f"• {erg_amount:.9f} ERG\n"
        
        # Format token balances
        tokens = balance.get("tokens", [])
        if tokens:
            result += "\nTokens:\n"
            for token in tokens:
                token_amount = token.get("amount", 0)
                token_name = token.get("name", "Unknown Token")
                token_id = token.get("tokenId", "")
                token_decimals = token.get("decimals", 0)
                
                # Format decimal amount correctly
                if token_decimals > 0:
                    token_formatted_amount = token_amount / (10 ** token_decimals)
                    result += f"• {token_formatted_amount} {token_name} (ID: {token_id[:8]}...)\n"
                else:
                    result += f"• {token_amount} {token_name} (ID: {token_id[:8]}...)\n"
        else:
            result += "\nNo tokens found."
            
        return result
    except Exception as e:
        return f"Error fetching balance: {str(e)}"


async def get_transaction_history(address: str, limit: int = 20) -> str:
    """Get the transaction history for an Ergo address.
    
    Args:
        address: Ergo blockchain address
        limit: Maximum number of transactions to retrieve (default: 20)
    """
    try:
        tx_data = await fetch_address_transactions(address, limit=limit)
        
        # Extract basic statistics
        total = tx_data.get("total", 0)
        items = tx_data.get("items", [])
        
        if not items:
            return f"No transactions found for address {address}."
        
        result = f"Transaction History for {address}\n"
        result += f"Found {total} total transactions (showing {len(items)})\n\n"
        
        # Process each transaction
        for i, tx in enumerate(items, 1):
            tx_id = tx.get("id", "Unknown")
            timestamp = tx.get("timestamp", 0)
            date_time = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Calculate value change for this address
            value_in = 0
            value_out = 0
            
            # Process inputs
            for inp in tx.get("inputs", []):
                if inp.get("address") == address:
                    value_in += inp.get("value", 0)
            
            # Process outputs
            for out in tx.get("outputs", []):
                if out.get("address") == address:
                    value_out += out.get("value", 0)
            
            # Calculate net change
            net_change = value_out - value_in
            net_change_erg = net_change / 1_000_000_000
            
            # Format sign for readability
            if net_change > 0:
                change_str = f"+{net_change_erg:.9f} ERG"
            else:
                change_str = f"{net_change_erg:.9f} ERG"
            
            result += f"{i}. [{date_time}] {change_str}\n"
            result += f"   TX: {tx_id}\n"
            
            # Check if there were any token transfers
            in_tokens = set()
            out_tokens = set()
            
            # Process input tokens
            for inp in tx.get("inputs", []):
                if inp.get("address") == address:
                    for token in inp.get("assets", []):
                        in_tokens.add(token.get("tokenId", ""))
            
            # Process output tokens
            for out in tx.get("outputs", []):
                if out.get("address") == address:
                    for token in out.get("assets", []):
                        out_tokens.add(token.get("tokenId", ""))
            
            # Report token transfers
            if in_tokens or out_tokens:
                result += f"   Tokens: {'✓' if in_tokens or out_tokens else '✗'}\n"
            
            result += "\n"
        
        return result
    except Exception as e:
        return f"Error fetching transaction history: {str(e)}"


async def analyze_address(address: str, depth: int = 2, tx_limit: int = 5) -> str:
    """Perform forensic analysis on an Ergo address, following transaction flows up to a specified depth.
    
    Args:
        address: Ergo blockchain address to analyze
        depth: How many layers of transactions to analyze (1-4, default: 2)
        tx_limit: Maximum transactions per address to analyze (default: 5)
    """
    from ergo_explorer.api import fetch_transaction
    from datetime import datetime
    
    # Limit max depth to 4 for performance
    depth = min(depth, 4)
    
    try:
        # Results dictionary
        results = {
            "starting_address": address,
            "depth": depth,
            "related_addresses": set(),
            "transactions_analyzed": set(),
            "path_traces": []
        }
        
        async def analyze_level(addr, current_depth, parent_tx=None):
            """Recursive function to analyze an address at a specific depth level."""
            if current_depth > depth:
                return
                
            # Get transactions for this address
            tx_data = await fetch_address_transactions(addr, limit=tx_limit)
            tx_items = tx_data.get("items", [])
            
            for tx in tx_items:
                tx_id = tx.get("id")
                
                # Skip if already analyzed
                if tx_id in results["transactions_analyzed"]:
                    continue
                    
                results["transactions_analyzed"].add(tx_id)
                
                # Get full transaction details
                tx_details = await fetch_transaction(tx_id)
                
                # Record transaction path
                path = {
                    "tx_id": tx_id,
                    "depth": current_depth,
                    "parent_tx": parent_tx,
                    "timestamp": datetime.fromtimestamp(tx.get("timestamp", 0)/1000).strftime('%Y-%m-%d %H:%M:%S'),
                    "value": tx.get("value", 0) / 1_000_000_000,
                    "related_addresses": []
                }
                
                # Analyze inputs and outputs to find related addresses
                for inp in tx_details.get("inputs", []):
                    input_addr = inp.get("address")
                    if input_addr and input_addr != addr:
                        results["related_addresses"].add(input_addr)
                        path["related_addresses"].append({"address": input_addr, "type": "input"})
                
                for out in tx_details.get("outputs", []):
                    output_addr = out.get("address")
                    if output_addr and output_addr != addr:
                        results["related_addresses"].add(output_addr)
                        path["related_addresses"].append({"address": output_addr, "type": "output"})
                
                results["path_traces"].append(path)
                
                # Recursively analyze related addresses at next depth
                if current_depth < depth:
                    for rel_addr in path["related_addresses"]:
                        await analyze_level(rel_addr["address"], current_depth + 1, tx_id)
        
        # Start analysis from the root address
        await analyze_level(address, 1)
        
        # Format results into a readable report
        report = f"Forensic Analysis for {address}\n\n"
        report += f"Depth: {depth}\n"
        report += f"Transactions analyzed: {len(results['transactions_analyzed'])}\n"
        report += f"Related addresses found: {len(results['related_addresses'])}\n\n"
        
        # Transaction Paths
        if results["path_traces"]:
            report += "Transaction Paths:\n"
            
            # Group by depth for readability
            for level in range(1, depth + 1):
                level_paths = [p for p in results["path_traces"] if p["depth"] == level]
                
                if level_paths:
                    report += f"\nDepth {level}:\n"
                    
                    for path in level_paths:
                        report += f"• TX: {path['tx_id']}\n"
                        report += f"  Date: {path['timestamp']}\n"
                        report += f"  Value: {path['value']:.9f} ERG\n"
                        
                        if path["parent_tx"]:
                            report += f"  Parent TX: {path['parent_tx']}\n"
                            
                        if path["related_addresses"]:
                            report += f"  Related Addresses: {len(path['related_addresses'])}\n"
                        
                        report += "\n"
        
        return report
    except Exception as e:
        return f"Error during address analysis: {str(e)}" 