"""
MCP tools for direct Ergo Node API interaction.
"""
from typing import Dict, List, Optional
from ergo_explorer.api.node import (
    get_address_balance_node,
    get_transaction_node,
    get_transaction_by_address_node,
    get_box_by_id_node,
    get_unspent_boxes_by_address_node,
    get_token_by_id_node,
    search_for_token_node,
    get_network_info_node
)

async def get_address_balance_from_node(address: str) -> str:
    """Get the confirmed balance for an Ergo address.
    
    Args:
        address: Ergo blockchain address
    """
    try:
        result = await get_address_balance_node(address)
        
        confirmed = result.get("confirmed", {})
        unconfirmed = result.get("unconfirmed", {})
        
        # Format ERG amount
        confirmed_erg = confirmed.get("nanoErgs", 0) / 1_000_000_000
        unconfirmed_erg = unconfirmed.get("nanoErgs", 0) / 1_000_000_000
        
        output = f"Balance for {address}:\n"
        output += f"• Confirmed: {confirmed_erg:.9f} ERG\n"
        output += f"• Unconfirmed: {unconfirmed_erg:.9f} ERG\n\n"
        
        # Format token balances
        confirmed_tokens = confirmed.get("tokens", [])
        if confirmed_tokens:
            output += "Confirmed Tokens:\n"
            for token in confirmed_tokens:
                token_amount = token.get("amount", 0)
                token_name = token.get("name", "Unknown Token")
                token_id = token.get("tokenId", "")
                token_decimals = token.get("decimals", 0)
                
                # Format decimal amount correctly
                if token_decimals > 0:
                    token_formatted_amount = token_amount / (10 ** token_decimals)
                    output += f"• {token_formatted_amount} {token_name} (ID: {token_id[:8]}...)\n"
                else:
                    output += f"• {token_amount} {token_name} (ID: {token_id[:8]}...)\n"
        else:
            output += "No confirmed tokens found.\n"
            
        unconfirmed_tokens = unconfirmed.get("tokens", [])
        if unconfirmed_tokens:
            output += "\nUnconfirmed Tokens:\n"
            for token in unconfirmed_tokens:
                token_amount = token.get("amount", 0)
                token_name = token.get("name", "Unknown Token")
                token_id = token.get("tokenId", "")
                token_decimals = token.get("decimals", 0)
                
                # Format decimal amount correctly
                if token_decimals > 0:
                    token_formatted_amount = token_amount / (10 ** token_decimals)
                    output += f"• {token_formatted_amount} {token_name} (ID: {token_id[:8]}...)\n"
                else:
                    output += f"• {token_amount} {token_name} (ID: {token_id[:8]}...)\n"
            
        return output
    except Exception as e:
        return f"Error fetching balance from node: {str(e)}"

