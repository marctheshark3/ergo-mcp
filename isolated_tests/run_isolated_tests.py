#!/usr/bin/env python3
"""
Isolated Test Runner

This script runs tests without depending on the project's conftest.py or imports.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def discover_test_files():
    """Discover all available test files."""
    isolated_tests_dir = Path(__file__).parent
    
    isolated_tests = sorted([f.stem for f in isolated_tests_dir.glob("test_*.py")])
    
    return isolated_tests


def list_available_tests(test_files):
    """List all available tests."""
    print("\nAvailable isolated tests:")
    
    for test in test_files:
        print(f"  - {test}")


def run_specific_test(test_name, verbose=False):
    """Run a specific test file."""
    # Check if the test exists
    test_path = Path(__file__).parent / f"{test_name}.py"
    
    if not test_path.exists():
        print(f"Error: Test '{test_name}' not found.")
        return 1
    
    # Run the test
    print(f"Running isolated test: {test_name}")
    cmd = ["python", "-m", "pytest", str(test_path)]
    if verbose:
        cmd.append("-v")
    
    result = subprocess.run(cmd)
    return result.returncode


def run_all_tests(verbose=False):
    """Run all tests."""
    print("Running all isolated tests")
    
    test_path = Path(__file__).parent
    cmd = ["python", "-m", "pytest", str(test_path)]
    if verbose:
        cmd.append("-v")
    
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Isolated Test Runner")
    parser.add_argument("--test", help="Run a specific test file (without .py extension)")
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
        return run_specific_test(args.test, args.verbose)
    
    # Run all tests
    if args.all or (not args.test and not args.list):
        return run_all_tests(args.verbose)
    
    # No action specified
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main()) 