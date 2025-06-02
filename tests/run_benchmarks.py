#!/usr/bin/env python3
"""
Ergo Explorer MCP Benchmark Runner
This script runs performance benchmarks for all Ergo Explorer MCP endpoints.
"""

import os
import sys
import json
import argparse
import logging
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import benchmark modules
from tests.performance.benchmarks import run_all_benchmarks, save_benchmark_results
from tests.performance.visualization import generate_full_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / "benchmark.log")
    ]
)
logger = logging.getLogger("benchmark_runner")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run benchmarks for Ergo Explorer MCP endpoints")
    
    parser.add_argument(
        "--categories",
        type=str,
        help="Comma-separated list of endpoint categories to benchmark (default: all)"
    )
    
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Number of benchmark iterations to run (default: 5)"
    )
    
    parser.add_argument(
        "--warmup",
        type=int,
        default=2,
        help="Number of warmup iterations (default: 2)"
    )
    
    parser.add_argument(
        "--concurrent",
        type=int,
        default=1,
        help="Number of concurrent requests (default: 1)"
    )
    
    parser.add_argument(
        "--report-dir",
        type=str,
        default="tests/reports",
        help="Directory to save reports (default: tests/reports)"
    )
    
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:3001",
        help="Base URL for the API (default: http://localhost:3001)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()

def update_config(args):
    """Update configuration with command line arguments."""
    # Load config
    config_path = Path(__file__).parent / "config" / "test_config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Update config with args
    if args.iterations:
        config["performance"]["benchmark_iterations"] = args.iterations
    
    if args.warmup:
        config["performance"]["warmup_iterations"] = args.warmup
    
    if args.concurrent:
        config["performance"]["concurrent_users"] = [args.concurrent]
    
    if args.report_dir:
        config["reporting"]["output_directory"] = args.report_dir
    
    if args.base_url:
        config["general"]["base_url"] = args.base_url
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Save updated config
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    
    logger.info(f"Updated configuration: {config_path}")

def main():
    """Main function to run benchmarks."""
    start_time = time.time()
    
    # Parse arguments
    args = parse_args()
    
    # Update config
    update_config(args)
    
    # Create report directory if it doesn't exist
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Run benchmarks
    logger.info("Starting benchmarks")
    metrics = run_all_benchmarks()
    
    # Save results
    save_benchmark_results(metrics)
    
    # Generate report
    generate_full_report()
    
    # Log completion
    elapsed_time = time.time() - start_time
    logger.info(f"Benchmarks completed in {elapsed_time:.2f} seconds")
    logger.info(f"Reports saved to {report_dir}")

if __name__ == "__main__":
    main() 