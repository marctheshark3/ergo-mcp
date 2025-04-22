"""
Test for NFT collection counting

This script tests that the modified get_collection_holders correctly counts
distinct NFTs rather than total copies.
"""

import asyncio
import time
import sys
import os
from typing import List, Dict

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ergo_explorer.tools.token_holders.collections import (
    get_collection_nfts, 
    get_collection_metadata, 
    get_token_by_id,
    process_nft_holders,
    get_collection_holders
)

# Test collection with a mix of unique and non-unique NFTs
TEST_COLLECTION_ID = "4b0446611cd32c1412d962ba94ce5ef803ad6b3d543f7d5a0880cb63e97a338a"

async def test_nft_counting_logic():
    """Test the NFT counting logic"""
    print("\n--- Testing Distinct NFT Counting Logic ---")
    
    # Get collection metadata
    print("\n1. Getting collection metadata...")
    metadata = await get_collection_metadata(TEST_COLLECTION_ID)
    if "error" in metadata:
        print(f"❌ Error getting collection metadata: {metadata.get('error')}")
        return False
    
    print(f"✅ Collection name: {metadata.get('token_name', 'Unknown')}")
    
    # Get the NFTs
    print("\n2. Getting collection NFTs...")
    nfts = await get_collection_nfts(TEST_COLLECTION_ID, limit=20)
    if not nfts:
        print("❌ No NFTs found")
        return False
    
    print(f"✅ Found {len(nfts)} NFTs")
    
    # Check uniqueness for each NFT
    print("\n3. Checking NFT uniqueness...")
    unique_count = 0
    non_unique_count = 0
    nft_supply_data = []
    
    for i, nft_id in enumerate(nfts[:10], 1):  # Test first 10 NFTs
        holder_data = await process_nft_holders(nft_id)
        if holder_data:
            is_unique = holder_data.get("is_unique", False)
            supply = holder_data.get("supply", 0)
            token_name = holder_data.get("token_name", "Unknown")
            
            if is_unique:
                unique_count += 1
                status = "✅ Unique"
            else:
                non_unique_count += 1
                status = "⚠️ Non-Unique"
                
            print(f"{i}. {nft_id[:8]}...{nft_id[-8:]} - {token_name}: {status} (Supply: {supply})")
            nft_supply_data.append({
                "id": nft_id,
                "name": token_name,
                "supply": supply,
                "is_unique": is_unique
            })
    
    print(f"\nSummary: {unique_count} unique NFTs, {non_unique_count} non-unique NFTs checked")
    
    # Test collection holder analysis
    print("\n4. Testing collection holder analysis...")
    holder_data = await get_collection_holders(TEST_COLLECTION_ID, include_raw=True)
    
    if isinstance(holder_data, dict) and "error" not in holder_data:
        total_distinct_nfts = holder_data.get("total_nfts", 0)
        total_holders = holder_data.get("total_holders", 0)
        
        print(f"✅ Collection has {total_distinct_nfts} distinct NFTs and {total_holders} holders")
        
        # Print top holders
        holders = holder_data.get("holders", [])
        print("\nTop 5 Holders:")
        
        for i, holder in enumerate(holders[:5], 1):
            address = holder.get("address", "Unknown")
            nft_count = holder.get("nft_count", 0)
            percentage = holder.get("percentage", 0)
            
            print(f"{i}. {address[:8]}...{address[-8:]} holds {nft_count} distinct NFTs ({percentage}%)")
            
        print("\n5. Getting formatted analysis...")
        formatted = await get_collection_holders(TEST_COLLECTION_ID, include_raw=False)
        if isinstance(formatted, str):
            print("\nFormatted Analysis Preview (first 500 chars):")
            print(formatted[:500] + "...\n")
        else:
            print(f"❌ Failed to get formatted analysis: {formatted}")
    else:
        print(f"❌ Error getting holder data: {holder_data.get('error') if isinstance(holder_data, dict) else holder_data}")
        return False
    
    print("\n--- Test completed successfully ---")
    return True

async def main():
    try:
        await test_nft_counting_logic()
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 