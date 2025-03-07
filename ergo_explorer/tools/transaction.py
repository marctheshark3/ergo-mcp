"""
MCP tools for working with Ergo blockchain transactions.
"""

from datetime import datetime
from ergo_explorer.api import fetch_transaction


async def analyze_transaction(tx_id: str) -> str:
    """Analyze a transaction on the Ergo blockchain.
    
    Args:
        tx_id: Transaction ID (hash)
    """
    try:
        # Fetch transaction data
        tx = await fetch_transaction(tx_id)
        
        # Parse basic information
        timestamp = tx.get("timestamp", 0)
        date_time = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S UTC')
        block_id = tx.get("blockId", "Unknown")
        height = tx.get("inclusionHeight", 0)
        size = tx.get("size", 0)
        
        # Initialize result string with basic details
        result = "Transaction Analysis\n"
        result += "====================\n\n"
        result += f"Transaction ID: {tx_id}\n"
        result += f"Timestamp: {date_time}\n"
        result += f"Block: {block_id}\n"
        result += f"Block Height: {height}\n"
        result += f"Size: {size} bytes\n"
        
        # Calculate total input/output values
        inputs = tx.get("inputs", [])
        outputs = tx.get("outputs", [])
        
        total_input_value = sum(inp.get("value", 0) for inp in inputs)
        total_output_value = sum(out.get("value", 0) for out in outputs)
        fee = total_input_value - total_output_value
        
        input_erg = total_input_value / 1_000_000_000
        output_erg = total_output_value / 1_000_000_000
        fee_erg = fee / 1_000_000_000
        
        result += f"Total Input: {input_erg:.9f} ERG\n"
        result += f"Total Output: {output_erg:.9f} ERG\n"
        result += f"Fee: {fee_erg:.9f} ERG\n\n"
        
        # Process inputs
        result += f"Inputs ({len(inputs)})\n"
        result += "----------\n"
        
        for i, inp in enumerate(inputs, 1):
            address = inp.get("address", "Unknown")
            value = inp.get("value", 0) / 1_000_000_000
            box_id = inp.get("boxId", "Unknown")
            
            result += f"Input #{i}\n"
            result += f"Address: {address}\n"
            result += f"Value: {value:.9f} ERG\n"
            result += f"Box ID: {box_id}\n"
            
            # Process tokens in input
            assets = inp.get("assets", [])
            if assets:
                result += "Tokens:\n"
                for asset in assets:
                    token_id = asset.get("tokenId", "Unknown")
                    token_name = asset.get("name", "Unknown Token") 
                    amount = asset.get("amount", 0)
                    decimals = asset.get("decimals", 0)
                    
                    # Format amount with decimals
                    if decimals > 0:
                        formatted_amount = amount / (10 ** decimals)
                        result += f"• {formatted_amount} {token_name} (ID: {token_id[:8]}...)\n"
                    else:
                        result += f"• {amount} {token_name} (ID: {token_id[:8]}...)\n"
            
            result += "\n"
        
        # Process outputs
        result += f"Outputs ({len(outputs)})\n"
        result += "-----------\n"
        
        for i, out in enumerate(outputs, 1):
            address = out.get("address", "Unknown")
            value = out.get("value", 0) / 1_000_000_000
            box_id = out.get("boxId", "Unknown")
            
            result += f"Output #{i}\n"
            result += f"Address: {address}\n"
            result += f"Value: {value:.9f} ERG\n"
            result += f"Box ID: {box_id}\n"
            
            # Process tokens in output
            assets = out.get("assets", [])
            if assets:
                result += "Tokens:\n"
                for asset in assets:
                    token_id = asset.get("tokenId", "Unknown")
                    token_name = asset.get("name", "Unknown Token")
                    amount = asset.get("amount", 0)
                    decimals = asset.get("decimals", 0)
                    
                    # Format amount with decimals
                    if decimals > 0:
                        formatted_amount = amount / (10 ** decimals)
                        result += f"• {formatted_amount} {token_name} (ID: {token_id[:8]}...)\n"
                    else:
                        result += f"• {amount} {token_name} (ID: {token_id[:8]}...)\n"
            
            result += "\n"
        
        # Summarize token transfers
        all_input_tokens = {}
        all_output_tokens = {}
        
        # Collect input tokens
        for inp in inputs:
            for asset in inp.get("assets", []):
                token_id = asset.get("tokenId", "")
                amount = asset.get("amount", 0)
                name = asset.get("name", "Unknown Token")
                decimals = asset.get("decimals", 0)
                
                if token_id in all_input_tokens:
                    all_input_tokens[token_id]["amount"] += amount
                else:
                    all_input_tokens[token_id] = {
                        "amount": amount,
                        "name": name,
                        "decimals": decimals
                    }
        
        # Collect output tokens
        for out in outputs:
            for asset in out.get("assets", []):
                token_id = asset.get("tokenId", "")
                amount = asset.get("amount", 0)
                name = asset.get("name", "Unknown Token")
                decimals = asset.get("decimals", 0)
                
                if token_id in all_output_tokens:
                    all_output_tokens[token_id]["amount"] += amount
                else:
                    all_output_tokens[token_id] = {
                        "amount": amount,
                        "name": name,
                        "decimals": decimals
                    }
        
        # Display token summary if tokens were transferred
        if all_input_tokens or all_output_tokens:
            result += "Token Summary\n"
            result += "------------\n"
            
            all_token_ids = set(list(all_input_tokens.keys()) + list(all_output_tokens.keys()))
            
            for token_id in all_token_ids:
                input_amount = all_input_tokens.get(token_id, {"amount": 0, "name": "Unknown", "decimals": 0})
                output_amount = all_output_tokens.get(token_id, {"amount": 0, "name": "Unknown", "decimals": 0})
                
                token_name = input_amount["name"] if token_id in all_input_tokens else output_amount["name"]
                decimals = input_amount["decimals"] if token_id in all_input_tokens else output_amount["decimals"]
                
                in_amount = input_amount["amount"]
                out_amount = output_amount["amount"]
                
                # Apply decimal formatting if needed
                if decimals > 0:
                    in_amount = in_amount / (10 ** decimals)
                    out_amount = out_amount / (10 ** decimals)
                
                diff = out_amount - in_amount
                
                # Format the difference with sign
                if diff > 0:
                    diff_str = f"+{diff}"
                else:
                    diff_str = f"{diff}"
                
                result += f"Token: {token_name} (ID: {token_id[:8]}...)\n"
                result += f"Input: {in_amount}\n"
                result += f"Output: {out_amount}\n"
                result += f"Net: {diff_str}\n\n"
        
        return result
    except Exception as e:
        return f"Error analyzing transaction: {str(e)}" 