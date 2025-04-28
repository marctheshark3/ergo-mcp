"""
Blockchain-related tools for the Ergo Explorer MCP server.

This module provides high-level tools for interacting with the Ergo blockchain:
- Get blockchain height and indexing status
- Search and retrieve transactions
- Search and retrieve boxes
- Get token information
- Get address balances
"""

import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime

from ergo_explorer.api.node import (
    get_indexed_height,
    get_transaction_by_id,
    get_transaction_by_index,
    get_transactions_by_address,
    get_transaction_range,
    get_box_by_id,
    get_box_by_index,
    get_boxes_by_token_id,
    get_unspent_boxes_by_token_id,
    get_boxes_by_address,
    get_unspent_boxes_by_address,
    get_box_range,
    get_boxes_by_ergo_tree,
    get_unspent_boxes_by_ergo_tree,
    get_token_by_id,
    get_tokens,
    get_address_balance,
    get_all_token_holders
)

# Import from network module for blockchain data
from ergo_explorer.api.explorer import fetch_api, fetch_network_state
from ergo_explorer.api.node import fetch_node_api

# Import response standardization utilities
from ergo_explorer.response_standardizer import standardize_response

# Set up logging
logger = logging.getLogger(__name__)

# Original function kept for backward compatibility
async def get_blockchain_height() -> str:
    """
    Get the current blockchain height and indexing status.
    
    Returns:
        A formatted string with blockchain height information
    """
    try:
        height_data = await get_indexed_height()
        
        indexed_height = height_data.get("indexedHeight", 0)
        full_height = height_data.get("fullHeight", 0)
        
        return (
            f"Blockchain Height Information:\n"
            f"• Indexed Height: {indexed_height:,}\n"
            f"• Full Height: {full_height:,}\n"
            f"• Blocks Behind: {full_height - indexed_height:,}"
        )
    except Exception as e:
        logger.error(f"Error getting blockchain height: {str(e)}")
        return f"Error getting blockchain height: {str(e)}"

async def get_blockchain_height_json() -> Dict[str, Any]:
    """
    Get the current blockchain height and indexing status in JSON format.
    
    Returns:
        Dictionary with blockchain height information
    """
    try:
        logger.info("Fetching blockchain height information")
        height_data = await get_indexed_height()
        
        indexed_height = height_data.get("indexedHeight", 0)
        full_height = height_data.get("fullHeight", 0)
        blocks_behind = full_height - indexed_height
        
        return {
            "indexedHeight": indexed_height,
            "fullHeight": full_height,
            "blocksBehind": blocks_behind,
            "lastBlockTimestamp": height_data.get("lastBlockTimestamp", 0),
            "isIndexingSynced": blocks_behind == 0
        }
    except Exception as e:
        logger.error(f"Error getting blockchain height: {str(e)}")
        raise Exception(f"Error retrieving blockchain height information: {str(e)}")

async def format_difficulty(difficulty: int) -> str:
    """
    Format difficulty in a more readable format.
    
    Args:
        difficulty: The raw difficulty value
        
    Returns:
        A human-readable string representation of the difficulty
    """
    if difficulty > 1_000_000_000_000:  # Trillion
        return f"{difficulty / 1_000_000_000_000:.2f}T"
    elif difficulty > 1_000_000_000:  # Billion
        return f"{difficulty / 1_000_000_000:.2f}B"
    elif difficulty > 1_000_000:  # Million
        return f"{difficulty / 1_000_000:.2f}M"
    elif difficulty > 1_000:  # Thousand
        return f"{difficulty / 1_000:.2f}K"
    else:
        return f"{difficulty}"

async def calculate_hashrate(difficulty: int) -> float:
    """
    Calculate estimated hashrate from difficulty.
    
    Args:
        difficulty: The network difficulty
        
    Returns:
        Estimated hashrate in H/s
    """
    # Ergo hashrate estimate: difficulty / 8192 * 2^32 / 120
    # where 120 is the target block time in seconds
    if difficulty:
        return difficulty * (2**32) / (8192 * 120)
    return 0

