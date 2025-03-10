#!/usr/bin/env python
"""
Simple installation script for the Ergo MCP server.

This is a non-interactive script that handles common installation issues.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """Run a simplified installation process."""
    print("=" * 60)
    print("Ergo MCP Server - Simple Installer")
    print("=" * 60)
    
    # Detect Python version
    python_version = ".".join(map(str, sys.version_info[:2]))
    print(f"Using Python {python_version}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or newer is required.")
        sys.exit(1)
    
    # Get the current directory
    current_dir = Path.cwd()
    print(f"Installing from: {current_dir}")
    
    # Check if we're in the right directory
    if not (current_dir / "setup.py").exists():
        print("Error: setup.py not found. Please run this script from the root directory of the project.")
        sys.exit(1)
    
    # Set up a new venv
    venv_path = current_dir / ".venv"
    if venv_path.exists():
        print(f"Removing existing virtual environment at {venv_path}")
        shutil.rmtree(venv_path)
    
    print(f"Creating fresh virtual environment at {venv_path}")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
    except subprocess.CalledProcessError:
        print("Error creating virtual environment. Trying with --without-pip option.")
        try:
            # Some systems may have issues with ensurepip
            subprocess.check_call([sys.executable, "-m", "venv", "--without-pip", str(venv_path)])
        except subprocess.CalledProcessError as e:
            print(f"Failed to create virtual environment: {e}")
            sys.exit(1)
    
    # Determine path to Python in the venv
    if os.name == "nt":  # Windows
        venv_python = venv_path / "Scripts" / "python.exe"
        venv_pip = venv_path / "Scripts" / "pip.exe"
    else:
        venv_python = venv_path / "bin" / "python"
        venv_pip = venv_path / "bin" / "pip"
    
    # Make sure the paths are strings
    venv_python = str(venv_python)
    venv_pip = str(venv_pip)
    
    # Check if pip exists in the venv
    if not os.path.exists(venv_pip):
        print("Installing pip in the virtual environment...")
        try:
            # Download get-pip.py
            get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
            get_pip_path = current_dir / "get-pip.py"
            
            print(f"Downloading pip installer from {get_pip_url}")
            import urllib.request
            urllib.request.urlretrieve(get_pip_url, get_pip_path)
            
            # Run get-pip.py
            print("Running pip installer...")
            subprocess.check_call([venv_python, str(get_pip_path)])
            
            # Clean up
            os.remove(get_pip_path)
        except Exception as e:
            print(f"Failed to install pip: {e}")
            sys.exit(1)
    
    # Upgrade pip and setuptools
    print("Upgrading pip and setuptools...")
    try:
        subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip", "setuptools"])
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to upgrade pip and setuptools: {e}")
        print("Continuing anyway...")
    
    # Install required packages
    print("Installing required packages...")
    try:
        subprocess.check_call([venv_python, "-m", "pip", "install", "wheel"])
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to install wheel: {e}")
    
    # Install the package
    print("\nInstalling Ergo MCP Server...")
    try:
        subprocess.check_call([venv_python, "-m", "pip", "install", "-e", "."])
        print("\n✅ Installation successful!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)
    
    # Verify installation
    print("\nVerifying installation...")
    try:
        output = subprocess.check_output(
            [venv_python, "-c", "import ergo_explorer; print('Import successful')"],
            stderr=subprocess.STDOUT,
            text=True
        )
        print(output.strip())
        print("✅ Package imported successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Verification failed: {e}")
        if hasattr(e, 'output'):
            print(e.output)
    
    # Print usage instructions
    print("\n" + "=" * 60)
    print("Installation complete!")
    print("=" * 60)
    
    if os.name == "nt":  # Windows
        activate_cmd = str(venv_path / "Scripts" / "activate")
    else:
        activate_cmd = f"source {venv_path / 'bin' / 'activate'}"
    
    print("\nTo use Ergo MCP Server:")
    print(f"1. Activate the virtual environment: {activate_cmd}")
    print("2. Run the server: ergo-mcp")
    print("   or: python -m ergo_explorer")
    print("\nFor more options, run: ergo-mcp --help")

if __name__ == "__main__":
    main() 