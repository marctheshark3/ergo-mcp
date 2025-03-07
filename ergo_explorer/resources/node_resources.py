"""
Node-specific MCP resources for Ergo blockchain.
"""

from ergo_explorer.api.node import (
    get_address_balance_node,
    get_transaction_node
)

async def get_address_balance_node_resource(address: str) -> dict:
    """Get the confirmed balance for an Ergo address from local node.
    
    Args:
        address: Ergo blockchain address
    """
    try:
        result = await get_address_balance_node(address)
        
        # Return a formatted version that's easier to use
        confirmed = result.get("confirmed", {})
        unconfirmed = result.get("unconfirmed", {})
        
        # Format ERG amount
        confirmed_erg = confirmed.get("nanoErgs", 0) / 1_000_000_000
        unconfirmed_erg = unconfirmed.get("nanoErgs", 0) / 1_000_000_000
        
        formatted_tokens = []
        for token in confirmed.get("tokens", []):
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
                "nanoErgs": confirmed.get("nanoErgs", 0),
                "ergs": confirmed_erg,
                "tokens": formatted_tokens
            },
            "unconfirmedBalance": {
                "nanoErgs": unconfirmed.get("nanoErgs", 0),
                "ergs": unconfirmed_erg,
                "tokens": [
                    {
                        "tokenId": token.get("tokenId", ""),
                        "name": token.get("name", "Unknown Token"),
                        "amount": token.get("amount", 0),
                        "decimals": token.get("decimals", 0),
                        "formatted": token.get("amount", 0) / (10 ** token.get("decimals", 0)) if token.get("decimals", 0) > 0 else token.get("amount", 0)
                    }
                    for token in unconfirmed.get("tokens", [])
                ]
            }
        }
    except Exception as e:
        return {"error": str(e)}

async def get_transaction_node_resource(tx_id: str) -> dict:
    """Get transaction details from local node.
    
    Args:
        tx_id: Transaction ID (hash)
    """
    try:
        tx = await get_transaction_node(tx_id)
        
        # Create formatted input info
        inputs = []
        for input_box in tx.get("inputs", []):
            inputs.append({
                "boxId": input_box.get("boxId", ""),
                "address": input_box.get("address", ""),
                "value": input_box.get("value", 0),
                "ergs": input_box.get("value", 0) / 1_000_000_000,
                "assets": [
                    {
                        "tokenId": asset.get("tokenId", ""),
                        "name": asset.get("name", "Unknown Token"),
                        "amount": asset.get("amount", 0),
                        "decimals": asset.get("decimals", 0),
                        "formatted": asset.get("amount", 0) / (10 ** asset.get("decimals", 0)) if asset.get("decimals", 0) > 0 else asset.get("amount", 0)
                    }
                    for asset in input_box.get("assets", [])
                ]
            })
            
        # Create formatted output info
        outputs = []
        for output_box in tx.get("outputs", []):
            outputs.append({
                "boxId": output_box.get("boxId", ""),
                "address": output_box.get("address", ""),
                "value": output_box.get("value", 0),
                "ergs": output_box.get("value", 0) / 1_000_000_000,
                "assets": [
                    {
                        "tokenId": asset.get("tokenId", ""),
                        "name": asset.get("name", "Unknown Token"),
                        "amount": asset.get("amount", 0),
                        "decimals": asset.get("decimals", 0),
                        "formatted": asset.get("amount", 0) / (10 ** asset.get("decimals", 0)) if asset.get("decimals", 0) > 0 else asset.get("amount", 0)
                    }
                    for asset in output_box.get("assets", [])
                ]
            })
            
        # Calculate fee
        total_input_value = sum(input_box.get("value", 0) for input_box in tx.get("inputs", []))
        total_output_value = sum(output_box.get("value", 0) for output_box in tx.get("outputs", []))
        fee = total_input_value - total_output_value
            
        return {
            "id": tx_id,
            "blockId": tx.get("blockId", ""),
            "timestamp": tx.get("timestamp", 0),
            "inclusionHeight": tx.get("inclusionHeight", 0),
            "confirmations": tx.get("numConfirmations", 0),
            "size": tx.get("size", 0),
            "inputs": inputs,
            "outputs": outputs,
            "fee": {
                "nanoErgs": fee,
                "ergs": fee / 1_000_000_000
            }
        }
    except Exception as e:
        return {"error": str(e)} 