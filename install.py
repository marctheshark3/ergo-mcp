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
import shutil
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
        action="store_true",
        default=True  # Default to upgrading pip
    )
    
    parser.add_argument(
        "--force",
        help="Force reinstallation even if package is already installed",
        action="store_true"
    )
    
    parser.add_argument(
        "--no-interactive",
        help="Run in non-interactive mode (no prompts)",
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

def ensure_pip(python_executable):
    """Ensure pip is installed in the environment."""
    # Check if pip is available
    try:
        subprocess.check_call(
            [python_executable, "-m", "pip", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Pip is available ✓")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Pip is not available in this environment. Attempting to install...")
        
        # Try to install pip
        try:
            # Download get-pip.py
            subprocess.check_call(
                [python_executable, "-c", "import urllib.request; urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')"]
            )
            
            # Run get-pip.py
            subprocess.check_call([python_executable, "get-pip.py"])
            
            # Clean up
            if os.path.exists("get-pip.py"):
                os.remove("get-pip.py")
                
            print("Pip installed successfully ✓")
            return True
        except Exception as e:
            print(f"Failed to install pip: {e}")
            return False

def setup_venv(venv_path, force=False):
    """Set up a virtual environment and return the path to its Python executable."""
    venv_path = Path(venv_path).absolute()
    
    # Check if venv already exists
    if venv_path.exists() and force:
        print(f"Removing existing virtual environment at {venv_path}...")
        shutil.rmtree(venv_path)
    
    # Create venv if needed
    if not venv_path.exists():
        print(f"Creating virtual environment at {venv_path}...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
            print("Virtual environment created successfully ✓")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
    else:
        print(f"Using existing virtual environment at {venv_path}")
    
    # Determine the Python executable in the virtual environment
    if platform.system() == "Windows":
        python_executable = venv_path / "Scripts" / "python.exe"
    else:
        python_executable = venv_path / "bin" / "python"
    
    # Convert to string for subprocess
    python_executable = str(python_executable)
    
    # Verify venv Python works
    try:
        result = subprocess.run(
            [python_executable, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print(f"Using Python from virtual environment: {result.stdout.strip()} ✓")
        else:
            raise subprocess.CalledProcessError(result.returncode, result.args)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error: Virtual environment Python not working: {e}")
        sys.exit(1)
            
    return python_executable

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
        # Ask for confirmation in interactive mode
        if not args.no_interactive and os.path.exists(args.venv_path):
            overwrite = input(f"Virtual environment already exists at {args.venv_path}. Overwrite? (y/n): ")
            if overwrite.lower() == 'y':
                python_executable = setup_venv(args.venv_path, force=True)
            else:
                python_executable = setup_venv(args.venv_path, force=False)
        else:
            python_executable = setup_venv(args.venv_path, force=args.force)
    
    # Ensure pip is available
    if not ensure_pip(python_executable):
        print("Cannot proceed without pip. Please install pip manually and try again.")
        sys.exit(1)
    
    # Upgrade pip and setuptools if requested
    if args.upgrade:
        print("Upgrading pip and setuptools...")
        try:
            subprocess.check_call([python_executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools"])
            print("Pip and setuptools upgraded ✓")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Error upgrading pip and setuptools: {e}")
            print("Continuing with installation...")
    
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
        
        # Try to get more information about the error
        print("\nAttempting to get more information about the error:")
        try:
            error_output = subprocess.check_output(
                [python_executable, "-m", "pip", "install", "-e", ".", "--verbose"],
                stderr=subprocess.STDOUT,
                text=True
            )
            print(error_output)
        except subprocess.CalledProcessError as verbose_e:
            if verbose_e.output:
                print(verbose_e.output)
        
        print("\nTroubleshooting tips:")
        print("  - Check if you have the required Python dependencies")
        print("  - Try manually running: pip install -e .")
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
            activate_cmd = str(Path(args.venv_path) / "Scripts" / "activate")
            print(f"  1. Activate the virtual environment: {activate_cmd}")
        else:
            activate_cmd = f"source {Path(args.venv_path) / 'bin' / 'activate'}"
            print(f"  1. Activate the virtual environment: {activate_cmd}")
        
        print("  2. Run the server: ergo-mcp")
    else:
        print("  Run the server: ergo-mcp")
    
    print("\nUse '--help' to see available options:")
    print("  ergo-mcp --help")
    
    print("\nThank you for installing Ergo MCP Server! 🚀")

if __name__ == "__main__":
    main() 