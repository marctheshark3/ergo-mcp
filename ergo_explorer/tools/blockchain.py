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
from datetime import datetime, timedelta

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

# Import the new utility function
from ergo_explorer.util.standardize import condense_address

# Import token history tracking tools
from ergo_explorer.tools.token_holders import (
    get_token_by_id,
    get_unspent_boxes_by_token_id,
    get_box_by_id,
    get_boxes_by_token_id,
    get_token_holders,
    get_collection_metadata,
    get_collection_nfts,
    get_collection_holders,
    search_collections,
    get_token_history,
    clear_token_history_cache,
    track_token_transfers_by_boxes
)

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

async def _get_token_holder_data(token_id: str) -> Dict[str, Any]:
    """
    Internal function to fetch and analyze token holder data.
    
    Args:
        token_id: Token ID to search for
        
    Returns:
        Dictionary containing detailed holder information and analysis.
    """
    try:
        # Get all holders
        holders = await get_all_token_holders(token_id)
        
        # If there are no holders, return appropriate structure
        if not holders:
            return {
                "token_id": token_id,
                "token_name": "Unknown Token",
                "decimals": 0,
                "total_supply_in_circulation": {"raw": 0, "formatted": 0},
                "total_holders": 0,
                "holders": [],
                "analysis": {
                    "error": "No holders found",
                    "message": (f"No holders found for token {token_id}. This could be because:\n"
                                f"1. The token doesn't exist\n"
                                f"2. The local node doesn't have information about this token\n"
                                f"3. All tokens are in spent boxes (try using full node with transaction index)")
                }
            }
        
        # Get token info if available
        try:
            token_info = await get_token_by_id(token_id)
            token_name = token_info.get("name", "Unknown Token")
            decimals = token_info.get("decimals", 0)
        except Exception as e:
            logger.warning(f"Could not get token info for {token_id}: {str(e)}")
            # If we can't get token info, use defaults
            token_name = "Unknown Token"
            decimals = 0
        
        # Sort holders by amount in descending order
        holders.sort(key=lambda x: x["amount"], reverse=True)
            
        # Calculate total supply in circulation
        total_supply = sum(holder["amount"] for holder in holders)
        
        # Process holder data
        holder_data = []
        for holder in holders:
            address = holder["address"]
            amount = holder["amount"]
            percentage = (amount / total_supply * 100) if total_supply > 0 else 0
            
            # Format amount based on decimals
            formatted_amount = amount / (10 ** decimals) if decimals > 0 else amount
            
            holder_data.append({
                # Condense address here
                "address": condense_address(address),
                "full_address": address, # Keep full address if needed elsewhere
                "amount": {
                    "raw": amount,
                    "formatted": formatted_amount
                },
                "percentage": round(percentage, 4)
            })
            
        # Calculate analysis metrics
        num_holders = len(holders)
        top_20_holders = holder_data[:min(20, num_holders)]
        top_20_percentage = sum(h["percentage"] for h in top_20_holders)
        
        remaining_holders_count = max(0, num_holders - 20)
        remaining_percentage = 100 - top_20_percentage if num_holders > 0 else 0
        
        # Format total supply based on decimals
        formatted_total_supply = total_supply / (10 ** decimals) if decimals > 0 else total_supply

        # Build the result dictionary
        result = {
            "token_id": token_id,
            "token_name": token_name,
            "decimals": decimals,
            "total_supply_in_circulation": {
                "raw": total_supply,
                "formatted": formatted_total_supply
            },
            "total_holders": num_holders,
            "holders": holder_data,
            "analysis": {
                "top_holders_count": len(top_20_holders),
                "top_holders_percentage": round(top_20_percentage, 2),
                "remaining_holders_count": remaining_holders_count,
                "remaining_holders_percentage": round(remaining_percentage, 2)
            }
        }

        return result
        
    except Exception as e:
        error_msg = f"Error analyzing token holders for {token_id}: {str(e)}"
        logger.error(error_msg)
        # Ensure error response also conforms to expected structure somewhat
        return {
            "token_id": token_id,
            "error": error_msg, 
            "token_name": "Unknown",
            "decimals": 0,
            "total_supply_in_circulation": {"raw": 0, "formatted": 0},
            "total_holders": 0,
            "holders": [],
            "analysis": {"error": error_msg}
        }

