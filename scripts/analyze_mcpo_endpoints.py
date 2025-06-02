#!/usr/bin/env python3
"""
MCPO Endpoint Token Estimator

This script analyzes the available MCPO endpoints in the Ergo Explorer MCP server
and estimates the average token count for each endpoint. It provides information
about implemented endpoints, their response sizes, and estimated token counts.

Usage:
    python analyze_mcpo_endpoints.py

Requirements:
    - Access to the running MCPO server
    - tiktoken (for token estimation)
"""

import os
import sys
import json
import inspect
import importlib
import asyncio
import aiohttp
import statistics
from typing import Dict, List, Any, Tuple, Optional
import tiktoken
from datetime import datetime

# Add the project root directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the tools and routes
from ergo_explorer.tools import address, blockchain, token, transaction, block, network, contracts, tokenomics, ergowatch

# Create a tokenizer for token counting
try:
    tokenizer = tiktoken.get_encoding("cl100k_base")  # Claude/Anthropic encoding
except:
    tokenizer = None
    print("Warning: tiktoken not installed or encoding not found. Token counts will not be calculated.")

# Test data for various endpoints
TEST_DATA = {
    "address": {
        "address": "9hdcMw4eRpJPJGx8RJhvdRgFRsE1URpQCsAWM3wG547gQ9awZgi"
    },
    "token": {
        "token_id": "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04"
    },
    "transaction": {
        "tx_id": "fc5e11dd6a4df7df9d03a74e3e2d3defa48e299abd94c55e80ffa2aedec37fc0"
    },
    "block": {
        "height": 960000,
        "hash": "a3485f81950397e4e9fd5aa85917b74d8af2570d018ef3685c51dc2e494d5fdf"
    }
}

