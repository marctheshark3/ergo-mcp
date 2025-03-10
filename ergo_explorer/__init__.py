"""
Ergo Explorer MCP Server package.

This package provides an MCP server for exploring the Ergo blockchain.
"""

from ergo_explorer.server import mcp, run_server

# Package information
__version__ = "0.1.0"
__package_name__ = "ergo_mcp"
__description__ = "MCP server for exploring and analyzing the Ergo blockchain"
__author__ = "Ergo MCP Team"
__url__ = "https://github.com/marctheshark3/ergo-mcp"

# Public API
__all__ = ["mcp", "run_server"]
