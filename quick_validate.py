#!/usr/bin/env python
"""
Quick validation script for testing individual tokenomics and smart contract features.

This script allows quick testing of specific features with command-line arguments,
making it easy to validate individual functionality.

Examples:
    # Check price for a token
    python quick_validate.py price SigUSD
    
    # Get liquidity pools
    python quick_validate.py pools
    
    # Get liquidity pools for a specific token
    python quick_validate.py pools SigUSD
    
    # Check swap information
    python quick_validate.py swap ERG SigUSD 10
    
    # Analyze contract
    python quick_validate.py contract 9hXmgvzndtakdSAgJ92fQ8ZjuKirYEPnQZ2KumygbrJao1rr5ko
    
    # Get contract statistics
    python quick_validate.py contract-stats
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Define function references that will be imported or mocked during testing
async def get_token_price_info(token_query: str) -> str:
    """Get token price information (imported or mocked during testing)."""
    # This will be imported or mocked during testing
    # For direct usage, we can import the real function
    try:
        from ergo_explorer.tools.tokenomics import get_token_price_info as get_price
        return await get_price(token_query)
    except ImportError:
        raise ImportError("Could not import get_token_price_info from ergo_explorer.tools.tokenomics")

async def get_token_price_chart(token_query: str, days: int = 7) -> str:
    """Get token price chart (imported or mocked during testing)."""
    try:
        from ergo_explorer.tools.tokenomics import get_token_price_chart as get_chart
        return await get_chart(token_query, days=days)
    except ImportError:
        raise ImportError("Could not import get_token_price_chart from ergo_explorer.tools.tokenomics")

async def get_liquidity_pool_info(token_query: Optional[str] = None) -> str:
    """Get liquidity pool information (imported or mocked during testing)."""
    try:
        from ergo_explorer.tools.tokenomics import get_liquidity_pool_info as get_pools
        return await get_pools(token_query)
    except ImportError:
        raise ImportError("Could not import get_liquidity_pool_info from ergo_explorer.tools.tokenomics")

async def get_token_swap_info(from_token: str, to_token: str, amount: float) -> str:
    """Get token swap information (imported or mocked during testing)."""
    try:
        from ergo_explorer.tools.tokenomics import get_token_swap_info as get_swap
        return await get_swap(from_token, to_token, amount)
    except ImportError:
        raise ImportError("Could not import get_token_swap_info from ergo_explorer.tools.tokenomics")

async def analyze_smart_contract(address: str) -> str:
    """Analyze smart contract (imported or mocked during testing)."""
    try:
        from ergo_explorer.tools.contracts import analyze_smart_contract as analyze
        return await analyze(address)
    except ImportError:
        raise ImportError("Could not import analyze_smart_contract from ergo_explorer.tools.contracts")

async def get_contract_statistics() -> str:
    """Get contract statistics (imported or mocked during testing)."""
    try:
        from ergo_explorer.tools.contracts import get_contract_statistics as get_stats
        return await get_stats()
    except ImportError:
        raise ImportError("Could not import get_contract_statistics from ergo_explorer.tools.contracts")

async def simulate_contract_execution(address: str, input_data: Dict[str, Any] = None) -> str:
    """Simulate contract execution (imported or mocked during testing)."""
    try:
        from ergo_explorer.tools.contracts import simulate_contract_execution as simulate
        return await simulate(address, input_data)
    except ImportError:
        raise ImportError("Could not import simulate_contract_execution from ergo_explorer.tools.contracts")


async def validate_token_price(token_query: str) -> int:
    """Validate token price information."""
    print(f"Getting price information for {token_query}...\n")
    start_time = datetime.now()
    
    try:
        result = await get_token_price_info(token_query)
        print(result)
        
        # Also get price chart
        print(f"\nGetting price chart for {token_query}...\n")
        chart = await get_token_price_chart(token_query, days=7)
        print(chart)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    print(f"\nCompleted in {elapsed:.2f} seconds")
    
    return 0


async def validate_liquidity_pools(token_query: str = None) -> int:
    """Validate liquidity pool information."""
    if token_query:
        print(f"Getting liquidity pools for {token_query}...\n")
    else:
        print("Getting all liquidity pools...\n")
    
    start_time = datetime.now()
    
    try:
        result = await get_liquidity_pool_info(token_query)
        print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    print(f"\nCompleted in {elapsed:.2f} seconds")
    
    return 0


async def validate_token_swap(from_token: str, to_token: str, amount: float) -> int:
    """Validate token swap information."""
    print(f"Getting swap information for {amount} {from_token} to {to_token}...\n")
    start_time = datetime.now()
    
    try:
        result = await get_token_swap_info(from_token, to_token, amount)
        print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    print(f"\nCompleted in {elapsed:.2f} seconds")
    
    return 0


async def validate_contract_analysis(address: str) -> int:
    """Validate contract analysis."""
    print(f"Analyzing contract {address}...\n")
    start_time = datetime.now()
    
    try:
        result = await analyze_smart_contract(address)
        print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    print(f"\nCompleted in {elapsed:.2f} seconds")
    
    return 0


async def validate_contract_statistics() -> int:
    """Validate contract statistics."""
    print("Getting contract statistics...\n")
    start_time = datetime.now()
    
    try:
        result = await get_contract_statistics()
        print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    print(f"\nCompleted in {elapsed:.2f} seconds")
    
    return 0


async def validate_contract_simulation(address: str) -> int:
    """Validate contract simulation."""
    print(f"Simulating contract execution for {address}...\n")
    start_time = datetime.now()
    
    try:
        # Sample input data for simulation
        input_data = {
            "recipient": "9hHDQb26AjnJUXxcqriqY1mnhpLuUeC81C4pggtK7tupr92Ea1K",
            "amount": 1.0,
            "token_id": None
        }
        
        result = await simulate_contract_execution(address, input_data)
        print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    print(f"\nCompleted in {elapsed:.2f} seconds")
    
    return 0


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Quick validation tool for Ergo features',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split('\n\n')[2]  # Extract examples from docstring
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Token price command
    price_parser = subparsers.add_parser('price', help='Get token price information')
    price_parser.add_argument('token', help='Token name or ID')
    
    # Liquidity pools command
    pools_parser = subparsers.add_parser('pools', help='Get liquidity pool information')
    pools_parser.add_argument('token', nargs='?', help='Optional token name or ID to filter pools')
    
    # Token swap command
    swap_parser = subparsers.add_parser('swap', help='Get token swap information')
    swap_parser.add_argument('from_token', help='Source token name or ID')
    swap_parser.add_argument('to_token', help='Target token name or ID')
    swap_parser.add_argument('amount', type=float, help='Amount of source token to swap')
    
    # Contract analysis command
    contract_parser = subparsers.add_parser('contract', help='Analyze smart contract')
    contract_parser.add_argument('address', help='Contract address')
    
    # Contract statistics command
    subparsers.add_parser('contract-stats', help='Get contract statistics')
    
    # Contract simulation command
    sim_parser = subparsers.add_parser('contract-sim', help='Simulate contract execution')
    sim_parser.add_argument('address', help='Contract address')
    
    return parser.parse_args()


async def main():
    """Run the validation based on command-line arguments."""
    args = parse_arguments()
    
    if args.command == 'price':
        return await validate_token_price(args.token)
    
    elif args.command == 'pools':
        return await validate_liquidity_pools(args.token)
    
    elif args.command == 'swap':
        return await validate_token_swap(args.from_token, args.to_token, args.amount)
    
    elif args.command == 'contract':
        return await validate_contract_analysis(args.address)
    
    elif args.command == 'contract-stats':
        return await validate_contract_statistics()
    
    elif args.command == 'contract-sim':
        return await validate_contract_simulation(args.address)
    
    else:
        print("Please specify a command. Use --help for available commands.")
        return 1


if __name__ == "__main__":
    # Python 3.7+ compatible asyncio run
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 