import asyncio
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

from ergo_explorer.api.routes.blockchain import blockchain_address_interactions
from ergo_explorer.api.routes.context import Context

async def main():
    address = '9gUDVVx75KyZ783YLECKngb1wy8KVwEfk3byjdfjUyDVAELAPUN'
    ctx = Context()
    
    print("Testing API with verbose=False...")
    condensed_result = await blockchain_address_interactions(
        ctx, 
        address=address, 
        limit=2, 
        min_interactions=2, 
        verbose=False
    )
    
    print("Keys in API result for condensed version:")
    print(list(condensed_result["result"].keys()))
    print("\nNumber of interactions in condensed version:")
    print(len(condensed_result["result"]["common_interactions"]))
    print("\nKeys in the first interaction (condensed):")
    print(list(condensed_result["result"]["common_interactions"][0].keys()))
    
    print("\n" + "-"*80 + "\n")
    
    print("Testing API with verbose=True...")
    verbose_result = await blockchain_address_interactions(
        ctx, 
        address=address, 
        limit=2, 
        min_interactions=2, 
        verbose=True
    )
    
    print("Keys in API result for verbose version:")
    print(list(verbose_result["result"].keys()))
    print("\nNumber of interactions in verbose version:")
    print(len(verbose_result["result"]["common_interactions"]))
    print("\nKeys in the first interaction (verbose):")
    print(list(verbose_result["result"]["common_interactions"][0].keys()))
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 