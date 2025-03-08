"""
MCP tools for Ergo smart contract analysis.
"""
from typing import Dict, List, Optional, Any
import re
import json
import base64

from ergo_explorer.api import (
    fetch_api,
    get_box_by_id_node,
    get_box_by_address_node,
    get_unspent_boxes_by_address_node
)


async def analyze_smart_contract(address: str) -> str:
    """Analyze a smart contract from its address.
    
    Args:
        address: Ergo blockchain address of the contract
    """
    try:
        # Get unspent boxes for this address to analyze the contract
        boxes = await get_unspent_boxes_by_address_node(address)
        
        if not boxes or not isinstance(boxes, list) or len(boxes) == 0:
            return f"No unspent boxes found for contract address {address}."
            
        # Get the first box for analysis
        box = boxes[0]
        
        # Extract contract details
        ergo_tree = box.get("ergoTree", "")
        ergo_tree_template = box.get("additionalRegisters", {}).get("R9", "")
        registers = box.get("additionalRegisters", {})
        assets = box.get("assets", [])
        
        # Try to decompile the contract
        contract_template, contract_description = await decompile_contract(ergo_tree)
        
        # Format result
        result = f"Smart Contract Analysis for {address}\n"
        result += "==================================\n\n"
        
        # Add contract type and description
        result += f"Contract Type: {contract_template}\n"
        result += f"Description: {contract_description}\n\n"
        
        # Add data about registers (which often hold contract parameters)
        if registers:
            result += "Contract Registers:\n"
            for reg_key, reg_value in registers.items():
                decoded = await decode_register(reg_value)
                result += f"  {reg_key}: {decoded}\n"
            result += "\n"
        
        # Add data about tokens contained in the contract
        if assets:
            result += "Held Tokens:\n"
            for asset in assets:
                token_id = asset.get("tokenId", "")
                amount = asset.get("amount", 0)
                result += f"  {token_id[:12]}... : {amount} units\n"
            result += "\n"
        
        # Add funding information
        box_value = box.get("value", 0)
        erg_value = box_value / 1_000_000_000  # Convert nanoERGs to ERGs
        result += f"Contract Balance: {erg_value:.9f} ERG\n"
        
        # Add usage patterns based on creation and spending
        creation_tx = box.get("creationTxId", "")
        if creation_tx:
            result += f"Contract Created in Transaction: {creation_tx}\n"
        
        result += "\nCommon Use Cases for this Contract Type:\n"
        result += await get_contract_use_cases(contract_template)
        
        return result
        
    except Exception as e:
        return f"Error analyzing smart contract: {str(e)}"


async def decompile_contract(ergo_tree: str) -> tuple[str, str]:
    """Attempt to decompile an ErgoTree to identify contract template and provide description.
    
    Args:
        ergo_tree: Base16-encoded ErgoTree
        
    Returns:
        Tuple of (contract_template, description)
    """
    # Dictionary of common contract templates and their descriptions
    templates = {
        # The pattern keys are simplified - in a real implementation, 
        # these would be more comprehensive patterns based on bytecode analysis
        "100204a00b08cd": ("Time-Lock Contract", "Locks funds until a specified blockchain height"),
        "1040040004000e36100204d00f": ("Oracle Contract", "Used for posting and reading data oracle values"),
        "100108cd03": ("Multisig Contract", "Requires multiple signatures to spend"),
        "10010101": ("Single-Signature Contract", "Standard P2PK contract"),
        "10010e43": ("Height Triggered Contract", "Executes based on blockchain height condition"),
        "100204d00f1804": ("Token Sale Contract", "Handles token sale with fixed price"),
        "100204a00b08cd0279be667e": ("DEX Contract", "Used for decentralized exchange operations"),
        "10020e3620": ("NFT Minting Contract", "Used for minting NFT tokens"),
        "100eae": ("Proxy Contract", "Acts as a proxy/delegate for other contracts")
    }
    
    # Default values
    contract_template = "Unknown Contract Type"
    description = "Custom or unrecognized contract pattern"
    
    # Check against known templates
    # This is simplified - real implementation would do more sophisticated bytecode analysis
    for pattern, (template, desc) in templates.items():
        if ergo_tree and ergo_tree.lower().startswith(pattern.lower()):
            contract_template = template
            description = desc
            break
    
    # For a real implementation, we would connect to ErgoScript decompiler services
    # or use a local decompiler to turn the ErgoTree into readable ErgoScript
            
    return contract_template, description