async def blockchain_status(response_format: str = "markdown", random_string: str = None) -> Union[str, Dict[str, Any]]:
    """
    Get comprehensive blockchain status including height, difficulty metrics,
    network hashrate, and recent adjustments.
    
    Args:
        response_format: The format of the response ("markdown" or "json")
        random_string: Dummy parameter for no-parameter tools
        
    Returns:
        Formatted blockchain status in requested format
    """
    try:
        logger.info("Fetching comprehensive blockchain status")
        
        # Fetch data from multiple sources for complete status
        height_data = await get_indexed_height()
        node_info = await fetch_node_api("info")
        network_state = await fetch_network_state()
        
        # Extract key information
        indexed_height = height_data.get("indexedHeight", 0)
        full_height = height_data.get("fullHeight", 0)
        blocks_behind = full_height - indexed_height
        
        # Network difficulty and hashrate
        difficulty = node_info.get("difficulty", 0)
        readable_difficulty = await format_difficulty(difficulty)
        hashrate = await calculate_hashrate(difficulty)
        hashrate_th = hashrate / 1_000_000_000_000  # Convert to TH/s
        
        # Prepare data in structured format
        status_data = {
            "height": {
                "current": full_height,
                "indexed": indexed_height,
                "blocksBehind": blocks_behind,
                "isIndexingSynced": blocks_behind == 0,
                "lastBlockTimestamp": height_data.get("lastBlockTimestamp", 0)
            },
            "mining": {
                "difficulty": difficulty,
                "readableDifficulty": readable_difficulty,
                "estimatedHashrate": hashrate,
                "estimatedHashrateTh": hashrate_th,
                "blockTimeTarget": 120  # Ergo's target block time in seconds
            },
            "network": {
                "name": node_info.get("network", "mainnet"),
                "version": node_info.get("appVersion", "Unknown"),
                "stateType": node_info.get("stateType", "Unknown"),
                "headersHeight": node_info.get("headersHeight", 0),
                "peersCount": node_info.get("peersCount", 0),
                "unconfirmedCount": node_info.get("unconfirmedCount", 0)
            }
        }
        
        # Check if the request is for JSON format
        if response_format.lower() == "json":
            return status_data
        
        # Otherwise, format as markdown
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        markdown_output = f"""
# Ergo Blockchain Status
*Last updated: {timestamp}*

## Height Information
• **Current Height**: {full_height:,}
• **Indexed Height**: {indexed_height:,}
• **Blocks Behind**: {blocks_behind:,}
• **Status**: {"Fully Synced" if blocks_behind == 0 else f"Indexing ({blocks_behind:,} blocks remaining)"}

## Mining Information
• **Difficulty**: {difficulty:,}
• **Readable Difficulty**: {readable_difficulty}
• **Estimated Hashrate**: {hashrate_th:.2f} TH/s
• **Target Block Time**: 120 seconds

## Network Status
• **Network**: {node_info.get("network", "mainnet")}
• **Version**: {node_info.get("appVersion", "Unknown")}
• **State Type**: {node_info.get("stateType", "Unknown")}
• **Headers Height**: {node_info.get("headersHeight", 0):,}
• **Connected Peers**: {node_info.get("peersCount", 0)}
• **Unconfirmed Transactions**: {node_info.get("unconfirmedCount", 0):,}
"""
        
        # Return the formatted response standardized to the requested format
        return standardize_response(markdown_output, response_format)
    
    except Exception as e:
        logger.error(f"Error fetching blockchain status: {str(e)}")
        error_msg = f"Error retrieving blockchain status: {str(e)}"
        
        if response_format.lower() == "json":
            return {"error": error_msg}
        return error_msg

