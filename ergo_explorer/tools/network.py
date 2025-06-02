"""
Network-related tools for the Ergo Explorer MCP server.

This module provides tools for interacting with Ergo blockchain network:
- Get network statistics
- Get mining difficulty
- Get network hashrate
- Get mempool information
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ergo_explorer.api.explorer import fetch_api, fetch_network_state
from ergo_explorer.api.node import (
    fetch_node_api
)

# Set up logging
logger = logging.getLogger(__name__)

async def get_blockchain_stats() -> Dict:
    """
    Fetch overall statistics about the Ergo blockchain.
    
    Returns:
        A dictionary containing blockchain statistics
    """
    try:
        logger.info("Fetching blockchain statistics")
        # Get the network state, which includes statistics
        stats_data = await fetch_network_state()
        
        # Fetch additional stats from the /info endpoint
        additional_stats = await fetch_api("info")
        
        # Combine the data
        combined_stats = {
            "networkState": stats_data,
            "additionalInfo": additional_stats
        }
        
        return combined_stats
    except Exception as e:
        logger.error(f"Error fetching blockchain statistics: {str(e)}")
        return {"error": f"Error fetching blockchain statistics: {str(e)}"}

def format_readable_difficulty(difficulty: int) -> str:
    """
    Format the difficulty value into a human-readable form.
    
    Args:
        difficulty: Raw difficulty value
        
    Returns:
        Formatted difficulty string with appropriate unit
    """
    if difficulty == 0:
        return "0"
    
    # Define units and thresholds
    units = ['', 'K', 'M', 'G', 'T', 'P', 'E']
    unit_index = 0
    
    # Convert to appropriate unit
    value = float(difficulty)
    while value >= 1000 and unit_index < len(units) - 1:
        value /= 1000
        unit_index += 1
    
    # Format with appropriate precision
    if value < 10:
        formatted = f"{value:.2f}"
    elif value < 100:
        formatted = f"{value:.1f}"
    else:
        formatted = f"{int(value)}"
    
    return f"{formatted} {units[unit_index]}"

async def format_blockchain_stats(stats_data: Dict) -> str:
    """
    Format blockchain statistics into a readable string.
    
    Args:
        stats_data: The blockchain statistics data to format
        
    Returns:
        A formatted string representation of the blockchain statistics
    """
    if "error" in stats_data:
        return stats_data["error"]
    
    network_state = stats_data.get("networkState", {})
    additional_info = stats_data.get("additionalInfo", {})
    
    # Extract relevant information
    last_blocks = network_state.get("lastBlocks", [])
    height = last_blocks[0].get("height") if last_blocks else "Unknown"
    
    # Format timestamp
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Calculate hashrate from the difficulty
    difficulty = network_state.get("difficulty", 0)
    # Ergo hashrate estimate: difficulty / 8192 * 2^32 / 120
    estimated_hashrate = difficulty * (2**32) / (8192 * 120) if difficulty else 0
    hashrate_th = estimated_hashrate / (10**12)  # Convert to TH/s
    
    # Get supply info
    supply_info = additional_info.get("supply", {})
    circulating_supply = supply_info.get("circulating", 0) / 1000000000 if supply_info else 0  # Convert nanoERG to ERG
    max_supply = supply_info.get("max", 0) / 1000000000 if supply_info else 0  # Convert nanoERG to ERG
    
    # Get version info
    version = additional_info.get("version", "Unknown")
    
    # Transaction stats
    total_transactions = additional_info.get("transactionsCount", 0)
    
    # Create a formatted string
    formatted_output = f"""
## Ergo Blockchain Statistics

### General Information
- **Current Height**: {height}
- **Timestamp**: {current_timestamp}
- **Network Version**: {version}

### Mining Statistics
- **Difficulty**: {difficulty:,}
- **Estimated Hashrate**: {hashrate_th:.2f} TH/s

### Supply Information
- **Circulating Supply**: {circulating_supply:,.2f} ERG
- **Maximum Supply**: {max_supply:,.2f} ERG
- **Emission Percentage**: {(circulating_supply / max_supply * 100) if max_supply else 0:.2f}%

