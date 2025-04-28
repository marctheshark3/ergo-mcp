"""
Tests for the comprehensive blockchain address info functionality.
"""

import asyncio
import json
import sys
import os

# Add the parent directory to the system path to import the ergo_explorer module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ergo_explorer.tools.blockchain_address_info import (
    blockchain_address_info, 
    blockchain_address_info_markdown
)

# Test address - a valid Ergo address
TEST_ADDRESS = "9gUDVVx75KyZ783YLECKngb1wy8KVwEfk3byjdfjUyDVAELAPUN"

def test_blockchain_address_info():
    """Test the blockchain_address_info function."""
    print("Testing blockchain_address_info...")
    
    try:
        # Test with transactions included
        result = blockchain_address_info(
            address=TEST_ADDRESS,
            include_transactions=True,
            tx_limit=5
        )
        
        # Pretty print the JSON result
        print(json.dumps(result, indent=2))
        
        print("\nTesting blockchain_address_info without transactions...")
        
        # Test without transactions
        result_no_tx = blockchain_address_info(
            address=TEST_ADDRESS,
            include_transactions=False
        )
        
        print(json.dumps(result_no_tx, indent=2))
        
        print("JSON tests completed successfully!")
        return True
    except Exception as e:
        print(f"Error in blockchain_address_info test: {str(e)}")
        return False

def test_blockchain_address_info_markdown():
    """Test the blockchain_address_info_markdown function."""
    print("\nTesting blockchain_address_info_markdown...")
    
    try:
        # Test with transactions included
        result = blockchain_address_info_markdown(
            address=TEST_ADDRESS,
            include_transactions=True,
            tx_limit=5
        )
        
        print(result)
        
        print("\nTesting blockchain_address_info_markdown without transactions...")
        
        # Test without transactions
        result_no_tx = blockchain_address_info_markdown(
            address=TEST_ADDRESS,
            include_transactions=False
        )
        
        print(result_no_tx)
        
        print("Markdown tests completed successfully!")
        return True
    except Exception as e:
        print(f"Error in blockchain_address_info_markdown test: {str(e)}")
        return False

def main():
    """Run all tests."""
    try:
        json_test_success = test_blockchain_address_info()
        markdown_test_success = test_blockchain_address_info_markdown()
        
        if json_test_success and markdown_test_success:
            print("\nAll tests completed successfully!")
        else:
            print("\nSome tests failed.")
    except Exception as e:
        print(f"Error during tests: {str(e)}")
        raise

if __name__ == "__main__":
    main() 