#!/bin/bash
# Ergo MCP Server installation script

set -e  # Exit on any error

echo "======================================================"
echo "Ergo MCP Server Installer"
echo "======================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or newer."
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Using Python $PYTHON_VERSION"

# Check Python version
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "Error: Python 3.8+ is required. You have $PYTHON_VERSION."
    exit 1
fi

# Ask about virtual environment
read -p "Create a virtual environment? (y/n): " CREATE_VENV
if [[ $CREATE_VENV == "y" ]]; then
    # Ask for venv location
    read -p "Virtual environment location (default: .venv): " VENV_PATH
    VENV_PATH=${VENV_PATH:-.venv}
    
    # Check if venv exists
    if [ -d "$VENV_PATH" ]; then
        read -p "Virtual environment already exists. Overwrite? (y/n): " OVERWRITE_VENV
        if [[ $OVERWRITE_VENV == "y" ]]; then
            echo "Removing existing virtual environment..."
            rm -rf "$VENV_PATH"
        fi
    fi
    
    # Create venv if needed
    if [ ! -d "$VENV_PATH" ]; then
        echo "Creating virtual environment at $VENV_PATH..."
        python3 -m venv "$VENV_PATH"
    fi
    
    # Activate venv
    source "$VENV_PATH/bin/activate"
    echo "Virtual environment activated."
    
    # Upgrade pip and setuptools
    echo "Upgrading pip and setuptools..."
    pip install --upgrade pip setuptools
fi

# Install the package
echo "Installing Ergo MCP Server..."
pip install -e .

# Verify installation
echo "Verifying installation..."
if python -c "import ergo_explorer; print('Import successful')"; then
    echo "✅ Package import successful!"
    
    # Check if ergo-mcp command is available
    if command -v ergo-mcp &> /dev/null; then
        echo "✅ 'ergo-mcp' command is available in PATH"
    else
        echo "⚠️ 'ergo-mcp' command is not available in PATH"
        echo "This is normal if you installed in a virtual environment."
    fi
else
    echo "❌ Failed to import package"
fi

# Print usage instructions
echo ""
echo "To run the Ergo MCP server:"
if [[ $CREATE_VENV == "y" ]]; then
    echo "  1. Activate the virtual environment: source $VENV_PATH/bin/activate"
    echo "  2. Run the server: ergo-mcp"
else
    echo "  Run the server: ergo-mcp"
fi

echo ""
echo "Use '--help' to see available options:"
echo "  ergo-mcp --help"

echo ""
echo "Thank you for installing Ergo MCP Server! 🚀" 