async def analyze_transaction_from_node(tx_id: str) -> str:
    """Analyze a transaction on the Ergo blockchain using direct node connection.
    
    Args:
        tx_id: Transaction ID (hash)
    """
    try:
        tx = await get_transaction_node(tx_id)
        
        # Basic transaction info
        result = f"Transaction: {tx_id}\n"
        result += f"Block: {tx.get('blockId', 'Unknown')[:8]}...\n"
        result += f"Height: {tx.get('inclusionHeight', 'Unknown')}\n"
        result += f"Timestamp: {tx.get('timestamp', 0)}\n"
        result += f"Confirmations: {tx.get('numConfirmations', 0)}\n"
        result += f"Size: {tx.get('size', 0)} bytes\n\n"
        
        # Analyze inputs
        inputs = tx.get("inputs", [])
        total_input_value = sum(input.get("value", 0) for input in inputs)
        input_erg = total_input_value / 1_000_000_000
        
        result += f"Inputs: {len(inputs)}\n"
        result += f"Total Input Value: {input_erg:.9f} ERG\n"
        
        # Input addresses
        input_addresses = set()
        for input in inputs:
            addr = input.get("address")
            if addr:
                input_addresses.add(addr)
        
        if input_addresses:
            result += f"Input Addresses: {', '.join(list(input_addresses)[:3])}"
            if len(input_addresses) > 3:
                result += f" and {len(input_addresses) - 3} more"
            result += "\n\n"
        
        # Analyze outputs
        outputs = tx.get("outputs", [])
        total_output_value = sum(output.get("value", 0) for output in outputs)
        output_erg = total_output_value / 1_000_000_000
        
        result += f"Outputs: {len(outputs)}\n"
        result += f"Total Output Value: {output_erg:.9f} ERG\n"
        
        # Output addresses
        output_addresses = set()
        for output in outputs:
            addr = output.get("address")
            if addr:
                output_addresses.add(addr)
        
        if output_addresses:
            result += f"Output Addresses: {', '.join(list(output_addresses)[:3])}"
            if len(output_addresses) > 3:
                result += f" and {len(output_addresses) - 3} more"
            result += "\n\n"
        
        # Fee calculation
        fee = total_input_value - total_output_value
        fee_erg = fee / 1_000_000_000
        result += f"Fee: {fee_erg:.9f} ERG\n"
        
        # Token transfers
        input_tokens = {}
        for input in inputs:
            for asset in input.get("assets", []):
                token_id = asset.get("tokenId")
                token_amount = asset.get("amount", 0)
                token_name = asset.get("name", "Unknown")
                
                if token_id in input_tokens:
                    input_tokens[token_id]["amount"] += token_amount
                else:
                    input_tokens[token_id] = {
                        "amount": token_amount,
                        "name": token_name,
                        "decimals": asset.get("decimals", 0)
                    }
        
        output_tokens = {}
        for output in outputs:
            for asset in output.get("assets", []):
                token_id = asset.get("tokenId")
                token_amount = asset.get("amount", 0)
                token_name = asset.get("name", "Unknown")
                
                if token_id in output_tokens:
                    output_tokens[token_id]["amount"] += token_amount
                else:
                    output_tokens[token_id] = {
                        "amount": token_amount,
                        "name": token_name,
                        "decimals": asset.get("decimals", 0)
                    }
        
        if input_tokens or output_tokens:
            result += "\nToken Transfers:\n"
            
            all_token_ids = set(list(input_tokens.keys()) + list(output_tokens.keys()))
            for token_id in all_token_ids:
                input_amount = input_tokens.get(token_id, {}).get("amount", 0)
                output_amount = output_tokens.get(token_id, {}).get("amount", 0)
                token_name = input_tokens.get(token_id, output_tokens.get(token_id))["name"]
                decimals = input_tokens.get(token_id, output_tokens.get(token_id)).get("decimals", 0)
                
                # Format the amounts according to decimals
                if decimals > 0:
                    input_formatted = input_amount / (10 ** decimals)
                    output_formatted = output_amount / (10 ** decimals)
                    difference = output_formatted - input_formatted
                else:
                    input_formatted = input_amount
                    output_formatted = output_amount
                    difference = output_formatted - input_formatted
                
                result += f"• {token_name} (ID: {token_id[:8]}...): "
                if difference > 0:
                    result += f"Minted {difference}\n"
                elif difference < 0:
                    result += f"Burned {abs(difference)}\n"
                else:
                    result += f"Transferred {input_formatted}\n"
        
        return result
    except Exception as e:
        return f"Error analyzing transaction from node: {str(e)}"

