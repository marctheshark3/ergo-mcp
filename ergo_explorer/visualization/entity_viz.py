"""
Visualization functions for Ergo entity identification and address clustering.
"""

from typing import Dict, Any, List
import json
import random
import html

def process_entity_data_for_viz(entity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the raw entity detection data into a format suitable for visualization.
    
    Args:
        entity_data: Raw data from identify_entities
        
    Returns:
        Processed data ready for visualization
    """
    # Extract data for visualization
    seed_address = entity_data.get("seed_address", "Unknown")
    seed_cluster_id = entity_data.get("seed_cluster_id")
    clusters = entity_data.get("clusters", {})
    relationships = entity_data.get("relationships", [])
    
    # Create cluster counts dictionary
    cluster_counts = {}
    for cluster_id in set(clusters.values()):
        cluster_counts[cluster_id] = list(clusters.values()).count(cluster_id)
    
    # Create color mapping for clusters
    color_palette = [
        "#4285F4", "#EA4335", "#FBBC05", "#34A853",  # Google colors
        "#3B5998", "#00ACEE", "#DD4B39", "#E60023",  # Social media colors
        "#9C27B0", "#673AB7", "#3F51B5", "#2196F3",  # Material design colors
        "#03A9F4", "#00BCD4", "#009688", "#4CAF50",
        "#8BC34A", "#CDDC39", "#FFEB3B", "#FFC107"
    ]
    
    # Create a stable color mapping regardless of the order
    cluster_ids = sorted(set(clusters.values()))
    color_mapping = {cluster_id: color_palette[i % len(color_palette)] 
                    for i, cluster_id in enumerate(cluster_ids)}
    
    # Add special color for seed cluster if it exists
    if seed_cluster_id:
        color_mapping[seed_cluster_id] = "#FF0000"  # Red for seed cluster
    
    # Generate nodes for each address
    nodes = []
    for address, cluster_id in clusters.items():
        is_seed = address == seed_address
        node = {
            "id": address,
            "address": address,  # Keep this for backward compatibility
            "cluster": cluster_id,
            "isSeed": is_seed,
            "value": 1,  # Default node size
            "color": color_mapping.get(cluster_id, "#999999")  # Default color if no cluster
        }
        nodes.append(node)
    
    # If we have no addresses, at least add the seed address
    if not nodes and seed_address:
        nodes.append({
            "id": seed_address,
            "address": seed_address,
            "cluster": seed_cluster_id,
            "isSeed": True,
            "value": 1,
            "color": "#FF0000"  # Red for seed address
        })
    
    # Generate links from relationships
    links = []
    for rel in relationships:
        source = rel.get("source")
        target = rel.get("target")
        strength = rel.get("strength", 1)
        
        if source and target:
            link = {
                "source": source,
                "target": target,
                "value": strength
            }
            links.append(link)
    
    # Handle the case where we have nodes but no links
    # Add some default connections to make visualization work better
    if nodes and not links and len(nodes) > 1:
        # Connect seed to first few addresses
        seed_node = next((n for n in nodes if n.get("isSeed")), nodes[0])
        for i, node in enumerate(nodes[:5]):
            if node["id"] != seed_node["id"]:
                links.append({
                    "source": seed_node["id"],
                    "target": node["id"],
                    "value": 1
                })
    
    # Create the visualization data structure
    viz_data = {
        "nodes": nodes,
        "links": links,
        "seedAddress": seed_address,
        "seedClusterId": seed_cluster_id,
        "clusterCounts": cluster_counts,
        "clusterColors": color_mapping,
        "totalAddresses": len(nodes),
        "totalClusters": len(cluster_counts)
    }
    
    return viz_data

def generate_entity_viz_html(viz_data: Dict[str, Any], debug_mode: bool = False) -> str:
    """
    Generate HTML visualization for entity clusters.
    
    Args:
        viz_data: Processed visualization data
        debug_mode: Whether to include debug information
        
    Returns:
        HTML string with visualization
    """
    # Ensure JSON data is properly escaped for inclusion in JavaScript
    viz_data_json = json.dumps(viz_data)
    viz_data_json_safe = html.escape(viz_data_json).replace("'", "\\'")
    
    # Optional debug info
    if debug_mode:
        debug_info_html = """
        <div id="debug-info" style="position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; max-width: 400px; max-height: 200px; overflow: auto;">
            <button id="toggle-debug" style="margin-bottom: 5px;">Toggle Debug</button>
            <pre id="debug-data"></pre>
        </div>
        """
    else:
        debug_info_html = ""
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entity Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: Arial, sans-serif;
        }
        
        .container {
            display: flex;
            height: 100%;
        }
        
        .sidebar {
            width: 300px;
            background-color: #f8f9fa;
            border-right: 1px solid #ddd;
            padding: 20px;
            height: 100%;
            box-sizing: border-box;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }
        
        .viz-container {
            flex: 1;
            position: relative;
            overflow: hidden;
            min-height: 600px;
        }
        
        h1, h2, h3 {
            margin-top: 0;
            color: #333;
        }
        
        .legend {
            margin-bottom: 20px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .legend-text {
            font-size: 14px;
        }
        
        .stats-container {
            margin-bottom: 20px;
        }
        
        .stats-item {
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .controls {
            margin-top: auto;
            padding-top: 20px;
        }
        
        .btn {
            padding: 8px 12px;
            background-color: #4285F4;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 8px;
            font-size: 14px;
        }
        
        .btn:hover {
            background-color: #3367d6;
        }
        
        #visualization {
            width: 100%;
            height: 100%;
            min-height: 600px;
        }
        
        .tooltip {
            position: absolute;
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            max-width: 300px;
            font-size: 12px;
            z-index: 1000;
        }
        
        .search-box {
            margin-bottom: 15px;
        }
        
        .search-box input {
            width: 100%;
            padding: 8px;
            box-sizing: border-box;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .address-list-container {
            margin-bottom: 20px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .address-list {
            font-size: 12px;
        }
        
        .address-item {
            padding: 4px 8px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
        }
        
        .address-item:hover {
            background-color: #f0f0f0;
        }
        
        .badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 12px;
            margin-left: 5px;
        }
        
        .badge-info {
            background-color: #4285F4;
            color: white;
        }
        
        .seed-indicator {
            margin-left: 5px;
            color: #EA4335;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h1>Entity Visualization</h1>
            
            <div class="stats-container">
                <h3>Statistics</h3>
                <div class="stats-item">Total Addresses: <strong id="total-addresses">0</strong></div>
                <div class="stats-item">Clusters: <strong id="total-clusters">0</strong></div>
                <div class="stats-item">Seed Address: <strong id="seed-address" style="word-break: break-all;"></strong></div>
            </div>
            
            <div class="legend">
                <h3>Clusters</h3>
                <div id="legend-items">
                    <!-- Legend items will be added here by JavaScript -->
                </div>
            </div>
                
            <div class="search-box">
                <h3>Find Address</h3>
                <input type="text" id="address-search" placeholder="Enter partial address...">
            </div>
            
            <div class="address-list-container">
                <h3>Addresses <span id="filtered-count" class="badge badge-info">0</span></h3>
                <div class="address-list" id="address-list">
                    <!-- Address items will be added here by JavaScript -->
                </div>
            </div>
            
            <div class="controls">
                <button class="btn" id="center-view">Center View</button>
                <button class="btn" id="toggle-physics">Pause Physics</button>
            </div>
        </div>
        
        <div class="viz-container">
            <div id="visualization"></div>
            <div class="tooltip" id="tooltip"></div>
            """ + debug_info_html + """
        </div>
    </div>
</div>

<script>
    // Parse the visualization data
    const vizData = JSON.parse('""" + viz_data_json_safe + """');
    
    // Log data to console for debugging
    console.log("Visualization data:", vizData);
    
    // Set up the D3.js force-directed graph
    const width = document.querySelector('.viz-container').clientWidth || 800;
    const height = document.querySelector('.viz-container').clientHeight || 600;
    
    // Create SVG container
    const svg = d3.select('#visualization')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .call(d3.zoom().on('zoom', function(event) {
            svg.attr('transform', event.transform);
        }))
        .append('g');
    
    // Create tooltip element
    const tooltip = d3.select('#tooltip');
    
    // Set up color scale for clusters
    const clusterIds = [...new Set(vizData.nodes.map(d => d.cluster))].filter(d => d !== undefined);
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10).domain(clusterIds);
    
    // Make sure nodes have initial positions
    vizData.nodes.forEach((node, i) => {
        if (node.x === undefined) {
            node.x = width / 2 + 100 * Math.cos(2 * Math.PI * i / vizData.nodes.length);
            node.y = height / 2 + 100 * Math.sin(2 * Math.PI * i / vizData.nodes.length);
        }
        
        // Make seed node larger
        if (node.isSeed) {
            node.value = 5;  // Larger value for seed node
        } else {
            node.value = 1;  // Default size
        }
    });
    
    // Create links with varying thickness
    const link = svg.append('g')
        .selectAll('line')
        .data(vizData.links)
        .enter()
        .append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', d => Math.max(Math.sqrt(d.value || 1), 1));
    
    // Create nodes with clear size and visibility
    const node = svg.append('g')
        .selectAll('circle')
        .data(vizData.nodes)
        .enter()
        .append('circle')
        .attr('r', d => d.isSeed ? 15 : Math.max(Math.sqrt(d.value) * 5, 8))
        .attr('fill', d => d.color || colorScale(d.cluster))
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Add hover effects
    node.on('mouseover', function(event, d) {
            d3.select(this)
                .attr('stroke', '#000')
                .attr('stroke-width', 3);
            
            let tooltipContent = '<div><strong>Address:</strong> ' + d.id + '</div>';
            tooltipContent += '<div><strong>Cluster:</strong> ' + (d.cluster || 'None') + '</div>';
            if (d.isSeed) {
                tooltipContent += '<div><strong>Seed Address</strong></div>';
            }
            
            tooltip
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px')
                .style('opacity', 1)
                .html(tooltipContent);
        })
        .on('mouseout', function() {
            d3.select(this)
                .attr('stroke', '#fff')
                .attr('stroke-width', 2);
            
            tooltip.style('opacity', 0);
        });
    
    // Set up force simulation with stronger forces
    const simulation = d3.forceSimulation(vizData.nodes)
        .force('link', d3.forceLink(vizData.links).id(d => d.id).distance(150))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collide', d3.forceCollide().radius(d => d.isSeed ? 40 : 20))
        .on('tick', ticked)
        .alpha(1)
        .restart();
    
    // Center view button functionality
    document.getElementById('center-view').addEventListener('click', function() {
        // Reset fixed positions for all nodes
        vizData.nodes.forEach(function(d) {
            d.fx = null;
            d.fy = null;
        });
        
        simulation
            .alpha(1)
            .restart();
    });
    
    // Toggle physics button
    let physicsEnabled = true;
    document.getElementById('toggle-physics').addEventListener('click', function() {
        physicsEnabled = !physicsEnabled;
        this.textContent = physicsEnabled ? 'Pause Physics' : 'Resume Physics';
        
        if (physicsEnabled) {
            simulation.alphaTarget(0).restart();
        } else {
            simulation.alphaTarget(0).stop();
        }
    });
    
    // Update node and link positions on each tick
    function ticked() {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
    }
    
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
        // Comment out the following lines to keep nodes fixed after dragging
        d.fx = null;
        d.fy = null;
    }
    
    // Update statistics in sidebar
    document.getElementById('total-addresses').textContent = vizData.nodes.length;
    document.getElementById('total-clusters').textContent = clusterIds.length;
    document.getElementById('seed-address').textContent = vizData.seedAddress;
    
    // Populate the cluster legend
    const legendContainer = document.getElementById('legend-items');
    
    // Find address list container
    const addressList = document.getElementById('address-list');
    const addressSearch = document.getElementById('address-search');
    const filteredCount = document.getElementById('filtered-count');
    
    function updateAddressList(filterText = '') {
        if (!addressList || !filteredCount) return;
        
        addressList.innerHTML = '';
        const lowerFilter = filterText.toLowerCase();
        const filteredNodes = vizData.nodes.filter(node => 
            !filterText || node.id.toLowerCase().includes(lowerFilter)
        );
        
        filteredCount.textContent = filteredNodes.length;
        
        filteredNodes.forEach(node => {
            const item = document.createElement('div');
            item.className = 'address-item';
            item.textContent = node.id;
            if (node.isSeed) {
                item.innerHTML += '<span class="seed-indicator">(Seed)</span>';
            }
            
            // Scroll to and highlight the node when clicking on the address
            item.addEventListener('click', () => {
                // Center view on the node
                const transform = d3.zoomIdentity
                    .translate(width/2 - node.x, height/2 - node.y)
                    .scale(1);
                    
                svg.transition().duration(750).call(d3.zoom().transform, transform);
                
                // Highlight the node
                const event = {pageX: node.x + width/2, pageY: node.y + 50};
                node.dispatchEvent(new MouseEvent('mouseover', event));
            });
            
            addressList.appendChild(item);
        });
    }
    
    // Initialize address list
    updateAddressList();
    
    // Add search functionality
    if (addressSearch) {
        addressSearch.addEventListener('input', (e) => {
            updateAddressList(e.target.value);
        });
    }
    
    // Add double-click to zoom
    svg.on('dblclick', function(event) {
        const [x, y] = d3.pointer(event);
        const transform = d3.zoomIdentity
            .translate(width/2 - x, height/2 - y)
            .scale(2);
            
        svg.transition().duration(750).call(d3.zoom().transform, transform);
    });
</script>
</body>
</html>"""
    
    return html_content 