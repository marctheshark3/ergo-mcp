#!/usr/bin/env python3
"""
MCP Response Analyzer

This script analyzes the responses from various MCP endpoints to understand
their format, structure, and characteristics. It helps in determining a
standardized response format for the Ergo Explorer MCP integration.
"""

import os
import re
import json
import time
import requests
from datetime import datetime
from prettytable import PrettyTable

# Configuration
MCP_API_KEY = os.getenv("MCP_API_KEY")
if not MCP_API_KEY:
    print("ERROR: MCP_API_KEY environment variable not set")
    print("Please set it using: export MCP_API_KEY=your_api_key_here")
    exit(1)

# BASE_URL = "https://api.mcpai.xyz/api/v1/tools"
RESULTS_DIR = "analysis_results"
TIMEOUT = 30  # seconds

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

# List of endpoints to test
ENDPOINTS = [
    {"name": "blockchain_status", "params": {"random_string": "analysis"}},
    {"name": "blockchain_address_info", "params": {"address": "9hXmgvzndtakdVwTGjsLNVF44jRuVUQRcvXwC8Qyb1KJaXGYEGq"}},
    {"name": "get_token", "params": {"token_id": "03faf2cb329f2e90d6d23b58d91bbb6c046aa143261cc21f52fbe2824bfcbf04"}},
    {"name": "list_eips", "params": {"random_string": "analysis"}},
    {"name": "search_token", "params": {"query": "sigmaUSD"}},
]

def call_mcp_endpoint(endpoint_name, params):
    """Call an MCP endpoint and return the response with timing information."""
    url = f"{BASE_URL}/mcp_ergo_{endpoint_name}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MCP_API_KEY}"
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=params, timeout=TIMEOUT)
        end_time = time.time()
        execution_time = end_time - start_time
        
        return {
            "status_code": response.status_code,
            "content": response.text,
            "execution_time": execution_time,
            "content_type": response.headers.get('Content-Type', 'unknown'),
            "content_length": len(response.text)
        }
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        return {
            "status_code": 0,
            "content": str(e),
            "execution_time": execution_time,
            "content_type": "error",
            "content_length": len(str(e))
        }

def analyze_response_format(content):
    """Analyze the format of the response content."""
    format_analysis = {
        "contains_markdown": False,
        "contains_json": False,
        "contains_table": False,
        "is_valid_json": False,
        "has_markdown_headers": False,
        "has_markdown_lists": False,
        "has_markdown_code_blocks": False
    }
    
    # Check for Markdown elements
    if "##" in content or "#" in content:
        format_analysis["contains_markdown"] = True
        format_analysis["has_markdown_headers"] = True
    
    if "- " in content or "* " in content:
        format_analysis["contains_markdown"] = True
        format_analysis["has_markdown_lists"] = True
    
    if "```" in content:
        format_analysis["contains_markdown"] = True
        format_analysis["has_markdown_code_blocks"] = True
    
    # Check for ASCII tables
    if "+-" in content and "-+" in content:
        format_analysis["contains_table"] = True
    
    # Check for JSON content
    if "{" in content and "}" in content:
        format_analysis["contains_json"] = True
        
        # Try to extract JSON
        json_pattern = r'({[\s\S]*})'
        json_matches = re.findall(json_pattern, content)
        
        if json_matches:
            for json_str in json_matches:
                try:
                    json.loads(json_str)
                    format_analysis["is_valid_json"] = True
                    break
                except:
                    pass
    
    return format_analysis

def extract_json_structure(content):
    """Try to extract JSON structure from the content."""
    if not ("{" in content and "}" in content):
        return None
    
    # Try to find JSON objects
    json_pattern = r'({[\s\S]*})'
    json_matches = re.findall(json_pattern, content)
    
    extracted_jsons = []
    
    for json_str in json_matches:
        try:
            parsed_json = json.loads(json_str)
            # Get only the structure (keys and types)
            structure = json_structure(parsed_json)
            extracted_jsons.append(structure)
        except:
            pass
    
    return extracted_jsons if extracted_jsons else None

def json_structure(obj, parent_key=""):
    """Extract the structure of a JSON object (keys and value types)."""
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, (dict, list)):
                result[k] = json_structure(v, new_key)
            else:
                result[k] = type(v).__name__
        return result
    elif isinstance(obj, list):
        if obj and isinstance(obj[0], (dict, list)):
            return [json_structure(obj[0], parent_key + "[]")]
        else:
            return f"[{type(obj[0]).__name__}]" if obj else "[]"
    else:
        return type(obj).__name__

