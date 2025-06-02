import asyncio
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Import directly from the tools module
from ergo_explorer.tools.address import get_common_interactions

async def main():
    address = '9gUDVVx75KyZ783YLECKngb1wy8KVwEfk3byjdfjUyDVAELAPUN'
    
    print("Testing with verbose=False...")
    condensed_result = await get_common_interactions(
        address=address, 
        limit=2, 
        min_interactions=2, 
        verbose=False
    )
    
    print("Keys in the result object:")
    print(list(condensed_result.keys()))
    print("\nNumber of interactions:")
    print(len(condensed_result["common_interactions"]))
    print("\nKeys in the first interaction (condensed):")
    print(list(condensed_result["common_interactions"][0].keys()))
    print("\nKeys in statistics (condensed):")
    print(list(condensed_result["statistics"].keys()))
    
    print("\n" + "-"*80 + "\n")
    
    print("Testing with verbose=True...")
    verbose_result = await get_common_interactions(
        address=address, 
        limit=2, 
        min_interactions=2, 
        verbose=True
    )
    
    print("Keys in the result object:")
    print(list(verbose_result.keys()))
    print("\nNumber of interactions:")
    print(len(verbose_result["common_interactions"]))
    print("\nKeys in the first interaction (verbose):")
    print(list(verbose_result["common_interactions"][0].keys()))
    print("\nKeys in statistics (verbose):")
    print(list(verbose_result["statistics"].keys()))
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 