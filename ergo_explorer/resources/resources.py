"""
MCP resource handlers for the Ergo blockchain.
"""

from datetime import datetime
from ergo_explorer.api import fetch_balance, fetch_transaction


async def get_address_balance_resource(address: str) -> str:
    """Get the current balance of an Ergo address.
    
    Args:
        address: Ergo blockchain address to check
    """
    try:
        # Fetch the balance data
        balance_data = await fetch_balance(address)
        
        # Format the confirmed balance in ERG
        erg_balance = balance_data.get("nanoErgs", 0) / 1_000_000_000
        
        # Get token balances
        tokens = balance_data.get("tokens", [])
        token_objects = []
        
        for token in tokens:
            token_id = token.get("tokenId", "")
            token_name = token.get("name", "Unknown Token")
            token_amount = token.get("amount", 0)
            token_decimals = token.get("decimals", 0)
            
            # Format token amount with decimals
            formatted_amount = token_amount
            if token_decimals > 0:
                formatted_amount = token_amount / (10 ** token_decimals)
                
            token_objects.append({
                "id": token_id,
                "name": token_name, 
                "amount": formatted_amount,
                "raw_amount": token_amount,
                "decimals": token_decimals
            })
        
        # Construct the JSON response object
        result = {
            "address": address,
            "balance_erg": erg_balance,
            "raw_balance_nano_erg": balance_data.get("nanoErgs", 0),
            "tokens": token_objects
        }
        
        return result
    except Exception as e:
        return {"error": str(e)}


async def get_transaction_resource(tx_id: str) -> str:
    """Get details of a specific transaction.
    
    Args:
        tx_id: Transaction ID (hash)
    """
    try:
        # Fetch transaction data
        tx_data = await fetch_transaction(tx_id)
        
        # Extract basic information
        timestamp = tx_data.get("timestamp", 0)
        date_time = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Process inputs and outputs
        inputs = []
        outputs = []
        
        # Format input data
        for inp in tx_data.get("inputs", []):
            address = inp.get("address", "")
            value = inp.get("value", 0) / 1_000_000_000
            
            # Process tokens in input
            tokens = []
            for asset in inp.get("assets", []):
                token_id = asset.get("tokenId", "")
                token_name = asset.get("name", "Unknown")
                amount = asset.get("amount", 0)
                decimals = asset.get("decimals", 0)
                
                # Format amount with decimals if applicable
                formatted_amount = amount
                if decimals > 0:
                    formatted_amount = amount / (10 ** decimals)
                    
                tokens.append({
                    "id": token_id,
                    "name": token_name,
                    "amount": formatted_amount,
                    "raw_amount": amount,
                    "decimals": decimals
                })
                
            inputs.append({
                "address": address,
                "value": value,
                "raw_value": inp.get("value", 0),
                "tokens": tokens
            })
            
        # Format output data
        for out in tx_data.get("outputs", []):
            address = out.get("address", "")
            value = out.get("value", 0) / 1_000_000_000
            
            # Process tokens in output
            tokens = []
            for asset in out.get("assets", []):
                token_id = asset.get("tokenId", "")
                token_name = asset.get("name", "Unknown")
                amount = asset.get("amount", 0)
                decimals = asset.get("decimals", 0)
                
                # Format amount with decimals if applicable
                formatted_amount = amount
                if decimals > 0:
                    formatted_amount = amount / (10 ** decimals)
                    
                tokens.append({
                    "id": token_id,
                    "name": token_name,
                    "amount": formatted_amount,
                    "raw_amount": amount,
                    "decimals": decimals
                })
                
            outputs.append({
                "address": address,
                "value": value,
                "raw_value": out.get("value", 0),
                "tokens": tokens
            })
        
        # Calculate total input/output values and fee
        total_input_value = sum(inp.get("raw_value", 0) for inp in inputs)
        total_output_value = sum(out.get("raw_value", 0) for out in outputs)
        fee = total_input_value - total_output_value
        
        # Construct the result object
        result = {
            "id": tx_id,
            "timestamp": timestamp,
            "formatted_timestamp": date_time,
            "block_id": tx_data.get("blockId", ""),
            "block_height": tx_data.get("inclusionHeight", 0),
            "confirmations": tx_data.get("numConfirmations", 0),
            "size": tx_data.get("size", 0),
            "fee": fee / 1_000_000_000,
            "fee_nano_erg": fee,
            "inputs": inputs,
            "outputs": outputs,
            "total_input_value": total_input_value / 1_000_000_000,
            "total_output_value": total_output_value / 1_000_000_000
        }
        
        return result
    except Exception as e:
        return {"error": str(e)} 