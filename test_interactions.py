import asyncio
import json
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Import the function directly from the module rather than through __init__
from ergo_explorer.tools.address import get_common_interactions

async def main():
    address = '9gUDVVx75KyZ783YLECKngb1wy8KVwEfk3byjdfjUyDVAELAPUN'
    print(f"Analyzing interactions for address: {address}")
    
    try:
        # Call the function directly
        result = await get_common_interactions(address, limit=20)
        
        # Pretty print the result
        # Convert to dictionary first if it's a custom object
        if hasattr(result, 'to_dict'):
            result_dict = result.to_dict()
        else:
            result_dict = result
            
        print(json.dumps(result_dict, indent=2, default=str))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 