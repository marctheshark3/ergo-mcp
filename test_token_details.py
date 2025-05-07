#!/usr/bin/env python
"""
Test script to display detailed token holder history information.

This script shows comprehensive information about token transfers
including block heights and detailed holder snapshots.
"""

import asyncio
import json
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_token_details")

# Import necessary functions
from ergo_explorer.tools.blockchain import get_historical_token_holder_data
from ergo_explorer.tools.token_holders import track_token_transfers_by_boxes

# Custom JSON encoder to handle datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def display_token_details(token_id):
    """Display detailed token information"""
    logger.info(f"Fetching comprehensive details for token {token_id}")
    
    try:
        # Get token data with a higher transaction limit for a more complete history
        result = await get_historical_token_holder_data(
            token_id,
            max_transactions=200,
            offset=0,
            limit=100  # Higher limit to get more transfers in response
        )
        
        if "error" in result:
            logger.error(f"Error retrieving token data: {result['error']}")
            return
        
        # Basic token information
        logger.info(f"\n{'=' * 50}")
        logger.info(f"TOKEN DETAILS: {result.get('token_name', 'Unknown')}")
        logger.info(f"{'=' * 50}")
        logger.info(f"Token ID: {token_id}")
        logger.info(f"Total transfers processed: {result.get('total_transfers', 0)}")
        logger.info(f"Total boxes examined: {result.get('boxes_examined', 0)}")
        logger.info(f"Earliest height: {result.get('earliest_height', 'N/A')}")
        logger.info(f"Latest height: {result.get('latest_height', 'N/A')}")
        
        # Display recent transfers with block heights
        transfers = result.get("recent_transfers", [])
        if transfers:
            logger.info(f"\n{'-' * 50}")
            logger.info(f"RECENT TRANSFERS (with block heights):")
            logger.info(f"{'-' * 50}")
            for i, transfer in enumerate(transfers[:20]):  # Limit to first 20 for readability
                logger.info(f"Transfer {i+1}:")
                logger.info(f"  From: {transfer.get('from_address', 'Genesis')}")
                logger.info(f"  To: {transfer.get('to_address', 'N/A')}")
                logger.info(f"  Amount: {transfer.get('amount', 'N/A')}")
                logger.info(f"  Block Height: {transfer.get('block_height', 'N/A')}")
                logger.info(f"  Timestamp: {transfer.get('timestamp', 'N/A')}")
                logger.info(f"  Transaction ID: {transfer.get('tx_id', 'N/A')}")
                logger.info(f"  {'-' * 30}")
        else:
            logger.info("No transfers found.")
        
        # Display holder snapshots
        snapshots = result.get("snapshots", [])
        if snapshots:
            logger.info(f"\n{'-' * 50}")
            logger.info(f"HOLDER SNAPSHOTS:")
            logger.info(f"{'-' * 50}")
            
            # Sort snapshots by timestamp if available
            if snapshots and "timestamp" in snapshots[0]:
                snapshots = sorted(snapshots, key=lambda x: x.get("timestamp", ""))
            
            for i, snapshot in enumerate(snapshots[:5]):  # Limit to first 5 for readability
                logger.info(f"Snapshot {i+1}:")
                
                # Extract timestamp and associated height
                timestamp = snapshot.get("timestamp", "N/A")
                block_height = snapshot.get("block_height", "N/A")
                logger.info(f"  Timestamp: {timestamp}")
                logger.info(f"  Block Height: {block_height}")
                
                # List holders in this snapshot
                holders = snapshot.get("holders", {})
                if holders:
                    logger.info(f"  Holders: {len(holders)} addresses")
                    # Show top 5 holders by amount
                    sorted_holders = sorted(holders.items(), key=lambda x: int(x[1]) if isinstance(x[1], (int, str)) else 0, reverse=True)
                    for j, (address, amount) in enumerate(sorted_holders[:5]):
                        logger.info(f"    {j+1}. {address}: {amount}")
                    
                    if len(sorted_holders) > 5:
                        logger.info(f"    ... and {len(sorted_holders) - 5} more addresses")
                else:
                    logger.info("  No holders in this snapshot")
                logger.info(f"  {'-' * 30}")
        else:
            logger.info("No snapshots found.")
            
    except Exception as e:
        logger.error(f"Error retrieving token details: {str(e)}")

async def main(token_id):
    """Main function to run the test"""
    logger.info(f"Starting detailed token analysis for: {token_id}")
    await display_token_details(token_id)
    logger.info("Analysis complete")

if __name__ == "__main__":
    # Get token ID from command line argument or use default
    token_id = "123a3dae88b226ea2f2771ec70919fc252fba792aab4c415f23752225bbb49b1"
    if len(sys.argv) > 1:
        token_id = sys.argv[1]
    
    asyncio.run(main(token_id)) 