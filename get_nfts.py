#!/usr/bin/env python3
"""
Utility script to get a few NFTs from a collection.
"""

import asyncio
from ergo_explorer.tools.nft_analysis import get_collection_nfts
from ergo_explorer.logging_config import get_logger

# Configure logger
logger = get_logger("get_nfts")

async def get_nfts():
    """Get NFTs from the Shark collection."""
    collection_id = "4b0446611cd32c1412d962ba94ce5ef803ad6b3d543f7d5a0880cb63e97a338a"
    nfts = await get_collection_nfts(collection_id, limit=5)
    print(f"\nFirst 5 NFTs from collection {collection_id}:")
    for i, nft in enumerate(nfts, 1):
        print(f"{i}. {nft}")
    return nfts

if __name__ == "__main__":
    """Run the script."""
    asyncio.run(get_nfts()) 