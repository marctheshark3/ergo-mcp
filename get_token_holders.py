#!/usr/bin/env python
"""
Token Holder Analysis Script

This script fetches historical token holder data from an Ergo node by analyzing boxes
that contained the specified token. It can be used to track token holder distribution
and analyze token transfers.

Usage:
    python get_token_holders.py <token_id> [--output file.json] [--url url] [--limit n] [--max n]
"""

import argparse
import requests
import json
import time
import sys
from datetime import datetime

def fetch_boxes(api_url, token_id, offset, limit):
    """Fetch boxes containing the token from the node API."""
    url = f"{api_url}/blockchain/box/byTokenId/{token_id}"
    params = {"offset": offset, "limit": limit}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching boxes at offset {offset}: {str(e)}")
        return {"items": []}

def fetch_block_timestamp(api_url, height):
    """Fetch the timestamp for a given block height."""
    try:
        url = f"{api_url}/blocks/at/{height}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:
            return data[0].get("timestamp")
    except Exception as e:
        print(f"Warning: Could not fetch timestamp for height {height}: {str(e)}")
    return None

def get_token_holders(api_url, token_id, max_boxes=200, batch_size=50):
    """
    Analyze boxes to determine token holder distribution and transfer history.
    
    Args:
        api_url: Base URL for the Ergo node API
        token_id: ID of the token to analyze
        max_boxes: Maximum number of boxes to process
        batch_size: Number of boxes to fetch in each batch
        
    Returns:
        Dictionary containing holder data and transfer history
    """
    # We'll track address to height mapping for holder analysis
    address_to_height = {}
    current_offset = 0
    processed_boxes = 0
    transfers = []
    height_to_timestamp = {}
    
    # Process boxes in batches
    while processed_boxes < max_boxes:
        print(f"Fetching boxes at offset {current_offset}...")
        data = fetch_boxes(api_url, token_id, current_offset, batch_size)
        
        items = data.get("items", [])
        if not items:
            print("No more boxes found.")
            break
        
        print(f"Processing {len(items)} boxes...")
        
        # Process this batch of boxes
        for item in items:
            address = item.get("address")
            height = item.get("inclusionHeight")
            box_id = item.get("boxId")
            value = item.get("value", 0)
            spent_tx_id = item.get("spentTransactionId")
            
            # Get token amount
            token_amount = 0
            for asset in item.get("assets", []):
                if asset.get("tokenId") == token_id:
                    token_amount = asset.get("amount", 0)
                    break
            
            # Add to transfer history
            transfers.append({
                "boxId": box_id,
                "address": address,
                "inclusionHeight": height,
                "spentTransactionId": spent_tx_id,
                "value": value,
                "tokenAmount": token_amount
            })
            
            # Update address to height mapping
            if address:
                # Store the latest blockheight for each address
                if address not in address_to_height or height > address_to_height[address]["height"]:
                    address_to_height[address] = {
                        "height": height,
                        "amount": token_amount
                    }
        
        # Update for next iteration
        processed_boxes += len(items)
        if len(items) < batch_size:
            print("Reached the last page of results.")
            break
            
        current_offset += batch_size
        time.sleep(0.1)  # Small delay to avoid hammering the API
    
    # Fetch timestamps for the most recent boxes (limit to 20 to avoid too many requests)
    print("Fetching block timestamps...")
    recent_heights = sorted(list(set(item["inclusionHeight"] for item in transfers[-20:])))
    for height in recent_heights:
        timestamp = fetch_block_timestamp(api_url, height)
        if timestamp:
            height_to_timestamp[height] = timestamp
    
    # Add timestamps to transfers and holders
    for transfer in transfers:
        height = transfer.get("inclusionHeight")
        if height in height_to_timestamp:
            transfer["timestamp"] = height_to_timestamp[height]
    
    # Calculate distribution metrics
    holder_count = len(address_to_height)
    print(f"Found {holder_count} unique token holders")
    
    # Convert address_to_height to a sorted list of holders
    holders = [
        {
            "address": address, 
            "lastHeight": data["height"], 
            "amount": data["amount"],
            "timestamp": height_to_timestamp.get(data["height"])
        } 
        for address, data in address_to_height.items()
    ]
    
    # Sort by token amount (descending)
    holders.sort(key=lambda x: x["amount"], reverse=True)
    
    # Calculate simple Gini coefficient if we have enough holders
    gini = 0
    if holder_count > 1:
        amounts = [holder["amount"] for holder in holders]
        total = sum(amounts)
        if total > 0:
            # Calculate Gini coefficient (measure of concentration)
            n = len(amounts)
            s1 = 0
            for i, xi in enumerate(sorted(amounts)):
                s1 += xi * (n - i)
            gini = 1 - 2 * (s1 / (n * sum(amounts)))
            print(f"Gini coefficient (concentration measure): {gini:.4f}")
    
    # Prepare response object
    return {
        "tokenId": token_id,
        "holderCount": holder_count,
        "holders": holders,
        "concentration": {
            "gini": gini,
            "top10Percent": sum(h["amount"] for h in holders[:max(1, holder_count // 10)]) / sum(h["amount"] for h in holders) if holders else 0
        },
        "transfers": transfers,
        "processedBoxes": processed_boxes,
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Analyze token holder distribution and history")
    parser.add_argument("token_id", help="Token ID to analyze")
    parser.add_argument("--output", default="token_holders.json", help="Output JSON file name")
    parser.add_argument("--url", default="http://localhost:9053", help="Ergo node API URL")
    parser.add_argument("--max", type=int, default=200, help="Maximum number of boxes to process")
    parser.add_argument("--batch", type=int, default=50, help="Number of boxes to fetch in each batch")
    args = parser.parse_args()
    
    print(f"Analyzing token: {args.token_id}")
    print(f"Using node API at: {args.url}")
    
    # Get token holder data
    result = get_token_holders(args.url, args.token_id, args.max, args.batch)
    
    # Save to file
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Analysis complete. Results saved to {args.output}")
    print(f"Found {result['holderCount']} unique token holders")
    print(f"Processed {result['processedBoxes']} boxes")
    
    # Display top 5 holders
    if result["holders"]:
        print("\nTop Token Holders:")
        for i, holder in enumerate(result["holders"][:5], 1):
            print(f"{i}. {holder['address']}: {holder['amount']} tokens (last seen at height {holder['lastHeight']})")

if __name__ == "__main__":
    main() 