# Original function kept for backward compatibility
async def get_transaction_info(identifier: Union[str, int], by_index: bool = False) -> str:
    """
    Get detailed information about a transaction.
    
    Args:
        identifier: Transaction ID (hex string) or index number
        by_index: Whether to search by index instead of ID
        
    Returns:
        A formatted string with transaction details
    """
    try:
        if by_index:
            tx_data = await get_transaction_by_index(identifier)
        else:
            tx_data = await get_transaction_by_id(identifier)
        
        # Format transaction data
        tx_id = tx_data.get("id", "Unknown")
        size = tx_data.get("size", 0)
        inputs = tx_data.get("inputs", [])
        outputs = tx_data.get("outputs", [])
        
        result = f"Transaction Details for {tx_id}:\n"
        result += f"• Size: {size:,} bytes\n"
        result += f"• Inputs: {len(inputs)}\n"
        result += f"• Outputs: {len(outputs)}\n\n"
        
        # Add input details
        result += "Inputs:\n"
        for i, input in enumerate(inputs, 1):
            box_id = input.get("boxId", "Unknown")
            value = input.get("value", 0) / 1_000_000_000  # Convert nanoERG to ERG
            result += f"{i}. Box ID: {box_id}\n   Value: {value:.9f} ERG\n"
        
        # Add output details
        result += "\nOutputs:\n"
        for i, output in enumerate(outputs, 1):
            box_id = output.get("boxId", "Unknown")
            value = output.get("value", 0) / 1_000_000_000  # Convert nanoERG to ERG
            address = output.get("address", "Unknown")
            result += f"{i}. Box ID: {box_id}\n   Address: {address}\n   Value: {value:.9f} ERG\n"
            
            # Add token details if any
            assets = output.get("assets", [])
            if assets:
                result += "   Tokens:\n"
                for asset in assets:
                    token_id = asset.get("tokenId", "Unknown")
                    amount = asset.get("amount", 0)
                    result += f"   - {token_id}: {amount:,}\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting transaction info: {str(e)}")
        return f"Error getting transaction info: {str(e)}"

@standardize_response
async def get_transaction_info_json(identifier: Union[str, int], by_index: bool = False) -> Dict[str, Any]:
    """
    Get detailed information about a transaction in standardized JSON format.
    
    Args:
        identifier: Transaction ID (hex string) or index number
        by_index: Whether to search by index instead of ID
        
    Returns:
        Dictionary with transaction details
    """
    try:
        logger.info(f"Fetching transaction info for {identifier} (by_index={by_index})")
        
        if by_index:
            tx_data = await get_transaction_by_index(identifier)
        else:
            tx_data = await get_transaction_by_id(identifier)
        
        # Extract basic transaction information
        tx_id = tx_data.get("id", "Unknown")
        size = tx_data.get("size", 0)
        inputs = tx_data.get("inputs", [])
        outputs = tx_data.get("outputs", [])
        
        # Format inputs with standardized structure
        formatted_inputs = []
        for input_data in inputs:
            box_id = input_data.get("boxId", "Unknown")
            value = input_data.get("value", 0)
            
            # Create structured input data
            formatted_input = {
                "boxId": box_id,
                "value": value,
                "valueErg": value / 1_000_000_000,  # Convert nanoERG to ERG
                "address": input_data.get("address", "Unknown"),
                "assets": input_data.get("assets", [])
            }
            
            formatted_inputs.append(formatted_input)
        
        # Format outputs with standardized structure
        formatted_outputs = []
        for output_data in outputs:
            box_id = output_data.get("boxId", "Unknown")
            value = output_data.get("value", 0)
            
            # Create structured output data
            formatted_output = {
                "boxId": box_id,
                "value": value,
                "valueErg": value / 1_000_000_000,  # Convert nanoERG to ERG
                "address": output_data.get("address", "Unknown"),
                "assets": output_data.get("assets", []),
                "creationHeight": output_data.get("creationHeight", 0),
                "ergoTree": output_data.get("ergoTree", "")
            }
            
            formatted_outputs.append(formatted_output)
        
        # Create standardized transaction data
        return {
            "id": tx_id,
            "size": size,
            "inputs": {
                "count": len(inputs),
                "items": formatted_inputs
            },
            "outputs": {
                "count": len(outputs),
                "items": formatted_outputs
            },
            "timestamp": tx_data.get("timestamp", 0),
            "confirmationsCount": tx_data.get("confirmationsCount", 0),
            "inclusionHeight": tx_data.get("inclusionHeight", 0)
        }
        
    except Exception as e:
        logger.error(f"Error getting transaction info: {str(e)}")
        raise Exception(f"Error retrieving transaction information: {str(e)}")

