# ergo_mcp_server.py
import asyncio
import httpx
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context, Image
from dataclasses import dataclass

# Create MCP server
mcp = FastMCP("Ergo Explorer", dependencies=["httpx"], port=3001)

# Constants
ERGO_EXPLORER_API = "https://api.ergoplatform.com/api/v1"
USER_AGENT = "ErgoMCPServer/1.0"

# Helper API functions
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

# MCP Tools

@mcp.tool()
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

@mcp.tool()
async def analyze_transaction(tx_id: str) -> str:
    """Analyze a transaction on the Ergo blockchain.
    
    Args:
        tx_id: Transaction ID (hash)
    """
    try:
        tx = await fetch_transaction(tx_id)
        
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
        return f"Error analyzing transaction: {str(e)}"

@mcp.tool()
async def get_transaction_history(address: str, limit: int = 20) -> str:
    """Get the transaction history for an Ergo address.
    
    Args:
        address: Ergo blockchain address
        limit: Maximum number of transactions to retrieve (default: 20)
    """
    try:
        tx_data = await fetch_address_transactions(address, limit=limit)
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
            
            # Calculate transaction value for this address
            address_inputs = [inp for inp in tx.get("inputs", []) if inp.get("address") == address]
            address_outputs = [out for out in tx.get("outputs", []) if out.get("address") == address]
            
            input_value = sum(inp.get("value", 0) for inp in address_inputs)
            output_value = sum(out.get("value", 0) for out in address_outputs)
            
            net_value = output_value - input_value
            net_erg = net_value / 1_000_000_000
            
            # Determine if this is incoming or outgoing
            tx_type = "RECEIVE" if net_value > 0 else "SEND" if net_value < 0 else "SELF"
            
            result += f"{i}. {tx_type}: {abs(net_erg):.9f} ERG\n"
            result += f"   TX: {tx_id}\n"
            result += f"   Height: {height}\n"
            result += f"   Timestamp: {timestamp}\n"
            
            # Show token transfers if any
            address_token_inputs = {}
            for inp in address_inputs:
                for asset in inp.get("assets", []):
                    token_id = asset.get("tokenId")
                    token_amount = asset.get("amount", 0)
                    if token_id in address_token_inputs:
                        address_token_inputs[token_id] += token_amount
                    else:
                        address_token_inputs[token_id] = token_amount
            
            address_token_outputs = {}
            for out in address_outputs:
                for asset in out.get("assets", []):
                    token_id = asset.get("tokenId")
                    token_amount = asset.get("amount", 0)
                    token_name = asset.get("name", "Unknown")
                    if token_id in address_token_outputs:
                        address_token_outputs[token_id]["amount"] += token_amount
                    else:
                        address_token_outputs[token_id] = {
                            "amount": token_amount,
                            "name": token_name
                        }
            
            # Calculate token net changes
            token_transfers = []
            all_token_ids = set(list(address_token_inputs.keys()) + list(address_token_outputs.keys()))
            
            for token_id in all_token_ids:
                input_amount = address_token_inputs.get(token_id, 0)
                output_info = address_token_outputs.get(token_id, {"amount": 0, "name": "Unknown"})
                output_amount = output_info["amount"]
                token_name = output_info["name"]
                
                net_token = output_amount - input_amount
                if net_token != 0:
                    token_transfers.append((token_name, token_id, net_token))
            
            if token_transfers:
                result += "   Tokens:\n"
                for name, id, amount in token_transfers:
                    direction = "+" if amount > 0 else "-"
                    result += f"   {direction} {abs(amount)} {name} (ID: {id[:8]}...)\n"
            
            result += "\n"
        
        return result
    except Exception as e:
        return f"Error fetching transaction history: {str(e)}"

