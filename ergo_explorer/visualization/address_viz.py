"""
Visualization functions for Ergo address interactions.
"""

from typing import Dict, Any, List
import json

def process_interaction_data_for_viz(interaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the raw interaction data into a format suitable for visualization.
    
    Args:
        interaction_data: Raw data from get_common_interactions
        
    Returns:
        Processed data ready for visualization
    """
    # Extract the common interactions
    common_interactions = interaction_data.get("common_interactions", [])
    
    # Create nodes
    nodes = [{
        "id": "center",
        "label": interaction_data.get("address", "Unknown"),
        "type": "main",
        "size": 25,
    }]
    
    # Create edges
    edges = []
    
    # Process each interaction
    for idx, interaction in enumerate(common_interactions):
        address = interaction.get("address", f"unknown_{idx}")
        node_id = f"node_{idx}"
        
        # Determine node type based on classification
        node_type = "default"
        if interaction.get("is_dex", False):
            node_type = "dex"
        elif interaction.get("is_smartcontract", False):
            node_type = "contract"
        elif interaction.get("is_p2p", False):
            node_type = "p2p"
        elif interaction.get("is_recurring", False):
            node_type = "recurring"
            
        # Calculate node size based on interaction count (min 5, max 20)
        interaction_count = interaction.get("incoming_count", 0) + interaction.get("outgoing_count", 0)
        node_size = min(20, max(5, 5 + interaction_count))
        
        # Create node
        nodes.append({
            "id": node_id,
            "label": interaction.get("formatted_address", address),
            "type": node_type,
            "size": node_size,
            "title": interaction.get("name", "") or ("Known: " + interaction.get("type", "Unknown")) if interaction.get("name") or interaction.get("type") else None,
        })
        
        # Create edges
        incoming = interaction.get("incoming_count", 0)
        outgoing = interaction.get("outgoing_count", 0)
        
        if incoming > 0:
            edges.append({
                "id": f"edge_in_{idx}",
                "source": node_id,
                "target": "center",
                "width": min(5, max(1, incoming / 5)),
                "count": incoming
            })
            
        if outgoing > 0:
            edges.append({
                "id": f"edge_out_{idx}",
                "source": "center",
                "target": node_id,
                "width": min(5, max(1, outgoing / 5)),
                "count": outgoing
            })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": interaction_data.get("statistics", {})
    }

def generate_interaction_viz_html(interaction_data: Dict[str, Any]) -> str:
    """
    Generate an HTML visualization of address interactions using D3.js.
    
    Args:
        interaction_data: Raw data from get_common_interactions
        
    Returns:
        HTML string containing the visualization
    """
    # Process the data for visualization
    viz_data = process_interaction_data_for_viz(interaction_data)
    
    # Convert data to JSON for embedding in HTML
    viz_data_json = json.dumps(viz_data)
    
    # JavaScript code with template literals properly escaped
    js_code = """
    // The visualization data
    const data = GRAPH_DATA_PLACEHOLDER;
    
    // Create a force-directed graph
    const width = 900;
    const height = 600;
    
    const svg = d3.select("#chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
        
    const tooltip = d3.select("#tooltip");
    
    // Create a force simulation
    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.edges).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2));
        
    // Create links
    const link = svg.append("g")
        .selectAll("line")
        .data(data.edges)
        .enter().append("line")
        .attr("class", "link")
        .attr("stroke-width", d => d.width || 1);
        
    // Create nodes
    const node = svg.append("g")
        .selectAll("circle")
        .data(data.nodes)
        .enter().append("circle")
        .attr("class", d => "node " + d.type)
        .attr("r", d => d.size || 5)
        .on("mouseover", (event, d) => {
            // Show tooltip with node info
            const incoming = data.edges.filter(e => e.target === d.id).map(e => e.count || 0).reduce((a, b) => a + b, 0);
            const outgoing = data.edges.filter(e => e.source === d.id).map(e => e.count || 0).reduce((a, b) => a + b, 0);
            
            tooltip.html(`
                <div><strong>${d.label}</strong></div>
                <div>Type: ${d.type}</div>
                ${d.title ? `<div>${d.title}</div>` : ''}
                <div>Incoming: ${incoming}</div>
                <div>Outgoing: ${outgoing}</div>
            `)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 20) + "px")
            .style("opacity", 1);
        })
        .on("mouseout", () => {
            tooltip.style("opacity", 0);
        })
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));
            
    // Add labels to the nodes
    const label = svg.append("g")
        .selectAll("text")
        .data(data.nodes)
        .enter().append("text")
        .text(d => d.label)
        .attr("font-size", 10)
        .attr("dx", 12)
        .attr("dy", 4);
        
    // Update positions on simulation tick
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
            
        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
            
        label
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    });
    
    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    """
    
    # Replace placeholder with actual data
    js_code = js_code.replace('GRAPH_DATA_PLACEHOLDER', viz_data_json)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Ergo Address Interaction Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        #chart {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin: 0 auto;
            width: 900px;
            height: 600px;
        }}
        h1, h2 {{
            text-align: center;
            color: #333;
        }}
        .node {{
            stroke: #fff;
            stroke-width: 1.5px;
            cursor: pointer;
        }}
        .node.main {{
            fill: #ff7f0e;
        }}
        .node.dex {{
            fill: #1f77b4;
        }}
        .node.contract {{
            fill: #2ca02c;
        }}
        .node.p2p {{
            fill: #d62728;
        }}
        .node.recurring {{
            fill: #9467bd;
        }}
        .node.default {{
            fill: #7f7f7f;
        }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
        }}
        .legend {{
            margin: 20px auto;
            width: 600px;
            display: flex;
            justify-content: space-between;
            background-color: white;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        .legend-item {{
            display: flex;
            align-items: center;
        }}
        .legend-color {{
            width: 15px;
            height: 15px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }}
        .tooltip {{
            position: absolute;
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
        }}
        .stats {{
            margin: 20px auto;
            width: 800px;
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        .stat-item {{
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-weight: bold;
            float: right;
        }}
    </style>
</head>
<body>
    <h1>Ergo Address Interaction Visualization</h1>
    <p style="text-align: center;">Address: <strong>{interaction_data.get("address", "Unknown")}</strong></p>
    
    <div class="legend">
        <div class="legend-item"><div class="legend-color" style="background-color: #ff7f0e;"></div> Main Address</div>
        <div class="legend-item"><div class="legend-color" style="background-color: #1f77b4;"></div> DEX</div>
        <div class="legend-item"><div class="legend-color" style="background-color: #2ca02c;"></div> Smart Contract</div>
        <div class="legend-item"><div class="legend-color" style="background-color: #d62728;"></div> P2P</div>
        <div class="legend-item"><div class="legend-color" style="background-color: #9467bd;"></div> Recurring</div>
    </div>
    
    <div id="chart"></div>
    
    <div class="tooltip" id="tooltip"></div>
    
    <div class="stats">
        <h2>Statistics</h2>
        <div class="stats-grid">
            <div class="stat-item">
                Transactions Analyzed <span class="stat-value">{viz_data["stats"].get("total_transactions_analyzed", 0)}</span>
            </div>
            <div class="stat-item">
                Unique Addresses <span class="stat-value">{viz_data["stats"].get("unique_addresses", 0)}</span>
            </div>
            <div class="stat-item">
                Total Volume <span class="stat-value">{viz_data["stats"].get("total_volume_erg", 0):.4f} ERG</span>
            </div>
            <div class="stat-item">
                First Transaction <span class="stat-value">{viz_data["stats"].get("first_tx_date", "Unknown")}</span>
            </div>
        </div>
    </div>
    
    <script>
{js_code}
    </script>
</body>
</html>
"""
    return html 