"""
Block-related tools for the Ergo Explorer MCP server.

This module provides tools for interacting with Ergo blockchain blocks:
- Retrieving blocks by height
- Retrieving blocks by hash
- Getting latest blocks
- Fetching transactions from a block
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ergo_explorer.api.node import fetch_node_api

# Set up logging
logger = logging.getLogger(__name__)

async def get_block_by_height(height: int) -> Dict:
    """
    Fetch a block by its height using the direct Node API.
    
    Args:
        height: The height of the block to fetch
        
    Returns:
        A dictionary containing block data or an error message
    """
    try:
        logger.info(f"Fetching block info at height {height} via Node API")
        # Step 1: Get block header ID(s) using the /blocks/at/{height} endpoint
        headers_response = await fetch_node_api(f"blocks/at/{height}")
        
        # Check if the response is valid and contains header IDs
        if headers_response and isinstance(headers_response, list) and len(headers_response) > 0:
            block_id = headers_response[0] # The API returns a list of header IDs (strings)
            logger.info(f"Found block ID {block_id} at height {height}, fetching full block...")
            
            # Step 2: Fetch the complete block data using the /blocks/{block_id} endpoint
            block_data = await fetch_node_api(f"blocks/{block_id}")
            return block_data # Return the full block data
        else:
            logger.warning(f"Node API did not return a valid block ID for height {height}. Response: {headers_response}")
            # Check for specific error structure if the node returns one, otherwise generic error
            if isinstance(headers_response, dict) and 'detail' in headers_response:
                 error_detail = headers_response['detail']
                 logger.warning(f"Node API error for height {height}: {error_detail}")
                 # Handle 404 specifically if possible from detail
                 if "404" in str(error_detail):
                      return {"error": f"No block found at height {height}"}
                 else:
                      return {"error": f"Node API error: {error_detail}"}
            else:
                 # Assume block not found if response wasn't expected list or known error format
                 return {"error": f"No block found at height {height}"}
                 
    except Exception as e:
        # Log the exception with traceback for debugging
        logger.error(f"Error fetching block at height {height} via Node API: {e}", exc_info=True)
        # Check if the error is due to HTTPStatusError (e.g., 404) which might have been caught by fetch_node_api logging
        # Return a user-friendly error
        return {"error": f"Failed to fetch block data from Node API: {str(e)}"}

async def get_block_by_hash(block_hash: str) -> Dict:
    """
    Fetch a block by its hash using the direct Node API.
    
    Args:
        block_hash: The hash (ID) of the block to fetch
        
    Returns:
        A dictionary containing block data or an error message
    """
    try:
        logger.info(f"Fetching block with hash {block_hash} via Node API")
        # Directly use the /blocks/{block_hash} endpoint
        block_data = await fetch_node_api(f"blocks/{block_hash}")
        return block_data
    except Exception as e:
        logger.error(f"Error fetching block with hash {block_hash} via Node API: {e}", exc_info=True)
        return {"error": f"Failed to fetch block data from Node API: {str(e)}"}
    
async def get_block_by_block_id(block_id: str) -> Dict:
    """
    Fetch a block by its ID using the direct Node API.
    
    Args:
        block_id: The ID of the block to fetch

    Returns:
        A dictionary containing block data or an error message
    """
    try:
        logger.info(f"Fetching block with ID {block_id} via Node API")
        # Directly use the /blocks/{block_id} endpoint
        block_data = await fetch_node_api(f"blocks/{block_id}")
        return block_data
    except Exception as e:
        logger.error(f"Error fetching block with ID {block_id} via Node API: {e}", exc_info=True)
        return {"error": f"Failed to fetch block data from Node API: {str(e)}"} 
    
    

async def get_latest_blocks(limit: int = 10) -> Dict:
    """
    Fetch the latest blocks from the Ergo blockchain.
    
    Args:
        limit: Maximum number of blocks to retrieve (default: 10)
        
    Returns:
        A dictionary containing the latest blocks
    """
    try:
        logger.info(f"Fetching latest {limit} blocks")
        response = await fetch_node_api(f"blocks/latest?limit={limit}")
        return response
    except Exception as e:
        logger.error(f"Error fetching latest blocks: {str(e)}")
        return {"error": f"Error fetching latest blocks: {str(e)}"}

async def get_block_transactions(block_id: str, limit: int = 100) -> Dict:
    """
    Fetch transactions from a specific block.
    
    Args:
        block_id: The ID of the block
        limit: Maximum number of transactions to retrieve (default: 100)
        
    Returns:
        A dictionary containing the block's transactions
    """
    try:
        logger.info(f"Fetching transactions for block {block_id}")
        response = await fetch_node_api(f"blocks/{block_id}/transactions?limit={limit}")
        return response
    except Exception as e:
        logger.error(f"Error fetching transactions for block {block_id}: {str(e)}")
        return {"error": f"Error fetching block transactions: {str(e)}"}

async def format_block_data(block_data: Dict) -> str:
    """
    Format block data (received from Node API's /blocks/{id} endpoint) into a readable string.
    
    Args:
        block_data: The block data dictionary to format
        
    Returns:
        A formatted string representation of the block data
    """
    if not block_data or isinstance(block_data, str) or "header" not in block_data:
        # Handle cases where block_data might be an error string or missing the header
        if isinstance(block_data, dict) and "error" in block_data:
            return block_data["error"]
        logger.warning(f"Invalid or incomplete block data received for formatting: {block_data}")
        return "Error: Received invalid or incomplete block data for formatting."

    header = block_data.get("header", {})
    transactions_data = block_data.get("blockTransactions", {})
    transactions = transactions_data.get("transactions", [])
    block_size = block_data.get("size")

    # Log the data just before creating block_info
    logger.debug(f"Formatting block data. Header keys: {list(header.keys())}, TxData keys: {list(transactions_data.keys())}, Top-level keys: {list(block_data.keys())}")

    # Extract relevant information using correct paths
    # Remove fields not reliably available from Node API /blocks/{id}
    block_info = {
        "height": header.get("height"),
        "id": header.get("id"),
        "timestamp": header.get("timestamp"),
        # Derive transaction count from the list
        "transactionsCount": len(transactions),
        "size": block_size,
        "difficulty": header.get("difficulty"),
        # Node API doesn't directly provide miner name/address/reward in /blocks/{id}
        # "miner": "Unknown (Not in Node API /blocks/{id})",
        # "minerAddress": "Unknown (Not in Node API /blocks/{id})",
        # "minerReward": 0, # Set to 0 as it's not directly available
        # "blockTime": header.get("blockTime"), # This might not exist either
        # "mainChain": header.get("mainChain"), # This might not exist either
    }
    
    # Log after creating block_info
    logger.debug(f"Created block_info dictionary: {block_info}")
    
    # Format timestamp
    if block_info["timestamp"]:
        try:
            timestamp = datetime.fromtimestamp(block_info["timestamp"] / 1000)
            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception as e:
            logger.warning(f"Could not format timestamp {block_info['timestamp']}: {e}")
            formatted_timestamp = "Invalid Timestamp"
    else:
        formatted_timestamp = "Unknown"
    
    # Create a formatted string
    formatted_output = f"""
## Block Details (from Node API)

- **Height**: {block_info['height']}
- **ID**: {block_info['id']}
- **Timestamp**: {formatted_timestamp}
- **Transactions**: {block_info['transactionsCount']}
- **Size**: {block_info['size']} bytes
- **Difficulty**: {block_info['difficulty']}
# - **Miner**: {block_info['miner']}
# - **Miner Address**: {block_info['minerAddress']}
# - **Miner Reward**: {block_info['minerReward']} ERG
# - **Block Time**: {block_info.get('blockTime', 'N/A')}
# - **Main Chain**: {block_info.get('mainChain', 'N/A')}
"""
    return formatted_output

async def format_latest_blocks(blocks_data: Dict) -> str:
    """
    Format latest blocks data into a readable string.
    
    Args:
        blocks_data: The blocks data to format
        
    Returns:
        A formatted string representation of the latest blocks
    """
    if "error" in blocks_data:
        return blocks_data["error"]
    
    if "items" not in blocks_data or not blocks_data["items"]:
        return "No blocks found."
    
    blocks = blocks_data["items"]
    formatted_output = "## Latest Blocks\n\n"
    
    for block in blocks:
        # Format timestamp
        if block.get("timestamp"):
            timestamp = datetime.fromtimestamp(block["timestamp"] / 1000)
            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
        else:
            formatted_timestamp = "Unknown"
        
        miner_name = block.get("miner", {}).get("name", "Unknown")
        miner_reward = block.get("minerReward", 0) / 1000000000  # Convert nanoERG to ERG
        
        formatted_output += f"""
### Block {block.get('height')}
- **ID**: {block.get('id')}
- **Timestamp**: {formatted_timestamp}
- **Transactions**: {block.get('transactionsCount')}
- **Size**: {block.get('size')} bytes
- **Miner**: {miner_name}
- **Reward**: {miner_reward} ERG
"""
    
    return formatted_output

async def format_block_transactions(tx_data: Dict, block_id: str) -> str:
    """
    Format block transactions data into a readable string.
    
    Args:
        tx_data: The transactions data to format
        block_id: The ID of the block
        
    Returns:
        A formatted string representation of the block transactions
    """
    if "error" in tx_data:
        return tx_data["error"]
    
    if "items" not in tx_data or not tx_data["items"]:
        return f"No transactions found for block {block_id}."
    
    transactions = tx_data["items"]
    formatted_output = f"## Transactions in Block {block_id}\n\n"
    
    for idx, tx in enumerate(transactions, 1):
        tx_id = tx.get("id", "Unknown")
        tx_size = tx.get("size", 0)
        
        inputs_count = len(tx.get("inputs", []))
        outputs_count = len(tx.get("outputs", []))
        
        # Calculate total value
        total_value = sum([output.get("value", 0) for output in tx.get("outputs", [])])
        total_value_erg = total_value / 1000000000  # Convert nanoERG to ERG
        
        formatted_output += f"""
### Transaction {idx}
- **ID**: {tx_id}
- **Size**: {tx_size} bytes
- **Inputs**: {inputs_count}
- **Outputs**: {outputs_count}
- **Total Value**: {total_value_erg} ERG
"""
    
    return formatted_output 