"""
Test for NFT collection discovery using the R7 register pattern

This script tests the correct NFT collection discovery mechanism by looking for
the 0e20<tokenid> pattern in the R7 register of boxes containing the collection token.
"""

import asyncio
import sys
import os
from typing import List, Dict

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ergo_explorer.tools.token_holders.collections import (
    get_collection_nfts, 
    get_collection_metadata, 
    get_token_by_id
)
from ergo_explorer.tools.token_holders.boxes import (
    get_boxes_by_token_id,
    get_box_by_id
)

# Test collection ID - Shark collection
TEST_COLLECTION_ID = "4b0446611cd32c1412d962ba94ce5ef803ad6b3d543f7d5a0880cb63e97a338a"

# Expected NFTs that should be part of the collection based on manual inspection
EXPECTED_NFTS = [
    "28c8ec4b03a88fcdfa004f229de5cca14beca41fe266047ae0463f22da43c18b",  # Should be found
    "43e8803ca559976ad631d69807311f5476daaa1271efcbdfb4695e5ee0d8856e"   # Should be found
]

async def test_manual_box_inspection():
    """Test R7 register inspection manually to verify our understanding"""
    print("\n--- Testing manual R7 pattern inspection ---")
    
    # Get boxes containing the collection token
    print(f"Fetching boxes containing collection token {TEST_COLLECTION_ID[:8]}...{TEST_COLLECTION_ID[-8:]}")
    boxes = await get_boxes_by_token_id(TEST_COLLECTION_ID, 0, 10)
    
    if not boxes:
        print("❌ No boxes found for this collection token")
        return False
    
    print(f"✅ Found {len(boxes)} boxes containing the collection token")
    
    # Look for the R7 pattern in each box
    found_nfts = []
    pattern = f"0e20{TEST_COLLECTION_ID}"
    
    for i, box in enumerate(boxes[:5], 1):  # Analyze first 5 boxes
        box_id = box.get("boxId")
        additionalRegisters = box.get("additionalRegisters", {})
        
        print(f"\nBox {i}: {box_id[:8]}...{box_id[-8:]}")
        
        if "R7" in additionalRegisters:
            r7_data = additionalRegisters["R7"]
            r7_value = None
            
            if isinstance(r7_data, str):
                r7_value = r7_data
            elif isinstance(r7_data, dict):
                r7_value = r7_data.get("serializedValue", r7_data.get("renderedValue", ""))
                
            print(f"  R7: {r7_value}")
            
            if r7_value and pattern in r7_value:
                print(f"  ✅ Pattern match! Box ID {box_id} is an NFT in the collection")
                found_nfts.append(box_id)
                
                # Check if it's a valid token
                token_info = await get_token_by_id(box_id)
                if "error" not in token_info:
                    print(f"  ✅ Box ID is a valid token: {token_info.get('name', 'Unnamed')}")
                else:
                    print(f"  ❌ Box ID is not a valid token")
            else:
                print(f"  ❌ No pattern match in R7")
        else:
            print(f"  ❌ No R7 register found")
    
    return found_nfts

async def test_collection_discovery():
    """Test the collection discovery function"""
    print("\n--- Testing collection NFT discovery ---")
    
    # Get NFTs using our updated get_collection_nfts function
    print(f"Discovering NFTs for collection {TEST_COLLECTION_ID[:8]}...{TEST_COLLECTION_ID[-8:]}")
    start_time = asyncio.get_event_loop().time()
    nfts = await get_collection_nfts(TEST_COLLECTION_ID, limit=20, use_cache=False)
    elapsed = asyncio.get_event_loop().time() - start_time
    
    if not nfts:
        print("❌ No NFTs found for this collection")
        return False
    
    print(f"✅ Found {len(nfts)} NFTs in {elapsed:.2f} seconds")
    
    # Check if expected NFTs were found
    expected_found = [nft for nft in EXPECTED_NFTS if nft in nfts]
    print(f"Found {len(expected_found)}/{len(EXPECTED_NFTS)} expected NFTs")
    
    for nft_id in expected_found:
        print(f"✅ Found expected NFT: {nft_id[:8]}...{nft_id[-8:]}")
    
    for nft_id in set(EXPECTED_NFTS) - set(expected_found):
        print(f"❌ Missing expected NFT: {nft_id[:8]}...{nft_id[-8:]}")
    
    # Show details of all discovered NFTs
    print("\nDiscovered NFTs:")
    for i, nft_id in enumerate(nfts[:10], 1):  # Show first 10 NFTs
        token_info = await get_token_by_id(nft_id)
        name = token_info.get("name", "Unnamed") if "error" not in token_info else "Invalid Token"
        print(f"{i}. {nft_id[:8]}...{nft_id[-8:]} - {name}")
    
    return nfts

async def main():
    try:
        print("\n===== TESTING NFT COLLECTION DISCOVERY =====")
        
        # First do manual inspection to verify our understanding
        found_nfts = await test_manual_box_inspection()
        
        # Then test the automated discovery function
        discovered_nfts = await test_collection_discovery()
        
        # Validate the results
        if found_nfts and discovered_nfts:
            manual_set = set(found_nfts)
            auto_set = set(discovered_nfts)
            overlap = manual_set.intersection(auto_set)
            
            print("\n--- Validation Results ---")
            print(f"Manual inspection found {len(found_nfts)} NFTs")
            print(f"Automated discovery found {len(discovered_nfts)} NFTs")
            print(f"Overlap between methods: {len(overlap)} NFTs")
            
            if manual_set.issubset(auto_set):
                print("✅ All manually found NFTs were also discovered by the automated method")
            else:
                print("❌ Some manually found NFTs were missed by the automated method")
                
        print("\n===== TEST COMPLETED =====")
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 