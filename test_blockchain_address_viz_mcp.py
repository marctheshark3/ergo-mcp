"""
Test script for the blockchain_address_interaction_viz MCP tool.
"""

import asyncio
import logging
import json
import sys
from mcp.server.fastmcp import Context, FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Import routes
from ergo_explorer.api.routes.blockchain import register_blockchain_routes

class TestMCP(FastMCP):
    """Simple MCP implementation for testing."""
    
    def __init__(self):
        self.tools = {}
        
    def tool(self, name=None):
        def wrapper(func):
            tool_name = name or func.__name__
            self.tools[tool_name] = func
            return func
        return wrapper
    
    async def call_tool(self, name, **kwargs):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        return await self.tools[name](Context(), **kwargs)

async def test_address_viz():
    # Create MCP instance
    mcp = TestMCP()
    
    # Register routes
    register_blockchain_routes(mcp)
    
    # Test address
    address = '9gUDVVx75KyZ783YLECKngb1wy8KVwEfk3byjdfjUyDVAELAPUN'
    
    print(f"Testing blockchain_address_interaction_viz for {address}...")
    
    # Test HTML format
    print("Testing HTML format...")
    result_html = await mcp.call_tool("blockchain_address_interaction_viz", 
        address=address, 
        limit=100, 
        min_interactions=5,
        format="html"
    )
    
    # Save HTML output
    with open("mcp_address_viz.html", "w") as f:
        f.write(result_html["content"])
    
    print(f"HTML visualization saved to mcp_address_viz.html")
    
    # Test JSON format
    print("Testing JSON format...")
    result_json = await mcp.call_tool("blockchain_address_interaction_viz", 
        address=address, 
        limit=10, 
        min_interactions=2,
        format="json"
    )
    
    # Save JSON output
    with open("mcp_address_viz.json", "w") as f:
        json.dump(result_json["data"], f, indent=2)
    
    print(f"JSON visualization data saved to mcp_address_viz.json")
    
    print("Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_address_viz()) 