def analyze_all_endpoints():
    """Analyze all endpoints and generate a report."""
    results = []
    
    for endpoint in ENDPOINTS:
        print(f"Analyzing endpoint: {endpoint['name']}...")
        response = call_mcp_endpoint(endpoint["name"], endpoint["params"])
        
        # Analyze the response format
        format_analysis = analyze_response_format(response["content"])
        
        # Extract JSON structure if present
        json_structures = extract_json_structure(response["content"])
        
        # Save the full response to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{RESULTS_DIR}/{endpoint['name']}_{timestamp}.txt"
        with open(filename, "w") as f:
            f.write(f"Endpoint: {endpoint['name']}\n")
            f.write(f"Parameters: {endpoint['params']}\n")
            f.write(f"Status Code: {response['status_code']}\n")
            f.write(f"Execution Time: {response['execution_time']:.3f} seconds\n")
            f.write(f"Content Type: {response['content_type']}\n")
            f.write(f"Content Length: {response['content_length']} bytes\n")
            f.write("\n--- FORMAT ANALYSIS ---\n")
            for key, value in format_analysis.items():
                f.write(f"{key}: {value}\n")
            f.write("\n--- JSON STRUCTURES ---\n")
            if json_structures:
                f.write(json.dumps(json_structures, indent=2))
            else:
                f.write("No valid JSON structures found\n")
            f.write("\n--- FULL RESPONSE ---\n")
            f.write(response["content"])
        
        # Store results for summary report
        results.append({
            "endpoint": endpoint["name"],
            "status_code": response["status_code"],
            "execution_time": response["execution_time"],
            "content_length": response["content_length"],
            "format_analysis": format_analysis,
            "json_structures": json_structures,
            "saved_to": filename
        })
        
        # Small delay to avoid rate limiting
        time.sleep(1)
    
    return results

def generate_summary_report(results):
    """Generate a summary report of the analysis."""
    # Create a table for format analysis
    format_table = PrettyTable()
    format_table.field_names = ["Endpoint", "Status", "Time (s)", "Markdown", "JSON", "Table", "Valid JSON"]
    
    for result in results:
        format_table.add_row([
            result["endpoint"],
            result["status_code"],
            f"{result['execution_time']:.3f}",
            result["format_analysis"]["contains_markdown"],
            result["format_analysis"]["contains_json"],
            result["format_analysis"]["contains_table"],
            result["format_analysis"]["is_valid_json"]
        ])
    
    # Create statistics
    total_endpoints = len(results)
    markdown_count = sum(1 for r in results if r["format_analysis"]["contains_markdown"])
    json_count = sum(1 for r in results if r["format_analysis"]["contains_json"])
    table_count = sum(1 for r in results if r["format_analysis"]["contains_table"])
    valid_json_count = sum(1 for r in results if r["format_analysis"]["is_valid_json"])
    
    # Calculate average execution time
    avg_execution_time = sum(r["execution_time"] for r in results) / total_endpoints if total_endpoints > 0 else 0
    
    # Generate the summary report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"{RESULTS_DIR}/summary_report_{timestamp}.txt"
    
    with open(report_filename, "w") as f:
        f.write("# MCP Response Format Analysis Summary\n\n")
        f.write(f"Analysis timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Format Analysis\n\n")
        f.write(format_table.get_string())
        f.write("\n\n")
        
        f.write("## Statistics\n\n")
        f.write(f"Total endpoints analyzed: {total_endpoints}\n")
        f.write(f"Endpoints with Markdown formatting: {markdown_count} ({markdown_count/total_endpoints*100:.1f}%)\n")
        f.write(f"Endpoints with JSON content: {json_count} ({json_count/total_endpoints*100:.1f}%)\n")
        f.write(f"Endpoints with table content: {table_count} ({table_count/total_endpoints*100:.1f}%)\n")
        f.write(f"Endpoints with valid JSON: {valid_json_count} ({valid_json_count/total_endpoints*100:.1f}%)\n")
        f.write(f"Average execution time: {avg_execution_time:.3f} seconds\n\n")
        
        f.write("## JSON Structure Analysis\n\n")
        for result in results:
            if result["json_structures"]:
                f.write(f"### Endpoint: {result['endpoint']}\n\n")
                f.write("```json\n")
                f.write(json.dumps(result["json_structures"], indent=2))
                f.write("\n```\n\n")
        
        f.write("## Conclusion\n\n")
        f.write("Based on the analysis, we can see that the MCP responses vary in format. ")
        
        if markdown_count > json_count:
            f.write("The majority of responses use Markdown formatting. ")
        elif json_count > markdown_count:
            f.write("The majority of responses contain JSON data. ")
        else:
            f.write("There's an even mix of Markdown and JSON formatting. ")
            
        if table_count > 0:
            f.write(f"{table_count} out of {total_endpoints} responses contain ASCII tables. ")
            
        f.write("\n\nThis analysis should be used to design a standardized response format ")
        f.write("that can maintain the human-readable aspects while ensuring machine-parseability.")
        
    print(f"\nSummary report saved to: {report_filename}")
    
    # Print the format analysis table to the console
    print("\nFormat Analysis:")
    print(format_table)
    
    # Print statistics
    print("\nStatistics:")
    print(f"Total endpoints analyzed: {total_endpoints}")
    print(f"Endpoints with Markdown formatting: {markdown_count} ({markdown_count/total_endpoints*100:.1f}%)")
    print(f"Endpoints with JSON content: {json_count} ({json_count/total_endpoints*100:.1f}%)")
    print(f"Endpoints with table content: {table_count} ({table_count/total_endpoints*100:.1f}%)")
    print(f"Endpoints with valid JSON: {valid_json_count} ({valid_json_count/total_endpoints*100:.1f}%)")
    print(f"Average execution time: {avg_execution_time:.3f} seconds")
    
    return report_filename

if __name__ == "__main__":
    print("MCP Response Analyzer")
    print("====================")
    print(f"Analyzing {len(ENDPOINTS)} endpoints...")
    
    results = analyze_all_endpoints()
    summary_report = generate_summary_report(results)
    
    print("\nAnalysis complete!")
    print(f"Results saved to: {RESULTS_DIR}/")
    print(f"Summary report: {summary_report}") 