"""
Integration tests for the address clustering functionality.

These tests validate the end-to-end functionality of the address clustering
feature using real Ergo blockchain addresses.
"""

import asyncio
import json
import logging
import sys
import time
from pprint import pprint

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))

# Import the entity identification functions
from ergo_explorer.tools.entity_identification import identify_entities_json, identify_entities

# Known addresses with clusters for testing
# These addresses have known transaction relationships
TEST_ADDRESSES = [
    # Active address with many transactions
    "9iMWaVQbnKUxQei1yT9gVaP7TbVnRz9U68tXjZGZWXB8Wc3U3Md",
    
    # Address from SigUSD bank contract
    "2k6J5ocjeESe4cuNH5MfgpV4vcXLUvYmNrPDAN4GgDAKKXs1wR4sfpHJPJUnQzGKr4d6JrDMxVhUQCMWkBnGqsxVs6CdkeBV4PQWpd2M4Vej2KvwgvKgxmDfZ1H4WsBnfR2UwKY99vbBvsHTaXzRBAbTuyxfKNGJsUDkq6QeK1mYu9ATwNFi7YPBJ7T1mRae2pjctCZ5oGDmQnMgxYmbKR2C3hahR8z62MhaUqbCgTTdop8M1N8VPMX1fvfLaP8L4swFNv1sTndpeHB64ZgGxhyLhTxjfuU6QkFVbbQMKAcHQaZuKRgVkJfK15zRMY9xz7BRYTEh8qZG7bwELuKWRdZJwJvejaG5s1xP3cWyivsy2WvSNRYNcZLwn2j14kZ9dzcnmCdCJfzeFmUkJVk58QS4gX32T6cAAGmnZ5QWMekwVAA",
    
    # Exchange-related address
    "9fowPvQ8xscVYkY3VRLNAkFgHVnGZKpQsXEMkQAXttRGqFcDX5c",
    
    # Mining pool address
    "9iN1j7v3zDMHkGP8RKgpXVpQMeK1gy6zDQbiT9N7SWxmPXs1DSt"
]

async def test_entity_identification(address):
    """Test entity identification for a specific address and print results."""
    logger.info(f"Testing entity identification for address: {address}")
    
    start_time = time.time()
    
    try:
        # Use optimized parameters for testing
        result_json = await identify_entities_json(
            address,
            depth=1,           # Lower depth for faster testing
            tx_limit=50,       # Reasonable number of transactions
            concurrency_limit=5,
            memory_limit_mb=512,
            batch_size=10,
            transactions_per_batch=20
        )
        
        # Parse the result
        result = json.loads(result_json)
        
        # Print basic results
        logger.info(f"Entity identification completed in {time.time() - start_time:.2f} seconds")
        logger.info(f"Found {result.get('total_addresses', 0)} addresses in {len(result.get('clusters', {}))} clusters")
        
        # Validate the result structure
        assert "seed_address" in result, "Missing seed_address in result"
        assert "seed_cluster_id" in result, "Missing seed_cluster_id in result"
        assert "addresses" in result, "Missing addresses in result"
        assert "clusters" in result, "Missing clusters in result"
        assert "relationships" in result, "Missing relationships in result"
        
        # Make sure the seed address is in the result
        assert address in result["addresses"], "Seed address not found in addresses list"
        
        # Check if we found any clusters
        if len(result.get("clusters", {})) <= 1:
            logger.warning(f"Only found {len(result.get('clusters', {}))} clusters, expected more")
        
        # Check if we found any relationships
        if len(result.get("relationships", [])) == 0:
            logger.warning("No relationships found, expected some")
        else:
            logger.info(f"Found {len(result.get('relationships', []))} relationships")
            
        # Check that seed address has a cluster assigned
        assert result["seed_cluster_id"] is not None, "Seed address has no cluster assigned"
        
        # Verify the cluster exists in the clusters list
        seed_cluster_id = result["seed_cluster_id"]
        assert seed_cluster_id in result["clusters"], f"Seed cluster {seed_cluster_id} not found in clusters list"
        
        # Check that the cluster contains the seed address
        if seed_cluster_id in result["clusters"]:
            # Get cluster addresses
            cluster_addresses = result["clusters"][seed_cluster_id]
            assert address in cluster_addresses, "Seed address not found in its assigned cluster"
            
            # Check if the cluster has multiple addresses
            if len(cluster_addresses) > 1:
                logger.info(f"Seed address cluster contains {len(cluster_addresses)} addresses")
            else:
                logger.warning("Seed address cluster only contains the seed address")
        
        # Check performance metrics
        performance = result.get("performance", {})
        logger.info(f"Performance metrics: {json.dumps(performance, indent=2)}")
        
        # Verify all required performance metrics are present
        assert "total_time_ms" in performance, "Missing total_time_ms in performance metrics"
        assert "memory_usage_mb" in performance, "Missing memory_usage_mb in performance metrics"
        
        return True, result
        
    except Exception as e:
        logger.error(f"Error testing entity identification: {e}")
        import traceback
        traceback.print_exc()
        return False, None

async def run_integration_tests():
    """Run integration tests for all test addresses."""
    logger.info("Starting address clustering integration tests")
    results = {}
    success_count = 0
    
    for address in TEST_ADDRESSES:
        success, result = await test_entity_identification(address)
        results[address] = {
            "success": success,
            "clusters_found": len(result.get("clusters", {})) if result else 0,
            "addresses_found": len(result.get("addresses", [])) if result else 0,
            "relationships_found": len(result.get("relationships", [])) if result else 0
        }
        
        if success:
            success_count += 1
    
    # Print summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"Total test addresses: {len(TEST_ADDRESSES)}")
    logger.info(f"Successful tests: {success_count}")
    logger.info(f"Failed tests: {len(TEST_ADDRESSES) - success_count}")
    
    for address, result in results.items():
        status = "✅ Passed" if result["success"] else "❌ Failed"
        logger.info(f"{status} - {address}: {result['clusters_found']} clusters, {result['addresses_found']} addresses, {result['relationships_found']} relationships")
    
    # Return overall success status
    return success_count == len(TEST_ADDRESSES)

if __name__ == "__main__":
    # Run all tests
    if asyncio.run(run_integration_tests()):
        logger.info("✅ All address clustering integration tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some address clustering integration tests failed!")
        sys.exit(1) 