#!/usr/bin/env python
"""
Test script for the token history API endpoint.

This script sends requests to the token history API endpoint with
various parameter combinations and outputs the results.
"""

import asyncio
import json
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure API base URL (adjust if needed)
API_BASE_URL = "http://localhost:3000/api"  # Default MCP server endpoint

# Example token IDs to test with (using some known tokens from Ergo blockchain)
TEST_TOKENS = [
    "d71693c49a84fbbecd4908c94813b46514b18b67a99952dc1e6e4791556de413",  # ergopad
    "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",  # Sigmaverse
    "472c3d4ecaa08fb7392ff041ee2e6af75f4a558810a74b28600549d5392810e8",  # NETA
]

# Custom JSON encoder to handle datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def test_historical_token_holders():
    """Test the historical token holders API with various parameter combinations"""
    
    token_id = TEST_TOKENS[0]  # Use the first test token
    print(f"\n📊 Testing historical token holders API for {token_id}")
    
    # Define test scenarios focused on essential parameters
    test_cases = [
        # Basic usage - just token ID and time range
        {
            "name": "Basic usage with time range",
            "params": {
                "token_id": token_id,
                "time_range": "30 days"
            }
        },
        # With pagination
        {
            "name": "With pagination parameters",
            "params": {
                "token_id": token_id,
                "time_range": "60 days",
                "offset": 0,
                "limit": 50
            }
        },
        # With transaction limit
        {
            "name": "With transaction limit",
            "params": {
                "token_id": token_id,
                "time_range": "90 days",
                "max_transactions": 200
            }
        }
    ]
    
    # Run test cases
    for case in test_cases:
        print(f"\n📝 Test: {case['name']}")
        print(f"Parameters: {json.dumps(case['params'], indent=2)}")
        
        try:
            url = f"{API_BASE_URL}/token/historical_token_holders"
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=case["params"])
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract key metrics for a brief overview
                    if "status" in result and result["status"] == "success":
                        transfers_count = len(result.get("recent_transfers", []))
                        snapshots_count = len(result.get("distribution_changes", []))
                        time_range = result.get("query", {}).get("time_range_readable", "unknown")
                        
                        print(f"✅ Success: Found {transfers_count} transfers and {snapshots_count} snapshots")
                        print(f"   Time Range: {time_range}")
                    else:
                        print(f"❌ API error: {result.get('error', 'Unknown error')}")
                else:
                    print(f"❌ HTTP error: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

async def main():
    """Run the test script."""
    # Test with the first token ID
    await test_historical_token_holders()
    
    # Uncomment to test additional tokens
    # for token_id in TEST_TOKENS[1:]:
    #     await test_historical_token_holders_api(token_id)

if __name__ == "__main__":
    asyncio.run(main()) 