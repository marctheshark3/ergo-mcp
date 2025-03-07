#!/usr/bin/env python
"""
Simple test script to validate the refactored package structure.
"""

import importlib.util
import os

def test_imports():
    """Test importing all modules from the refactored package."""
    modules = [
        "ergo_explorer",
        "ergo_explorer.config",
        "ergo_explorer.api",
        "ergo_explorer.tools",
        "ergo_explorer.tools.address",
        "ergo_explorer.tools.transaction",
        "ergo_explorer.tools.misc",
        "ergo_explorer.resources",
        "ergo_explorer.resources.resources",
        "ergo_explorer.prompts",
        "ergo_explorer.prompts.prompts",
        "ergo_explorer.server"
    ]
    
    print("Testing imports...")
    for module_name in modules:
        try:
            # Using importlib to import modules
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                print(f"❌ Module {module_name} not found")
                continue
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"✅ Successfully imported {module_name}")
        except Exception as e:
            print(f"❌ Failed to import {module_name}: {str(e)}")
    
    print("\nTesting complete.")

if __name__ == "__main__":
    test_imports() 