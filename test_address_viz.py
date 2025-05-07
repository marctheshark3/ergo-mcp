"""
Test script for address interaction visualization.
"""

import asyncio
import json
import os
from ergo_explorer.tools.address import get_common_interactions
from ergo_explorer.visualization.address_viz import (
    process_interaction_data_for_viz,
    generate_interaction_viz_html
)

async def test_visualization():
    # Test address - Ergo Foundation
    address = '9gUDVVx75KyZ783YLECKngb1wy8KVwEfk3byjdfjUyDVAELAPUN'
    
    print(f"Analyzing interactions for {address}...")
    
    # Get the interaction data
    interaction_data = await get_common_interactions(
        address=address, 
        limit=20,
        min_interactions=2, 
        verbose=True
    )
    
    print(f"Found {len(interaction_data['common_interactions'])} common interactions")
    
    # Process for visualization
    viz_data = process_interaction_data_for_viz(interaction_data)
    print(f"Visualization data contains {len(viz_data['nodes'])} nodes and {len(viz_data['edges'])} edges")
    
    # Generate HTML
    html = generate_interaction_viz_html(interaction_data)
    print(f"Generated HTML visualization ({len(html)} characters)")
    
    # Save the HTML file
    output_path = "address_interaction_viz.html"
    with open(output_path, "w") as f:
        f.write(html)
    
    print(f"Visualization saved to {os.path.abspath(output_path)}")
    
    # Also save the raw data for reference
    with open("address_interaction_data.json", "w") as f:
        json.dump(interaction_data, f, indent=2)
    
    print("Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_visualization()) 