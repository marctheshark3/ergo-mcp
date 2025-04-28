#!/usr/bin/env python3
"""
Test script for the response standardizer.

This script demonstrates how to use the response standardizer to convert
markdown-formatted responses to structured JSON data.
"""

import asyncio
import json
import sys
from typing import Dict, Any

from ergo_explorer.tools.address import get_address_balance, get_transaction_history
from ergo_explorer.tools.blockchain import get_blockchain_height, get_transaction_info, get_box_info, get_token_info
from ergo_explorer.tools.eip_manager import list_eips
from ergo_explorer.response_standardizer import convert_markdown_to_json

async def test_standardizer():
    """Test the response standardizer with real endpoints."""
    results = []
    
    # Test address balance standardization
    address = "9hHDQb26AjnJUXxcqriqY1mnhpLuUeC81C4pggtK7tupr92Ea1K"
    print(f"Testing address balance for {address}...")
    
    try:
        # Get original markdown-formatted balance
        balance_md = await get_address_balance(address)
        print("Original balance response:")
        print(balance_md)
        print("\n")
        
        # Convert to structured JSON
        balance_json = convert_markdown_to_json(balance_md, "balance")
        print("Structured JSON balance:")
        print(json.dumps(balance_json, indent=2))
        print("\n")
        
        results.append({
            "test": "address_balance",
            "markdown": balance_md,
            "json": balance_json
        })
    except Exception as e:
        print(f"Error testing address balance: {str(e)}")
    
    # Test transaction history standardization
    print(f"Testing transaction history for {address}...")
    
    try:
        # Get original markdown-formatted transaction history
        tx_history_md = await get_transaction_history(address, limit=2)
        print("Original transaction history response:")
        print(tx_history_md)
        print("\n")
        
        # For transaction history, we'd need to implement a custom parser
        # This is just a placeholder for demonstration
        results.append({
            "test": "transaction_history",
            "markdown": tx_history_md,
            "json": {"status": "not_implemented"}
        })
    except Exception as e:
        print(f"Error testing transaction history: {str(e)}")
    
    # Test blockchain height standardization
    print("Testing blockchain height...")
    
    try:
        # Get original markdown-formatted blockchain height
        height_md = await get_blockchain_height()
        print("Original blockchain height response:")
        print(height_md)
        print("\n")
        
        # Create custom structured data for blockchain height
        height_json = {
            "blockchain_height": {
                "indexed_height": None,
                "full_height": None,
                "blocks_behind": None
            }
        }
        
        # Extract height information using regex
        import re
        
        indexed_match = re.search(r"Indexed Height: ([0-9,]+)", height_md)
        if indexed_match:
            height_json["blockchain_height"]["indexed_height"] = int(indexed_match.group(1).replace(",", ""))
            
        full_match = re.search(r"Full Height: ([0-9,]+)", height_md)
        if full_match:
            height_json["blockchain_height"]["full_height"] = int(full_match.group(1).replace(",", ""))
            
        behind_match = re.search(r"Blocks Behind: ([0-9,]+)", height_md)
        if behind_match:
            height_json["blockchain_height"]["blocks_behind"] = int(behind_match.group(1).replace(",", ""))
        
        print("Structured JSON blockchain height:")
        print(json.dumps(height_json, indent=2))
        print("\n")
        
        results.append({
            "test": "blockchain_height",
            "markdown": height_md,
            "json": height_json
        })
    except Exception as e:
        print(f"Error testing blockchain height: {str(e)}")
    
    # Test transaction info standardization
    tx_id = "ff9b418e98074562f337d3ece5bfabbe78c3e7f38c6536cc382827caf15c6890"
    print(f"Testing transaction info for {tx_id}...")
    
    try:
        # Get original markdown-formatted transaction info
        tx_info_md = await get_transaction_info(tx_id)
        print("Original transaction info response:")
        print(tx_info_md[:500] + "..." if len(tx_info_md) > 500 else tx_info_md)
        print("\n")
        
        # Convert to structured JSON
        tx_info_json = convert_markdown_to_json(tx_info_md, "transaction")
        print("Structured JSON transaction info:")
        print(json.dumps(tx_info_json, indent=2))
        print("\n")
        
        results.append({
            "test": "transaction_info",
            "markdown": tx_info_md,
            "json": tx_info_json
        })
    except Exception as e:
        print(f"Error testing transaction info: {str(e)}")
    
    # Test EIP list standardization
    print("Testing EIP list...")
    
    try:
        # Get original markdown-formatted EIP list
        eip_list_md = await list_eips()
        print("Original EIP list response:")
        print(eip_list_md[:500] + "..." if len(eip_list_md) > 500 else eip_list_md)
        print("\n")
        
        # Convert to structured JSON
        eip_list_json = convert_markdown_to_json(eip_list_md, "eip")
        print("Structured JSON EIP list:")
        print(json.dumps(eip_list_json, indent=2))
        print("\n")
        
        results.append({
            "test": "eip_list",
            "markdown": eip_list_md,
            "json": eip_list_json
        })
    except Exception as e:
        print(f"Error testing EIP list: {str(e)}")
    
    # Write test results to file
    with open("standardizer_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Test results written to standardizer_test_results.json")

if __name__ == "__main__":
    asyncio.run(test_standardizer()) 