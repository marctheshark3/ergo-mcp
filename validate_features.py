#!/usr/bin/env python
"""
Validation script for testing tokenomics and smart contract analysis features
with real Ergo blockchain data.

This script automatically tests the new features with known working examples
and outputs the results, making it easy to verify functionality without
manual input.
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Define function references that will be imported or mocked during testing
async def get_token_price_info(token_query: str) -> str:
    """Get token price information (imported or mocked during testing)."""
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


async def run_validation_test(name: str, func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Run a validation test and capture results and timing."""
    print(f"\n[TEST] {name}...")
    start_time = datetime.now()
    
    try:
        result = await func(*args, **kwargs)
        success = True
        
        # Format the result for better readability
        if isinstance(result, str) and len(result) > 1000:
            result = result[:1000] + "... [output truncated]"
            
    except Exception as e:
        result = f"ERROR: {str(e)}"
        success = False
    
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    
    print(f"  ✓ Completed in {elapsed:.2f}s")
    if not success:
        print(f"  ✗ {result}")
    else:
        print(f"  ✓ Success")
    
    return {
        "name": name,
        "success": success,
        "result": result,
        "elapsed_seconds": elapsed
    }


async def validate_tokenomics_features() -> List[Dict[str, Any]]:
    """Validate tokenomics features."""
    print("\n===== TOKENOMICS FEATURES VALIDATION =====")
    results = []
    
    # Known Ergo tokens to test with
    tokens = {
        "ERG": "ERG",  # Native Ergo token
        "SigUSD": "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04",  # SigUSD stablecoin
        "SigRSV": "003bd19d0187117f130b62e1bcab0939929ff5c7709f843c5c4dd158949285d0",  # SigRSV reserve coin
        "NETA": "472c3d4ecaa08fb7392ff041ee2e6af75f4a558810a74b28600549d5392810e8",  # NETA token
        "ergopad": "d71693c49a84fbbecd4908c94813b46514b18b67a99952dc1e6e4791556de413"  # ergopad token
    }
    
    # Test token price info for multiple tokens
    for name, token_id in tokens.items():
        results.append(
            await run_validation_test(
                f"Get price info for {name}",
                get_token_price_info,
                token_id
            )
        )
    
    # Test price chart
    results.append(
        await run_validation_test(
            "Get price chart for SigUSD (7 days)",
            get_token_price_chart,
            "SigUSD",
            7
        )
    )
    
    # Test liquidity pools
    results.append(
        await run_validation_test(
            "Get all liquidity pools",
            get_liquidity_pool_info
        )
    )
    
    results.append(
        await run_validation_test(
            "Get liquidity pools for SigUSD",
            get_liquidity_pool_info,
            "SigUSD"
        )
    )
    
    # Test token swap
    results.append(
        await run_validation_test(
            "Get swap info (ERG to SigUSD, 10 ERG)",
            get_token_swap_info,
            "ERG",
            "SigUSD",
            10.0
        )
    )
    
    results.append(
        await run_validation_test(
            "Get swap info (SigUSD to NETA, 50 SigUSD)",
            get_token_swap_info,
            "SigUSD",
            "NETA",
            50.0
        )
    )
    
    return results


