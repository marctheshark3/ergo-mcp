#!/usr/bin/env python3
"""
Test wrapper script that ensures mocks are applied before any imports.

This script injects our mocks into sys.modules before running the test runner.
"""

import sys
import os
import importlib.util

# Add the project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import our mock_logging module
mock_logging_path = os.path.join(os.path.dirname(__file__), "mock_logging.py")
spec = importlib.util.spec_from_file_location("mock_logging", mock_logging_path)
mock_logging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mock_logging)

# Replace the actual logging configuration with our mock
sys.modules["ergo_explorer.logging_config"] = mock_logging

# Now run the test runner
from tests.run_ergo_tools_tests import main

if __name__ == "__main__":
    sys.exit(main()) 