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
    get_all_token_holders,
    fetch_node_api  # Import fetch_node_api from the same module
)

# Import from network module for blockchain data
from ergo_explorer.api.explorer import fetch_api, fetch_network_state

# Import response standardization utilities
from ergo_explorer.response_standardizer import standardize_response

# Set up logging
logger = logging.getLogger(__name__)

async def get_blockchain_height() -> Dict[str, Any]:
    """
    Get the current blockchain height and indexing status.
    
    Returns:
        Dictionary with blockchain height information including:
        - blockHeight: Current full blockchain height
      
    """
    try:
        logger.info("Fetching blockchain height information")
        height_data = await get_indexed_height()
        
        full_height = height_data.get("fullHeight", 0)
        
        return {
            "blockHeight": full_height,
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

async def blockchain_status() -> Dict[str, Any]:
    """
    Get comprehensive blockchain status including height, difficulty metrics,
    network hashrate, and recent adjustments.
    
    Returns:
        Dictionary containing blockchain status information including:
        - height: Current blockchain height information
        - mining: Mining statistics and difficulty metrics
        - network: Network state and node information
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
        
        # Return data in structured format
        return {
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
    
    except Exception as e:
        logger.error(f"Error fetching blockchain status: {str(e)}")
        raise Exception(f"Error retrieving blockchain status: {str(e)}")

async def get_transaction_info(identifier: Union[str, int], by_index: bool = False) -> Dict[str, Any]:
    """
    Get detailed information about a transaction in standardized JSON format.
    
    Args:
        identifier: Transaction ID (hex string) or index number
        by_index: Whether to search by index instead of ID
        
    Returns:
        Dictionary with transaction details
    """
    try:
        logger.info(f"Starting get_transaction_info for {identifier} (by_index={by_index})")
        
        if by_index:
            logger.info(f"Fetching transaction by index for {identifier}")
            tx_data = await get_transaction_by_index(identifier)
        else:
            logger.info(f"Fetching transaction by ID for {identifier}")
            tx_data = await get_transaction_by_id(identifier)
            
        if not tx_data:
            logger.error(f"No transaction data returned for {identifier}")
            raise Exception("No transaction data returned from node")
            
        logger.debug(f"Raw transaction data received: {tx_data}")
        logger.info(f"Successfully fetched transaction data for {identifier}")

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
        result = {
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
        
        logger.info(f"Successfully formatted transaction info for {identifier}")
        logger.debug(f"Returning formatted result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting transaction info for {identifier}: {str(e)}", exc_info=True)
        raise Exception(f"Error retrieving transaction information: {str(e)}")

async def get_address_transaction_history(
    address: str,
    offset: int = 0,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Get transaction history for an address.
    
    Args:
        address: Ergo blockchain address
        offset: Number of transactions to skip
        limit: Maximum number of transactions to return
        
    Returns:
        Dictionary containing:
        - address: The queried address
        - total_transactions: Total number of transactions found
        - transactions: List of transaction details
        - offset: Current offset
        - limit: Current limit
    """
    try:
        tx_data = await get_transactions_by_address(address, offset, limit)
        transactions = tx_data.get("items", [])
        total = tx_data.get("total", 0)
        
        if not transactions:
            return {
                "address": address,
                "total_transactions": 0,
                "transactions": [],
                "offset": offset,
                "limit": limit
            }
        
        processed_txs = []
        for tx in transactions:
            tx_id = tx.get("id", "Unknown")
            timestamp = tx.get("timestamp", 0)
            
            # Calculate value change for this address
            value_change = 0
            token_changes = {}
            
            # Process inputs
            for input_box in tx.get("inputs", []):
                if input_box.get("address") == address:
                    value_change -= input_box.get("value", 0)
                    
                    # Track tokens being sent
                    for asset in input_box.get("assets", []):
                        token_id = asset.get("tokenId")
                        amount = asset.get("amount", 0)
                        name = asset.get("name", "Unknown Token")
                        
                        if token_id in token_changes:
                            token_changes[token_id]["change"] -= amount
                        else:
                            token_changes[token_id] = {
                                "id": token_id,
                                "name": name,
                                "change": -amount
                            }
            
            # Process outputs
            for output_box in tx.get("outputs", []):
                if output_box.get("address") == address:
                    value_change += output_box.get("value", 0)
                    
                    # Track tokens being received
                    for asset in output_box.get("assets", []):
                        token_id = asset.get("tokenId")
                        amount = asset.get("amount", 0)
                        name = asset.get("name", "Unknown Token")
                        
                        if token_id in token_changes:
                            token_changes[token_id]["change"] += amount
                        else:
                            token_changes[token_id] = {
                                "id": token_id,
                                "name": name,
                                "change": amount
                            }
            
            # Convert to ERG
            erg_change = value_change / 1_000_000_000
            
            # Determine transaction type
            tx_type = "received" if erg_change > 0 else "sent" if erg_change < 0 else "self"
            
            # Convert token dict to list and filter out zero-change tokens
            token_list = [t for t in token_changes.values() if t["change"] != 0]
            
            processed_txs.append({
                "id": tx_id,
                "timestamp": timestamp,
                "datetime": datetime.fromtimestamp(timestamp/1000).strftime("%Y-%m-%d %H:%M:%S"),
                "type": tx_type,
                "value_change": {
                    "nanoerg": value_change,
                    "erg": erg_change
                },
                "confirmations": tx.get("confirmationsCount", 0),
                "tokens": token_list,
                "size": tx.get("size", 0)
            })
        
        return {
            "address": address,
            "total_transactions": total,
            "transactions": processed_txs,
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting transaction history: {str(e)}")
        return {
            "error": f"Error getting transaction history: {str(e)}",
            "address": address,
            "total_transactions": 0,
            "transactions": [],
            "offset": offset,
            "limit": limit
        }

async def get_box_info(identifier: Union[str, int], by_index: bool = False) -> Dict[str, Any]:
    """
    Get detailed information about a box.
    
    Args:
        identifier: Box ID (hex string) or index number
        by_index: Whether to search by index instead of ID
        
    Returns:
        Dictionary containing box details including:
        - id: Box ID
        - value: Dictionary with nanoERG and ERG values
        - creation_height: Block height when box was created
        - ergo_tree: Box's ErgoTree script
        - assets: List of tokens in the box
    """
    try:
        if by_index:
            box_data = await get_box_by_index(identifier)
        else:
            box_data = await get_box_by_id(identifier)
        
        box_id = box_data.get("boxId", "Unknown")
        value_nanoerg = box_data.get("value", 0)
        value_erg = value_nanoerg / 1_000_000_000  # Convert nanoERG to ERG
        creation_height = box_data.get("creationHeight", 0)
        ergo_tree = box_data.get("ergoTree", "Unknown")
        assets = box_data.get("assets", [])
        
        # Format assets/tokens data
        formatted_assets = []
        for asset in assets:
            formatted_assets.append({
                "token_id": asset.get("tokenId", "Unknown"),
                "amount": asset.get("amount", 0)
            })
        
        return {
            "id": box_id,
            "value": {
                "nanoerg": value_nanoerg,
                "erg": value_erg
            },
            "creation_height": creation_height,
            "ergo_tree": ergo_tree,
            "assets": {
                "count": len(formatted_assets),
                "tokens": formatted_assets
            }
        }
    except Exception as e:
        logger.error(f"Error getting box info: {str(e)}")
        return {
            "error": str(e),
            "id": identifier,
            "success": False
        }

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

async def get_address_full_balance(address: str) -> Dict[str, Any]:
    """
    Get detailed balance information for an address.
    
    Args:
        address: Ergo blockchain address
        
    Returns:
        Dictionary containing balance details including:
        - address: The queried address
        - confirmed: Dictionary containing confirmed balance info
        - unconfirmed: Dictionary containing unconfirmed balance info
    """
    try:
        balance_data = await get_address_balance(address)
        
        confirmed = balance_data.get("confirmed", {})
        unconfirmed = balance_data.get("unconfirmed", {})
        
        # Format ERG amounts
        confirmed_erg = confirmed.get("nanoErgs", 0) / 1_000_000_000
        unconfirmed_erg = unconfirmed.get("nanoErgs", 0) / 1_000_000_000
        
        # Process confirmed tokens
        confirmed_tokens = []
        for token in confirmed.get("tokens", []):
            token_id = token.get("tokenId", "Unknown")
            amount = token.get("amount", 0)
            decimals = token.get("decimals", 0)
            name = token.get("name", "Unknown Token")
            
            # Format amount based on decimals
            formatted_amount = amount / (10 ** decimals) if decimals > 0 else amount
            
            confirmed_tokens.append({
                "id": token_id,
                "name": name,
                "amount": {
                    "raw": amount,
                    "formatted": formatted_amount
                },
                "decimals": decimals
            })
        
        # Process unconfirmed tokens
        unconfirmed_tokens = []
        for token in unconfirmed.get("tokens", []):
            token_id = token.get("tokenId", "Unknown")
            amount = token.get("amount", 0)
            decimals = token.get("decimals", 0)
            name = token.get("name", "Unknown Token")
            
            # Format amount based on decimals
            formatted_amount = amount / (10 ** decimals) if decimals > 0 else amount
            
            unconfirmed_tokens.append({
                "id": token_id,
                "name": name,
                "amount": {
                    "raw": amount,
                    "formatted": formatted_amount
                },
                "decimals": decimals
            })
        
        return {
            "address": address,
            "confirmed": {
                "erg": {
                    "nanoerg": confirmed.get("nanoErgs", 0),
                    "erg": confirmed_erg
                },
                "tokens": confirmed_tokens,
                "token_count": len(confirmed_tokens)
            },
            "unconfirmed": {
                "erg": {
                    "nanoerg": unconfirmed.get("nanoErgs", 0),
                    "erg": unconfirmed_erg
                },
                "tokens": unconfirmed_tokens,
                "token_count": len(unconfirmed_tokens)
            }
        }
    except Exception as e:
        logger.error(f"Error getting address balance: {str(e)}")
        return {
            "error": f"Error getting address balance: {str(e)}",
            "address": address,
            "confirmed": None,
            "unconfirmed": None
        }

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