"""Unit tests for Smart Contract analysis functionality."""
import pytest
from unittest.mock import patch, AsyncMock
from ergo_explorer.tools import contracts

@pytest.fixture
def mock_contract_box():
    return {
        "boxId": "test_box_id",
        "value": 1000000000,  # 1 ERG
        "ergoTree": "100204a00b08cd0279be667e",
        "creationTxId": "test_creation_tx_id",
        "additionalRegisters": {
            "R4": "0e012a",  # Int 42
            "R5": "0c0548656c6c6f",  # String "Hello"
            "R6": "07abcdef"  # ErgoTree
        },
        "assets": [
            {
                "tokenId": "test_token_id_123",
                "amount": 100
            },
            {
                "tokenId": "test_token_id_456",
                "amount": 200
            }
        ]
    }

@pytest.fixture
def mock_contract_boxes():
    return [
        {
            "boxId": "test_box_id",
            "value": 1000000000,  # 1 ERG
            "ergoTree": "100204a00b08cd0279be667e",
            "creationTxId": "test_creation_tx_id",
            "additionalRegisters": {
                "R4": "0e012a",  # Int 42
                "R5": "0c0548656c6c6f",  # String "Hello"
                "R6": "07abcdef"  # ErgoTree
            },
            "assets": [
                {
                    "tokenId": "test_token_id_123",
                    "amount": 100
                }
            ]
        }
    ]

@pytest.mark.asyncio
async def test_analyze_smart_contract(mock_contract_boxes):
    """Test analyzing a smart contract from its address."""
    with patch('ergo_explorer.api.get_unspent_boxes_by_address_node', new_callable=AsyncMock) as mock_boxes:
        mock_boxes.return_value = mock_contract_boxes
        
        result = await contracts.analyze_smart_contract("test_address")
        
        assert "Smart Contract Analysis for test_address" in result
        assert "Contract Type:" in result
        assert "Description:" in result
        assert "Contract Registers:" in result
        assert "R4: 42 (int)" in result
        assert "R5: \"Hello\" (text)" in result
        assert "R6: ErgoTree (contract)" in result
        assert "Held Tokens:" in result
        assert "test_token_id_1" in result
        assert "Contract Balance: 1.000000000 ERG" in result
        assert "Contract Created in Transaction: test_creation_tx_id" in result
        assert "Common Use Cases for this Contract Type:" in result
        
        mock_boxes.assert_called_once_with("test_address")

@pytest.mark.asyncio
async def test_analyze_smart_contract_no_boxes():
    """Test analyzing a contract with no unspent boxes."""
    with patch('ergo_explorer.api.get_unspent_boxes_by_address_node', new_callable=AsyncMock) as mock_boxes:
        mock_boxes.return_value = []
        
        result = await contracts.analyze_smart_contract("test_address")
        
        assert "No unspent boxes found for contract address test_address" in result
        mock_boxes.assert_called_once_with("test_address")

@pytest.mark.asyncio
async def test_decompile_contract():
    """Test decompiling ErgoTree to identify contract template."""
    # Test with DEX contract pattern
    template, description = await contracts.decompile_contract("100204a00b08cd0279be667e")
    assert template == "DEX Contract"
    assert "decentralized exchange" in description.lower()
    
    # Test with time-lock contract pattern
    template, description = await contracts.decompile_contract("100204a00b08cd")
    assert template == "Time-Lock Contract"
    assert "locks funds" in description.lower()
    
    # Test with unknown pattern
    template, description = await contracts.decompile_contract("unknown_pattern")
    assert template == "Unknown Contract Type"
    assert "unrecognized" in description.lower()

@pytest.mark.asyncio
async def test_decode_register():
    """Test decoding register values to human readable format."""
    # Test integer encoding
    result = await contracts.decode_register("0e012a")
    assert "42 (int)" in result
    
    # Test text encoding
    result = await contracts.decode_register("0c0548656c6c6f")
    assert "\"Hello\" (text)" in result
    
    # Test ErgoTree encoding
    result = await contracts.decode_register("07abcdef")
    assert "ErgoTree (contract)" in result
    
    # Test unknown encoding
    result = await contracts.decode_register("unexpected_value")
    assert "unexpected_value" in result

@pytest.mark.asyncio
async def test_get_contract_use_cases():
    """Test getting common use cases for contract templates."""
    # Test DEX contract use cases
    result = await contracts.get_contract_use_cases("DEX Contract")
    assert "Automated Market Maker" in result
    assert "Token swapping" in result
    
    # Test multisig contract use cases
    result = await contracts.get_contract_use_cases("Multisig Contract")
    assert "DAO treasury" in result
    assert "Shared wallet" in result
    
    # Test unknown contract use cases
    result = await contracts.get_contract_use_cases("Unknown Contract")
    assert "Custom contract" in result

@pytest.mark.asyncio
async def test_get_contract_statistics():
    """Test getting statistics about smart contract usage."""
    result = await contracts.get_contract_statistics()
    
    assert "Smart Contract Statistics on Ergo Blockchain" in result
    assert "Total Contracts:" in result
    assert "Active Contracts:" in result
    assert "Total Value Locked:" in result
    assert "Contract Type Distribution:" in result
    
    # Verify some of the contract types are present
    assert "P2PK" in result
    assert "DEX" in result
    assert "Oracle" in result
    assert "NFT" in result

@pytest.mark.asyncio
async def test_simulate_contract_execution():
    """Test simulating smart contract execution."""
    input_data = {
        "recipient": "recipient_address",
        "amount": 1.0
    }
    
    result = await contracts.simulate_contract_execution("test_contract", input_data)
    
    assert "Contract Simulation for test_contract" in result
    assert "Input Parameters:" in result
    assert "recipient: recipient_address" in result
    assert "amount: 1.0" in result
    assert "Simulation Result: SUCCESS" in result
    assert "Expected Outputs:" in result
    assert "Output Box 1:" in result
    assert "Output Box 2:" in result
    assert "Fee:" in result 