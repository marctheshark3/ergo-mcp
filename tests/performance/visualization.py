"""
Visualization tools for benchmark results.
This module provides functions for creating visual reports from benchmark data.
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default paths
REPORT_DIR = Path("tests/reports")
BENCHMARK_RESULTS = REPORT_DIR / "benchmark_results.json"

# Create report directory if it doesn't exist
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_benchmark_results(file_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load benchmark results from a JSON file.
    
    Args:
        file_path: Path to the benchmark results file
        
    Returns:
        List of benchmark result dictionaries
    """
    if file_path is None:
        file_path = BENCHMARK_RESULTS
        
    if not file_path.exists():
        logger.error(f"Benchmark results file not found: {file_path}")
        return []
        
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in benchmark results file: {file_path}")
        return []


def create_response_time_chart(results: List[Dict[str, Any]], 
                              output_path: Optional[Path] = None):
    """Create a chart of response times.
    
    Args:
        results: List of benchmark result dictionaries
        output_path: Path to save the chart
    """
    if not results:
        logger.warning("No results to create response time chart")
        return
        
    # Prepare data
    endpoints = []
    mean_times = []
    p95_times = []
    max_times = []
    
    for result in results:
        if "error" in result:
            continue
            
        endpoints.append(result["endpoint"])
        response_times = result.get("response_time_ms", {})
        mean_times.append(response_times.get("mean", 0))
        p95_times.append(response_times.get("p95", 0))
        max_times.append(response_times.get("max", 0))
    
    if not endpoints:
        logger.warning("No valid results to create response time chart")
        return
        
    # Create DataFrame for seaborn
    df = pd.DataFrame({
        "Endpoint": endpoints * 3,
        "Response Time (ms)": mean_times + p95_times + max_times,
        "Metric": ["Mean"] * len(endpoints) + ["95th Percentile"] * len(endpoints) + ["Max"] * len(endpoints)
    })
    
    # Create chart
    plt.figure(figsize=(14, 8))
    
    # Use seaborn for better aesthetics
    sns.set_style("whitegrid")
    chart = sns.barplot(x="Endpoint", y="Response Time (ms)", hue="Metric", data=df)
    
    # Add performance threshold line if defined
    threshold = 2000  # 2 seconds
    plt.axhline(y=threshold, color='r', linestyle='--', alpha=0.7)
    plt.text(len(endpoints)-1, threshold*1.02, f"Target: {threshold}ms", 
             color='r', ha='right', va='bottom')
    
    # Customize chart
    chart.set_title("API Endpoint Response Times", fontsize=16)
    chart.set_xlabel("Endpoint", fontsize=12)
    chart.set_ylabel("Response Time (ms)", fontsize=12)
    
    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save chart
    if output_path is None:
        output_path = REPORT_DIR / "response_times_detailed.png"
        
    plt.savefig(output_path)
    logger.info(f"Response time chart saved to {output_path}")
    plt.close()


