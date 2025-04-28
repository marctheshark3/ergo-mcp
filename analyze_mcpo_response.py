#!/usr/bin/env python
"""
Analyze MCPO responses to understand their format.

This script sends requests to various MCPO endpoints and analyzes the response format
to help diagnose issues with the expected JSON format versus the actual responses.
"""

import os
import json
import requests
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
if os.path.exists(".env"):
    load_dotenv()
    logger.info("Loaded environment variables from .env file")

# Get API key for authorization
MCPO_API_KEY = os.environ.get("MCPO_API_KEY", "hello")
logger.info(f"Using MCPO API key: {MCPO_API_KEY[:4]}***")

# Base URL for MCPO
BASE_URL = "http://localhost:3003"
TIMEOUT = 10

# Headers with API key
HEADERS = {
    "Authorization": f"Bearer {MCPO_API_KEY}",
    "Content-Type": "application/json"
}

# List of endpoints to test
ENDPOINTS = [
    {
        "name": "blockchain_status",
        "params": {}
    },
    {
        "name": "get_block_by_height",
        "params": {"height": 1000000}
    },
    {
        "name": "get_token",
        "params": {"token_id": "d71693c49a84fbbecd4908c94813b46514b18b67a99952dc1e6e4791556de413"}
    },
    {
        "name": "list_eips",
        "params": {}
    },
    {
        "name": "blockchain_address_info",
        "params": {"address": "9hHDQb26AjnJUXxcqriqY1mnhpLuUeC81C4pggtK7tupr92Ea1K"}
    }
]

def analyze_response(endpoint_name: str, raw_response: Any) -> Dict[str, Any]:
    """Analyze the format and content of a response."""
    analysis = {
        "endpoint": endpoint_name,
        "type": type(raw_response).__name__,
        "is_json": False,
        "has_standard_fields": False,
        "content_preview": str(raw_response)[:100] + "..." if len(str(raw_response)) > 100 else str(raw_response),
        "metadata": {}
    }
    
    # Check if it's a string that might be JSON
    if isinstance(raw_response, str):
        try:
            json_data = json.loads(raw_response)
            analysis["is_json"] = True
            analysis["parsed_json"] = json_data
        except json.JSONDecodeError:
            analysis["is_json"] = False
    
    # Check if it's a dictionary (already parsed JSON)
    if isinstance(raw_response, dict):
        analysis["is_json"] = True
        
        # Check for standard fields
        standard_fields = ["status", "data", "metadata"]
        present_fields = [field for field in standard_fields if field in raw_response]
        analysis["has_standard_fields"] = len(present_fields) == len(standard_fields)
        analysis["present_fields"] = present_fields
        
        # Add structure info
        for key, value in raw_response.items():
            analysis["metadata"][key] = {
                "type": type(value).__name__,
                "preview": str(value)[:50] + "..." if isinstance(value, (str, list, dict)) and len(str(value)) > 50 else value
            }
    
    return analysis

def test_endpoint(endpoint_info: Dict[str, Any]) -> Dict[str, Any]:
    """Test a specific endpoint and analyze its response."""
    endpoint_name = endpoint_info["name"]
    params = endpoint_info["params"]
    url = f"{BASE_URL}/{endpoint_name}"
    
    logger.info(f"Testing endpoint: {endpoint_name}")
    
    try:
        response = requests.post(url, json=params, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        
        # Try to parse as JSON
        try:
            data = response.json()
            logger.info(f"Successfully parsed JSON response from {endpoint_name}")
            return analyze_response(endpoint_name, data)
        except json.JSONDecodeError:
            # If not JSON, analyze as text
            logger.info(f"Non-JSON response from {endpoint_name}")
            return analyze_response(endpoint_name, response.text)
            
    except requests.RequestException as e:
        logger.error(f"Error testing {endpoint_name}: {str(e)}")
        return {
            "endpoint": endpoint_name,
            "error": str(e)
        }

def main():
    """Test all endpoints and generate a summary report."""
    results = []
    
    for endpoint_info in ENDPOINTS:
        result = test_endpoint(endpoint_info)
        results.append(result)
        
    # Generate a summary
    print("\n" + "=" * 50)
    print("MCPO RESPONSE ANALYSIS SUMMARY")
    print("=" * 50)
    
    for result in results:
        endpoint = result.get("endpoint", "Unknown")
        print(f"\nEndpoint: {endpoint}")
        
        if "error" in result:
            print(f"  Error: {result['error']}")
            continue
            
        print(f"  Response Type: {result['type']}")
        print(f"  Is JSON: {result['is_json']}")
        print(f"  Has Standard Fields: {result.get('has_standard_fields', False)}")
        if result.get('present_fields'):
            print(f"  Present Fields: {', '.join(result['present_fields'])}")
        print(f"  Content Preview: {result['content_preview']}")
        
    # Save detailed results to a file
    with open("mcpo_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info("Analysis complete. Detailed results saved to mcpo_analysis_results.json")

if __name__ == "__main__":
    main() 