async def get_token_stats(token_id: str) -> Dict[str, Any]:
    """
    Get statistical analysis for token holders.

    Args:
        token_id: Token ID to analyze.

    Returns:
        Dictionary containing token statistics like total holders, supply, and distribution.
    """
    logger.info(f"Getting token stats for {token_id}")
    try:
        data = await _get_token_holder_data(token_id)
        if "error" in data and "analysis" in data and "error" in data["analysis"]:
             # Propagate specific error structure if it exists
            return data
        
        # Extract only the stats part
        stats = {
            "token_id": data["token_id"],
            "token_name": data["token_name"],
            "decimals": data["decimals"],
            "total_supply_in_circulation": data["total_supply_in_circulation"],
            "total_holders": data["total_holders"],
            "analysis": data["analysis"]
        }
        return stats
    except Exception as e:
        error_msg = f"Error getting token stats for {token_id}: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg, "token_id": token_id}

async def get_token_holders(token_id: str, include_raw: bool = False, include_analysis: bool = True) -> Dict[str, Any]:
    """
    Get comprehensive token holder information.
    
    Args:
        token_id: Token ID to analyze
        include_raw: Include raw holder data
        include_analysis: Include holder analysis
    """
    logger.info(f"Getting token holder list for {token_id}")
    try:
        data = await _get_token_holder_data(token_id)
        if "error" in data:
            # Propagate error structure if it exists
            return {"error": data.get("error"), "token_id": token_id, "holders": []}
            
        # Extract simplified holder information
        simplified_holders = []
        for holder in data.get("holders", []):
            simplified_holder = {
                "address": holder["address"],
                "amount": holder["amount"]["raw"]
            }
            
            # Optionally include formatted amount
            if include_raw:
                simplified_holder["formatted_amount"] = holder["amount"]["formatted"]
                simplified_holder["percentage"] = holder["percentage"]
                simplified_holder["full_address"] = holder.get("full_address", holder["address"])
            
            simplified_holders.append(simplified_holder)
        
        result = {
            "token_id": data["token_id"],
            "token_name": data["token_name"],
            "holders": simplified_holders
        }
        
        # Optionally include analysis data
        if include_analysis:
            result["decimals"] = data["decimals"]
            result["total_supply"] = data["total_supply_in_circulation"]["raw"]
            result["formatted_total_supply"] = data["total_supply_in_circulation"]["formatted"]
            result["total_holders"] = data["total_holders"]
            result["analysis"] = data["analysis"]
            
        return result
    except Exception as e:
        error_msg = f"Error getting token holder list for {token_id}: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg, "token_id": token_id, "holders": []}

async def get_histogram_token_stats(token_id: str, bin_count: int = 10) -> Dict[str, Any]:
    """
    Get token holder distribution data suitable for histogram visualization.
    
    Args:
        token_id: Token ID to analyze
        bin_count: Number of bins to divide the holder amounts into
        
    Returns:
        Dictionary containing binned distribution data for token holders.
    """
    logger.info(f"Getting token histogram data for {token_id} with {bin_count} bins")
    try:
        data = await _get_token_holder_data(token_id)
        if "error" in data:
            return {"error": data.get("error"), "token_id": token_id}
            
        holders = data.get("holders", [])
        if not holders:
            return {
                "token_id": token_id,
                "token_name": data.get("token_name", "Unknown Token"),
                "error": "No holders found",
                "bins": []
            }
            
        # Extract amounts from holders
        amounts = [holder["amount"]["raw"] for holder in holders]
        
        # Find min and max amounts (excluding outliers if there are enough data points)
        amounts.sort()
        min_amount = amounts[0]
        max_amount = amounts[-1]
        
        # Create bins
        bins = []
        if min_amount == max_amount:
            # All holders have the same amount
            bins.append({
                "min_value": min_amount,
                "max_value": max_amount,
                "count": len(amounts),
                "percentage": 100.0
            })
        else:
            bin_size = (max_amount - min_amount) / bin_count
            
            # Create empty bins
            for i in range(bin_count):
                bin_min = min_amount + i * bin_size
                bin_max = min_amount + (i + 1) * bin_size
                # For the last bin, ensure we include the max value
                if i == bin_count - 1:
                    bin_max = max_amount
                    
                bins.append({
                    "min_value": bin_min,
                    "max_value": bin_max,
                    "count": 0,
                    "addresses": []
                })
            
            # Fill bins with holder data
            for holder in holders:
                amount = holder["amount"]["raw"]
                # Find appropriate bin
                bin_index = min(int((amount - min_amount) / bin_size), bin_count - 1)
                bins[bin_index]["count"] += 1
                bins[bin_index]["addresses"].append(holder["address"])
            
            # Calculate percentages
            total_holders = len(holders)
            for bin_data in bins:
                bin_data["percentage"] = round((bin_data["count"] / total_holders) * 100, 2)
        
        return {
            "token_id": token_id,
            "token_name": data.get("token_name", "Unknown Token"),
            "total_holders": len(holders),
            "min_amount": min_amount,
            "max_amount": max_amount,
            "bin_count": len(bins),
            "bins": bins
        }
        
    except Exception as e:
        error_msg = f"Error generating histogram data for {token_id}: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg, "token_id": token_id}