### Transaction Statistics
- **Total Transactions**: {total_transactions:,}
"""
    
    # Add additional stats if available
    if "blockSummary" in additional_info:
        block_summary = additional_info["blockSummary"]
        block_size = block_summary.get("avgBlockSize", 0)
        avg_tx_per_block = block_summary.get("avgTxsPerBlock", 0)
        
        formatted_output += f"""
### Block Statistics
- **Average Block Size**: {block_size:,} bytes
- **Average Transactions Per Block**: {avg_tx_per_block:.2f}
"""
    
    return formatted_output

async def format_network_hashrate(hashrate_data: Dict) -> str:
    """
    Format network hashrate data into a readable string.
    
    Args:
        hashrate_data: The hashrate data to format
        
    Returns:
        A formatted string representation of the network hashrate
    """
    if "error" in hashrate_data:
        return hashrate_data["error"]
    
    # Extract relevant information
    difficulty = hashrate_data.get("difficulty", 0)
    hashrate_th = hashrate_data.get("hashrateTH", 0)
    hashrate_ph = hashrate_data.get("hashratePH", 0)
    
    # Format timestamp
    if "timestamp" in hashrate_data:
        timestamp = datetime.fromtimestamp(hashrate_data["timestamp"] / 1000)
        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        formatted_timestamp = "Unknown"
    
    # Create a formatted string
    formatted_output = f"""
## Ergo Network Hashrate

- **Estimated Hashrate**: {hashrate_th:.2f} TH/s ({hashrate_ph:.6f} PH/s)
- **Current Difficulty**: {difficulty:,}
- **Timestamp**: {formatted_timestamp}

### Hashrate Explanation

The hashrate is an estimate calculated from the current network difficulty.
Formula used: `hashrate = difficulty * 2^32 / (8192 * 120)`

### Note

The actual network hashrate may fluctuate based on several factors including:
- Number of active miners
- Mining hardware efficiency
- Network difficulty adjustments
"""
    
    return formatted_output

async def format_mining_difficulty(difficulty_data: Dict) -> str:
    """
    Format mining difficulty data into a readable string.
    
    Args:
        difficulty_data: The difficulty data to format
        
    Returns:
        A formatted string representation of the mining difficulty
    """
    if "error" in difficulty_data:
        return difficulty_data["error"]
    
    # Extract relevant information
    raw_difficulty = difficulty_data.get("difficulty", 0)
    readable_difficulty = difficulty_data.get("readableDifficulty", "Unknown")
    block_time_target = difficulty_data.get("blockTimeTarget", 120)  # in seconds
    state_type = difficulty_data.get("stateType", "Unknown")
    full_height = difficulty_data.get("fullHeight", 0)
    headers_height = difficulty_data.get("headersHeight", 0)
    
    # Format timestamp
    if "timestamp" in difficulty_data:
        timestamp = datetime.fromtimestamp(difficulty_data["timestamp"] / 1000)
        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        formatted_timestamp = "Unknown"
    
    # Calculate estimated hashrate
    # Ergo hashrate estimate: difficulty / 8192 * 2^32 / 120
    estimated_hashrate = raw_difficulty * (2**32) / (8192 * block_time_target) if raw_difficulty else 0
    hashrate_th = estimated_hashrate / 1000000000000  # TH/s
    
    # Create a formatted string
    formatted_output = f"""
## Ergo Mining Difficulty

- **Raw Difficulty**: {raw_difficulty:,}
- **Readable Difficulty**: {readable_difficulty}
- **Block Time Target**: {block_time_target} seconds
- **State Type**: {state_type}
- **Current Height**: {full_height:,}
- **Headers Height**: {headers_height:,}
- **Estimated Hashrate**: {hashrate_th:.2f} TH/s
- **Timestamp**: {formatted_timestamp}
"""
    
    return formatted_output

# Remove get_mempool_info function
# async def get_mempool_info() -> Dict:
#     ...

# Remove format_mempool_info function
# async def format_mempool_info(mempool_data: Dict) -> str:
#     ...

# (Ensure no other code relies on these before full deletion)
# The functions seem self-contained for the mempool tool, so removing them should be safe.

# <<< End of file (implicitly) >>> 