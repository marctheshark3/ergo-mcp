#!/usr/bin/env python3
"""
Test script for blockchain_status function.

This script tests both markdown and JSON formats of the blockchain status endpoint.
"""

import asyncio
import json
from ergo_explorer.tools.blockchain import blockchain_status

async def test_blockchain_status():
    """Test the blockchain_status function with both formats."""
    # Test markdown format
    print("Testing blockchain_status with markdown format:")
    markdown_response = await blockchain_status(response_format="markdown")
    print(markdown_response)
    print("\n" + "="*80 + "\n")
    
    # Test JSON format
    print("Testing blockchain_status with JSON format:")
    json_response = await blockchain_status(response_format="json")
    print(json.dumps(json_response, indent=2))

if __name__ == "__main__":
    asyncio.run(test_blockchain_status()) 