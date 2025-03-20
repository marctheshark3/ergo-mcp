#!/usr/bin/env python3
"""
Test runner for Ergo Explorer MCP tests.
"""

import os
import sys
import pytest


def main():
    """Run the test suite."""
    # Add the root directory to the Python path for imports
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, root_dir)

    # Run the tests
    args = [
        "-v",  # verbose output
        "--cov=ergo_explorer",  # coverage for ergo_explorer package
        "--cov-report=term",  # coverage report to terminal
        "--cov-report=html:coverage_html",  # coverage report to HTML
        "tests/unit/",  # path to unit tests
    ]
    
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(main()) 