async def get_address_transaction_history(
    address: str,
    offset: int = 0,
    limit: int = 20
) -> str:
    """
    Get transaction history for an address.
    
    Args:
        address: Ergo blockchain address
        offset: Number of transactions to skip
        limit: Maximum number of transactions to return
        
    Returns:
        A formatted string with transaction history
    """
    try:
        tx_data = await get_transactions_by_address(address, offset, limit)
        transactions = tx_data.get("items", [])
        total = tx_data.get("total", 0)
        
        if not transactions:
            return f"No transactions found for address {address}"
        
        result = f"Transaction History for {address}\n"
        result += f"Found {total:,} transactions. Showing {len(transactions):,}:\n\n"
        
        for i, tx in enumerate(transactions, 1):
            tx_id = tx.get("id", "Unknown")
            timestamp = tx.get("timestamp", 0)
            
            # Calculate value change for this address
            value_change = 0
            for output in tx.get("outputs", []):
                if output.get("address") == address:
                    value_change += output.get("value", 0)
            
            for input in tx.get("inputs", []):
                if input.get("address") == address:
                    value_change -= input.get("value", 0)
            
            # Convert to ERG
            value_change_erg = value_change / 1_000_000_000
            
            result += f"{i}. Transaction: {tx_id}\n"
            result += f"   Timestamp: {datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if value_change > 0:
                result += f"   Received: +{value_change_erg:.9f} ERG\n"
            else:
                result += f"   Sent: {value_change_erg:.9f} ERG\n"
            
            # Add token transfers
            token_changes = {}
            for output in tx.get("outputs", []):
                if output.get("address") == address:
                    for asset in output.get("assets", []):
                        token_id = asset.get("tokenId")
                        amount = asset.get("amount", 0)
                        token_changes[token_id] = token_changes.get(token_id, 0) + amount
            
            for input in tx.get("inputs", []):
                if input.get("address") == address:
                    for asset in input.get("assets", []):
                        token_id = asset.get("tokenId")
                        amount = asset.get("amount", 0)
                        token_changes[token_id] = token_changes.get(token_id, 0) - amount
            
            if token_changes:
                result += "   Token Changes:\n"
                for token_id, change in token_changes.items():
                    if change > 0:
                        result += f"   + {change:,} of {token_id}\n"
                    else:
                        result += f"   - {abs(change):,} of {token_id}\n"
            
            result += "\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting transaction history: {str(e)}")
        return f"Error getting transaction history: {str(e)}"

# Original function kept for backward compatibility
async def get_box_info(identifier: Union[str, int], by_index: bool = False) -> str:
    """
    Get detailed information about a box.
    
    Args:
        identifier: Box ID (hex string) or index number
        by_index: Whether to search by index instead of ID
        
    Returns:
        A formatted string with box details
    """
    try:
        if by_index:
            box_data = await get_box_by_index(identifier)
        else:
            box_data = await get_box_by_id(identifier)
        
        box_id = box_data.get("boxId", "Unknown")
        value = box_data.get("value", 0) / 1_000_000_000  # Convert nanoERG to ERG
        creation_height = box_data.get("creationHeight", 0)
        ergo_tree = box_data.get("ergoTree", "Unknown")
        assets = box_data.get("assets", [])
        
        result = f"Box Details for {box_id}:\n"
        result += f"• Value: {value:.9f} ERG\n"
        result += f"• Creation Height: {creation_height:,}\n"
        result += f"• ErgoTree: {ergo_tree}\n"
        
        if assets:
            result += "\nTokens:\n"
            for asset in assets:
                token_id = asset.get("tokenId", "Unknown")
                amount = asset.get("amount", 0)
                result += f"• {token_id}: {amount:,}\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting box info: {str(e)}")
        return f"Error getting box info: {str(e)}"