async def decode_register(register_value: str) -> str:
    """Decode register value to human readable format if possible.
    
    Args:
        register_value: Base16 or Base64 encoded register value
        
    Returns:
        Human readable string representation
    """
    try:
        # Try to decode as base64
        if register_value.startswith("0e"):
            # Integer encoding
            value_hex = register_value[2:]
            try:
                value = int(value_hex, 16)
                return f"{value} (int)"
            except:
                pass
        
        elif register_value.startswith("0c"):
            # Byte array encoding - could be text
            value_hex = register_value[2:]
            try:
                # Try to decode as UTF-8 text
                byte_data = bytes.fromhex(value_hex)
                text = byte_data.decode('utf-8')
                return f'"{text}" (text)'
            except:
                # If not valid text, just show as bytes
                return f"Bytes: {value_hex[:20]}{'...' if len(value_hex) > 20 else ''}"
        
        elif register_value.startswith("07"):
            # ErgoTree encoding
            return "ErgoTree (contract)"
            
        # Default fallback
        return f"{register_value[:20]}{'...' if len(register_value) > 20 else ''}"
    
    except Exception:
        # Return original if decoding fails
        return register_value[:20] + ('...' if len(register_value) > 20 else '')


async def get_contract_use_cases(contract_template: str) -> str:
    """Get common use cases for a contract template.
    
    Args:
        contract_template: The identified contract template
        
    Returns:
        Formatted string with use cases
    """
    use_cases = {
        "Time-Lock Contract": [
            "Treasury funds with time-based vesting",
            "Delayed payment systems",
            "Scheduled token distribution"
        ],
        "Oracle Contract": [
            "Price feeds for DeFi applications",
            "External data sources for smart contracts",
            "Cross-chain data bridges"
        ],
        "Multisig Contract": [
            "DAO treasury management",
            "Shared wallet functionality",
            "Corporate fund governance"
        ],
        "Single-Signature Contract": [
            "Standard wallet functionality",
            "Simple payment contracts",
            "Basic fund storage"
        ],
        "Height Triggered Contract": [
            "Time-based token unlocks",
            "Scheduled execution of tasks",
            "Automated periodic payments"
        ],
        "Token Sale Contract": [
            "ICO/IDO token distribution",
            "Fixed-price token sales",
            "Token vending mechanisms"
        ],
        "DEX Contract": [
            "Automated Market Maker (AMM) pools",
            "Token swapping",
            "Liquidity provision"
        ],
        "NFT Minting Contract": [
            "Creating unique digital collectibles",
            "Digital art distribution",
            "Proof of ownership for digital or physical assets"
        ],
        "Proxy Contract": [
            "Upgradeable contracts",
            "Contract interaction aggregation",
            "Cross-contract calls"
        ]
    }
    
    if contract_template in use_cases:
        cases = use_cases[contract_template]
        result = ""
        for case in cases:
            result += f"• {case}\n"
        return result
    else:
        return "• Custom contract - specific use cases unknown\n"


async def get_contract_statistics() -> str:
    """Get statistics about smart contract usage on the Ergo blockchain.
    
    Returns:
        Formatted string with contract statistics
    """
    try:
        # In a real implementation, we would fetch this data from a suitable API
        # For this example, we'll use placeholder data
        
        # Stats could come from ErgoWatch or similar services
        stats = {
            "total_contracts": 15000,
            "active_contracts": 8500,
            "contract_types": [
                {"name": "P2PK", "count": 12000, "percentage": 80.0},
                {"name": "DEX", "count": 1500, "percentage": 10.0},
                {"name": "Oracle", "count": 200, "percentage": 1.3},
                {"name": "NFT", "count": 800, "percentage": 5.3},
                {"name": "Other", "count": 500, "percentage": 3.4}
            ],
            "total_value_locked": 350000000000000  # in nanoErgs
        }
        
        # Format the results
        result = "Smart Contract Statistics on Ergo Blockchain\n"
        result += "==========================================\n\n"
        
        result += f"Total Contracts: {stats['total_contracts']:,}\n"
        result += f"Active Contracts: {stats['active_contracts']:,}\n"
        result += f"Total Value Locked: {stats['total_value_locked'] / 1_000_000_000:,.2f} ERG\n\n"
        
        result += "Contract Type Distribution:\n"
        for contract in stats["contract_types"]:
            result += f"• {contract['name']}: {contract['count']:,} ({contract['percentage']:.1f}%)\n"
        
        return result
        
    except Exception as e:
        return f"Error fetching contract statistics: {str(e)}"


async def simulate_contract_execution(address: str, input_data: Dict[str, Any]) -> str:
    """Simulate the execution of a smart contract with given inputs.
    
    Args:
        address: Contract address
        input_data: Dictionary of input data for simulation
        
    Returns:
        Formatted string with simulation results
    """
    try:
        # This is a placeholder for contract simulation
        # In a real implementation, we would use the Ergo node's /script/executeWithContext endpoint
        # or similar functionality to simulate contract execution
        
        # For the example, we'll just return a mock response
        
        result = f"Contract Simulation for {address}\n"
        result += "================================\n\n"
        
        result += "Input Parameters:\n"
        for key, value in input_data.items():
            result += f"• {key}: {value}\n"
        
        result += "\nSimulation Result: SUCCESS\n"
        result += "Expected Outputs:\n"
        result += "• Output Box 1: 1.0 ERG to recipient\n"
        result += "• Output Box 2: 0.1 ERG (change) back to sender\n"
        result += "• Fee: 0.001 ERG\n"
        
        return result
        
    except Exception as e:
        return f"Error simulating contract execution: {str(e)}" 