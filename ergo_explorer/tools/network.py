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