# Helper function to count tokens
def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string using tiktoken."""
    if tokenizer is None:
        return -1
    
    try:
        tokens = tokenizer.encode(text)
        return len(tokens)
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return -1

async def fetch_response(session: aiohttp.ClientSession, url: str, data: Dict = None) -> Dict:
    """Fetch a response from the MCPO server."""
    try:
        if data:
            async with session.post(url, json=data) as response:
                return await response.json()
        else:
            async with session.get(url) as response:
                return await response.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {"error": str(e)}

async def test_endpoint(session: aiohttp.ClientSession, endpoint_name: str, 
                        func_name: str, params: Dict = None) -> Dict[str, Any]:
    """Test an endpoint with the provided parameters and return response metrics."""
    base_url = "http://localhost:3001/api"  # Adjust if your MCPO server runs on a different port
    
    url = f"{base_url}/{endpoint_name}/{func_name}"
    
    start_time = datetime.now()
    response = await fetch_response(session, url, params)
    end_time = datetime.now()
    
    response_time = (end_time - start_time).total_seconds() * 1000  # in milliseconds
    
    # Convert the response to a JSON string for token counting
    response_str = json.dumps(response, ensure_ascii=False)
    token_count = count_tokens(response_str)
    
    response_size = len(response_str.encode('utf-8'))
    
    return {
        "endpoint": f"{endpoint_name}/{func_name}",
        "response_time_ms": response_time,
        "response_size_bytes": response_size,
        "estimated_token_count": token_count,
        "status": "success" if "error" not in response else "error",
        "error": response.get("error") if "error" in response else None
    }

async def analyze_endpoints():
    """Analyze all MCPO endpoints and generate a report."""
    # Dictionary to store module name to endpoint mappings
    module_to_endpoint = {
        "blockchain": "blockchain",
        "address": "address",
        "token": "token",
        "transaction": "transaction",
        "block": "block",
        "network": "network",
        "contracts": "contracts",
        "tokenomics": "tokenomics",
        "ergowatch": "ergowatch"
    }
    
    # List to store endpoint test results
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Test blockchain endpoints
        blockchain_funcs = [f for f in dir(blockchain) if not f.startswith('_') and callable(getattr(blockchain, f))]
        for func_name in blockchain_funcs:
            if func_name == "blockchain_status":
                results.append(await test_endpoint(session, "blockchain", func_name))
            elif func_name == "get_address_full_balance":
                results.append(await test_endpoint(session, "blockchain", func_name, 
                                                  {"address": TEST_DATA["address"]["address"]}))
        
        # Test address endpoints
        address_funcs = [f for f in dir(address) if not f.startswith('_') and callable(getattr(address, f))]
        for func_name in address_funcs:
            if func_name in ["get_transaction_history", "analyze_address"]:
                results.append(await test_endpoint(session, "address", func_name,
                                                 {"address": TEST_DATA["address"]["address"]}))
        
        # Test token endpoints
        token_funcs = [f for f in dir(token) if not f.startswith('_') and callable(getattr(token, f))]
        for func_name in token_funcs:
            if func_name == "get_token_price":
                results.append(await test_endpoint(session, "token", func_name,
                                                 {"token_id": TEST_DATA["token"]["token_id"]}))
        
        # Test transaction endpoints
        tx_funcs = [f for f in dir(transaction) if not f.startswith('_') and callable(getattr(transaction, f))]
        for func_name in tx_funcs:
            if func_name == "analyze_transaction":
                results.append(await test_endpoint(session, "transaction", func_name,
                                                 {"tx_id": TEST_DATA["transaction"]["tx_id"]}))
        
        # Test block endpoints
        block_funcs = [f for f in dir(block) if not f.startswith('_') and callable(getattr(block, f))]
        for func_name in block_funcs:
            if func_name == "get_block_by_height":
                results.append(await test_endpoint(session, "block", func_name,
                                                 {"height": TEST_DATA["block"]["height"]}))
            elif func_name == "get_block_by_hash":
                results.append(await test_endpoint(session, "block", func_name,
                                                 {"hash": TEST_DATA["block"]["hash"]}))
            elif func_name == "get_latest_blocks":
                results.append(await test_endpoint(session, "block", func_name,
                                                 {"limit": 5}))
    
    return results

def generate_report(results: List[Dict[str, Any]]) -> None:
    """Generate a report of endpoint token estimates."""
    # Sort results by token count (descending)
    sorted_results = sorted(results, key=lambda x: x.get("estimated_token_count", 0), reverse=True)
    
    # Calculate statistics
    successful_results = [r for r in results if r["status"] == "success" and r["estimated_token_count"] > 0]
    
    if successful_results:
        token_counts = [r["estimated_token_count"] for r in successful_results]
        avg_token_count = statistics.mean(token_counts)
        median_token_count = statistics.median(token_counts)
        min_token_count = min(token_counts)
        max_token_count = max(token_counts)
        total_endpoints = len(results)
        successful_endpoints = len(successful_results)
        
        # Print the report
        print("\n" + "="*80)
        print(f"MCPO ENDPOINT TOKEN ESTIMATE REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        print(f"\nSummary:")
        print(f"  Total endpoints tested: {total_endpoints}")
        print(f"  Successful endpoints: {successful_endpoints}")
        print(f"  Average token count: {avg_token_count:.2f}")
        print(f"  Median token count: {median_token_count:.2f}")
        print(f"  Min token count: {min_token_count}")
        print(f"  Max token count: {max_token_count}")
        
        print("\nEndpoint Details (sorted by token count):")
        print("-"*80)
        print(f"{'Endpoint':<40} {'Status':<10} {'Size (bytes)':<15} {'Tokens':<10} {'Time (ms)':<10}")
        print("-"*80)
        
        for result in sorted_results:
            status = result["status"]
            endpoint = result["endpoint"]
            size = result.get("response_size_bytes", 0)
            tokens = result.get("estimated_token_count", "N/A")
            time = f"{result.get('response_time_ms', 0):.2f}"
            
            print(f"{endpoint:<40} {status:<10} {size:<15} {tokens:<10} {time:<10}")
        
        print("\n")
        print("Recommendations for Future Endpoints:")
        print("-"*80)
        print(f"Based on the current endpoints, new endpoints should aim for:")
        print(f"  - Token count: Less than {avg_token_count:.0f} tokens for standard endpoints")
        print(f"  - Response time: Less than 1000ms for standard queries")
        print(f"  - For data-intensive endpoints, consider pagination or response truncation")
        print(f"  - Add token_estimate in metadata for accurate client-side handling")
        
        # Save the results to a JSON file
        output_file = os.path.join(os.path.dirname(__file__), "mcpo_endpoint_analysis.json")
        with open(output_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_endpoints": total_endpoints,
                    "successful_endpoints": successful_endpoints,
                    "average_token_count": avg_token_count,
                    "median_token_count": median_token_count,
                    "min_token_count": min_token_count,
                    "max_token_count": max_token_count
                },
                "endpoints": sorted_results
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {output_file}")
    else:
        print("No successful endpoint tests to analyze.")

if __name__ == "__main__":
    # Run the analysis
    results = asyncio.run(analyze_endpoints())
    generate_report(results) 