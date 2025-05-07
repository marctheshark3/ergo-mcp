#!/usr/bin/env python
"""
Ergo Token Data Collector

This script fetches data about token holders from the Ergo blockchain.
It can collect either just the current holders with their most recent blockheights
or the complete history of all token transactions.

Usage:
    python get_token_data.py <token_id> [--history] [--output filename.json] [--node-url url]
"""

import requests
import json
import time
import argparse
import sys

def fetch_boxes(node_url, token_id, offset, limit):
    """Fetch boxes containing the specified token from the Ergo node API."""
    api_url = f"{node_url}/blockchain/box/byTokenId/{token_id}"
    params = {"offset": offset, "limit": limit}
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching boxes at offset {offset}: {str(e)}")
        return {"items": []}

def get_token_data(node_url, token_id, collect_history=False, batch_size=50):
    """
    Collect data about token holders and optionally transaction history.
    
    Args:
        node_url: Base URL for the Ergo node API
        token_id: ID of the token to analyze
        collect_history: If True, collect full transaction history
        batch_size: Number of boxes to fetch in each batch
        
    Returns:
        If collect_history=False: Dictionary mapping addresses to their latest blockheights
        If collect_history=True: Dictionary with both current holders and transaction history
    """
    # For storing current holders (address → most recent blockheight)
    address_to_height = {}
    
    # For storing full history if requested
    token_history = []
    
    offset = 0
    total_processed = 0
    
    print(f"Fetching data for token: {token_id}")
    
    while True:
        # Fetch a batch of boxes
        print(f"Fetching boxes at offset {offset}...")
        data = fetch_boxes(node_url, token_id, offset, batch_size)
        items = data.get("items", [])
        
        if not items:
            print("No more boxes found.")
            break
        
        # Process this batch
        total_processed += len(items)
        print(f"Processing {len(items)} boxes...")
        
        for item in items:
            address = item.get("address")
            height = item.get("inclusionHeight")
            box_id = item.get("boxId")
            spent_tx_id = item.get("spentTransactionId")
            value = item.get("value", 0)
            
            # Get token amount
            token_amount = 0
            for asset in item.get("assets", []):
                if asset.get("tokenId") == token_id:
                    token_amount = asset.get("amount", 0)
                    break
            
            # Store transaction history if requested
            if collect_history:
                token_history.append({
                    "boxId": box_id,
                    "address": address,
                    "inclusionHeight": height,
                    "spentTransactionId": spent_tx_id,
                    "value": value,
                    "tokenAmount": token_amount
                })
            
            # Always update the current holder map
            if address:
                # Store the latest blockheight for each address
                if address not in address_to_height or height > address_to_height[address]["height"]:
                    address_to_height[address] = {
                        "height": height,
                        "amount": token_amount
                    }
        
        # If we received fewer boxes than requested, we've reached the end
        if len(items) < batch_size:
            print("Reached the last page of results.")
            break
        
        # Move to the next batch
        offset += batch_size
        time.sleep(0.1)  # Avoid hammering the API
    
    # Prepare result based on whether we're collecting history
    if collect_history:
        result = {
            "tokenId": token_id,
            "holders": {
                addr: data for addr, data in address_to_height.items()
            },
            "history": token_history,
            "processedBoxes": total_processed
        }
    else:
        # Simple map of address to blockheight data
        result = {
            addr: data for addr, data in address_to_height.items()
        }
    
    return result

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Collect token holder data from Ergo blockchain")
    parser.add_argument("token_id", help="Token ID to analyze")
    parser.add_argument("--history", action="store_true", help="Collect full transaction history")
    parser.add_argument("--output", default="token_data.json", help="Output JSON file name")
    parser.add_argument("--node-url", default="http://localhost:9053", help="Ergo node API URL")
    parser.add_argument("--batch-size", type=int, default=50, help="Number of boxes to fetch in each batch")
    args = parser.parse_args()
    
    # Collect the token data
    result = get_token_data(
        args.node_url, 
        args.token_id, 
        collect_history=args.history,
        batch_size=args.batch_size
    )
    
    # Save to file
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)
    
    # Output summary
    if args.history:
        print(f"Saved data for {len(result['holders'])} unique addresses with full history")
        print(f"Total transactions processed: {result['processedBoxes']}")
    else:
        print(f"Saved {len(result)} unique addresses with blockheights to {args.output}")
    
    # Display top 5 holders if we have amount data
    if args.history:
        holders = [{
            "address": addr,
            "amount": data["amount"],
            "height": data["height"]
        } for addr, data in result["holders"].items()]
        
        # Sort by token amount (descending)
        holders.sort(key=lambda x: x["amount"], reverse=True)
        
        if holders:
            print("\nTop Token Holders:")
            for i, holder in enumerate(holders[:5], 1):
                print(f"{i}. {holder['address']}: {holder['amount']} tokens (at height {holder['height']})")

if __name__ == "__main__":
    main() 