async def validate_contract_features() -> List[Dict[str, Any]]:
    """Validate smart contract analysis features."""
    print("\n===== SMART CONTRACT FEATURES VALIDATION =====")
    results = []
    
    # Known contract addresses to test with
    # These are examples of different types of contracts on the Ergo blockchain
    contract_addresses = [
        # ErgoDEX LP contract
        "9hXmgvzndtakdSAgJ92fQ8ZjuKirYEPnQZ2KumygbrJao1rr5ko",
        # Oracle Core contract
        "2k6J5ocjeESe4cuXP6rwwq55t6cUwiyqDzNdEFgnKhwnWhttnSShZb2dodFoMjnVsRmhLTHGQGhzEmsZ4zXATnSvwrqiPHLQjwJKcXVCdP4qdmuHCuTsFJED4pRKRKpbAWmgcAaAPUUy8RC8jaqwciYmZhzM3C4pxXzrP3AiamaR98Z4qUuJk4R9RPeVgELzbsxGVYtY7eh8UC8UFTXi8kEYQNvv3pLe9Tz5cJyAr14Jo6CrKJKCFMdLqEMGdnC9yCaSKxhXJUUS7fYXXFQkYMKEjaMeU6Wn7o2gp6UJQ4qFAbs9qyk2qJ8S9UQkLDCZsGCmCjXTRKXRZbUbgFFoUjCoUpHSMGRgj6Vn9Z",
        # Auction contract
        "2mhKdna5JbZgANBzPbCrXQBVck7xQvq2z6m6HJYxkn79jjkD9fi7H9AqVZwzXyh5vwFZBS2hSD8Wf1JdADLcSGjRQVt5oXKXm1pt8MpJyQKEpPRtEMNPgH8A54CSUM1pTbpXnBJLnY8BvBaxzQUXqP7SZFs6Rer18DTcokQYx1C2pjKA6D7cP7zgZNbmCqqPybrmZGR9HmVb2VpMzwyhbrBbbQ8ZbVxKFoQgjR2xyKSctGDf1qBMbjF5sYqaRZEW7mmxsY7q8hCLCRjY3fFUaxqsQ8PYJKv3PPKwz5CM8QjV1YhtVdQkVYGwXrxegQJTzQ",
        # Treasury contract
        "2kUW5HKLdGBUZXAtz8Nc5Qmffr7kJZwjWF4zCp3cXz86FRjGt8CgKKBLtqjQRvcXkPHEVvqfS9rjhrid7i3ZXWut8QWMtwGmZUEHPKGJquXYQs1qXTG4zzJC8qQgmAn13nQkbKKvzbFRUQZGQszZnJfzYiHd6xJqG4f3LJ5EfriFKrWKXKBDCGRQrBqgeLkPbjMYhfGBZw5mKnPyLAeWZ9GHj7qTrUW4GvXVDN9nXnmsXmd4JP3eZxCYCQeQNG8kW9G6Q3kTxEYnRUarHQVDzbyPZxwwbxnzLbMRGACbQYPsZF7YVhMJVXvjiV3HEMDyr93QyHLUnCjFrEQGBVELDpWV8aTJMGVnxRNvn6R",
        # NFT sale contract
        "NTkuk55NdwCXkF1e2nCABxq7bHjtFXyFzbNDQg8HZXoB9NTVEt2P6h95abzTHEi5iveFkSNfuK4z8exS1rYHbEunD17KVMWMQZJqjY6dVELPNeEUSvZPD883mPb1o5BDpVvqyCRXH3K4zxfmXNXETfQnBJBSryuk3CrLeHdWECKxHnWpAMTEKbr7UKcjJQauZXKKUJgQ43DCyFTAVtQ1iuJLK9L7TaAdVhwwdReb2Fe68X4y4PDTvHCrRbxsEKgzVk"
    ]
    
    # Test contract analysis
    for address in contract_addresses:
        results.append(
            await run_validation_test(
                f"Analyze contract {address[:10]}...",
                analyze_smart_contract,
                address
            )
        )
    
    # Test contract statistics
    results.append(
        await run_validation_test(
            "Get contract statistics",
            get_contract_statistics
        )
    )
    
    # Test contract simulation
    results.append(
        await run_validation_test(
            "Simulate contract execution",
            simulate_contract_execution,
            contract_addresses[0],  # Use first contract address
            {
                "recipient": "9hHDQb26AjnJUXxcqriqY1mnhpLuUeC81C4pggtK7tupr92Ea1K",
                "amount": 1.0,
                "token_id": None
            }
        )
    )
    
    return results


async def generate_report(tokenomics_results: List[Dict[str, Any]], 
                         contract_results: List[Dict[str, Any]]) -> None:
    """Generate a validation report."""
    all_results = tokenomics_results + contract_results
    total_tests = len(all_results)
    successful_tests = sum(1 for r in all_results if r["success"])
    
    print("\n===== VALIDATION REPORT =====")
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success rate: {successful_tests / total_tests * 100:.1f}%")
    
    # List failed tests if any
    failed_tests = [r for r in all_results if not r["success"]]
    if failed_tests:
        print("\nFailed tests:")
        for i, test in enumerate(failed_tests, 1):
            print(f"{i}. {test['name']} - {test['result']}")
    
    # Save detailed results to file
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"validation_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "failed_tests": total_tests - successful_tests,
                    "success_rate": successful_tests / total_tests
                },
                "results": all_results
            }, f, indent=2)
        
        print(f"\nDetailed report saved to {filename}")
    except Exception as e:
        print(f"\nFailed to save report: {str(e)}")


async def main():
    """Run validation tests for new features."""
    print("=== ERGO FEATURES VALIDATION ===")
    print(f"Starting validation at {datetime.now().isoformat()}")
    
    try:
        # Run tokenomics tests
        tokenomics_results = await validate_tokenomics_features()
        
        # Run contract analysis tests
        contract_results = await validate_contract_features()
        
        # Generate report
        await generate_report(tokenomics_results, contract_results)
        
    except Exception as e:
        print(f"Validation failed with error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    # Python 3.7+ compatible asyncio run
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 