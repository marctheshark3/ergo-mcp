#!/usr/bin/env python3
"""
MCPO Endpoint Analyzer

This script analyzes the available MCPO endpoints in the Ergo Explorer MCP server
and generates a report on the implemented features and future work.

Usage:
    python mcpo_endpoints.py
"""

import os
import sys
import inspect
import importlib
from typing import Dict, List, Any, Set

# Add the project root directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the tools modules
from ergo_explorer.tools import blockchain, address, token, transaction, block, network
from ergo_explorer.tools import contracts, tokenomics, ergowatch

def get_module_functions(module) -> List[str]:
    """Get all public functions from a module."""
    return [f for f in dir(module) if not f.startswith('_') and callable(getattr(module, f))]

def analyze_functions(module, module_name: str) -> Dict[str, Any]:
    """Analyze functions in a module and extract information."""
    functions = get_module_functions(module)
    
    function_info = []
    for func_name in functions:
        func = getattr(module, func_name)
        try:
            doc = func.__doc__ or "No documentation available"
            source_file = inspect.getsourcefile(func)
            if source_file:
                source_file = os.path.basename(source_file)
            else:
                source_file = "Unknown"
                
            function_info.append({
                "name": func_name,
                "doc": doc.strip(),
                "file": source_file,
                "is_async": inspect.iscoroutinefunction(func)
            })
        except (TypeError, ValueError) as e:
            function_info.append({
                "name": func_name,
                "doc": "Error retrieving information: " + str(e),
                "file": "Unknown",
                "is_async": False
            })
    
    return {
        "module": module_name,
        "functions": function_info,
        "function_count": len(function_info)
    }

def get_unimplemented_features(prd_features: List[str], implemented: Set[str]) -> List[str]:
    """Compare PRD features with implemented features."""
    return [feature for feature in prd_features if not any(impl in feature.lower() for impl in implemented)]

def main():
    """Main function to analyze MCPO endpoints."""
    # Modules to analyze
    modules = {
        "blockchain": blockchain,
        "address": address,
        "token": token,
        "transaction": transaction,
        "block": block,
        "network": network,
        "contracts": contracts,
        "tokenomics": tokenomics,
        "ergowatch": ergowatch
    }
    
    # Analyze modules
    results = {}
    total_functions = 0
    implemented_features = set()
    
    for module_name, module in modules.items():
        module_info = analyze_functions(module, module_name)
        results[module_name] = module_info
        total_functions += module_info["function_count"]
        
        # Add function names to implemented features
        for func in module_info["functions"]:
            name_parts = func["name"].lower().split('_')
            implemented_features.update(name_parts)
    
    # PRD features from Phase 2 and 3
    prd_phase2_features = [
        "Comprehensive address information with token details",
        "Transaction categorization and analysis",
        "Support for both JSON and markdown output formats",
        "Common address interaction detection",
        "Address clustering for entity identification",
        "Transaction pattern analysis between multiple addresses",
        "Token name-based search capabilities",
        "Historical token holder distribution tracking",
        "Non-standard collection lookup mechanisms",
        "Collection marketplace statistics (listings, sales frequency)",
        "Liquidity pool analysis (balance, % locked, holder distribution)",
        "Token money flow trend analysis (inflow/outflow)",
        "Advanced token metrics calculation (RSI, momentum indicators)",
        "Comprehensive automated testing suite",
        "MCPO OpenAPI endpoint testing framework",
        "Performance optimization for data-intensive queries",
        "ErgoScript contract analysis",
        "Oracle pool integration",
        "DEX price and liquidity data"
    ]
    
    prd_phase3_features = [
        "Advanced analytics and visualization data",
        "Transaction pattern recognition",
        "Simplified transaction creation",
        "Smart contract simulation",
        "Enhanced security features"
    ]
    
    # Find unimplemented features
    unimplemented_phase2 = get_unimplemented_features(prd_phase2_features, implemented_features)
    unimplemented_phase3 = get_unimplemented_features(prd_phase3_features, implemented_features)
    
    # Print report
    print("\n" + "="*80)
    print("MCPO ENDPOINT ANALYSIS REPORT")
    print("="*80)
    
    print(f"\nTotal functions implemented: {total_functions}")
    
    print("\nFunction count by module:")
    for module_name, module_info in results.items():
        print(f"  - {module_name}: {module_info['function_count']} functions")
    
    print("\nImplemented features:")
    implemented_list = sorted(list(implemented_features))
    for feature in implemented_list:
        if len(feature) > 3:  # Skip short words
            print(f"  - {feature}")
    
    print("\nUnimplemented Phase 2 features:")
    for feature in unimplemented_phase2:
        print(f"  - {feature}")
    
    print("\nUnimplemented Phase 3 features:")
    for feature in unimplemented_phase3:
        print(f"  - {feature}")
    
    # Generate detailed report
    print("\nDetailed function listing:")
    for module_name, module_info in results.items():
        print(f"\n{module_name.upper()} MODULE ({module_info['function_count']} functions):")
        for func in module_info["functions"]:
            print(f"  - {func['name']} ({'async' if func['is_async'] else 'sync'})")
            doc_lines = func["doc"].split("\n")
            if doc_lines and doc_lines[0]:
                # Print just the first line of documentation
                print(f"    {doc_lines[0]}")
    
    # Output markdown report
    output_file = os.path.join(os.path.dirname(__file__), "mcpo_endpoint_report.md")
    with open(output_file, "w") as f:
        f.write("# MCPO Endpoint Analysis Report\n\n")
        f.write(f"Total functions implemented: **{total_functions}**\n\n")
        
        f.write("## Function count by module\n\n")
        for module_name, module_info in results.items():
            f.write(f"- **{module_name}**: {module_info['function_count']} functions\n")
        
        f.write("\n## Unimplemented Phase 2 features\n\n")
        for feature in unimplemented_phase2:
            f.write(f"- {feature}\n")
        
        f.write("\n## Unimplemented Phase 3 features\n\n")
        for feature in unimplemented_phase3:
            f.write(f"- {feature}\n")
        
        f.write("\n## Detailed function listing\n\n")
        for module_name, module_info in results.items():
            f.write(f"### {module_name.upper()} MODULE ({module_info['function_count']} functions)\n\n")
            for func in module_info["functions"]:
                f.write(f"#### {func['name']} ({'async' if func['is_async'] else 'sync'})\n\n")
                f.write(f"{func['doc']}\n\n")
        
        f.write("\n## Next steps\n\n")
        f.write("1. Implement missing Phase 2 features with highest priority\n")
        f.write("2. Develop token usage optimization for existing endpoints\n")
        f.write("3. Add comprehensive tests for all endpoints\n")
        f.write("4. Prepare for Phase 3 feature development\n")
    
    print(f"\nDetailed markdown report saved to: {output_file}")

if __name__ == "__main__":
    main() 