#!/usr/bin/env python3
"""
Response Format Checker for Ergo Explorer MCP.

This script runs all Ergo MCP endpoints and documents their response formats
to identify if they're returning markdown instead of JSON. It generates a 
response.md file containing the format of each endpoint response.
"""

import json
import os
import sys
import time
import requests
from pathlib import Path
import logging
from typing import Dict, List, Any, Union, Optional
import markdown2
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
if os.path.exists(".env"):
    load_dotenv()
    logger.info("Loaded environment variables from .env file")

# Get API key for authorization
MCPO_API_KEY = os.environ.get("MCPO_API_KEY", "hello")  # Default to "hello" if not set
logger.info(f"Using MCPO API key: {MCPO_API_KEY[:4]}***")

# Load test configuration
def load_config():
    """Load test configuration from JSON file."""
    config_path = Path(__file__).parent / "config" / "test_config.json"
    with open(config_path, "r") as f:
        return json.load(f)

CONFIG = load_config()
BASE_URL = CONFIG["general"]["base_url"]
TIMEOUT = CONFIG["general"]["timeout"]

def load_endpoint_params():
    """Load endpoint parameters from configuration."""
    params_path = Path(__file__).parent / "config" / "endpoint_params.json"
    with open(params_path, "r") as f:
        return json.load(f)

ENDPOINT_PARAMS = load_endpoint_params()

# Define headers with API key for all requests
HEADERS = {
    "Authorization": f"Bearer {MCPO_API_KEY}",
    "Content-Type": "application/json"
}

def detect_response_type(response_text: str) -> str:
    """
    Detect if the response is JSON, Markdown, or something else.
    
    Args:
        response_text: The raw response text
        
    Returns:
        String indicating the detected type: "json", "markdown", or "unknown"
    """
    # Try to parse as JSON
    try:
        json.loads(response_text)
        return "json"
    except json.JSONDecodeError:
        pass
    
    # Check for markdown indicators
    markdown_indicators = [
        "# ", "## ", "### ", "#### ", "##### ", "###### ",  # Headers
        "- ", "* ", "1. ",  # Lists
        "|", "---",  # Tables
        "```", "~~~",  # Code blocks
        "**", "__",  # Bold
        "_", "*"  # Italic (this is weaker evidence)
    ]
    
    # Count markdown indicators
    indicators_found = sum(1 for indicator in markdown_indicators if indicator in response_text)
    
    # If multiple markdown indicators are found, it's likely markdown
    if indicators_found >= 2:
        return "markdown"
    
    return "unknown"

def format_for_markdown(data: Any) -> str:
    """Format data for inclusion in markdown document."""
    if isinstance(data, (dict, list)):
        return f"```json\n{json.dumps(data, indent=2)}\n```"
    return f"`{data}`"