@standardize_response
async def get_box_info_json(identifier: Union[str, int], by_index: bool = False) -> Dict[str, Any]:
    """
    Get detailed information about a box in standardized JSON format.
    
    Args:
        identifier: Box ID (hex string) or index number
        by_index: Whether to search by index instead of ID
        
    Returns:
        Dictionary with box details
    """
    try:
        logger.info(f"Fetching box info for {identifier} (by_index={by_index})")
        
        if by_index:
            box_data = await get_box_by_index(identifier)
        else:
            box_data = await get_box_by_id(identifier)
        
        # Extract basic box information
        box_id = box_data.get("id", "Unknown")
        value = box_data.get("value", 0)
        
        # Format assets (tokens) in the box
        assets = box_data.get("assets", [])
        formatted_assets = []
        
        for asset in assets:
            token_id = asset.get("tokenId", "Unknown")
            amount = asset.get("amount", 0)
            
            formatted_assets.append({
                "tokenId": token_id,
                "amount": amount
            })
        
        # Create standardized box data
        return {
            "id": box_id,
            "value": value,
            "valueErg": value / 1_000_000_000,  # Convert nanoERG to ERG
            "creationHeight": box_data.get("creationHeight", 0),
            "settlementHeight": box_data.get("settlementHeight", 0),
            "ergoTree": box_data.get("ergoTree", ""),
            "address": box_data.get("address", ""),
            "assets": {
                "count": len(formatted_assets),
                "items": formatted_assets
            },
            "additionalRegisters": box_data.get("additionalRegisters", {}),
            "confirmed": box_data.get("confirmed", False),
            "mainChain": box_data.get("mainChain", False)
        }
        
    except Exception as e:
        logger.error(f"Error getting box info: {str(e)}")
        raise Exception(f"Error retrieving box information: {str(e)}")

# Original function kept for backward compatibility
async def get_token_info(token_id: str) -> str:
    """
    Get detailed information about a token.
    
    Args:
        token_id: Token ID (hex string)
        
    Returns:
        A formatted string with token details
    """
    try:
        token_data = await get_token_by_id(token_id)
        
        token_id = token_data.get("id", "Unknown")
        box_id = token_data.get("boxId", "Unknown")
        name = token_data.get("name", "Unknown")
        description = token_data.get("description", "")
        decimals = token_data.get("decimals", 0)
        token_type = token_data.get("type", "Unknown")
        
        result = f"Token Details for {token_id}:\n"
        result += f"• Name: {name}\n"
        result += f"• Description: {description}\n"
        result += f"• Decimals: {decimals}\n"
        result += f"• Type: {token_type}\n"
        result += f"• Minting Box: {box_id}\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting token info: {str(e)}")
        return f"Error getting token info: {str(e)}"

