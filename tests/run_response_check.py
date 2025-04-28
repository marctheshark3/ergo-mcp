#!/usr/bin/env python3
"""
Runner script for the Ergo Explorer MCP response format checker.
"""

import os
import sys
from pathlib import Path
import subprocess

def main():
    """Run the response format checker and update the documentation."""
    # Get the path to the response_format_checker.py script
    checker_path = Path(__file__).parent / "response_format_checker.py"
    
    print(f"Running response format checker from {checker_path}")
    
    # Run the checker script
    result = subprocess.run(
        [sys.executable, str(checker_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error running response format checker: {result.stderr}")
        sys.exit(1)
        
    print(result.stdout)
    print("Response format check completed.")
    print("Results written to tests/response.md")
    
    # Remind about updating ergo-mcp.md
    print("\nTo complete this task:")
    print("1. Review tests/response.md")
    print("2. Update ergo-mcp.md with findings")
    print("3. Add response format standardization to Phase 2 tasks if needed")

if __name__ == "__main__":
    main() 