def test_endpoint_response(
    endpoint_name: str, 
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Test the response format of a specific endpoint.
    
    Args:
        endpoint_name: Name of the endpoint to test
        params: Parameters to send to the endpoint
        
    Returns:
        Dictionary with response information
    """
    url = f"{BASE_URL}/{endpoint_name}"
    result = {
        "endpoint": endpoint_name,
        "params": params,
        "response_type": None,
        "raw_response": None,
        "status_code": None,
        "error": None,
        "response_excerpt": None,
        "execution_time_ms": None
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=params, headers=HEADERS, timeout=TIMEOUT)
        end_time = time.time()
        
        result["status_code"] = response.status_code
        result["execution_time_ms"] = round((end_time - start_time) * 1000, 2)
        
        # Store raw response
        result["raw_response"] = response.text
        
        # Get excerpt of response for documentation
        if len(response.text) > 2000:
            result["response_excerpt"] = response.text[:2000] + "..."
        else:
            result["response_excerpt"] = response.text
        
        # Detect response type
        result["response_type"] = detect_response_type(response.text)
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def generate_response_markdown(results: List[Dict[str, Any]]) -> str:
    """
    Generate markdown documentation of endpoint responses.
    
    Args:
        results: List of endpoint response results
        
    Returns:
        Markdown formatted documentation
    """
    markdown = "# Ergo Explorer MCP Response Format Documentation\n\n"
    markdown += "This document contains the response format analysis for all Ergo Explorer MCP endpoints.\n\n"
    
    # Add summary table
    markdown += "## Response Format Summary\n\n"
    markdown += "| Endpoint | Response Type | Status Code | Execution Time (ms) |\n"
    markdown += "|----------|--------------|-------------|--------------------|\n"
    
    for result in results:
        markdown += f"| `{result['endpoint']}` | {result['response_type']} | {result['status_code']} | {result['execution_time_ms']} |\n"
    
    # Add detailed results for each endpoint
    markdown += "\n## Detailed Endpoint Responses\n\n"
    
    for result in results:
        markdown += f"### {result['endpoint']}\n\n"
        markdown += f"**Parameters:** {format_for_markdown(result['params'])}\n\n"
        markdown += f"**Response Type:** {result['response_type']}\n\n"
        markdown += f"**Status Code:** {result['status_code']}\n\n"
        
        if result["error"]:
            markdown += f"**Error:** {result['error']}\n\n"
            
        markdown += "**Response Excerpt:**\n\n"
        
        if result["response_type"] == "json":
            try:
                # Pretty print the JSON
                json_data = json.loads(result["response_excerpt"])
                markdown += f"```json\n{json.dumps(json_data, indent=2)}\n```\n\n"
            except json.JSONDecodeError:
                markdown += f"```\n{result['response_excerpt']}\n```\n\n"
        else:
            markdown += f"```\n{result['response_excerpt']}\n```\n\n"
    
    # Add recommendations section
    markdown += "## Response Format Recommendations\n\n"
    markdown += "Based on the above findings, here are recommendations for standardizing response formats:\n\n"
    
    # Determine if there are mixed formats
    response_types = set(result["response_type"] for result in results)
    
    if len(response_types) > 1:
        markdown += "**There are inconsistencies in response formats across endpoints.** Some endpoints return "
        markdown += ", ".join(f"'{rtype}'" for rtype in response_types) + ".\n\n"
        markdown += "Recommendation: Standardize all responses to use a consistent JSON format with the following structure:\n\n"
    elif "json" in response_types:
        markdown += "All endpoints are returning JSON, which is the recommended format. However, the structure should be standardized as follows:\n\n"
    elif "markdown" in response_types:
        markdown += "All endpoints are returning Markdown. This should be changed to JSON for better interoperability with AI tools.\n\n"
        markdown += "Recommendation: Convert all responses to use a consistent JSON format with the following structure:\n\n"
    
    markdown += "```json\n{\n  \"status\": \"success\",\n  \"data\": {\n    // Endpoint-specific data\n  },\n  \"metadata\": {\n    \"execution_time_ms\": 123,\n    \"result_size_bytes\": 456,\n    \"is_truncated\": false,\n    \"token_estimate\": 789\n  }\n}\n```\n\n"
    
    return markdown

def main():
    """Run the response format checker on all endpoints."""
    results = []
    
    logger.info(f"Testing endpoint responses for {BASE_URL}")
    
    # Process each endpoint category
    for category, endpoints in ENDPOINT_PARAMS.items():
        logger.info(f"Testing {category}...")
        
        for endpoint_name, endpoint_config in endpoints.items():
            if not endpoint_config["valid_params"]:
                logger.warning(f"No valid parameters for {endpoint_name}, skipping")
                continue
                
            params = endpoint_config["valid_params"][0]
            logger.info(f"Testing endpoint: {endpoint_name}")
            
            result = test_endpoint_response(endpoint_name, params)
            results.append(result)
            
            logger.info(f"Response type: {result['response_type']}, Status: {result['status_code']}")
    
    # Generate markdown documentation
    markdown_content = generate_response_markdown(results)
    
    # Write markdown to file
    output_path = Path(__file__).parent / "response.md"
    with open(output_path, "w") as f:
        f.write(markdown_content)
    
    logger.info(f"Response documentation written to {output_path}")
    
    # Calculate statistics
    total_endpoints = len(results)
    json_count = sum(1 for r in results if r["response_type"] == "json")
    markdown_count = sum(1 for r in results if r["response_type"] == "markdown")
    unknown_count = sum(1 for r in results if r["response_type"] == "unknown")
    success_count = sum(1 for r in results if r["status_code"] == 200)
    
    logger.info(f"Summary: {total_endpoints} endpoints tested")
    logger.info(f"JSON: {json_count}, Markdown: {markdown_count}, Unknown: {unknown_count}")
    logger.info(f"Success: {success_count}, Failed: {total_endpoints - success_count}")
    
    # Return summary for updating ergo-mcp.md
    return {
        "total": total_endpoints,
        "json": json_count,
        "markdown": markdown_count,
        "unknown": unknown_count,
        "success": success_count
    }

if __name__ == "__main__":
    main() 