async def get_transaction_history_from_node(address: str, limit: int = 20) -> str:
    """Get the transaction history for an Ergo address using direct node connection.
    
    Args:
        address: Ergo blockchain address
        limit: Maximum number of transactions to retrieve (default: 20)
    """
    try:
        tx_data = await get_transaction_by_address_node(address, limit=limit)
        transactions = tx_data.get("items", [])
        total = tx_data.get("total", 0)
        
        if not transactions:
            return f"No transactions found for address {address}"
        
        result = f"Transaction History for {address}\n"
        result += f"Found {total} transactions. Showing latest {len(transactions)}:\n\n"
        
        for i, tx in enumerate(transactions, 1):
            tx_id = tx.get("id", "Unknown")
            height = tx.get("inclusionHeight", "Unknown")
            timestamp = tx.get("timestamp", 0)
            
            # Calculate value for this address
            value_change = 0
            for output in tx.get("outputs", []):
                if output.get("address") == address:
                    value_change += output.get("value", 0)
            
            for input in tx.get("inputs", []):
                if input.get("address") == address:
                    value_change -= input.get("value", 0)
            
            # Convert to ERG
            value_change_erg = value_change / 1_000_000_000
            
            # Format transaction info
            result += f"{i}. Transaction ID: {tx_id}\n"
            result += f"   Block Height: {height}\n"
            result += f"   Timestamp: {timestamp}\n"
            
            if value_change > 0:
                result += f"   Received: +{value_change_erg:.9f} ERG\n"
            else:
                result += f"   Sent: {value_change_erg:.9f} ERG\n"
            
            # Add token transfers if any
            token_changes = {}
            
            for output in tx.get("outputs", []):
                if output.get("address") == address:
                    for asset in output.get("assets", []):
                        token_id = asset.get("tokenId", "")
                        amount = asset.get("amount", 0)
                        if token_id in token_changes:
                            token_changes[token_id]["amount"] += amount
                        else:
                            token_changes[token_id] = {
                                "amount": amount,
                                "name": asset.get("name", "Unknown Token"),
                                "decimals": asset.get("decimals", 0)
                            }
            
            for input in tx.get("inputs", []):
                if input.get("address") == address:
                    for asset in input.get("assets", []):
                        token_id = asset.get("tokenId", "")
                        amount = asset.get("amount", 0)
                        if token_id in token_changes:
                            token_changes[token_id]["amount"] -= amount
                        else:
                            token_changes[token_id] = {
                                "amount": -amount,
                                "name": asset.get("name", "Unknown Token"),
                                "decimals": asset.get("decimals", 0)
                            }
            
            if token_changes:
                result += "   Token Transfers:\n"
                for token_id, info in token_changes.items():
                    amount = info["amount"]
                    name = info["name"]
                    decimals = info["decimals"]
                    
                    # Format amount according to decimals
                    if decimals > 0:
                        formatted_amount = amount / (10 ** decimals)
                    else:
                        formatted_amount = amount
                    
                    if amount > 0:
                        result += f"     Received: +{formatted_amount} {name}\n"
                    else:
                        result += f"     Sent: {formatted_amount} {name}\n"
            
            result += "\n"
        
        return result
    except Exception as e:
        return f"Error fetching transaction history from node: {str(e)}"

async def get_network_status_from_node() -> str:
    """Get the current status of the Ergo blockchain network from direct node connection."""
    try:
        info = await get_network_info_node()
        
        result = "Ergo Network Status:\n"
        result += f"Node Version: {info.get('appVersion', 'Unknown')}\n"
        result += f"Network Type: {info.get('networkType', 'Unknown')}\n"
        result += f"Current Height: {info.get('fullHeight', 'Unknown')}\n"
        result += f"Headers Height: {info.get('headersHeight', 'Unknown')}\n"
        result += f"Connected Peers: {info.get('peersCount', 'Unknown')}\n"
        result += f"Unconfirmed Transactions: {info.get('unconfirmedCount', 'Unknown')}\n"
        result += f"Difficulty: {info.get('difficulty', 'Unknown')}\n"
        
        # Add mining info if available
        result += f"Mining Enabled: {info.get('isMining', False)}\n"
        
        # Add state info
        state_type = info.get('stateType', 'Unknown')
        result += f"State Type: {state_type}\n"
        
        return result
    except Exception as e:
        return f"Error fetching network status from node: {str(e)}"

async def search_for_token_from_node(query: str) -> str:
    """Search for tokens on the Ergo blockchain using direct node connection.
    
    Args:
        query: Token name or ID (minimum 3 characters)
    """
    try:
        tokens = await search_for_token_node(query)
        
        if not tokens:
            return f"No tokens found matching '{query}'"
        
        result = f"Tokens matching '{query}':\n\n"
        
        for i, token in enumerate(tokens, 1):
            token_id = token.get("id", "Unknown")
            token_name = token.get("name", "Unknown")
            token_description = token.get("description", "No description")
            token_decimals = token.get("decimals", 0)
            token_emission = token.get("emissionAmount", 0)
            
            # Format emission amount
            if token_decimals > 0:
                formatted_emission = token_emission / (10 ** token_decimals)
            else:
                formatted_emission = token_emission
            
            result += f"{i}. {token_name} (ID: {token_id})\n"
            result += f"   Description: {token_description}\n"
            result += f"   Decimals: {token_decimals}\n"
            result += f"   Total Supply: {formatted_emission}\n\n"
        
        return result
    except Exception as e:
        return f"Error searching for tokens from node: {str(e)}" 