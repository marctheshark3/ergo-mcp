"""Integration tests for Ergo Explorer MCP tools using real blockchain data."""

import asyncio
import pytest
import logging
import os
import json
import httpx
from unittest.mock import MagicMock

# Set up logging to a file in the isolated_tests directory
log_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "logs", "live_integration_tests.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("live_integration_tests")

# Known valid Ergo addresses for testing
KNOWN_ADDRESSES = [
    "9fRAWhdxEsTcdb8PhGNrZfwqa65zfkuYHAMmkQLcic1gdLSV5vA",  # A known active address
    "9g1b69CQYaJKSY9ycjYJJnQxCJL8VEPn5kiVKQKDgkrQKGPRVf9"   # Another known address
]

# Known valid token IDs for testing
KNOWN_TOKEN_IDS = [
    "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",  # SigUSD
    "003bd19d0187117f130b62e1bcab0939929ff5c7709f843c5c4dd158949285d0"   # SigRSV
]

# Known valid block IDs for testing
KNOWN_BLOCK_IDS = [
    "b732d0ac7a5cdfa9c2c5d94f06542f867c4cf80d607b8625b9d5ae19be19c9b7"
]

# Known valid transaction IDs for testing
KNOWN_TX_IDS = [
    "9148408c04c2e38a6402a7950d6157730fa7d49e9ab3b9cadec481d7769918e9"
]

# Known valid box IDs for testing
KNOWN_BOX_IDS = [
    "b51a34d3a1e184599137aa25139d282144dab328f0afa1afdeb5f0b6d2ed0923"
]

class ErgoExplorerClient:
    """A simple client for Ergo Explorer API to use in live integration tests."""
    
    def __init__(self):
        self.explorer_base_url = os.environ.get("ERGO_EXPLORER_API", "https://api.ergoplatform.com/api/v1")
        self.node_base_url = os.environ.get("ERGO_NODE_API", "http://213.239.193.208:9053")
        self.user_agent = "ErgoExplorerMCP-Integration-Tests/1.0"
        logger.info(f"Using Explorer API: {self.explorer_base_url}")
        logger.info(f"Using Node API: {self.node_base_url}")
    
    async def get_explorer_data(self, endpoint, params=None):
        """Get data from Ergo Explorer API."""
        url = f"{self.explorer_base_url}/{endpoint}"
        try:
            async with httpx.AsyncClient() as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching from Explorer API {url}: {str(e)}")
            return {"error": str(e)}
    
    async def get_node_data(self, endpoint, params=None):
        """Get data from Ergo Node API."""
        url = f"{self.node_base_url}/{endpoint}"
        try:
            async with httpx.AsyncClient() as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching from Node API {url}: {str(e)}")
            return {"error": str(e)}
    
    async def get_address_balance(self, address):
        """Get balance for an address directly from the API."""
        return await self.get_explorer_data(f"addresses/{address}/balance/confirmed")
    
    async def get_token_by_id(self, token_id):
        """Get token information directly from the API."""
        return await self.get_explorer_data(f"tokens/{token_id}")
    
    async def get_block_by_id(self, block_id):
        """Get block information directly from the API."""
        return await self.get_explorer_data(f"blocks/{block_id}")
    
    async def get_transaction(self, tx_id):
        """Get transaction information directly from the API."""
        return await self.get_explorer_data(f"transactions/{tx_id}")
    
    async def get_box(self, box_id):
        """Get box information directly from the API."""
        return await self.get_explorer_data(f"boxes/{box_id}")
    
    async def get_blockchain_info(self):
        """Get blockchain information directly from the API."""
        return await self.get_node_data("info")


@pytest.fixture
def ergo_client():
    """Fixture to provide an Ergo Explorer API client."""
    return ErgoExplorerClient()


@pytest.fixture
def mock_context():
    """Mock Context for testing."""
    return MagicMock()


@pytest.fixture
def mock_mcp():
    """Mock MCP server for testing."""
    class MockMCP:
        def __init__(self):
            self.tools = {}
        
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator
    
    return MockMCP()


@pytest.mark.asyncio
async def test_live_get_address_balance(ergo_client):
    """Test get_address_balance with live data."""
    for address in KNOWN_ADDRESSES:
        logger.info(f"Testing get_address_balance with address: {address}")
        
        # Get the balance directly from the API
        api_result = await ergo_client.get_address_balance(address)
        
        # Basic validation
        assert api_result is not None, f"API returned None for address {address}"
        assert "confirmed" in api_result, f"API response missing 'confirmed' field: {api_result}"
        
        # The real tool would format this, but we're just validating the API response for now
        logger.info(f"Address {address} balance: {json.dumps(api_result, indent=2)}")
        
        # Additional validations if needed
        if "nanoErgs" in api_result["confirmed"]:
            assert isinstance(api_result["confirmed"]["nanoErgs"], int), "nanoErgs should be an integer"
            assert api_result["confirmed"]["nanoErgs"] >= 0, "nanoErgs should be non-negative"


