#!/usr/bin/env python
"""
Test script for the historical token holder tracking functionality.

This script tests both time-based and transaction-based methods for tracking
historical token holders with various parameter combinations.
"""

import asyncio
from datetime import datetime, timedelta
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_historical_token_holders")

# Custom JSON encoder to handle datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# No need to monkey patch json.dumps
# original_dumps = json.dumps
# json.dumps = lambda obj, **kwargs: original_dumps(obj, cls=CustomJSONEncoder, **kwargs)

# Import necessary functions
from ergo_explorer.tools.blockchain import get_historical_token_holder_data
from ergo_explorer.tools.token_holders import (
    track_token_transfers, 
    track_token_transfers_by_boxes,
    PERIOD_DAILY,
    PERIOD_WEEKLY,
    PERIOD_MONTHLY
)

# Example token IDs to test with 
# (using some known tokens from Ergo blockchain; replace with real tokens if needed)
TEST_TOKENS = [
    "d71693c49a84fbbecd4908c94813b46514b18b67a99952dc1e6e4791556de413",  # ergopad
    "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",  # Sigmaverse
    "472c3d4ecaa08fb7392ff041ee2e6af75f4a558810a74b28600549d5392810e8",  # NETA
]

# If running on testnet, replace with testnet tokens
TESTNET_TOKENS = [
    "0034c44f0c7a38e92d1553c03e31a244730382583a4b7ffb01b9b0f5b8456c01" # tSigUSD
]

async def test_time_based_tracking(token_id):
    """Test time-based historical token holder tracking"""
    logger.info(f"Testing time-based tracking for token {token_id}")
    
    try:
        # Test with time_range parameter (primary method)
        result = await get_historical_token_holder_data(
            token_id,
            time_range="15 days"
        )
        
        if "error" in result:
            logger.error(f"Error with time_range parameter: {result['error']}")
        else:
            logger.info(f"Successfully retrieved data with time_range parameter")
            logger.info(f"Found {len(result.get('recent_transfers', []))} transfers")
            logger.info(f"Found {len(result.get('distribution_changes', []))} distribution snapshots")
        
        # Test with max_transactions parameter
        result = await get_historical_token_holder_data(
            token_id,
            time_range="10 days",
            max_transactions=50
        )
        
        if "error" in result:
            logger.error(f"Error with max_transactions parameter: {result['error']}")
        else:
            logger.info(f"Successfully retrieved data with max_transactions parameter")
            logger.info(f"Time range: {result.get('query', {}).get('time_range_readable', 'Not provided')}")
        
        # Return the last result for inspection
        return result
    
    except Exception as e:
        logger.error(f"Exception in time-based tracking test: {str(e)}")
        return {"error": str(e)}

async def test_transaction_based_tracking(token_id):
    """Test transaction-based historical token holder tracking"""
    logger.info(f"Testing transaction-based tracking for token {token_id}")
    
    try:
        # Demonstrate using only the essential parameters
        result = await get_historical_token_holder_data(
            token_id,
            max_transactions=50
        )
        
        if "error" in result:
            logger.error(f"Error with basic parameters: {result['error']}")
        else:
            logger.info(f"Successfully retrieved data with basic parameters")
            logger.info(f"Found {len(result.get('recent_transfers', []))} transfers")
        
        # Return the result for inspection
        return result
    
    except Exception as e:
        logger.error(f"Exception in transaction-based tracking test: {str(e)}")
        return {"error": str(e)}

async def test_time_range_parameter(token_id):
    """Test the time_range parameter format"""
    logger.info(f"Testing time_range parameter for token {token_id}")
    
    # Test various time_range expressions
    time_ranges = ["30 days", "2 weeks", "1 month", "3 months", "1 year"]
    
    results = {}
    
    for time_range in time_ranges:
        logger.info(f"Testing time_range: {time_range}")
        try:
            # Use only the essential parameters
            result = await get_historical_token_holder_data(
                token_id,
                time_range=time_range
            )
            
            # Store result summary
            if "error" in result:
                results[time_range] = f"Error: {result['error']}"
            else:
                days_back = result["query"].get("days_back", "unknown")
                start_date = result["query"].get("start_date", "unknown")
                end_date = result["query"].get("end_date", "unknown")
                results[time_range] = {
                    "status": result.get("status", "unknown"),
                    "days_back": days_back,
                    "date_range": f"{start_date} to {end_date}",
                    "snapshots": len(result.get("snapshots", [])),
                    "transfers": len(result.get("recent_transfers", []))
                }
        except Exception as e:
            results[time_range] = f"Exception: {str(e)}"
    
    # Print results
    logger.info("Time Range Parameter Test Results:")
    print(json.dumps(results, indent=2, cls=CustomJSONEncoder))
    return results

async def run_tests():
    """Run all tests with a sample token"""
    # Choose one token for comprehensive testing
    token_id = TEST_TOKENS[0]  # Use the first test token
    
    logger.info(f"Running comprehensive tests for token {token_id}")
    
    # Test time-based tracking
    time_based_result = await test_time_based_tracking(token_id)
    
    # Test transaction-based tracking
    tx_based_result = await test_transaction_based_tracking(token_id)
    
    # Test time_range parameter
    time_range_results = await test_time_range_parameter(token_id)
    
    # Print summary
    logger.info("\n===== TEST SUMMARY =====")
    
    logger.info("\nTime-based tracking:")
    if "error" in time_based_result:
        logger.info(f"  Failed: {time_based_result['error']}")
    else:
        logger.info(f"  Success: Found {len(time_based_result.get('recent_transfers', []))} transfers")
    
    logger.info("\nTransaction-based tracking:")
    if "error" in tx_based_result:
        logger.info(f"  Failed: {tx_based_result['error']}")
    else:
        logger.info(f"  Success: Found {len(tx_based_result.get('recent_transfers', []))} transfers")
    
    # Print time range test results
    logger.info("\nTime range parameter tests:")
    for time_range, result in time_range_results.items():
        if isinstance(result, dict) and "status" in result:
            logger.info(f"  {time_range}: Success - days_back: {result['days_back']}, "
                        f"snapshots: {result['snapshots']}, transfers: {result['transfers']}")
        else:
            logger.info(f"  {time_range}: {result}")
    
    logger.info("\n=======================")

if __name__ == "__main__":
    # Run the async test
    asyncio.run(run_tests()) 