"""
Test for NFT collection holder analysis with no duplicate holders

This script tests the holder aggregation logic to ensure we're correctly counting
unique holders without duplications in the collection holder analysis.
"""

import asyncio
import sys
import os
from typing import List, Dict, Set

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ergo_explorer.tools.token_holders.collections import (
    get_collection_nfts, 
    get_collection_holders,
    process_nft_holders
)

# Test collection ID - Shark collection
TEST_COLLECTION_ID = "4b0446611cd32c1412d962ba94ce5ef803ad6b3d543f7d5a0880cb63e97a338a"

async def test_holder_uniqueness():
    """Test that holder analysis correctly handles unique holders"""
    print("\n--- Testing holder uniqueness in collection analysis ---")
    
    # Get NFTs in the collection
    print(f"Finding NFTs for collection {TEST_COLLECTION_ID[:8]}...{TEST_COLLECTION_ID[-8:]}")
    nfts = await get_collection_nfts(TEST_COLLECTION_ID, limit=10)
    
    if not nfts:
        print("❌ No NFTs found for this collection")
        return False
    
    print(f"✅ Found {len(nfts)} NFTs")
    
    # Check individual NFT holders
    print("\nChecking individual NFT holders:")
    nft_holders = {}  # Maps NFT IDs to sets of holder addresses
    all_addresses = set()  # All unique addresses across all NFTs
    
    for i, nft_id in enumerate(nfts[:5], 1):  # Check first 5 NFTs
        holder_data = await process_nft_holders(nft_id)
        if holder_data:
            holders = holder_data.get("holders", [])
            addresses = {h.get("address") for h in holders if h.get("address")}
            nft_holders[nft_id] = addresses
            all_addresses.update(addresses)
            
            print(f"{i}. NFT {nft_id[:8]}...{nft_id[-8:]} - {len(addresses)} unique holders")
            
            # Print first few holder addresses
            for j, addr in enumerate(list(addresses)[:3], 1):
                print(f"   {j}. {addr[:8]}...{addr[-8:]}")
    
    # Now check potential duplicates between NFTs
    print("\nChecking for holder overlaps between NFTs:")
    
    nft_ids = list(nft_holders.keys())
    for i in range(len(nft_ids)):
        for j in range(i+1, len(nft_ids)):
            nft1 = nft_ids[i]
            nft2 = nft_ids[j]
            
            holders1 = nft_holders[nft1]
            holders2 = nft_holders[nft2]
            
            overlap = holders1.intersection(holders2)
            
            if overlap:
                print(f"NFTs {nft1[:8]}...{nft1[-8:]} and {nft2[:8]}...{nft2[-8:]} share {len(overlap)} holder(s)")
            else:
                print(f"NFTs {nft1[:8]}...{nft1[-8:]} and {nft2[:8]}...{nft2[-8:]} have no holder overlap")
    
    # Get collection holder analysis
    print("\n--- Testing collection holder aggregation ---")
    holder_data = await get_collection_holders(TEST_COLLECTION_ID, include_raw=True)
    
    if isinstance(holder_data, dict) and "error" not in holder_data:
        total_nfts = holder_data.get("total_nfts", 0)
        total_holders = holder_data.get("total_holders", 0)
        holders = holder_data.get("holders", [])
        
        print(f"✅ Collection has {total_nfts} NFTs and {total_holders} unique holders")
        
        if len(all_addresses) != total_holders:
            print(f"⚠️ Warning: Manual count found {len(all_addresses)} unique holders vs. {total_holders} from aggregation")
        
        # Verify each holder's NFT count
        print("\nVerifying no duplicate counts for top holders:")
        
        for i, holder in enumerate(holders[:5], 1):
            addr = holder.get("address", "")
            nft_count = holder.get("nft_count", 0)
            nfts_held = holder.get("nfts_held", [])
            
            if len(nfts_held) != nft_count:
                print(f"❌ Holder {addr[:8]}...{addr[-8:]} shows inconsistency: count={nft_count}, actual NFTs={len(nfts_held)}")
            else:
                print(f"✅ Holder {addr[:8]}...{addr[-8:]} holds {nft_count} unique NFTs")
        
        # Get formatted analysis for display
        print("\n--- Getting formatted analysis ---")
        formatted = await get_collection_holders(TEST_COLLECTION_ID, include_raw=False)
        
        if isinstance(formatted, str):
            print("\nFormatted analysis preview:")
            print(formatted.split("\n\n")[0] + "\n")  # Show first section
        else:
            print(f"❌ Error getting formatted analysis: {formatted}")
    else:
        error = holder_data.get("error") if isinstance(holder_data, dict) else str(holder_data)
        print(f"❌ Error getting holder data: {error}")
        return False
    
    return True

async def main():
    try:
        print("\n===== TESTING COLLECTION HOLDER ANALYSIS =====")
        await test_holder_uniqueness()
        print("\n===== TEST COMPLETED =====")
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 