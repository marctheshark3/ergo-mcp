#!/usr/bin/env python3
"""
Batch Export Token Holders to JSON

This script makes it easy to export token holder data for multiple tokens at once.
It uses the token_holders module to fetch the data and saves it to files.
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from typing import List
from ergo_explorer.tools.export_token_holders import export_token_holders

async def batch_export_token_holders(token_ids: List[str], output_dir: str = "token_holders"):
    """
    Export token holders data for multiple tokens.
    
    Args:
        token_ids: List of token IDs to export
        output_dir: Directory to save the exported files
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Starting batch export of {len(token_ids)} tokens to {output_dir}...")
    
    success_count = 0
    error_count = 0
    
    for i, token_id in enumerate(token_ids):
        print(f"[{i+1}/{len(token_ids)}] Processing token: {token_id}")
        try:
            result = await export_token_holders(token_id, output_dir)
            if result:
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            print(f"Error exporting token {token_id}: {str(e)}")
            error_count += 1
    
    print(f"\nBatch export complete. Success: {success_count}, Errors: {error_count}")
    return success_count, error_count

def read_token_ids_from_file(filename: str) -> List[str]:
    """Read token IDs from a file, one per line."""
    token_ids = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                # Strip whitespace and skip empty lines or comments
                line = line.strip()
                if line and not line.startswith('#'):
                    token_ids.append(line)
        return token_ids
    except Exception as e:
        print(f"Error reading token IDs from file {filename}: {str(e)}")
        return []

async def main_async(args):
    """Async main function."""
    # Get token IDs from arguments or file
    token_ids = []
    if args.file:
        token_ids = read_token_ids_from_file(args.file)
        if not token_ids:
            print(f"No valid token IDs found in file: {args.file}")
            return False
    elif args.tokens:
        token_ids = args.tokens
    else:
        print("No token IDs provided.")
        return False
    
    # Run batch export
    success, errors = await batch_export_token_holders(token_ids, args.output_dir)
    return success > 0

def main():
    """Main function for command-line use."""
    parser = argparse.ArgumentParser(description="Batch export token holders data for multiple tokens")
    
    # Add arguments
    parser.add_argument("-f", "--file", type=str, help="File containing token IDs, one per line")
    parser.add_argument("-t", "--tokens", type=str, nargs="+", help="One or more token IDs to export")
    parser.add_argument("-o", "--output-dir", type=str, default="token_holders", help="Directory to save exported files")
    
    args = parser.parse_args()
    
    # Ensure at least one of --file or --tokens is provided
    if not args.file and not args.tokens:
        parser.error("You must provide either a file (-f) or token IDs (-t)")
    
    # Run the batch export
    if asyncio.run(main_async(args)):
        print("Batch export completed successfully.")
    else:
        print("Batch export failed.")
        sys.exit(1)

if __name__ == "__main__":
    main() 