@pytest.mark.asyncio
async def test_live_get_token_info(ergo_client):
    """Test get_token with live data."""
    for token_id in KNOWN_TOKEN_IDS:
        logger.info(f"Testing get_token with token_id: {token_id}")
        
        # Get the token directly from the API
        api_result = await ergo_client.get_token_by_id(token_id)
        
        # Basic validation
        assert api_result is not None, f"API returned None for token {token_id}"
        assert "id" in api_result, f"API response missing 'id' field: {api_result}"
        assert api_result["id"] == token_id, f"Token ID mismatch: {api_result['id']} != {token_id}"
        
        # The real tool would format this, but we're just validating the API response for now
        logger.info(f"Token {token_id} info: {json.dumps(api_result, indent=2)}")
        
        # Additional validations
        assert "name" in api_result, f"API response missing 'name' field: {api_result}"
        if "emissionAmount" in api_result:
            assert isinstance(api_result["emissionAmount"], int), "emissionAmount should be an integer"


@pytest.mark.asyncio
async def test_live_get_block(ergo_client):
    """Test get_block with live data."""
    for block_id in KNOWN_BLOCK_IDS:
        logger.info(f"Testing get_block with block_id: {block_id}")
        
        # Get the block directly from the API
        api_result = await ergo_client.get_block_by_id(block_id)
        
        # Basic validation
        assert api_result is not None, f"API returned None for block {block_id}"
        assert "id" in api_result, f"API response missing 'id' field: {api_result}"
        assert api_result["id"] == block_id, f"Block ID mismatch: {api_result['id']} != {block_id}"
        
        # The real tool would format this, but we're just validating the API response for now
        logger.info(f"Block {block_id} height: {api_result.get('height')}")
        
        # Additional validations
        assert "height" in api_result, f"API response missing 'height' field: {api_result}"
        assert isinstance(api_result["height"], int), "height should be an integer"


@pytest.mark.asyncio
async def test_live_get_transaction(ergo_client):
    """Test get_transaction with live data."""
    for tx_id in KNOWN_TX_IDS:
        logger.info(f"Testing get_transaction with tx_id: {tx_id}")
        
        # Get the transaction directly from the API
        api_result = await ergo_client.get_transaction(tx_id)
        
        # Basic validation
        assert api_result is not None, f"API returned None for transaction {tx_id}"
        assert "id" in api_result, f"API response missing 'id' field: {api_result}"
        assert api_result["id"] == tx_id, f"Transaction ID mismatch: {api_result['id']} != {tx_id}"
        
        # The real tool would format this, but we're just validating the API response for now
        logger.info(f"Transaction {tx_id} info: Block ID: {api_result.get('blockId')}")
        
        # Additional validations
        assert "inputs" in api_result, f"API response missing 'inputs' field: {api_result}"
        assert "outputs" in api_result, f"API response missing 'outputs' field: {api_result}"
        assert isinstance(api_result["inputs"], list), "inputs should be a list"
        assert isinstance(api_result["outputs"], list), "outputs should be a list"


@pytest.mark.asyncio
async def test_live_get_box(ergo_client):
    """Test get_box with live data."""
    for box_id in KNOWN_BOX_IDS:
        logger.info(f"Testing get_box with box_id: {box_id}")
        
        # Get the box directly from the API
        api_result = await ergo_client.get_box(box_id)
        
        # Basic validation
        assert api_result is not None, f"API returned None for box {box_id}"
        assert "id" in api_result, f"API response missing 'id' field: {api_result}"
        assert api_result["id"] == box_id, f"Box ID mismatch: {api_result['id']} != {box_id}"
        
        # The real tool would format this, but we're just validating the API response for now
        logger.info(f"Box {box_id} value: {api_result.get('value')}")
        
        # Additional validations
        assert "value" in api_result, f"API response missing 'value' field: {api_result}"
        assert isinstance(api_result["value"], int), "value should be an integer"


@pytest.mark.asyncio
async def test_live_blockchain_status(ergo_client):
    """Test blockchain_status with live data."""
    logger.info("Testing blockchain_status")
    
    # Get the blockchain info directly from the API
    api_result = await ergo_client.get_blockchain_info()
    
    # Basic validation
    assert api_result is not None, "API returned None for blockchain info"
    
    # The real tool would format this, but we're just validating the API response for now
    if "fullHeight" in api_result:
        logger.info(f"Blockchain height: {api_result.get('fullHeight')}")
        assert isinstance(api_result["fullHeight"], int), "fullHeight should be an integer"
    
    if "difficulty" in api_result:
        logger.info(f"Blockchain difficulty: {api_result.get('difficulty')}")
        assert isinstance(api_result["difficulty"], int), "difficulty should be an integer" 