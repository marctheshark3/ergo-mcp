"""
Transaction-related MCP resources for Ergo blockchain.
"""

from ergo_explorer.api import fetch_transaction

async def get_transaction_resource(tx_id: str) -> dict:
    """Get transaction details.
    
    Args:
        tx_id: Transaction ID (hash)
    """
    try:
        tx = await fetch_transaction(tx_id)
        
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