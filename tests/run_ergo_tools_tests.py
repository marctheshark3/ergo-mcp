#!/usr/bin/env python3
"""
Ergo MCP Tools Test Runner

This script can run individual tests for Ergo MCP tools or the entire test suite.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def discover_test_files():
    """Discover all available test files."""
    api_tests_dir = Path(__file__).parent / "api"
    unit_tests_dir = Path(__file__).parent / "unit"
    
    api_tests = sorted([f.stem for f in api_tests_dir.glob("test_*.py")])
    unit_tests = sorted([f.stem for f in unit_tests_dir.glob("test_*.py")])
    
    root_tests = sorted([
        f.stem for f in Path(__file__).parent.glob("test_*.py") 
        if f.stem != "test_collection" and f.stem != "test_eip_manager"
    ])
    
    return {
        "api": api_tests,
        "unit": unit_tests,
        "root": root_tests
    }


def list_available_tests(test_files):
    """List all available tests."""
    print("\nAvailable tests:")
    
    print("\nAPI Tests:")
    for test in test_files["api"]:
        print(f"  - {test}")
    
    print("\nUnit Tests:")
    for test in test_files["unit"]:
        print(f"  - {test}")
    
    print("\nRoot Tests:")
    for test in test_files["root"]:
        print(f"  - {test}")


def run_specific_test(test_name, test_files, verbose=False):
    """Run a specific test file."""
    # Check if the test exists
    test_path = None
    test_type = None
    
    for test_type, tests in test_files.items():
        if test_name in tests:
            if test_type == "api":
                test_path = Path(__file__).parent / "api" / f"{test_name}.py"
            elif test_type == "unit":
                test_path = Path(__file__).parent / "unit" / f"{test_name}.py"
            else:  # root
                test_path = Path(__file__).parent / f"{test_name}.py"
            break
    
    if test_path is None:
        print(f"Error: Test '{test_name}' not found.")
        return 1
    
    # Run the test
    print(f"Running test: {test_name}")
    cmd = ["pytest", str(test_path)]
    if verbose:
        cmd.append("-v")
    
    result = subprocess.run(cmd)
    return result.returncode


def run_tests_by_category(category, test_files, verbose=False):
    """Run all tests in a specific category."""
    if category not in test_files:
        print(f"Error: Category '{category}' not found.")
        return 1
    
    tests = test_files[category]
    if not tests:
        print(f"No tests found in category: {category}")
        return 0
    
    print(f"Running all tests in category: {category}")
    
    if category == "api":
        test_path = Path(__file__).parent / "api"
    elif category == "unit":
        test_path = Path(__file__).parent / "unit"
    else:  # root
        # For root, we need to run each test individually
        return_code = 0
        for test in tests:
            test_path = Path(__file__).parent / f"{test}.py"
            cmd = ["pytest", str(test_path)]
            if verbose:
                cmd.append("-v")
            result = subprocess.run(cmd)
            if result.returncode != 0:
                return_code = result.returncode
        return return_code
    
    cmd = ["pytest", str(test_path)]
    if verbose:
        cmd.append("-v")
    
    result = subprocess.run(cmd)
    return result.returncode


def run_all_tests(verbose=False):
    """Run all tests."""
    print("Running all tests")
    cmd = ["pytest"]
    if verbose:
        cmd.append("-v")
    
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Ergo MCP Tools Test Runner")
    parser.add_argument("--test", help="Run a specific test file (without .py extension)")
    parser.add_argument("--category", choices=["api", "unit", "root"], help="Run all tests in a specific category")
    parser.add_argument("--list", action="store_true", help="List all available tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # Discover available test files
    test_files = discover_test_files()
    
    # List available tests
    if args.list:
        list_available_tests(test_files)
        return 0
    
    # Run a specific test
    if args.test:
        return run_specific_test(args.test, test_files, args.verbose)
    
    # Run tests by category
    if args.category:
        return run_tests_by_category(args.category, test_files, args.verbose)
    
    # Run all tests
    if args.all or (not args.test and not args.category and not args.list):
        return run_all_tests(args.verbose)
    
    # No action specified
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main()) 