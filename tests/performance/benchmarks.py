"""
Performance benchmarking for the Ergo Explorer MCP.
This module provides tools for testing endpoint performance and estimating token usage.
"""

import time
import json
import os
import requests
import statistics
import tracemalloc
import concurrent.futures
from typing import Dict, List, Any, Optional, Callable, Tuple
import logging
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

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
BENCHMARK_ITERATIONS = CONFIG["performance"]["benchmark_iterations"]
WARMUP_ITERATIONS = CONFIG["performance"]["warmup_iterations"]
REPORT_DIR = Path(CONFIG["reporting"]["output_directory"])

# Create report directory if it doesn't exist
REPORT_DIR.mkdir(parents=True, exist_ok=True)

class PerformanceMetrics:
    """Container for performance metrics from benchmark runs."""
    
    def __init__(self, endpoint_name: str):
        self.endpoint_name = endpoint_name
        self.response_times: List[float] = []
        self.memory_usages: List[int] = []
        self.token_estimates: List[int] = []
        self.response_sizes: List[int] = []
        self.status_codes: List[int] = []
        self.errors: List[str] = []
        
    def add_result(self, response_time: float, memory_usage: int = 0, 
                  token_estimate: int = 0, response_size: int = 0,
                  status_code: int = 200, error: Optional[str] = None):
        """Add a benchmark result."""
        self.response_times.append(response_time)
        self.memory_usages.append(memory_usage)
        self.token_estimates.append(token_estimate)
        self.response_sizes.append(response_size)
        self.status_codes.append(status_code)
        if error:
            self.errors.append(error)
            
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        if not self.response_times:
            return {
                "endpoint": self.endpoint_name,
                "error": "No benchmark results collected"
            }
            
        valid_times = [t for t, s in zip(self.response_times, self.status_codes) if s == 200]
        
        if not valid_times:
            return {
                "endpoint": self.endpoint_name,
                "error": "No successful requests"
            }
            
        return {
            "endpoint": self.endpoint_name,
            "requests": {
                "total": len(self.response_times),
                "successful": len(valid_times),
                "failed": len(self.response_times) - len(valid_times)
            },
            "response_time_ms": {
                "min": min(valid_times) * 1000,
                "max": max(valid_times) * 1000,
                "mean": statistics.mean(valid_times) * 1000,
                "median": statistics.median(valid_times) * 1000,
                "p95": self._percentile(valid_times, 95) * 1000,
                "std_dev": statistics.stdev(valid_times) * 1000 if len(valid_times) > 1 else 0
            },
            "memory_usage_kb": {
                "mean": statistics.mean(self.memory_usages) / 1024 if self.memory_usages else 0
            },
            "response_size_bytes": {
                "mean": statistics.mean(self.response_sizes) if self.response_sizes else 0,
                "max": max(self.response_sizes) if self.response_sizes else 0
            },
            "token_estimate": {
                "mean": statistics.mean(self.token_estimates) if self.token_estimates else 0,
                "max": max(self.token_estimates) if self.token_estimates else 0
            },
            "errors": self.errors[:5]  # Limit to first 5 errors
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value from a list of floats."""
        size = len(data)
        if not size:
            return 0
            
        sorted_data = sorted(data)
        idx = int(size * percentile / 100)
        return sorted_data[idx]
    
    def clear(self):
        """Reset all metrics."""
        self.response_times = []
        self.memory_usages = []
        self.token_estimates = []
        self.response_sizes = []
        self.status_codes = []
        self.errors = []


def run_single_benchmark(endpoint: str, params: Dict[str, Any]) -> Tuple[float, int, Dict[str, Any]]:
    """Run a single benchmark request and return metrics.
    
    Args:
        endpoint: The endpoint to test
        params: Parameters to pass to the endpoint
        
    Returns:
        Tuple of (response_time, status_code, response_data)
    """
    url = f"{BASE_URL}/{endpoint}"
    
    # Start memory tracking
    tracemalloc.start()
    start_snapshot = tracemalloc.take_snapshot()
    
    # Make the request
    start_time = time.time()
    try:
        response = requests.post(url, json=params, timeout=TIMEOUT)
        status_code = response.status_code
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"error": "Invalid JSON response"}
            
    except Exception as e:
        end_time = time.time()
        status_code = 500
        response_data = {"error": str(e)}
    else:
        end_time = time.time()
    
    # Get memory usage
    end_snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()
    
    # Calculate differences
    memory_diff = sum(stat.size for stat in end_snapshot.compare_to(start_snapshot, 'lineno'))
    response_time = end_time - start_time
    
    return response_time, status_code, response_data


def benchmark_endpoint(endpoint: str, params: Dict[str, Any], 
                       iterations: int = BENCHMARK_ITERATIONS,
                       warmup: int = WARMUP_ITERATIONS) -> PerformanceMetrics:
    """Benchmark an endpoint with given parameters.
    
    Args:
        endpoint: The endpoint to test
        params: Parameters to pass to the endpoint
        iterations: Number of iterations to run
        warmup: Number of warmup iterations (not counted in results)
        
    Returns:
        PerformanceMetrics object with results
    """
    metrics = PerformanceMetrics(endpoint)
    
    # Warmup
    logger.info(f"Warming up {endpoint} ({warmup} iterations)...")
    for _ in range(warmup):
        run_single_benchmark(endpoint, params)
    
    # Benchmark
    logger.info(f"Benchmarking {endpoint} ({iterations} iterations)...")
    for i in range(iterations):
        response_time, status_code, response_data = run_single_benchmark(endpoint, params)
        
        # Extract metadata if available
        token_estimate = 0
        response_size = 0
        error = None
        
        if isinstance(response_data, dict):
            if "metadata" in response_data:
                metadata = response_data.get("metadata", {})
                token_estimate = metadata.get("token_estimate", 0)
                response_size = metadata.get("result_size_bytes", 0)
            
            if "error" in response_data:
                error = response_data["error"]
                
        # Add result to metrics
        metrics.add_result(
            response_time=response_time,
            memory_usage=0,  # Memory tracking disabled for now
            token_estimate=token_estimate,
            response_size=response_size,
            status_code=status_code,
            error=error
        )
        
        logger.debug(f"  Iteration {i+1}/{iterations}: {response_time*1000:.2f}ms, {response_size} bytes")
    
    return metrics


def generate_charts(metrics_list: List[PerformanceMetrics]):
    """Generate performance charts from collected metrics.
    
    Args:
        metrics_list: List of PerformanceMetrics objects to visualize
    """
    if not CONFIG["reporting"]["generate_charts"]:
        return
        
    if not metrics_list:
        logger.warning("No metrics to generate charts from")
        return
        
    # Response time comparison chart
    plt.figure(figsize=(12, 8))
    
    # Extract data
    endpoints = []
    mean_times = []
    p95_times = []
    
    for metrics in metrics_list:
        summary = metrics.get_summary()
        if "error" in summary:
            continue
            
        endpoints.append(metrics.endpoint_name)
        mean_times.append(summary["response_time_ms"]["mean"])
        p95_times.append(summary["response_time_ms"]["p95"])
    
    # Create bar chart
    x = np.arange(len(endpoints))
    width = 0.35
    
    plt.bar(x - width/2, mean_times, width, label='Mean')
    plt.bar(x + width/2, p95_times, width, label='95th Percentile')
    
    plt.xlabel('Endpoints')
    plt.ylabel('Response Time (ms)')
    plt.title('Endpoint Response Times')
    plt.xticks(x, endpoints, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    
    # Save chart
    chart_path = REPORT_DIR / "response_times.png"
    plt.savefig(chart_path)
    logger.info(f"Response time chart saved to {chart_path}")
    
    # Token estimate chart
    plt.figure(figsize=(12, 8))
    
    # Extract data
    token_estimates = []
    
    for metrics in metrics_list:
        summary = metrics.get_summary()
        if "error" in summary:
            continue
            
        token_estimates.append(summary["token_estimate"]["mean"])
    
    # Create bar chart
    plt.bar(endpoints, token_estimates)
    plt.xlabel('Endpoints')
    plt.ylabel('Estimated Token Count')
    plt.title('Endpoint Token Usage Estimates')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save chart
    chart_path = REPORT_DIR / "token_estimates.png"
    plt.savefig(chart_path)
    logger.info(f"Token estimate chart saved to {chart_path}")
    
    # Response size chart
    plt.figure(figsize=(12, 8))
    
    # Extract data
    response_sizes = []
    
    for metrics in metrics_list:
        summary = metrics.get_summary()
        if "error" in summary:
            continue
            
        response_sizes.append(summary["response_size_bytes"]["mean"] / 1024)  # Convert to KB
    
    # Create bar chart
    plt.bar(endpoints, response_sizes)
    plt.xlabel('Endpoints')
    plt.ylabel('Response Size (KB)')
    plt.title('Endpoint Response Sizes')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save chart
    chart_path = REPORT_DIR / "response_sizes.png"
    plt.savefig(chart_path)
    logger.info(f"Response size chart saved to {chart_path}")


def save_benchmark_results(metrics_list: List[PerformanceMetrics]):
    """Save benchmark results to a JSON file.
    
    Args:
        metrics_list: List of PerformanceMetrics objects
    """
    if not CONFIG["reporting"]["save_raw_data"]:
        return
        
    results = []
    for metrics in metrics_list:
        results.append(metrics.get_summary())
    
    output_file = REPORT_DIR / "benchmark_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Benchmark results saved to {output_file}")


def load_endpoint_params() -> Dict[str, Dict[str, Dict]]:
    """Load endpoint parameters from configuration."""
    params_path = Path(__file__).parent.parent / "config" / "endpoint_params.json"
    with open(params_path, "r") as f:
        return json.load(f)


def run_benchmarks_for_category(category: str, endpoint_params: Dict[str, Dict]) -> List[PerformanceMetrics]:
    """Run benchmarks for all endpoints in a category.
    
    Args:
        category: Category name
        endpoint_params: Dictionary of endpoint parameters
        
    Returns:
        List of PerformanceMetrics objects
    """
    results = []
    
    for endpoint, params in endpoint_params.items():
        logger.info(f"Benchmarking {category}/{endpoint}")
        
        # Use first valid params for benchmarking
        if not params["valid_params"]:
            logger.warning(f"No valid parameters for {endpoint}, skipping")
            continue
            
        test_params = params["valid_params"][0]
        
        # Run benchmark
        metrics = benchmark_endpoint(endpoint, test_params)
        results.append(metrics)
    
    return results


def run_all_benchmarks() -> List[PerformanceMetrics]:
    """Run benchmarks for all endpoints.
    
    Returns:
        List of PerformanceMetrics objects
    """
    all_metrics = []
    
    # Load endpoint parameters
    endpoint_params = load_endpoint_params()
    
    # Run benchmarks for each category
    for category, endpoints in endpoint_params.items():
        logger.info(f"Running benchmarks for {category}")
        category_metrics = run_benchmarks_for_category(category, endpoints)
        all_metrics.extend(category_metrics)
    
    return all_metrics


if __name__ == "__main__":
    logger.info("Starting performance benchmarks")
    
    # Run all benchmarks
    metrics = run_all_benchmarks()
    
    # Save results
    save_benchmark_results(metrics)
    
    # Generate charts
    generate_charts(metrics)
    
    logger.info("Performance benchmarks completed") 