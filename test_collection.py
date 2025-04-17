#!/usr/bin/env python3
"""
Test script for collection analysis
"""

import asyncio
import json
import logging
from ergo_explorer.tools.token_holders import get_collection_metadata, get_collection_nfts, get_collection_holders, get_box_by_id, get_token_by_id

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Get logger
logger = logging.getLogger(__name__)

# Sample collection ID (Shark collection)
COLLECTION_ID = "4b0446611cd32c1412d962ba94ce5ef803ad6b3d543f7d5a0880cb63e97a338a"
# Let's use a known valid NFT ID from the collection
EXPECTED_NFT_ID = "28c8ec4b03a88fcdfa004f229de5cca14beca41fe266047ae0463f22da43c18b"  # Dark Ergo Botz #1

async def main():
    print("\n🔍 Starting collection analysis tests...\n")
    try:
        # Test 1: Get collection metadata
        print("[1/4] Testing collection metadata...")
        logger.info(f"Testing get_collection_metadata for {COLLECTION_ID[:8]}...{COLLECTION_ID[-8:]}")
        metadata = await get_collection_metadata(COLLECTION_ID)
        print("\n=== COLLECTION METADATA ===")
        print(json.dumps(metadata, indent=2))

        # Test 2: Test specific NFT
        print("\n[2/4] Testing specific NFT...")
        logger.info(f"Testing NFT {EXPECTED_NFT_ID[:8]}...{EXPECTED_NFT_ID[-8:]}")
        
        # Get NFT box
        nft_box = await get_box_by_id(EXPECTED_NFT_ID)
        # Debug print the response type and structure
        print(f"\nBox API Response Type: {type(nft_box)}")
        print(f"Box API Response: {nft_box}")
        
        # Handle the response appropriately
        if isinstance(nft_box, dict) and "error" not in nft_box:
            has_collection = False
            for asset in nft_box.get("assets", []):
                if asset.get("tokenId") == COLLECTION_ID:
                    has_collection = True
                    break
                    
            # Check R7 register for collection references
            additional_registers = nft_box.get("additionalRegisters", {})
            r7_has_collection = False
            if "R7" in additional_registers:
                r7_data = additional_registers["R7"]
                if isinstance(r7_data, dict):
                    r7_value = r7_data.get("serializedValue", "") + r7_data.get("renderedValue", "")
                    if COLLECTION_ID in r7_value:
                        r7_has_collection = True
            
            print("\n=== SPECIFIC NFT BOX ===")
            print(f"Box contains collection token: {has_collection}")
            print(f"R7 register contains collection ID: {r7_has_collection}")
        else:
            print("\n=== SPECIFIC NFT BOX ===")
            print(f"Error getting box: {nft_box}")
            print("Skipping box analysis")
            
        # Get token info
        nft_token = await get_token_by_id(EXPECTED_NFT_ID)
        # Debug print the response type and structure
        print(f"\nToken API Response Type: {type(nft_token)}")
        print(f"Token API Response: {nft_token}")
        
        # Handle token response
        if isinstance(nft_token, dict) and "error" not in nft_token:
            print(f"Token Name: {nft_token.get('name', 'Unknown')}")
            print(f"Token Description: {nft_token.get('description', 'No description')}")
        else:
            print(f"Error getting token: {nft_token}")

        # Test 3: Get all NFTs in the collection
        print("\n[3/4] Testing NFT discovery...")
        logger.info(f"Testing get_collection_nfts for {COLLECTION_ID[:8]}...{COLLECTION_ID[-8:]}")
        nfts = await get_collection_nfts(COLLECTION_ID)
        
        print(f"\n=== COLLECTION NFTs ({len(nfts)}) ===")
        # Check if expected NFT is in the list
        if EXPECTED_NFT_ID in nfts:
            print(f"✅ Expected NFT {EXPECTED_NFT_ID[:8]}...{EXPECTED_NFT_ID[-8:]} found in the collection")
        else:
            print(f"❌ Expected NFT {EXPECTED_NFT_ID[:8]}...{EXPECTED_NFT_ID[-8:]} was NOT found in the collection")
            
        # Print first few NFTs
        for i, nft_id in enumerate(nfts[:10], 1):  # Limit to 10 for brevity
            token_info = await get_token_by_id(nft_id)
            if isinstance(token_info, dict) and "error" not in token_info:
                name = token_info.get("name", "Unknown")
                print(f"{i}. {nft_id[:8]}...{nft_id[-8:]} - {name}")
            else:
                print(f"{i}. {nft_id[:8]}...{nft_id[-8:]} - Error fetching token info")

        # Test 4: Get holder analysis
        print("\n[4/4] Testing holder analysis...")
        logger.info(f"Testing get_collection_holders for {COLLECTION_ID[:8]}...{COLLECTION_ID[-8:]}")
        
        # Get formatted analysis
        analysis = await get_collection_holders(COLLECTION_ID, include_raw=False, include_analysis=True)
        print("\n=== COLLECTION HOLDER ANALYSIS ===")
        print(f"Analysis type: {type(analysis)}")
        print(analysis)
        
        # Get raw data for statistics
        raw_data = await get_collection_holders(COLLECTION_ID, include_raw=True, include_analysis=False)
        print("\n=== RAW HOLDER DATA STATISTICS ===")
        print(f"Raw data type: {type(raw_data)}")
        
        if isinstance(raw_data, dict):
            print(f"Total holders: {raw_data.get('total_holders', 0)}")
            print(f"Total NFTs: {raw_data.get('total_nfts', 0)}")
            holders = raw_data.get('holders', [])
            if holders:
                print(f"Top holder: {holders[0].get('address', 'Unknown')} with {holders[0].get('nft_count', 0)} NFTs")
            else:
                print("No holders data available")
        else:
            print(f"Raw data is not a dictionary: {raw_data}")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"❌ Test failed: {str(e)}")
        # Print more detailed exception info
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 