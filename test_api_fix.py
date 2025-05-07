import asyncio
import json
import logging
import sys
from mcp.server.fastmcp import Context, FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))

# Import our routes module
from ergo_explorer.api.routes.blockchain import register_blockchain_routes

class TestMCP(FastMCP):
    def __init__(self):
        self.tools = {}
        
    def tool(self):
        def wrapper(func):
            name = func.__name__
            self.tools[name] = func
            return func
        return wrapper
    
    async def call_tool(self, name, **kwargs):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        return await self.tools[name](Context(), **kwargs)

async def main():
    # Register routes with our test MCP
    mcp = TestMCP()
    register_blockchain_routes(mcp)
    
    # Test address to analyze
    address = '9gUDVVx75KyZ783YLECKngb1wy8KVwEfk3byjdfjUyDVAELAPUN'
    
    print("\n=== Testing with verbose=False ===\n")
    try:
        result = await mcp.call_tool(
            "blockchain_address_interactions",
            address=address,
            limit=2,
            min_interactions=2,
            verbose=False
        )
        
        print(f"Request successful - Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Keys in result: {list(result['result'].keys())}")
            print(f"Number of interactions: {len(result['result']['common_interactions'])}")
            print(f"Keys in first interaction: {list(result['result']['common_interactions'][0].keys())}")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Exception calling API: {str(e)}")
    
    print("\n=== Testing with verbose=True ===\n")
    try:
        result = await mcp.call_tool(
            "blockchain_address_interactions",
            address=address,
            limit=2,
            min_interactions=2,
            verbose=True
        )
        
        print(f"Request successful - Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Keys in result: {list(result['result'].keys())}")
            print(f"Number of interactions: {len(result['result']['common_interactions'])}")
            print(f"Keys in first interaction: {list(result['result']['common_interactions'][0].keys())}")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Exception calling API: {str(e)}")
    
    print("\n=== Testing with verbose as string 'false' ===\n")
    try:
        result = await mcp.call_tool(
            "blockchain_address_interactions",
            address=address,
            limit=2,
            min_interactions=2,
            verbose='false'
        )
        
        print(f"Request successful - Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Keys in result: {list(result['result'].keys())}")
            print(f"Statistics keys: {list(result['result']['statistics'].keys())}")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Exception calling API: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 