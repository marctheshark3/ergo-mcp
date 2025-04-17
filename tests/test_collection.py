"""
Tests for NFT collection functionality.
"""

import asyncio
from ergo_explorer.logging_config import get_logger
from ergo_explorer.tools.token_holders import (
    get_collection_metadata,
    get_collection_nfts,
    get_collection_holders,
    search_collections
)

# Configure logger
logger = get_logger("test_collection")

# Test with the Ergo Botz collection as an example
COLLECTION_ID = "4b0446611cd32c1412d962ba94ce5ef803ad6b3d543f7d5a0880cb63e97a338a"  # Ergo Botz
EXPECTED_NFT = "28c8ec4b03a88fcdfa004f229de5cca14beca41fe266047ae0463f22da43c18b"  # Dark Ergo Botz #1

async def test_collection_metadata():
    """Test collection metadata retrieval."""
    try:
        logger.info(f"Testing collection metadata for {COLLECTION_ID}")
        metadata = await get_collection_metadata(COLLECTION_ID)
        
        assert "error" not in metadata, f"Error in metadata: {metadata.get('error')}"
        assert metadata.get("collection_id") == COLLECTION_ID, "Collection ID mismatch"
        assert "token_name" in metadata, "Missing token name"
        assert "token_description" in metadata, "Missing token description"
        
        logger.info(f"Collection Name: {metadata.get('token_name')}")
        logger.info(f"Description: {metadata.get('token_description')}")
        
        logger.info("Successfully retrieved collection metadata")
    except Exception as e:
        logger.error(f"Error in test_collection_metadata: {str(e)}")
        raise

async def test_expected_nft():
    """Test that our expected NFT is in the collection."""
    try:
        logger.info(f"Testing that NFT {EXPECTED_NFT} is in collection {COLLECTION_ID}")
        
        # Get NFT token info
        nft_tokens = await get_collection_nfts(COLLECTION_ID, limit=1000)
        
        assert EXPECTED_NFT in nft_tokens, f"Expected NFT {EXPECTED_NFT} not found in collection"
        logger.info(f"Successfully confirmed NFT {EXPECTED_NFT} is in collection")
    except Exception as e:
        logger.error(f"Error in test_expected_nft: {str(e)}")
        raise

async def test_collection_nfts():
    """Test NFT discovery in a collection."""
    try:
        logger.info(f"Testing NFT discovery for collection {COLLECTION_ID}")
        nft_tokens = await get_collection_nfts(COLLECTION_ID, limit=50)
        
        assert len(nft_tokens) > 0, "No NFTs found in collection"
        assert isinstance(nft_tokens, list), "Result should be a list"
        
        logger.info(f"Found {len(nft_tokens)} NFTs in collection")
        
        # Log the first 5 NFTs for inspection
        for i, nft_id in enumerate(nft_tokens[:5], 1):
            logger.info(f"NFT {i}: {nft_id}")
        
        logger.info("Successfully discovered NFTs in collection")
    except Exception as e:
        logger.error(f"Error in test_collection_nfts: {str(e)}")
        raise

async def test_collection_holders():
    """Test collection holder analysis functionality."""
    try:
        logger.info(f"Testing collection holders for {COLLECTION_ID}")
        analysis = await get_collection_holders(COLLECTION_ID, include_raw=False, include_analysis=True)
        
        print(f"\n{analysis}\n")
        
        assert isinstance(analysis, str), "Analysis should be a string"
        logger.info("Successfully retrieved and analyzed collection holders")
    except Exception as e:
        logger.error(f"Error in test_collection_holders: {str(e)}")
        raise

async def test_search_collections():
    """Test collection search functionality."""
    try:
        logger.info("Testing collection search with 'shark' query")
        # Test with a known collection name
        search_query = "shark"
        results = await search_collections(search_query, limit=5)
        
        assert isinstance(results, dict), "Results should be a dictionary"
        assert "items" in results, "Results should contain 'items' key"
        assert "total" in results, "Results should contain 'total' key"
        
        items = results.get("items", [])
        total = results.get("total", 0)
        
        logger.info(f"Found {total} collection(s) matching '{search_query}'")
        
        if items:
            for i, collection in enumerate(items, 1):
                logger.info(f"{i}. {collection.get('name')} (ID: {collection.get('collection_id')[:8]}...)")
        
        # Test with a specific collection ID
        logger.info(f"Testing collection search with known collection ID {COLLECTION_ID}")
        results_by_id = await search_collections(COLLECTION_ID, limit=1)
        
        assert isinstance(results_by_id, dict), "Results should be a dictionary"
        assert "items" in results_by_id, "Results should contain 'items' key"
        
        items_by_id = results_by_id.get("items", [])
        
        if items_by_id:
            found_collection = items_by_id[0]
            logger.info(f"Found collection: {found_collection.get('name')}")
            assert found_collection.get("collection_id") == COLLECTION_ID, "Should find the exact collection by ID"
        
        logger.info("Successfully tested collection search functionality")
    except Exception as e:
        logger.error(f"Error in test_search_collections: {str(e)}")
        raise

if __name__ == "__main__":
    """Run tests."""
    import asyncio
    
    logger.info("Running collection tests")
    
    asyncio.run(test_collection_metadata())
    asyncio.run(test_expected_nft())
    asyncio.run(test_collection_nfts())
    asyncio.run(test_collection_holders())
    asyncio.run(test_search_collections())
    
    logger.info("All tests completed") 