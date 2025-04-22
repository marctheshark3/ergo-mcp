#!/usr/bin/env python3
"""
Export Token Holders to JSON

This module makes it easy to export token holder data to JSON files.
It uses the token_holders module to fetch the data and saves it to a file.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from ergo_explorer.tools.token_holders.holders import get_token_holders

async def export_token_holders(token_id, output_dir=None):
    """Export token holders data to a JSON file."""
    # Create output directory if it doesn't exist
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"token_holders_{token_id[:8]}_{timestamp}.json"
    
    if output_dir:
        output_path = os.path.join(output_dir, filename)
    else:
        output_path = filename
    
    # Get token holders data
    print(f"Exporting token holders data for {token_id} to {output_path}...")
    try:
        # Get token holders with raw data
        holders_data = await get_token_holders(token_id, include_raw=True, include_analysis=False)
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(holders_data, f, indent=2)
        
        print(f"Successfully exported token holders data to {output_path}")
        return True
    except Exception as e:
        print(f"Error exporting token holders data: {str(e)}")
        return False

async def main_async(token_id, output_dir=None):
    """Async main function."""
    return await export_token_holders(token_id, output_dir)

def main():
    """Main function for command-line use."""
    if len(sys.argv) < 2:
        print("Usage: python -m ergo_explorer.tools.export_token_holders <token_id> [output_dir]")
        sys.exit(1)
    
    token_id = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Run the export function
    if asyncio.run(main_async(token_id, output_dir)):
        print("Export completed successfully.")
    else:
        print("Export failed.")
        sys.exit(1)

if __name__ == "__main__":
    main() 