@standardize_response
async def get_token_info_json(token_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a token in standardized JSON format.
    
    Args:
        token_id: Token ID to retrieve
        
    Returns:
        Dictionary with token details
    """
    try:
        logger.info(f"Fetching token info for {token_id}")
        token_data = await get_token_by_id(token_id)
        
        # Create standardized token data
        return {
            "id": token_data.get("id", "Unknown"),
            "boxId": token_data.get("boxId", ""),
            "name": token_data.get("name", "Unknown Token"),
            "description": token_data.get("description", ""),
            "decimals": token_data.get("decimals", 0),
            "emissionAmount": token_data.get("emissionAmount", 0),
            "type": token_data.get("type", ""),
            "mintingBoxId": token_data.get("mintingBoxId", ""),
            "transactionId": token_data.get("transactionId", ""),
            "mintingHeight": token_data.get("mintingHeight", 0),
            "mintingTimestamp": token_data.get("mintingTimestamp", 0)
        }
        
    except Exception as e:
        logger.error(f"Error getting token info: {str(e)}")
        raise Exception(f"Error retrieving token information: {str(e)}")

async def get_address_full_balance(address: str) -> str:
    """
    Get detailed balance information for an address.
    
    Args:
        address: Ergo blockchain address
        
    Returns:
        A formatted string with balance details
    """
    try:
        balance_data = await get_address_balance(address)
        
        confirmed = balance_data.get("confirmed", {})
        unconfirmed = balance_data.get("unconfirmed", {})
        
        # Format ERG amounts
        confirmed_erg = confirmed.get("nanoErgs", 0) / 1_000_000_000
        unconfirmed_erg = unconfirmed.get("nanoErgs", 0) / 1_000_000_000
        
        result = f"Balance for {address}:\n\n"
        result += "Confirmed Balance:\n"
        result += f"• {confirmed_erg:.9f} ERG\n"
        
        # Add confirmed tokens
        confirmed_tokens = confirmed.get("tokens", [])
        if confirmed_tokens:
            result += "\nConfirmed Tokens:\n"
            for token in confirmed_tokens:
                token_id = token.get("tokenId", "Unknown")
                amount = token.get("amount", 0)
                decimals = token.get("decimals", 0)
                name = token.get("name", "Unknown Token")
                
                # Format amount based on decimals
                formatted_amount = amount / (10 ** decimals) if decimals > 0 else amount
                
                result += f"• {name}\n"
                result += f"  ID: {token_id}\n"
                result += f"  Amount: {formatted_amount:,.{decimals}f}\n"
        
        # Add unconfirmed balance if any
        if unconfirmed_erg > 0 or unconfirmed.get("tokens"):
            result += "\nUnconfirmed Balance:\n"
            result += f"• {unconfirmed_erg:.9f} ERG\n"
            
            unconfirmed_tokens = unconfirmed.get("tokens", [])
            if unconfirmed_tokens:
                result += "\nUnconfirmed Tokens:\n"
                for token in unconfirmed_tokens:
                    token_id = token.get("tokenId", "Unknown")
                    amount = token.get("amount", 0)
                    decimals = token.get("decimals", 0)
                    name = token.get("name", "Unknown Token")
                    
                    # Format amount based on decimals
                    formatted_amount = amount / (10 ** decimals) if decimals > 0 else amount
                    
                    result += f"• {name}\n"
                    result += f"  ID: {token_id}\n"
                    result += f"  Amount: {formatted_amount:,.{decimals}f}\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting address balance: {str(e)}")
        return f"Error getting address balance: {str(e)}"

async def get_token_holders(token_id: str, format_output: bool = True) -> Union[str, List[Dict]]:
    """
    Get all addresses holding a specific token with detailed analysis.
    
    Args:
        token_id: Token ID to search for
        format_output: Whether to return formatted string (True) or raw data (False)
        
    Returns:
        If format_output is True: A formatted string with holder information
        If format_output is False: List of dictionaries with address and amount
    """
    try:
        # Get all holders
        holders = await get_all_token_holders(token_id)
        
        # If there are no holders, return appropriate message or empty list
        if not holders:
            if format_output:
                return f"No holders found for token {token_id}. This could be because:\n" \
                       f"1. The token doesn't exist\n" \
                       f"2. The local node doesn't have information about this token\n" \
                       f"3. All tokens are in spent boxes (try using full node with transaction index)"
            else:
                return []
        
        # Get token info if available
        try:
            token_info = await get_token_by_id(token_id)
            token_name = token_info.get("name", "Unknown Token")
            decimals = token_info.get("decimals", 0)
        except Exception:
            # If we can't get token info, use defaults
            token_name = "Unknown Token"
            decimals = 0
        
        # Sort holders by amount in descending order
        holders.sort(key=lambda x: x["amount"], reverse=True)
        
        if not format_output:
            return holders
            
        # Calculate total supply in circulation
        total_supply = sum(holder["amount"] for holder in holders)
        
        # Format the output
        result = f"Token Holder Analysis for {token_name} ({token_id})\n"
        result += f"Total Holders: {len(holders):,}\n"
        
        # Format total supply based on decimals
        if decimals > 0:
            formatted_supply = total_supply / (10 ** decimals)
            result += f"Total Supply in Circulation: {formatted_supply:,.{decimals}f}\n\n"
        else:
            result += f"Total Supply in Circulation: {total_supply:,}\n\n"
        
        result += "Top Holders:\n"
        for i, holder in enumerate(holders[:20], 1):  # Show top 20 holders
            address = holder["address"]
            amount = holder["amount"]
            
            # Format amount based on decimals
            if decimals > 0:
                formatted_amount = amount / (10 ** decimals)
                percentage = (amount / total_supply) * 100
                result += f"{i}. {address}\n"
                result += f"   Amount: {formatted_amount:,.{decimals}f} ({percentage:.2f}%)\n"
            else:
                percentage = (amount / total_supply) * 100
                result += f"{i}. {address}\n"
                result += f"   Amount: {amount:,} ({percentage:.2f}%)\n"
        
        if len(holders) > 20:
            remaining_holders = len(holders) - 20
            remaining_amount = sum(h["amount"] for h in holders[20:])
            remaining_percentage = (remaining_amount / total_supply) * 100
            
            result += f"\nRemaining {remaining_holders:,} holders: {remaining_percentage:.2f}% of supply"
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing token holders: {str(e)}")
        return f"Error analyzing token holders: {str(e)}" if format_output else [] 