@mcp.tool()
async def analyze_address(address: str, depth: int = 2, tx_limit: int = 5) -> str:
    """Perform forensic analysis on an Ergo address, following transaction flows up to a specified depth.
    
    Args:
        address: Ergo blockchain address to analyze
        depth: How many layers of transactions to analyze (1-4, default: 2)
        tx_limit: Maximum transactions per address to analyze (default: 5)
    """
    if depth < 1 or depth > 4:
        return "Depth must be between 1 and 4 inclusive"
    
    if tx_limit < 1 or tx_limit > 20:
        return "Transaction limit must be between 1 and 20 inclusive"
    
    try:
        # Get initial balance and transactions
        balance = await fetch_balance(address)
        erg_amount = balance.get("nanoErgs", 0) / 1_000_000_000
        
        result = f"Forensic Analysis: {address}\n"
        result += f"Current Balance: {erg_amount:.9f} ERG\n"
        
        # Track visited addresses to avoid loops
        visited_addresses = set([address])
        # Track all found addresses with their "distance" from the target
        all_related_addresses = {address: {"distance": 0, "txs": []}}
        
        # Recursive function to analyze address and its connections
        async def analyze_level(addr, current_depth, parent_tx=None):
            if current_depth > depth:
                return
            
            # Skip if we've already visited this address
            if addr in visited_addresses and current_depth > 0:
                return
            
            visited_addresses.add(addr)
            
            # Get transactions for this address
            tx_data = await fetch_address_transactions(addr, limit=tx_limit)
            transactions = tx_data.get("items", [])
            
            # Skip if no transactions found
            if not transactions:
                return
            
            # Track this address's transactions
            if addr not in all_related_addresses:
                all_related_addresses[addr] = {"distance": current_depth, "txs": []}
            
            # Analyze each transaction
            for tx in transactions:
                tx_id = tx.get("id")
                
                # Skip if we've already analyzed this transaction for this address
                if tx_id in all_related_addresses[addr]["txs"]:
                    continue
                
                all_related_addresses[addr]["txs"].append(tx_id)
                
                # Get all input and output addresses
                input_addresses = set()
                output_addresses = set()
                
                for inp in tx.get("inputs", []):
                    input_addr = inp.get("address")
                    if input_addr and input_addr != addr:
                        input_addresses.add(input_addr)
                
                for out in tx.get("outputs", []):
                    output_addr = out.get("address")
                    if output_addr and output_addr != addr:
                        output_addresses.add(output_addr)
                
                # Continue analysis for connected addresses
                for next_addr in input_addresses.union(output_addresses):
                    if next_addr not in visited_addresses:
                        await analyze_level(next_addr, current_depth + 1, tx_id)
        
        # Start the recursive analysis
        await analyze_level(address, 1)
        
        # Generate the report
        result += f"\nAnalysis Depth: {depth}, Transactions per Address: {tx_limit}\n"
        result += f"Found {len(all_related_addresses) - 1} related addresses\n\n"
        
        # Sort addresses by distance
        for distance in range(1, depth + 1):
            addresses_at_distance = {addr: info for addr, info in all_related_addresses.items() 
                                    if info["distance"] == distance}
            
            if not addresses_at_distance:
                continue
            
            result += f"=== Level {distance} ({len(addresses_at_distance)} addresses) ===\n"
            
            # Limit displayed addresses for readability
            display_limit = 5
            displayed = 0
            
            for addr, info in addresses_at_distance.items():
                if displayed >= display_limit:
                    result += f"... and {len(addresses_at_distance) - display_limit} more addresses\n"
                    break
                
                # Get balance for this address
                try:
                    addr_balance = await fetch_balance(addr)
                    addr_erg = addr_balance.get("nanoErgs", 0) / 1_000_000_000
                    
                    result += f"Address: {addr}\n"
                    result += f"Balance: {addr_erg:.9f} ERG\n"
                    result += f"Transactions: {len(info['txs'])}\n"
                    
                    # Add some token information if present
                    tokens = addr_balance.get("tokens", [])
                    if tokens:
                        token_count = len(tokens)
                        result += f"Holds {token_count} tokens\n"
                    
                    result += "\n"
                    displayed += 1
                except Exception:
                    # Skip addresses with errors
                    continue
        
        # Add transaction flow summary
        tx_count = sum(len(info["txs"]) for info in all_related_addresses.values())
        result += f"\nTransaction Flow Summary:\n"
        result += f"Total Transactions Analyzed: {tx_count}\n"
        
        # Check if there are any patterns or clusters
        # This is simplified and would need more sophisticated analysis in a real application
        large_clusters = [addr for addr, info in all_related_addresses.items() 
                         if len(info["txs"]) > 3 and addr != address]
        
        if large_clusters:
            result += f"\nPotential Hubs (addresses with high transaction counts):\n"
            for hub_addr in large_clusters[:3]:  # Show top 3
                hub_info = all_related_addresses[hub_addr]
                result += f"• {hub_addr} - {len(hub_info['txs'])} transactions, Level {hub_info['distance']}\n"
        
        return result
    except Exception as e:
        return f"Error during address analysis: {str(e)}"

@mcp.tool()
async def search_for_token(query: str) -> str:
    """Search for tokens on the Ergo blockchain by name or ID.
    
    Args:
        query: Token name or ID (minimum 3 characters)
    """
    if len(query) < 3:
        return "Search query must be at least 3 characters long"
    
    try:
        results = await search_tokens(query)
        items = results.get("items", [])
        total = results.get("total", 0)
        
        if not items:
            return f"No tokens found matching '{query}'"
        
        result = f"Found {total} tokens matching '{query}'. Showing top {len(items)}:\n\n"
        
        for token in items:
            token_id = token.get("id", "Unknown")
            token_name = token.get("name", "Unnamed Token")
            emission_amount = token.get("emissionAmount", 0)
            decimals = token.get("decimals", 0)
            
            # Format amounts according to decimals
            if decimals > 0:
                formatted_emission = emission_amount / (10 ** decimals)
                result += f"Token: {token_name}\n"
                result += f"ID: {token_id}\n"
                result += f"Supply: {formatted_emission} ({emission_amount} raw)\n"
                result += f"Decimals: {decimals}\n"
            else:
                result += f"Token: {token_name}\n"
                result += f"ID: {token_id}\n"
                result += f"Supply: {emission_amount}\n"
                result += f"Decimals: {decimals}\n"
            
            # Add token type if available
            token_type = token.get("type")
            if token_type:
                result += f"Type: {token_type}\n"
            
            result += "\n"
        
        return result
    except Exception as e:
        return f"Error searching for tokens: {str(e)}"

