#!/usr/bin/env python
"""
Installation script for the Ergo MCP server.

This script provides a simple way to install the Ergo MCP server.
"""

import os
import sys
import subprocess
import argparse

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Install the Ergo MCP server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--editable", "-e",
        help="Install in development mode",
        action="store_true"
    )
    
    parser.add_argument(
        "--venv", "-v",
        help="Create and use a virtual environment",
        action="store_true"
    )
    
    parser.add_argument(
        "--venv-path",
        help="Path to the virtual environment",
        default=".venv",
        type=str
    )
    
    return parser.parse_args()

def main():
    """Main installation function."""
    args = parse_args()
    
    # Create virtual environment if requested
    if args.venv:
        print(f"Creating virtual environment at {args.venv_path}...")
        subprocess.check_call([sys.executable, "-m", "venv", args.venv_path])
        
        # Determine the Python executable in the virtual environment
        if os.name == "nt":  # Windows
            python_executable = os.path.join(args.venv_path, "Scripts", "python.exe")
        else:  # Unix/Linux/macOS
            python_executable = os.path.join(args.venv_path, "bin", "python")
        
        print("Activating virtual environment...")
        # We can't activate the virtual environment in this process,
        # but we can use the Python from the virtual environment
    else:
        # Use the current Python executable
        python_executable = sys.executable
    
    # Install the package
    print("Installing the Ergo MCP server...")
    install_cmd = [python_executable, "-m", "pip", "install"]
    if args.editable:
        install_cmd.append("-e")
    install_cmd.append(".")
    
    subprocess.check_call(install_cmd)
    
    print("\nInstallation complete!")
    print("\nTo run the Ergo MCP server:")
    
    if args.venv:
        if os.name == "nt":  # Windows
            activate_cmd = os.path.join(args.venv_path, "Scripts", "activate")
            print(f"  1. Activate the virtual environment: {activate_cmd}")
        else:  # Unix/Linux/macOS
            activate_cmd = f"source {os.path.join(args.venv_path, 'bin', 'activate')}"
            print(f"  1. Activate the virtual environment: {activate_cmd}")
        
        print("  2. Run the server: ergo-mcp")
    else:
        print("  Run the server: ergo-mcp")
    
    print("\nUse '--help' to see available options:")
    print("  ergo-mcp --help")

if __name__ == "__main__":
    main() 