def create_token_usage_chart(results: List[Dict[str, Any]],
                            output_path: Optional[Path] = None):
    """Create a chart of token usage estimates.
    
    Args:
        results: List of benchmark result dictionaries
        output_path: Path to save the chart
    """
    if not results:
        logger.warning("No results to create token usage chart")
        return
        
    # Prepare data
    endpoints = []
    mean_tokens = []
    max_tokens = []
    
    for result in results:
        if "error" in result:
            continue
            
        endpoints.append(result["endpoint"])
        token_data = result.get("token_estimate", {})
        mean_tokens.append(token_data.get("mean", 0))
        max_tokens.append(token_data.get("max", 0))
    
    if not endpoints:
        logger.warning("No valid results to create token usage chart")
        return
        
    # Create DataFrame for seaborn
    df = pd.DataFrame({
        "Endpoint": endpoints * 2,
        "Token Count": mean_tokens + max_tokens,
        "Metric": ["Mean"] * len(endpoints) + ["Max"] * len(endpoints)
    })
    
    # Create chart
    plt.figure(figsize=(14, 8))
    
    # Use seaborn for better aesthetics
    sns.set_style("whitegrid")
    chart = sns.barplot(x="Endpoint", y="Token Count", hue="Metric", data=df)
    
    # Add warning threshold line
    warning_threshold = 4000  # Warning level for token count
    plt.axhline(y=warning_threshold, color='orange', linestyle='--', alpha=0.7)
    plt.text(len(endpoints)-1, warning_threshold*1.02, f"Warning: {warning_threshold}", 
             color='orange', ha='right', va='bottom')
    
    # Add critical threshold line
    critical_threshold = 8000  # Critical level for token count
    plt.axhline(y=critical_threshold, color='r', linestyle='--', alpha=0.7)
    plt.text(len(endpoints)-1, critical_threshold*1.02, f"Critical: {critical_threshold}", 
             color='r', ha='right', va='bottom')
    
    # Customize chart
    chart.set_title("API Endpoint Token Usage Estimates", fontsize=16)
    chart.set_xlabel("Endpoint", fontsize=12)
    chart.set_ylabel("Estimated Token Count", fontsize=12)
    
    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save chart
    if output_path is None:
        output_path = REPORT_DIR / "token_usage.png"
        
    plt.savefig(output_path)
    logger.info(f"Token usage chart saved to {output_path}")
    plt.close()


def create_response_size_chart(results: List[Dict[str, Any]],
                              output_path: Optional[Path] = None):
    """Create a chart of response sizes.
    
    Args:
        results: List of benchmark result dictionaries
        output_path: Path to save the chart
    """
    if not results:
        logger.warning("No results to create response size chart")
        return
        
    # Prepare data
    endpoints = []
    mean_sizes = []
    max_sizes = []
    
    for result in results:
        if "error" in result:
            continue
            
        endpoints.append(result["endpoint"])
        size_data = result.get("response_size_bytes", {})
        # Convert to KB
        mean_sizes.append(size_data.get("mean", 0) / 1024)
        max_sizes.append(size_data.get("max", 0) / 1024)
    
    if not endpoints:
        logger.warning("No valid results to create response size chart")
        return
        
    # Create DataFrame for seaborn
    df = pd.DataFrame({
        "Endpoint": endpoints * 2,
        "Response Size (KB)": mean_sizes + max_sizes,
        "Metric": ["Mean"] * len(endpoints) + ["Max"] * len(endpoints)
    })
    
    # Create chart
    plt.figure(figsize=(14, 8))
    
    # Use seaborn for better aesthetics
    sns.set_style("whitegrid")
    chart = sns.barplot(x="Endpoint", y="Response Size (KB)", hue="Metric", data=df)
    
    # Customize chart
    chart.set_title("API Endpoint Response Sizes", fontsize=16)
    chart.set_xlabel("Endpoint", fontsize=12)
    chart.set_ylabel("Response Size (KB)", fontsize=12)
    
    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save chart
    if output_path is None:
        output_path = REPORT_DIR / "response_sizes_detailed.png"
        
    plt.savefig(output_path)
    logger.info(f"Response size chart saved to {output_path}")
    plt.close()


