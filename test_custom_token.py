#!/usr/bin/env python
"""
Test script for box-based token history tracking functionality.

This script tests the box-based method for tracking historical token holders,
which provides comprehensive information including block heights.
"""

import asyncio
import json
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_custom_token")

# Import necessary functions
from ergo_explorer.tools.blockchain import get_historical_token_holder_data
from ergo_explorer.tools.token_holders import track_token_transfers_by_boxes

# Custom JSON encoder to handle datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def test_box_based_tracking(token_id):
    """Test box-based historical token holder tracking"""
    logger.info(f"Testing box-based tracking for token {token_id}")
    
    try:
        # Test with different max_transactions values
        for max_txs in [50, 100]:
            logger.info(f"Testing with max_transactions={max_txs}")
            
            # Track token transfers using box-based method
            result = await track_token_transfers_by_boxes(
                token_id,
                max_transactions=max_txs,
                include_snapshots=True
            )
            
            if "error" in result:
                logger.error(f"Error with box-based tracking: {result['error']}")
            else:
                logger.info(f"Successfully tracked token transfers with box-based method")
                logger.info(f"Found {result.get('transactions_processed', 0)} transactions")
                logger.info(f"Examined {result.get('boxes_examined', 0)} boxes")
                logger.info(f"Found {result.get('transfers_found', 0)} transfers")
                logger.info(f"Total transfers: {result.get('total_transfers', 0)}")
                logger.info(f"Block height range: {result.get('earliest_height', 'N/A')} - {result.get('latest_height', 'N/A')}")
                
                # Print token name
                logger.info(f"Token name: {result.get('token_name', 'Unknown')}")
    
    except Exception as e:
        logger.error(f"Error in box-based tracking test: {str(e)}")

async def test_historical_token_holder_data(token_id):
    """Test the get_historical_token_holder_data function"""
    logger.info(f"Testing get_historical_token_holder_data for token {token_id}")
    
    try:
        # Test with different max_transactions values
        result = await get_historical_token_holder_data(
            token_id,
            max_transactions=100
        )
        
        if "error" in result:
            logger.error(f"Error with get_historical_token_holder_data: {result['error']}")
        else:
            logger.info(f"Successfully retrieved historical token holder data")
            logger.info(f"Token name: {result.get('token_name', 'Unknown')}")
            logger.info(f"Total transfers: {result.get('total_transfers', 0)}")
            logger.info(f"Total snapshots: {result.get('total_snapshots', 0)}")
            
            # Check if recent_transfers has block_height
            transfers = result.get("recent_transfers", [])
            if transfers:
                logger.info(f"First transfer has block_height: {transfers[0].get('block_height')}")
    
    except Exception as e:
        logger.error(f"Error in get_historical_token_holder_data test: {str(e)}")

async def run_tests(token_id):
    """Run all tests"""
    logger.info(f"Starting box-based token history tests for token: {token_id}")
    
    # Test box-based tracking
    await test_box_based_tracking(token_id)
    
    # Test the API function
    await test_historical_token_holder_data(token_id)
    
    logger.info("All tests completed")

if __name__ == "__main__":
    # Get token ID from command line argument or use default
    token_id = "123a3dae88b226ea2f2771ec70919fc252fba792aab4c415f23752225bbb49b1"
    if len(sys.argv) > 1:
        token_id = sys.argv[1]
    
    asyncio.run(run_tests(token_id)) 