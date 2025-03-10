"""
Command-line interface for the Ergo Explorer MCP server.

This module provides a CLI for running the Ergo Explorer MCP server.
"""

import argparse
import os
import sys
import logging
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, List

from ergo_explorer.server import run_server

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments. If None, sys.argv[1:] is used.
        
    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Ergo Explorer MCP Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--env-file", "-e",
        help="Path to .env file for configuration",
        default=".env",
        type=str
    )
    
    parser.add_argument(
        "--port", "-p",
        help="Port to run the server on",
        default=3001,
        type=int
    )
    
    parser.add_argument(
        "--host", "-H",
        help="Host to run the server on",
        default="0.0.0.0",
        type=str
    )
    
    parser.add_argument(
        "--debug", "-d",
        help="Enable debug mode",
        action="store_true"
    )
    
    return parser.parse_args(args)

def load_environment(env_file: str) -> None:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file: Path to the .env file.
    """
    env_path = Path(env_file)
    if env_path.exists():
        logger.info(f"Loading environment from {env_path}")
        load_dotenv(env_path)
    else:
        logger.warning(f"Environment file {env_path} not found, using default environment variables")

def main(args: Optional[List[str]] = None) -> None:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments. If None, sys.argv[1:] is used.
    """
    parsed_args = parse_args(args)
    
    # Set log level
    if parsed_args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Load environment variables
    load_environment(parsed_args.env_file)
    
    # Set server options from command-line args or environment variables
    port = int(os.environ.get("SERVER_PORT", parsed_args.port))
    host = os.environ.get("SERVER_HOST", parsed_args.host)
    
    try:
        logger.info(f"Starting Ergo Explorer MCP server on {host}:{port}")
        run_server(host=host, port=port)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 