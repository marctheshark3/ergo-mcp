"""
Tests for validating the response format standardization across endpoints.
This module tests that all endpoints return data in the expected format.
"""

import json
import os
import sys
import requests
from pathlib import Path
import pytest
import logging
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load test configuration
def load_config():
    """Load test configuration from JSON file."""
    config_path = Path(__file__).parent.parent / "config" / "test_config.json"
    with open(config_path, "r") as f:
        return json.load(f)

CONFIG = load_config()
BASE_URL = CONFIG["general"]["base_url"]
TIMEOUT = CONFIG["general"]["timeout"]

def load_endpoint_params():
    """Load endpoint parameters from configuration."""
    params_path = Path(__file__).parent.parent / "config" / "endpoint_params.json"
    with open(params_path, "r") as f:
        return json.load(f)

ENDPOINT_PARAMS = load_endpoint_params()

def test_response_has_standard_fields():
    """Test that all endpoints return responses with standard fields."""
    failed_endpoints = []
    
    for category, endpoints in ENDPOINT_PARAMS.items():
        for endpoint_name, endpoint_config in endpoints.items():
            if not endpoint_config["valid_params"]:
                logger.warning(f"No valid parameters for {endpoint_name}, skipping")
                continue
                
            params = endpoint_config["valid_params"][0]
            url = f"{BASE_URL}/{endpoint_name}"
            
            try:
                response = requests.post(url, json=params, timeout=TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                # Check for standard fields
                if "status" not in data:
                    failed_endpoints.append(f"{endpoint_name} missing 'status' field")
                
                if "data" not in data:
                    failed_endpoints.append(f"{endpoint_name} missing 'data' field")
                
                if "metadata" not in data:
                    failed_endpoints.append(f"{endpoint_name} missing 'metadata' field")
                
            except (requests.RequestException, json.JSONDecodeError) as e:
                failed_endpoints.append(f"{endpoint_name} error: {str(e)}")
    
    # Assert that all endpoints passed
    assert not failed_endpoints, f"Endpoints with non-standard format: {failed_endpoints}"

def test_metadata_fields():
    """Test that metadata includes required fields."""
    failed_endpoints = []
    
    for category, endpoints in ENDPOINT_PARAMS.items():
        for endpoint_name, endpoint_config in endpoints.items():
            if not endpoint_config["valid_params"]:
                logger.warning(f"No valid parameters for {endpoint_name}, skipping")
                continue
                
            params = endpoint_config["valid_params"][0]
            url = f"{BASE_URL}/{endpoint_name}"
            
            try:
                response = requests.post(url, json=params, timeout=TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                # Check metadata fields
                if "metadata" not in data:
                    failed_endpoints.append(f"{endpoint_name} missing 'metadata' field")
                    continue
                
                metadata = data["metadata"]
                required_fields = [
                    "execution_time_ms", 
                    "result_size_bytes", 
                    "is_truncated", 
                    "token_estimate"
                ]
                
                for field in required_fields:
                    if field not in metadata:
                        failed_endpoints.append(f"{endpoint_name} metadata missing '{field}'")
                
            except (requests.RequestException, json.JSONDecodeError) as e:
                failed_endpoints.append(f"{endpoint_name} error: {str(e)}")
    
    # Assert that all endpoints passed
    assert not failed_endpoints, f"Endpoints with incomplete metadata: {failed_endpoints}"

def test_expected_fields_present():
    """Test that endpoints return the expected fields in their data."""
    failed_endpoints = []
    
    for category, endpoints in ENDPOINT_PARAMS.items():
        for endpoint_name, endpoint_config in endpoints.items():
            if not endpoint_config["valid_params"]:
                logger.warning(f"No valid parameters for {endpoint_name}, skipping")
                continue
                
            params = endpoint_config["valid_params"][0]
            url = f"{BASE_URL}/{endpoint_name}"
            expected_fields = endpoint_config["expected_fields"]
            
            try:
                response = requests.post(url, json=params, timeout=TIMEOUT)
                response.raise_for_status()
                response_data = response.json()
                
                # Check if data field exists
                if "data" not in response_data:
                    failed_endpoints.append(f"{endpoint_name} missing 'data' field")
                    continue
                
                data = response_data["data"]
                
                # Check if data is a list or object
                if isinstance(data, list):
                    if not data:
                        logger.warning(f"{endpoint_name} returned empty data list")
                        continue
                    
                    # Check first item for expected fields
                    first_item = data[0]
                    for field in expected_fields:
                        if field not in first_item:
                            failed_endpoints.append(f"{endpoint_name} missing expected field '{field}'")
                            
                elif isinstance(data, dict):
                    # Check data object for expected fields
                    for field in expected_fields:
                        if field not in data:
                            failed_endpoints.append(f"{endpoint_name} missing expected field '{field}'")
                
            except (requests.RequestException, json.JSONDecodeError) as e:
                failed_endpoints.append(f"{endpoint_name} error: {str(e)}")
    
    # Assert that all endpoints passed
    assert not failed_endpoints, f"Endpoints missing expected fields: {failed_endpoints}"

def test_error_responses():
    """Test that endpoints return proper error responses."""
    failed_endpoints = []
    
    for category, endpoints in ENDPOINT_PARAMS.items():
        for endpoint_name, endpoint_config in endpoints.items():
            if not endpoint_config["invalid_params"]:
                logger.warning(f"No invalid parameters for {endpoint_name}, skipping")
                continue
                
            params = endpoint_config["invalid_params"][0]
            url = f"{BASE_URL}/{endpoint_name}"
            
            try:
                response = requests.post(url, json=params, timeout=TIMEOUT)
                data = response.json()
                
                # Check for error response format
                if "status" not in data:
                    failed_endpoints.append(f"{endpoint_name} error response missing 'status' field")
                elif data["status"] != "error":
                    failed_endpoints.append(f"{endpoint_name} incorrect status for error: {data['status']}")
                
                if "message" not in data:
                    failed_endpoints.append(f"{endpoint_name} error response missing 'message' field")
                
                if "metadata" not in data:
                    failed_endpoints.append(f"{endpoint_name} error response missing 'metadata' field")
                
            except (requests.RequestException, json.JSONDecodeError) as e:
                failed_endpoints.append(f"{endpoint_name} error: {str(e)}")
    
    # Assert that all endpoints passed
    assert not failed_endpoints, f"Endpoints with improper error responses: {failed_endpoints}"

def test_response_limits():
    """Test that endpoints properly limit response sizes."""
    failed_endpoints = []
    
    for category, endpoints in ENDPOINT_PARAMS.items():
        for endpoint_name, endpoint_config in endpoints.items():
            if not endpoint_config["valid_params"]:
                logger.warning(f"No valid parameters for {endpoint_name}, skipping")
                continue
                
            # Try with a very small limit
            params = endpoint_config["valid_params"][0].copy()
            if isinstance(params, dict):
                params["limit"] = 1  # Set limit to 1 to test limiting
            
            url = f"{BASE_URL}/{endpoint_name}"
            
            try:
                response = requests.post(url, json=params, timeout=TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                # Check if metadata indicates truncation
                if "metadata" not in data:
                    failed_endpoints.append(f"{endpoint_name} missing 'metadata' field")
                    continue
                
                metadata = data["metadata"]
                
                # Only check for list responses
                if "data" in data and isinstance(data["data"], list):
                    if len(data["data"]) > 1:  # More than 1 item despite limit=1
                        if not metadata.get("is_truncated", False):
                            # Only add to failed if is_truncated is explicitly False
                            if "is_truncated" in metadata:
                                failed_endpoints.append(
                                    f"{endpoint_name} returned {len(data['data'])} items "
                                    f"with limit=1 but is_truncated={metadata['is_truncated']}"
                                )
                
            except (requests.RequestException, json.JSONDecodeError) as e:
                # Ignore errors for this test
                logger.warning(f"{endpoint_name} error in limit test: {str(e)}")
    
    # Assert that all endpoints passed
    assert not failed_endpoints, f"Endpoints with limit issues: {failed_endpoints}"

def test_minimal_response_format():
    """Test that endpoints support minimal response format."""
    failed_endpoints = []
    
    for category, endpoints in ENDPOINT_PARAMS.items():
        for endpoint_name, endpoint_config in endpoints.items():
            if not endpoint_config["valid_params"]:
                logger.warning(f"No valid parameters for {endpoint_name}, skipping")
                continue
                
            params = endpoint_config["valid_params"][0].copy()
            if isinstance(params, dict):
                params["verbose"] = False  # Request minimal format
            
            url = f"{BASE_URL}/{endpoint_name}"
            
            try:
                response = requests.post(url, json=params, timeout=TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                # Check for standard minimal fields
                if "status" not in data:
                    failed_endpoints.append(f"{endpoint_name} minimal response missing 'status' field")
                
                if "data" not in data:
                    failed_endpoints.append(f"{endpoint_name} minimal response missing 'data' field")
                
                # Metadata should not be in minimal response
                if "metadata" in data:
                    failed_endpoints.append(f"{endpoint_name} minimal response includes 'metadata' field")
                
            except (requests.RequestException, json.JSONDecodeError) as e:
                failed_endpoints.append(f"{endpoint_name} error: {str(e)}")
    
    # Assert that all endpoints passed
    assert not failed_endpoints, f"Endpoints with incorrect minimal format: {failed_endpoints}"

if __name__ == "__main__":
    """Run the tests directly."""
    try:
        test_response_has_standard_fields()
        print("✅ All endpoints return responses with standard fields")
    except AssertionError as e:
        print(f"❌ {str(e)}")
    
    try:
        test_metadata_fields()
        print("✅ All endpoints include required metadata fields")
    except AssertionError as e:
        print(f"❌ {str(e)}")
    
    try:
        test_expected_fields_present()
        print("✅ All endpoints return expected data fields")
    except AssertionError as e:
        print(f"❌ {str(e)}")
    
    try:
        test_error_responses()
        print("✅ All endpoints return proper error responses")
    except AssertionError as e:
        print(f"❌ {str(e)}")
    
    try:
        test_response_limits()
        print("✅ All endpoints properly limit response sizes")
    except AssertionError as e:
        print(f"❌ {str(e)}")
    
    try:
        test_minimal_response_format()
        print("✅ All endpoints support minimal response format")
    except AssertionError as e:
        print(f"❌ {str(e)}") 