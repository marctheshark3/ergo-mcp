#!/usr/bin/env python3
"""
MCP Response Standardizer

This module provides tools to standardize the varied response formats from the MCP API
into a consistent JSON structure for improved integration and usability.
"""

import json
import re
import datetime
import sys
import os


class MCPResponseStandardizer:
    """
    A class to standardize MCP API responses into a consistent JSON format
    regardless of the original format (JSON, Markdown, text, or mixed).
    """

    def __init__(self, debug=False):
        """
        Initialize the standardizer.

        Args:
            debug (bool): Whether to print debug information during processing
        """
        self.debug = debug

    def log(self, message):
        """Print debug messages if debug mode is enabled."""
        if self.debug:
            print(f"[DEBUG] {message}")

    def detect_format(self, content):
        """
        Detect the format of the response content.

        Args:
            content (str): The response content

        Returns:
            str: The detected format (json, markdown, text, or mixed)
        """
        # Check if it's valid JSON
        try:
            json.loads(content)
            return "json"
        except json.JSONDecodeError:
            pass

        # Check if it contains markdown elements
        markdown_patterns = [
            r'^#+\s+.+$',             # Headers
            r'^[-*]\s+.+$',           # List items
            r'^\|.+\|.+\|$',          # Tables
            r'```[a-z]*\n[\s\S]+?\n```'  # Code blocks
        ]

        has_markdown = any(re.search(pattern, content, re.MULTILINE) for pattern in markdown_patterns)
        has_json_block = bool(re.search(r'```json\n[\s\S]+?\n```', content))

        if has_markdown and has_json_block:
            return "mixed"
        elif has_markdown:
            return "markdown"
        else:
            return "text"

    def extract_json_from_markdown(self, content):
        """
        Extract JSON blocks from markdown content.

        Args:
            content (str): The markdown content

        Returns:
            dict: The extracted JSON data or empty dict if none found
        """
        json_blocks = re.findall(r'```json\n([\s\S]+?)\n```', content)
        
        if not json_blocks:
            return {}
        
        # Try to parse each JSON block, return the first valid one
        for block in json_blocks:
            try:
                return json.loads(block)
            except json.JSONDecodeError as e:
                self.log(f"Failed to parse JSON block: {e}")
        
        return {}

    def extract_tables_from_markdown(self, content):
        """
        Extract tables from markdown content and convert to structured data.

        Args:
            content (str): The markdown content

        Returns:
            list: A list of dictionaries representing the tables
        """
        # Find table blocks
        table_pattern = r'\|(.+?)\|\n\|(?:-+\|)+\n((?:\|.+?\|\n)+)'
        table_matches = re.findall(table_pattern, content)
        
        tables = []
        
        for header_row, data_rows in table_matches:
            try:
                # Process headers
                headers = [h.strip() for h in header_row.split('|') if h.strip()]
                
                # Process data rows
                rows = []
                for row in data_rows.strip().split('\n'):
                    if not row or '|' not in row:
                        continue
                    values = [v.strip() for v in row.split('|')[1:-1]]
                    row_dict = {headers[i]: values[i] for i in range(min(len(headers), len(values)))}
                    rows.append(row_dict)
                
                table_name = f"table_{len(tables) + 1}"
                tables.append({
                    "name": table_name,
                    "headers": headers,
                    "rows": rows
                })
            except Exception as e:
                self.log(f"Error processing table: {e}")
        
        return tables

    def extract_headers_from_markdown(self, content):
        """
        Extract headers from markdown content.

        Args:
            content (str): The markdown content

        Returns:
            dict: A dictionary of headers and their content
        """
        header_pattern = r'^(#+)\s+(.+)$'
        header_matches = re.findall(header_pattern, content, re.MULTILINE)
        
        headers = {}
        
        for level, title in header_matches:
            level_num = len(level)
            if level_num not in headers:
                headers[level_num] = []
            headers[level_num].append(title.strip())
        
        result = {}
        for level, titles in headers.items():
            result[f"h{level}"] = titles
        
        return result

    def extract_lists_from_markdown(self, content):
        """
        Extract lists from markdown content.

        Args:
            content (str): The markdown content

        Returns:
            list: A list of lists found in the content
        """
        list_pattern = r'(?:^[-*]\s+(.+?)$(?:\n|$))+'
        list_matches = re.findall(list_pattern, content, re.MULTILINE)
        
        return [item.strip() for item in list_matches]

    def extract_key_value_pairs(self, content):
        """
        Extract key-value pairs from text content.

        Args:
            content (str): The text content

        Returns:
            dict: A dictionary of extracted key-value pairs
        """
        # Look for patterns like "Key: Value" or "Key = Value"
        kv_pattern = r'^([^:=\n]+)[:|=]\s*(.+?)$'
        kv_matches = re.findall(kv_pattern, content, re.MULTILINE)
        
        result = {}
        for key, value in kv_matches:
            key = key.strip()
            value = value.strip()
            
            # Try to convert to appropriate types
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            elif re.match(r'^-?\d+(\.\d+)?$', value):
                try:
                    value = float(value)
                except ValueError:
                    pass
            
            result[key] = value
        
        return result

    def extract_data_from_markdown(self, content):
        """
        Extract structured data from markdown content.

        Args:
            content (str): The markdown content

        Returns:
            dict: A dictionary containing the extracted structured data
        """
        data = {}
        
        # Extract JSON blocks
        json_data = self.extract_json_from_markdown(content)
        if json_data:
            data.update(json_data)
        
        # Extract other structured elements
        headers = self.extract_headers_from_markdown(content)
        if headers:
            data['headers'] = headers
        
        tables = self.extract_tables_from_markdown(content)
        if tables:
            data['tables'] = tables
        
        lists = self.extract_lists_from_markdown(content)
        if lists:
            data['lists'] = lists
        
        # Extract any key-value pairs from the remaining text
        kv_pairs = self.extract_key_value_pairs(content)
        if kv_pairs:
            # Only add KV pairs that don't conflict with existing data
            for k, v in kv_pairs.items():
                if k not in data:
                    data[k] = v
        
        return data

    def standardize_response(self, endpoint_name, content, status_code=200):
        """
        Standardize an MCP API response into a consistent format.

        Args:
            endpoint_name (str): The name of the endpoint that produced the response
            content (str): The response content
            status_code (int): The HTTP status code of the response

        Returns:
            dict: The standardized response
        """
        # Detect response format
        format_type = self.detect_format(content)
        self.log(f"Detected format: {format_type}")
        
        # Create the metadata
        meta = {
            "format": format_type,
            "endpoint": endpoint_name,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Handle error responses
        if status_code >= 400:
            return {
                "success": False,
                "error": {
                    "code": status_code,
                    "message": content.strip()
                },
                "meta": meta
            }
        
        # Process response based on its format
        data = {}
        
        if format_type == "json":
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                self.log(f"JSON parsing error: {e}")
                return {
                    "success": False,
                    "error": {
                        "code": 500,
                        "message": f"Failed to parse JSON: {str(e)}"
                    },
                    "meta": meta
                }
                
        elif format_type == "markdown":
            data = self.extract_data_from_markdown(content)
            
        elif format_type == "mixed":
            data = self.extract_data_from_markdown(content)
            
        elif format_type == "text":
            data = self.extract_key_value_pairs(content)
            if not data:
                # If no structured data was found, store the raw text
                data = {"raw_text": content.strip()}
        
        # Return the standardized response
        return {
            "success": True,
            "data": data,
            "meta": meta
        }


def main():
    """Command line interface for the standardizer."""
    if len(sys.argv) < 3:
        print("Usage: python mcp_response_standardizer.py <endpoint_name> <response_file> [status_code]")
        sys.exit(1)
    
    endpoint_name = sys.argv[1]
    response_file = sys.argv[2]
    status_code = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    
    try:
        with open(response_file, 'r') as f:
            content = f.read()
        
        standardizer = MCPResponseStandardizer(debug=True)
        result = standardizer.standardize_response(endpoint_name, content, status_code)
        
        # Print the result
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 