#!/usr/bin/env python

import asyncio
import logging
import time
import json
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Import the collection analysis functions
from ergo_explorer.tools.token_holders import (
    get_collection_metadata, 
    get_collection_nfts,
    get_collection_holders,
    get_token_by_id,
    get_box_by_id,
    clear_cache,
    get_cache_stats
)

# Collection IDs to test
COLLECTIONS = {
    "shark": "4b0446611cd32c1412d962ba94ce5ef803ad6b3d543f7d5a0880cb63e97a338a",  # Smaller collection
    "cybercitizen": "5229337902454a79c1ff2f9ae2206568e0d46dba1a7df6992c399670b7943e3e"  # Larger collection
}

async def benchmark(func, *args, **kwargs):
    """Measure execution time of an async function."""
    start_time = time.time()
    result = await func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time

async def test_collection_performance(collection_name: str, collection_id: str, with_cache: bool = True):
    """Test performance of different aspects of collection analysis."""
    print(f"\n\n=== PERFORMANCE TEST: {collection_name.upper()} ===")
    
    # Clear cache if not using it
    if not with_cache:
        clear_cache()
        print("Cache cleared for clean test")
    
    # Test 1: Collection Metadata Performance
    print(f"\n[1/3] Testing collection metadata performance...")
    metadata, metadata_time = await benchmark(get_collection_metadata, collection_id)
    print(f"Collection metadata retrieval time: {metadata_time:.4f} seconds")
    
    # Test 2: NFT Discovery Performance
    print(f"\n[2/3] Testing NFT discovery performance...")
    # First run - should be slower without cache
    nfts_first, nfts_first_time = await benchmark(get_collection_nfts, collection_id, 100, with_cache)
    print(f"First run NFT discovery time: {nfts_first_time:.4f} seconds (found {len(nfts_first)} NFTs)")
    
    # Second run - should be faster with cache if enabled
    nfts_second, nfts_second_time = await benchmark(get_collection_nfts, collection_id, 100, with_cache)
    print(f"Second run NFT discovery time: {nfts_second_time:.4f} seconds (found {len(nfts_second)} NFTs)")
    
    cache_speedup = (nfts_first_time / nfts_second_time) if nfts_second_time > 0 else 0
    print(f"Cache speedup factor: {cache_speedup:.2f}x")
    
    # Test 3: Holder Analysis Performance with batch processing
    print(f"\n[3/3] Testing holder analysis performance...")
    
    # Test with different batch sizes
    batch_sizes = [5, 10, 20]
    holder_times = []
    
    for batch_size in batch_sizes:
        # If not using cache, clear it before each test
        if not with_cache:
            clear_cache()
            
        print(f"\nTesting with batch size: {batch_size}")
        holder_result, holder_time = await benchmark(
            get_collection_holders, 
            collection_id, 
            include_raw=True, 
            include_analysis=False,
            use_cache=with_cache,
            batch_size=batch_size
        )
        holder_times.append(holder_time)
        print(f"Holder analysis time: {holder_time:.4f} seconds")
        
        if "error" not in holder_result:
            total_nfts = len(await get_collection_nfts(collection_id, 1000, with_cache))
            total_holders = len(holder_result.get("holders", []))
            print(f"Analysis results: {total_nfts} NFTs, {total_holders} unique holders")
        else:
            print(f"Error: {holder_result.get('error')}")
    
    # Show cache statistics
    if with_cache:
        print(f"\nCache statistics after tests:")
        cache_stats = get_cache_stats()
        for cache_type, count in cache_stats.items():
            print(f"- {cache_type}: {count} items")
    
    # Return performance metrics
    return {
        "collection_id": collection_id,
        "name": metadata.get("token_name", "Unknown"),
        "metadata_time": metadata_time,
        "nfts_first_time": nfts_first_time,
        "nfts_second_time": nfts_second_time,
        "cache_speedup": cache_speedup,
        "holder_times": holder_times,
        "batch_sizes": batch_sizes,
        "with_cache": with_cache
    }

async def main():
    print("⚡ Starting performance benchmark tests for NFT collection analysis...\n")
    
    results = []
    
    # Test each collection with and without cache
    for name, collection_id in COLLECTIONS.items():
        # Test with cache
        with_cache_result = await test_collection_performance(name, collection_id, with_cache=True)
        results.append(with_cache_result)
        
        # Test without cache for comparison
        without_cache_result = await test_collection_performance(name, collection_id, with_cache=False)
        results.append(without_cache_result)
    
    # Print summary
    print("\n\n=== PERFORMANCE TEST SUMMARY ===")
    print("| Collection | Cache | Metadata Time | NFT Discovery | Holder Analysis | Cache Speedup |")
    print("|------------|-------|---------------|---------------|-----------------|---------------|")
    
    for result in results:
        cache_status = "✅" if result["with_cache"] else "❌"
        # Use the middle batch size for comparison
        middle_batch_index = len(result["batch_sizes"]) // 2
        holder_time = result["holder_times"][middle_batch_index]
        
        print(f"| {result['name']} | {cache_status} | {result['metadata_time']:.4f}s | {result['nfts_first_time']:.4f}s | {holder_time:.4f}s | {result['cache_speedup']:.2f}x |")
    
    print("\n🎯 Benchmark tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 