@mcp.tool()
async def get_network_status() -> str:
    """Get the current status of the Ergo blockchain network."""
    try:
        network_state = await fetch_network_state()
        
        result = "Ergo Network Status:\n"
        result += f"Height: {network_state.get('height', 'Unknown')}\n"
        result += f"Last Block ID: {network_state.get('lastBlockId', 'Unknown')[:8]}...\n"
        
        # Extract epoch parameters
        params = network_state.get('params', {})
        if params:
            result += "\nCurrent Epoch Parameters:\n"
            result += f"Storage Fee Factor: {params.get('storageFeeFactor', 'Unknown')}\n"
            result += f"Min Value Per Byte: {params.get('minValuePerByte', 'Unknown')}\n"
            result += f"Max Block Size: {params.get('maxBlockSize', 'Unknown')} bytes\n"
            result += f"Block Version: {params.get('blockVersion', 'Unknown')}\n"
        
        return result
    except Exception as e:
        return f"Error fetching network status: {str(e)}"

@mcp.resource("ergo://address/{address}/balance")
async def get_address_balance_resource(address: str) -> str:
    """Get the current balance of an Ergo address."""
    try:
        balance = await fetch_balance(address)
        erg_amount = balance.get("nanoErgs", 0) / 1_000_000_000
        
        result = f"Balance for {address}: {erg_amount:.9f} ERG\n\n"
        
        tokens = balance.get("tokens", [])
        if tokens:
            result += "Tokens:\n"
            for token in tokens:
                token_amount = token.get("amount", 0)
                token_name = token.get("name", "Unknown Token")
                token_id = token.get("tokenId", "")
                token_decimals = token.get("decimals", 0)
                
                # Format decimal amount
                if token_decimals > 0:
                    formatted_amount = token_amount / (10 ** token_decimals)
                    result += f"• {formatted_amount} {token_name} (ID: {token_id})\n"
                else:
                    result += f"• {token_amount} {token_name} (ID: {token_id})\n"
        
        return result
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.resource("ergo://transaction/{tx_id}")
async def get_transaction_resource(tx_id: str) -> str:
    """Get details of a specific transaction."""
    try:
        tx = await fetch_transaction(tx_id)
        
        result = f"Transaction: {tx_id}\n"
        result += f"Block: {tx.get('blockId', 'Unknown')}\n"
        result += f"Height: {tx.get('inclusionHeight', 'Unknown')}\n"
        result += f"Confirmations: {tx.get('numConfirmations', 0)}\n\n"
        
        result += "Inputs:\n"
        for inp in tx.get("inputs", []):
            result += f"• {inp.get('address', 'Unknown')}: {inp.get('value', 0) / 1_000_000_000} ERG\n"
        
        result += "\nOutputs:\n"
        for out in tx.get("outputs", []):
            result += f"• {out.get('address', 'Unknown')}: {out.get('value', 0) / 1_000_000_000} ERG\n"
        
        return result
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.prompt()
def check_balance_prompt(address: str) -> str:
    """Prompt for checking the balance of an Ergo address."""
    return f"""Please analyze the balance and holdings of Ergo address {address}.
Include the ERG balance and any tokens held by this address. If there are tokens,
provide details about each token including its name, ID, and amount."""

@mcp.prompt()
def analyze_transaction_prompt(tx_id: str) -> str:
    """Prompt for analyzing an Ergo transaction."""
    return f"""Please analyze Ergo blockchain transaction {tx_id} in detail.
I'd like to understand:
1. The basic transaction details (block, height, timestamp, size)
2. The inputs and their addresses
3. The outputs and their addresses
4. The transaction fee
5. Any token transfers that occurred

Please present this information in a structured format and provide any insights
you can derive from this transaction data."""

@mcp.prompt()
def forensic_analysis_prompt(address: str, depth: int = 2, tx_limit: int = 5) -> str:
    """Prompt for performing forensic analysis on an Ergo address."""
    return f"""Please perform a thorough forensic analysis on Ergo address {address}.
Analyze transaction flows up to {depth} levels deep, following at most {tx_limit} transactions per address.

In your analysis:
1. Start with the current balance and recent transactions
2. Identify related addresses at each level
3. Look for patterns in transaction flows
4. Identify any unusual transaction patterns
5. Note any high-value transfers or token movements

Present the results in a clear, structured format that emphasizes the most significant findings."""

# Run the server
if __name__ == "__main__":
    mcp.run()