def create_endpoint_comparison_table(results: List[Dict[str, Any]],
                                   output_path: Optional[Path] = None):
    """Create a markdown table comparing endpoint metrics.
    
    Args:
        results: List of benchmark result dictionaries
        output_path: Path to save the markdown file
    """
    if not results:
        logger.warning("No results to create comparison table")
        return
        
    # Filter out error results
    valid_results = [r for r in results if "error" not in r]
    
    if not valid_results:
        logger.warning("No valid results to create comparison table")
        return
        
    # Prepare markdown table
    table = "# Endpoint Performance Comparison\n\n"
    table += "| Endpoint | Mean Time (ms) | 95% Time (ms) | Mean Size (KB) | Token Est. | Success % |\n"
    table += "|----------|---------------|--------------|----------------|------------|----------|\n"
    
    for result in valid_results:
        endpoint = result["endpoint"]
        
        # Extract metrics
        response_time = result.get("response_time_ms", {})
        mean_time = response_time.get("mean", 0)
        p95_time = response_time.get("p95", 0)
        
        response_size = result.get("response_size_bytes", {})
        mean_size = response_size.get("mean", 0) / 1024  # Convert to KB
        
        token_estimate = result.get("token_estimate", {})
        mean_token = token_estimate.get("mean", 0)
        
        requests = result.get("requests", {})
        total = requests.get("total", 0)
        successful = requests.get("successful", 0)
        success_pct = (successful / total * 100) if total > 0 else 0
        
        # Add row to table
        table += f"| {endpoint} | {mean_time:.2f} | {p95_time:.2f} | {mean_size:.2f} | {mean_token:.0f} | {success_pct:.1f}% |\n"
    
    # Add performance warnings
    table += "\n## Performance Warnings\n\n"
    
    # Check for slow endpoints
    slow_endpoints = [r["endpoint"] for r in valid_results 
                    if r.get("response_time_ms", {}).get("mean", 0) > 2000]
    
    if slow_endpoints:
        table += "### Slow Endpoints (>2s response time)\n\n"
        for endpoint in slow_endpoints:
            table += f"- {endpoint}\n"
        table += "\n"
    
    # Check for large token usage
    high_token_endpoints = [r["endpoint"] for r in valid_results 
                           if r.get("token_estimate", {}).get("mean", 0) > 4000]
    
    if high_token_endpoints:
        table += "### High Token Usage Endpoints (>4000 tokens)\n\n"
        for endpoint in high_token_endpoints:
            table += f"- {endpoint}\n"
        table += "\n"
    
    # Check for large response sizes
    large_response_endpoints = [r["endpoint"] for r in valid_results 
                              if r.get("response_size_bytes", {}).get("mean", 0) > 500 * 1024]  # >500KB
    
    if large_response_endpoints:
        table += "### Large Response Endpoints (>500KB)\n\n"
        for endpoint in large_response_endpoints:
            table += f"- {endpoint}\n"
        table += "\n"
    
    # Save table
    if output_path is None:
        output_path = REPORT_DIR / "endpoint_comparison.md"
        
    with open(output_path, "w") as f:
        f.write(table)
    
    logger.info(f"Endpoint comparison table saved to {output_path}")


def generate_full_report(results_path: Optional[Path] = None,
                        output_dir: Optional[Path] = None):
    """Generate a full performance report with all charts and tables.
    
    Args:
        results_path: Path to benchmark results file
        output_dir: Directory to save report files
    """
    if output_dir is None:
        output_dir = REPORT_DIR
        
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load benchmark results
    results = load_benchmark_results(results_path)
    
    if not results:
        logger.error("No benchmark results to generate report")
        return
    
    # Generate charts
    create_response_time_chart(results, output_dir / "response_times.png")
    create_token_usage_chart(results, output_dir / "token_usage.png")
    create_response_size_chart(results, output_dir / "response_sizes.png")
    
    # Generate comparison table
    create_endpoint_comparison_table(results, output_dir / "endpoint_comparison.md")
    
    # Generate report index
    report_index = "# Performance Benchmark Report\n\n"
    report_index += f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    report_index += "## Performance Summary\n\n"
    report_index += "![Response Times](response_times.png)\n\n"
    report_index += "![Token Usage](token_usage.png)\n\n"
    report_index += "![Response Sizes](response_sizes.png)\n\n"
    
    report_index += "## Detailed Comparison\n\n"
    report_index += "See [Endpoint Comparison](endpoint_comparison.md) for detailed metrics.\n\n"
    
    # Save report index
    with open(output_dir / "report.md", "w") as f:
        f.write(report_index)
    
    logger.info(f"Full performance report generated in {output_dir}")


if __name__ == "__main__":
    # Generate report from latest benchmark results
    generate_full_report()
    logger.info("Visualization complete") 