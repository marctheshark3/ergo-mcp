#!/usr/bin/env python
"""
Test script to verify the Ergo MCP package installation.

Run this script to check if the package is installed correctly and can be imported.
"""

import sys
import subprocess
import importlib.util

def check_module_exists(module_name):
    """Check if a module can be imported."""
    return importlib.util.find_spec(module_name) is not None

def main():
    """Main test function."""
    print("Testing Ergo MCP package installation...\n")
    
    # Check if the ergo_explorer module is installable
    print("1. Testing core package imports:")
    
    # Try importing core modules
    modules_to_check = [
        'ergo_explorer',
        'ergo_explorer.server',
        'ergo_explorer.cli',
    ]
    
    all_modules_ok = True
    for module in modules_to_check:
        exists = check_module_exists(module)
        status = "✅ OK" if exists else "❌ Not found"
        print(f"   - {module}: {status}")
        if not exists:
            all_modules_ok = False
    
    # Additional module checks if the base import is successful
    if check_module_exists('ergo_explorer'):
        print("\n2. Testing package metadata:")
        import ergo_explorer
        
        for attr in ['__version__', '__package_name__', '__description__', '__author__']:
            if hasattr(ergo_explorer, attr):
                print(f"   - {attr}: {getattr(ergo_explorer, attr)} ✅")
            else:
                print(f"   - {attr}: Not defined ❌")
    
        print("\n3. Testing command-line script availability:")
        try:
            # We don't need to run the actual server, just check if the script is found
            result = subprocess.run(
                ["which", "ergo-mcp"] if sys.platform != "win32" else ["where", "ergo-mcp"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"   - Command 'ergo-mcp' found at: {result.stdout.strip()} ✅")
            else:
                print("   - Command 'ergo-mcp' not found in PATH ❌")
                print("     Note: This might be expected if installed in development mode")
                print("     Try checking: python -m ergo_explorer --help")
        except Exception as e:
            print(f"   - Error checking command: {e} ❌")
    
    # Overall result
    print("\nOverall test result:")
    if all_modules_ok:
        print("✅ Ergo MCP package appears to be installed correctly!")
        print("\nYou can run the server with:")
        print("  ergo-mcp")
        print("  or")
        print("  python -m ergo_explorer")
    else:
        print("❌ Some issues were detected with the Ergo MCP package installation.")
        print("\nTroubleshooting steps:")
        print("1. Make sure you're in the project directory")
        print("2. Try reinstalling with: pip install -e .")
        print("3. Check your Python environment and PATH")

if __name__ == "__main__":
    main() 