async def get_historical_token_holder_data(
    token_id: str,
    max_transactions: int = 1000000,  # Set to a very high value essentially removing the limit
    offset: int = 0,
    limit: int = 100,
    include_transfers: bool = False  # Default to False to reduce response size
) -> Dict[str, Any]:
    """
    Get historical token holder distribution data showing how ownership has changed over time.
    
    This function uses the box-based approach to analyze all boxes that have ever contained 
    the specified token. For each box, it extracts information about:
    - The address that held the token
    - The block height when the token was in that wallet
    - Transaction details for token movements
    
    This provides a comprehensive view of token history without relying on time-based filtering.
    
    Args:
        token_id: Token ID to analyze
        max_transactions: Maximum number of transactions to analyze
        offset: Number of transfers to skip for pagination 
        limit: Maximum number of transfers to return
        include_transfers: Whether to include transaction details in the response
        
    Returns:
        Dictionary containing historical token holder distribution data
    """
    try:
        logger.info(f"Getting historical token holder data for token ID: {token_id}")
        
        # Use the box-based method to track token transfers
        # This is more efficient and provides block height information
        update_result = await track_token_transfers_by_boxes(
            token_id, 
            max_transactions=max_transactions
        )
        
        if "error" in update_result:
            logger.error(f"Error tracking token transfers: {update_result.get('error')}")
            return {
                "error": update_result.get("error"),
                "status": "error"
            }
        
        # Get token history from cache/storage
        history = get_token_history(token_id)
        
        # Get all transfers (sorted by timestamp, newest first)
        transfers = sorted(history.transfers, key=lambda t: t.timestamp, reverse=True)
        
        # Create list of formatted transfers
        recent_transfers = [t.to_dict() for t in transfers[:100]]
        
        # Get snapshot data for all time periods
        snapshots = list(history.snapshots.values())
        snapshots.sort(key=lambda s: s.timestamp)
        
        # Format snapshots for distribution changes over time
        distribution_changes = []
        for snapshot in snapshots:
            snapshot_data = snapshot.to_dict()
            distribution_changes.append(snapshot_data)
        
        # Create the response dictionary
        result = {
            "token_id": token_id,
            "token_name": history.metadata.get("token_name", "Unknown"),
            "first_tracked": history.metadata.get("first_tracked"),
            "last_updated": history.metadata.get("last_updated"),
            "distribution_changes": distribution_changes,
            "recent_transfers": recent_transfers,
            "total_transfers": len(history.transfers),
            "total_snapshots": len(history.snapshots),
            "status": "success"
        }
        
        # Add some metadata to the response
        result["query"] = {
            "token_id": token_id,
            "max_transactions": max_transactions,
            "earliest_height": update_result.get("earliest_height"),
            "latest_height": update_result.get("latest_height")
        }
        
        # Format transfers with pagination
        if "recent_transfers" in result:
            transfers = result["recent_transfers"]
            
            # Calculate total transfers for pagination info
            total_transfers = len(transfers)
            
            # Apply pagination
            paginated_transfers = transfers[offset:offset+limit]
            
            # Format transfers for API consumption
            for transfer in paginated_transfers:
                # Convert timestamps to ISO format if needed
                if "timestamp" in transfer and not isinstance(transfer["timestamp"], str):
                    transfer["timestamp"] = transfer["timestamp"].isoformat()
                
                # Condense addresses for better display
                if "from_address" in transfer and transfer["from_address"]:
                    transfer["from_address_condensed"] = condense_address(transfer["from_address"])
                
                if "to_address" in transfer and transfer["to_address"]:
                    transfer["to_address_condensed"] = condense_address(transfer["to_address"])
            
            # Update result with paginated transfers
            result["recent_transfers"] = paginated_transfers
            
            # Add pagination info
            result["pagination"] = {
                "offset": offset,
                "limit": limit,
                "total": total_transfers,
                "has_more": (offset + limit) < total_transfers
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting historical token holder data: {str(e)}")
        return {
            "error": str(e),
            "status": "error",
            "token_id": token_id
        } 