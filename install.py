#!/usr/bin/env python
"""
Installation script for the Ergo MCP server.

This script provides a simple way to install the Ergo MCP server.
"""

import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Install the Ergo MCP server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--editable", "-e",
        help="Install in development mode",
        action="store_true",
        default=True  # Default to editable install for better development experience
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
    
    parser.add_argument(
        "--upgrade",
        help="Upgrade pip and setuptools before installation",
        action="store_true"
    )
    
    parser.add_argument(
        "--force",
        help="Force reinstallation even if package is already installed",
        action="store_true"
    )
    
    return parser.parse_args()

def check_python_version():
    """Check if Python version is compatible."""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"Error: Python 3.8+ is required. Current version is {major}.{minor}.")
        sys.exit(1)
    
    print(f"Python version: {major}.{minor} ✓")

def main():
    """Main installation function."""
    # Print welcome message
    print("=" * 60)
    print("Ergo MCP Server Installer")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Parse arguments
    args = parse_args()
    
    # Create virtual environment if requested
    python_executable = sys.executable
    if args.venv:
        venv_path = Path(args.venv_path).absolute()
        
        # Check if venv already exists
        if venv_path.exists():
            print(f"Virtual environment already exists at {venv_path}")
            overwrite = input("Do you want to overwrite it? (y/n): ")
            if overwrite.lower() == 'y':
                print(f"Removing existing virtual environment at {venv_path}...")
                import shutil
                shutil.rmtree(venv_path)
            else:
                print("Using existing virtual environment.")
        
        # Create venv if needed
        if not venv_path.exists():
            print(f"Creating virtual environment at {venv_path}...")
            try:
                subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
                print("Virtual environment created successfully ✓")
            except subprocess.CalledProcessError as e:
                print(f"Error creating virtual environment: {e}")
                sys.exit(1)
        
        # Determine the Python executable in the virtual environment
        if platform.system() == "Windows":
            python_executable = venv_path / "Scripts" / "python.exe"
        else:
            python_executable = venv_path / "bin" / "python"
            
        # Convert to string for subprocess
        python_executable = str(python_executable)
        
        # Verify venv Python works
        try:
            subprocess.check_call([python_executable, "--version"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: Failed to run Python from virtual environment")
            sys.exit(1)
            
        print(f"Using Python from virtual environment: {python_executable} ✓")
    
    # Upgrade pip and setuptools if requested
    if args.upgrade:
        print("Upgrading pip and setuptools...")
        try:
            subprocess.check_call([python_executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools"])
            print("Pip and setuptools upgraded ✓")
        except subprocess.CalledProcessError as e:
            print(f"Error upgrading pip and setuptools: {e}")
            sys.exit(1)
    
    # Install the package
    print("\nInstalling the Ergo MCP server...")
    
    install_cmd = [python_executable, "-m", "pip", "install"]
    
    if args.editable:
        install_cmd.append("-e")
        print("Installing in development mode for local changes ✓")
        
    if args.force:
        install_cmd.append("--force-reinstall")
        print("Forcing reinstallation ✓")
    
    install_cmd.append(".")
    
    try:
        subprocess.check_call(install_cmd)
        print("\n✅ Installation successful! ✅")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing package: {e}")
        print("\nTroubleshooting tips:")
        print("  - Check if you have the required Python dependencies")
        print("  - Try running as an administrator/with sudo")
        print("  - Check for errors in setup.py")
        sys.exit(1)
    
    # Verify installation
    try:
        print("\nVerifying installation...")
        # Try to import the package
        verify_cmd = [python_executable, "-c", "import ergo_explorer; print('Import successful')"]
        subprocess.check_call(verify_cmd)
        print("✅ Package import successful!")
        
        # Check if command-line entry point is working
        check_cmd = [python_executable, "-m", "pip", "list"]
        output = subprocess.check_output(check_cmd).decode()
        if "ergo-mcp" in output.lower() or "ergo_mcp" in output.lower():
            print("✅ Package installation verified in pip list")
    except (subprocess.CalledProcessError, ImportError) as e:
        print(f"⚠️ Warning: Verification failed: {e}")
        
    print("\nTo run the Ergo MCP server:")
    
    if args.venv:
        if platform.system() == "Windows":
            activate_cmd = str(venv_path / "Scripts" / "activate")
            print(f"  1. Activate the virtual environment: {activate_cmd}")
        else:
            activate_cmd = f"source {venv_path / 'bin' / 'activate'}"
            print(f"  1. Activate the virtual environment: {activate_cmd}")
        
        print("  2. Run the server: ergo-mcp")
    else:
        print("  Run the server: ergo-mcp")
    
    print("\nUse '--help' to see available options:")
    print("  ergo-mcp --help")
    
    print("\nThank you for installing Ergo MCP Server! 🚀")

if __name__ == "__main__":
    main() 