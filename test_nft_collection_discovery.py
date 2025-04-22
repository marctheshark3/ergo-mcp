"""
Test for NFT collection discovery without hardcoded collections

This script tests the get_collection_nfts function in the collections module to ensure it
can dynamically discover NFTs in a collection without relying on hardcoded values.
"""

import asyncio
import time
import sys
import os
from typing import List

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ergo_explorer.tools.token_holders.collections import get_collection_nfts, get_collection_metadata, get_token_by_id

# Test collection - Ergo Botz Collection
TEST_COLLECTION_ID = "4b0446611cd32c1412d962ba94ce5ef803ad6b3d543f7d5a0880cb63e97a338a"
# Another test collection - any other known collection
ALT_COLLECTION_ID = "d71693c49a84fbbecd4908c94813b46514b18b67a99952dc1e6e4791556de413"

async def test_collection_discovery():
    """Test NFT collection discovery without hardcoded values"""
    print(f"\n--- Testing NFT collection discovery for {TEST_COLLECTION_ID[:8]}...{TEST_COLLECTION_ID[-8:]} ---")
    
    # Get collection metadata
    print("\n1. Getting collection metadata...")
    metadata = await get_collection_metadata(TEST_COLLECTION_ID)
    if "error" in metadata:
        print(f"❌ Error getting collection metadata: {metadata.get('error')}")
        return False
    
    print(f"✅ Collection name: {metadata.get('token_name', 'Unknown')}")
    print(f"Description: {metadata.get('token_description', 'No description')}")
    
    # Test NFT discovery with our modified function
    print("\n2. Testing NFT discovery...")
    start_time = time.time()
    nfts = await get_collection_nfts(TEST_COLLECTION_ID, limit=20)
    discovery_time = time.time() - start_time
    
    print(f"✅ Discovered {len(nfts)} NFTs in {discovery_time:.2f} seconds")
    
    if not nfts:
        print("❌ No NFTs discovered for this collection")
        return False
    
    # Print details of discovered NFTs
    print("\n3. NFT details:")
    for i, nft_id in enumerate(nfts[:5], 1):  # Show first 5 NFTs
        token_info = await get_token_by_id(nft_id)
        if "error" not in token_info:
            name = token_info.get("name", "Unknown")
            print(f"{i}. {nft_id[:8]}...{nft_id[-8:]} - {name}")
        else:
            print(f"{i}. {nft_id[:8]}...{nft_id[-8:]} - Error: {token_info.get('error')}")
    
    # Test with another collection for comparison
    if ALT_COLLECTION_ID:
        print(f"\n--- Testing with alternative collection {ALT_COLLECTION_ID[:8]}...{ALT_COLLECTION_ID[-8:]} ---")
        alt_metadata = await get_collection_metadata(ALT_COLLECTION_ID)
        if "error" not in alt_metadata:
            print(f"✅ Alternative collection name: {alt_metadata.get('token_name', 'Unknown')}")
            
            start_time = time.time()
            alt_nfts = await get_collection_nfts(ALT_COLLECTION_ID, limit=20)
            alt_discovery_time = time.time() - start_time
            
            print(f"✅ Discovered {len(alt_nfts)} NFTs in {alt_discovery_time:.2f} seconds")
            
            if alt_nfts:
                print("\nAlternative collection NFT examples:")
                for i, nft_id in enumerate(alt_nfts[:3], 1):  # Show first 3 NFTs
                    token_info = await get_token_by_id(nft_id)
                    if "error" not in token_info:
                        name = token_info.get("name", "Unknown")
                        print(f"{i}. {nft_id[:8]}...{nft_id[-8:]} - {name}")
        else:
            print(f"❌ Could not get alternative collection: {alt_metadata.get('error')}")
    
    print("\n--- Test completed successfully ---")
    return True

async def main():
    try:
        await test_collection_discovery()
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 