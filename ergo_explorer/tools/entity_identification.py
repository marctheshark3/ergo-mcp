"""
Entity identification module for the Ergo Explorer.

This module provides tools for identifying and grouping addresses that are likely
controlled by the same entity, using various heuristic algorithms.
"""

import logging
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict, Counter
import asyncio
from asyncio import Semaphore, Lock
import networkx as nx
from datetime import datetime
import json
import time
import threading
import random
from functools import wraps
import psutil
import os
import traceback

from ergo_explorer.tools.address import fetch_transaction_cached, fetch_address_transactions, format_id
from ergo_explorer.tools.common import standardize_response

# Get logger
logger = logging.getLogger(__name__)

# Configuration parameters
DEFAULT_CONCURRENCY_LIMIT = 10
DEFAULT_BATCH_SIZE = 20
DEFAULT_MEMORY_LIMIT_MB = 1024  # 1GB memory limit
DEFAULT_TRANSACTIONS_PER_BATCH = 50

# Circuit breaker constants
CIRCUIT_OPEN = "open"      # Circuit is open, requests are failing
CIRCUIT_CLOSED = "closed"  # Circuit is closed, requests are working normally
CIRCUIT_HALF_OPEN = "half_open"  # Circuit is testing if requests can go through

# Performance monitoring
class PerformanceMonitor:
    """Class for monitoring performance metrics during execution."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.start_time = time.time()
        self.timers = {}
        self.counters = {}
        self.memory_usage = []
        self.process = psutil.Process(os.getpid())
        # Capture initial memory
        self.capture_memory_usage("init")
    
    def start_timer(self, name: str):
        """Start a named timer."""
        self.timers[name] = {"start": time.time(), "elapsed": 0}
    
    def stop_timer(self, name: str):
        """Stop a named timer and update elapsed time."""
        if name in self.timers:
            elapsed = time.time() - self.timers[name]["start"]
            self.timers[name]["elapsed"] += elapsed
            self.timers[name]["stop"] = time.time()
            return elapsed
        return 0
    
    def increment_counter(self, name: str, amount: int = 1):
        """Increment a named counter."""
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] += amount
    
    def capture_memory_usage(self, label: str):
        """Capture current memory usage with a label."""
        try:
            memory_info = self.process.memory_info()
            self.memory_usage.append({
                "label": label,
                "timestamp": time.time(),
                "rss_mb": memory_info.rss / (1024 * 1024),  # RSS in MB
                "vms_mb": memory_info.vms / (1024 * 1024)   # VMS in MB
            })
        except Exception as e:
            logger.error(f"Error capturing memory usage: {str(e)}")
    
    def get_detailed_metrics(self):
        """Get all collected metrics as a dictionary."""
        total_time = time.time() - self.start_time
        
        metrics = {
            "total_execution_time_seconds": round(total_time, 3),
            "timers": {k: round(v["elapsed"], 3) for k, v in self.timers.items()},
            "counters": self.counters,
            "memory": {
                "current_mb": round(self.process.memory_info().rss / (1024 * 1024), 2),
                "peak_mb": round(max(m["rss_mb"] for m in self.memory_usage) if self.memory_usage else 0, 2),
                "detailed": self.memory_usage
            }
        }
        
        # Calculate percentages for timers
        metrics["timer_percentages"] = {
            k: round(v * 100 / total_time, 1) for k, v in metrics["timers"].items()
        }
        
        return metrics

class EntityDetector:
    """Class for detecting entities through address clustering."""
    
    def __init__(self, 
                memory_limit_mb: int = DEFAULT_MEMORY_LIMIT_MB,
                transactions_per_batch: int = DEFAULT_TRANSACTIONS_PER_BATCH):
        """
        Initialize an entity detector.
        
        Args:
            memory_limit_mb: Maximum memory usage in MB before throttling
            transactions_per_batch: Number of transactions to process in a batch
        """
        # Set of all addresses seen
        self.address_set = set()
        
        # Graph for storing relationships between addresses
        self.graph = nx.Graph()
        
        # Store relationships between addresses
        self.relationships = []
        
        # Configuration
        self.memory_limit_mb = memory_limit_mb
        self.transactions_per_batch = transactions_per_batch
        
        # Performance tracking
        self.transactions_analyzed = 0
        self.start_time = time.time()
        self.performance_metrics = {
            "transaction_fetch_time": 0,
            "transaction_analysis_time": 0,
            "clustering_time": 0,
            "total_time": 0,
            "memory_usage_mb": 0,
            "peak_memory_mb": 0
        }
        
        # Performance monitoring
        self.monitor = PerformanceMonitor()
        
        # Add a lock for thread-safe graph operations
        self.graph_lock = Lock()
        
        # Capture baseline memory
        self._update_memory_usage("init")

    def _update_memory_usage(self, label: str):
        """Update memory usage metrics."""
        try:
            self.monitor.capture_memory_usage(label)
            current_memory = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            self.performance_metrics["memory_usage_mb"] = current_memory
            self.performance_metrics["peak_memory_mb"] = max(
                self.performance_metrics.get("peak_memory_mb", 0),
                current_memory
            )
        except Exception as e:
            logger.error(f"Error updating memory usage: {str(e)}")
    
    def check_memory_usage_and_throttle(self):
        """
        Check current memory usage and throttle processing if needed.
        
        Returns:
            True if processing should continue, False if it should be throttled
        """
        current_memory = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        if current_memory > self.memory_limit_mb:
            logger.warning(f"Memory usage ({current_memory:.2f}MB) exceeds limit ({self.memory_limit_mb}MB)")
            return False
        return True

    async def analyze_transaction_batch(self, batch: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
        """
        Analyze a batch of transactions and return address relationships.
        
        Args:
            batch: List of transaction data to analyze
            
        Returns:
            List of tuples containing address relationships (from_address, to_address)
        """
        relationships = []
        
        for tx_data in batch:
            if not isinstance(tx_data, dict):
                logger.warning(f"Invalid transaction data type: {type(tx_data).__name__}")
                continue
                
            # Extract inputs and outputs
            inputs = tx_data.get("inputs", [])
            outputs = tx_data.get("outputs", [])
            
            # Extract unique addresses from inputs and outputs
            input_addresses = []
            for input_data in inputs:
                if isinstance(input_data, dict) and "address" in input_data:
                    addr = input_data["address"]
                    if addr:  # Ensure address is not empty
                        input_addresses.append(addr)
            
            output_addresses = []
            for output_data in outputs:
                if isinstance(output_data, dict) and "address" in output_data:
                    addr = output_data["address"]
                    if addr:  # Ensure address is not empty
                        output_addresses.append(addr)
            
            # Create relationships between input and output addresses
            for input_addr in input_addresses:
                for output_addr in output_addresses:
                    if input_addr != output_addr:  # Avoid self-loops
                        relationships.append((input_addr, output_addr))
        
        return relationships

    async def add_to_graph(self, relationships: List[Tuple[str, str]]):
        """
        Thread-safe method to add relationships to the graph.
        
        Args:
            relationships: List of tuples (source_address, target_address) to add to the graph
        """
        async with self.graph_lock:
            relationships_found = 0
            
            for input_addr, output_addr in relationships:
                # Add nodes if they don't exist
                if input_addr not in self.graph:
                    self.graph.add_node(input_addr)
                    self.address_set.add(input_addr)
                    
                if output_addr not in self.graph:
                    self.graph.add_node(output_addr)
                    self.address_set.add(output_addr)
                    
                # Add or update edge
                if self.graph.has_edge(input_addr, output_addr):
                    # Increment weight if edge exists
                    self.graph[input_addr][output_addr]["weight"] += 1
                else:
                    # Create new edge with weight 1
                    self.graph.add_edge(input_addr, output_addr, weight=1)
                    relationships_found += 1
            
            return relationships_found

    async def analyze_transactions(self, addresses: List[str], txs: List[Dict[str, Any]]) -> None:
        """
        Analyze a batch of transactions to build the transaction graph.
        
        Args:
            addresses: List of addresses being analyzed (to identify input/output relationships)
            txs: List of transaction data to analyze
        """
        self.monitor.start_timer("analyze_transactions")
        analysis_start = time.time()
        
        # Handle case when txs is not a list (e.g., a string or error message)
        if not isinstance(txs, list):
            logger.error(f"Invalid transaction data type: {type(txs)}. Expected a list.")
            self.monitor.stop_timer("analyze_transactions")
            return
        
        logger.info(f"Analyzing {len(txs)} transactions for {len(addresses)} addresses")
        self.monitor.increment_counter("transactions_to_analyze", len(txs))
        
        if not txs:
            logger.warning("No transactions to analyze")
            self.monitor.stop_timer("analyze_transactions")
            return
        
        # Check memory before proceeding
        if not self.check_memory_usage_and_throttle():
            logger.warning("Throttling transaction analysis due to memory constraints")
            txs = txs[:min(len(txs), self.transactions_per_batch // 2)]
            logger.info(f"Reduced batch size to {len(txs)} transactions")
        
        # Process transactions in batches concurrently
        batch_size = min(self.transactions_per_batch, len(txs))  # Use configured or actual count, whichever is smaller
        batches = [txs[i:i+batch_size] for i in range(0, len(txs), batch_size)]
        
        logger.info(f"Processing {len(batches)} transaction batches of size ~{batch_size}")
        
        # Capture memory before batch processing
        self._update_memory_usage("before_batch_processing")
        
        # Process each batch concurrently and collect all relationships
        self.monitor.start_timer("batch_processing")
        batch_tasks = [self.analyze_transaction_batch(batch) for batch in batches]
        batch_results = await asyncio.gather(*batch_tasks)
        self.monitor.stop_timer("batch_processing")
        
        # Capture memory after batch processing
        self._update_memory_usage("after_batch_processing")
        
        # Flatten results
        self.monitor.start_timer("result_processing")
        all_relationships = []
        for relationships in batch_results:
            all_relationships.extend(relationships)
        
        # Increment relationship counter
        self.monitor.increment_counter("relationships_found", len(all_relationships))
        
        # Update graph with all discovered relationships using the thread-safe method
        self.monitor.start_timer("graph_update")
        relationships_found = await self.add_to_graph(all_relationships)
        self.monitor.stop_timer("graph_update")
        self.monitor.stop_timer("result_processing")
        
        # Update transaction count
        self.transactions_analyzed += len(txs)
        
        # Update performance metrics
        analysis_time = time.time() - analysis_start
        self.performance_metrics["transaction_analysis_time"] += analysis_time
        
        # Capture memory after full analysis
        self._update_memory_usage("after_analysis")
        
        logger.info(f"Found {relationships_found} new relationships in {analysis_time:.2f} seconds")
        self.monitor.stop_timer("analyze_transactions")

    def identify_clusters(self, min_confidence: float = 0.1) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
        """
        Run the cluster identification algorithm.
        
        Args:
            min_confidence: Minimum confidence threshold for clustering (0.0-1.0)
            
        Returns:
            Tuple of (clusters, relationships)
        """
        # Convert relationships to a format for the algorithm
        relationship_edges = []
        
        # Start with all relationships
        strong_relationships = []
        
        # Log cluster identification start
        logger.info(f"Starting cluster identification with min_confidence={min_confidence}")
        logger.info(f"Graph has {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
        
        # Add all edges from the graph
        for u, v, data in self.graph.edges(data=True):
            weight = data.get('weight', 0)
            if weight >= min_confidence:
                relationship_edges.append((u, v, weight))
                
                # Add to strong relationships list
                strong_relationships.append({
                    "source": u,
                    "target": v,
                    "strength": weight
                })
        
        logger.info(f"Found {len(relationship_edges)} edges that meet confidence threshold")
        
        # Create a new graph for community detection
        G = nx.Graph()
        
        # Add nodes and edges
        for u, v, weight in relationship_edges:
            G.add_edge(u, v, weight=weight)
        
        # Use community detection algorithm if we have edges
        clusters = {}
        if G.number_of_edges() > 0:
            try:
                # Use Louvain method for community detection
                logger.info("Running Louvain community detection")
                communities = nx.community.louvain_communities(G)
                
                # Assign addresses to clusters
                for i, community in enumerate(communities):
                    cluster_id = str(i)  # Convert to string for JSON serialization
                    logger.info(f"Found community {i} with {len(community)} addresses")
                    for address in community:
                        clusters[address] = cluster_id
            except Exception as e:
                logger.error(f"Error in community detection: {str(e)}")
                # Try alternative community detection if Louvain fails
                try:
                    logger.info("Trying alternative community detection (label propagation)")
                    communities = nx.community.label_propagation_communities(G)
                    for i, community in enumerate(communities):
                        cluster_id = f"lp_{i}"  # Label propagation prefix
                        for address in community:
                            clusters[address] = cluster_id
                except Exception as alt_e:
                    logger.error(f"Alternative community detection also failed: {str(alt_e)}")
        
        # Ensure all addresses have a cluster (even if singleton)
        singleton_count = 0
        for address in self.address_set:
            if address not in clusters:
                # Generate a unique cluster ID for singletons
                cluster_id = f"s_{singleton_count}"
                clusters[address] = cluster_id
                singleton_count += 1
        
        # Log final cluster statistics
        unique_clusters = set(clusters.values())
        logger.info(f"Identified {len(unique_clusters)} unique clusters for {len(self.address_set)} addresses")
        logger.info(f"Average cluster size: {len(self.address_set) / max(len(unique_clusters), 1):.2f} addresses")
        
        # Add statistics to strong relationships
        relationship_stats = {
            "total": len(strong_relationships),
            "min_weight": min([r["strength"] for r in strong_relationships]) if strong_relationships else 0,
            "max_weight": max([r["strength"] for r in strong_relationships]) if strong_relationships else 0,
            "avg_weight": sum([r["strength"] for r in strong_relationships]) / len(strong_relationships) if strong_relationships else 0
        }
        logger.info(f"Relationship statistics: {relationship_stats}")
        
        return clusters, strong_relationships

# Add circuit breaker configuration
class CircuitBreaker:
    """Circuit breaker pattern implementation for API requests."""
    
    def __init__(self, failure_threshold=5, recovery_timeout=30, test_requests=2):
        """Initialize the circuit breaker."""
        self.failure_threshold = failure_threshold  # Number of failures before opening circuit
        self.recovery_timeout = recovery_timeout    # Time to wait before attempting recovery
        self.test_requests = test_requests          # Number of test requests to try in half-open state
        
        self.failures = 0                  # Current failure count
        self.state = CIRCUIT_CLOSED        # Current circuit state
        self.last_failure_time = 0         # Time of last failure
        self.test_requests_remaining = 0   # Test requests remaining in half-open state
        self.lock = asyncio.Lock()         # Lock for thread safety
    
    async def execute(self, func, *args, **kwargs):
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Function result if successful
            
        Raises:
            Exception: If circuit is open or function fails
        """
        async with self.lock:
            # Check circuit state
            if self.state == CIRCUIT_OPEN:
                # Check if recovery timeout has elapsed
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    logger.info("Circuit half-open, testing requests")
                    self.state = CIRCUIT_HALF_OPEN
                    self.test_requests_remaining = self.test_requests
                else:
                    # Circuit is open and timeout hasn't elapsed
                    logger.warning("Circuit is open, request rejected")
                    raise Exception("Circuit breaker is open")
            
            # If we're in half-open state, decrement test requests
            if self.state == CIRCUIT_HALF_OPEN:
                self.test_requests_remaining -= 1
        
        # Execute the function
        try:
            result = await func(*args, **kwargs)
            
            # Function succeeded, update circuit state
            async with self.lock:
                if self.state == CIRCUIT_HALF_OPEN:
                    if self.test_requests_remaining <= 0:
                        # All test requests succeeded, close the circuit
                        logger.info("Circuit closed after successful test requests")
                        self.state = CIRCUIT_CLOSED
                        self.failures = 0
                elif self.state == CIRCUIT_CLOSED:
                    # Reset failure count on success
                    self.failures = 0
            
            return result
            
        except Exception as e:
            # Function failed, update circuit state
            async with self.lock:
                self.failures += 1
                self.last_failure_time = time.time()
                
                if self.state == CIRCUIT_HALF_OPEN or self.failures >= self.failure_threshold:
                    # Open the circuit
                    logger.warning(f"Circuit opened after {self.failures} failures")
                    self.state = CIRCUIT_OPEN
            
            # Re-raise the exception
            raise e

# Global circuit breaker instance
address_api_circuit_breaker = CircuitBreaker(
    failure_threshold=5,     # Open after 5 failures
    recovery_timeout=30,     # Try to recover after 30 seconds
    test_requests=2          # Test with 2 requests before closing
)

async def with_retry(func, *args, max_retries=3, base_delay=1.0, **kwargs):
    """
    Execute a function with exponential backoff retry logic.
    
    Args:
        func: Async function to execute
        *args: Positional arguments for the function
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds between retries (will be multiplied by 2^attempt)
        **kwargs: Keyword arguments for the function
        
    Returns:
        Function result if successful
        
    Raises:
        Exception: If all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):  # +1 for the initial attempt
        try:
            # First attempt or first retry (attempt=1)
            if attempt == 0:
                return await func(*args, **kwargs)
            
            # Calculate exponential backoff with jitter
            delay = base_delay * (2 ** (attempt - 1)) * (0.5 + random.random())
            logger.info(f"Retry attempt {attempt}/{max_retries} for {func.__name__} after {delay:.2f}s delay")
            
            # Wait before retry
            await asyncio.sleep(delay)
            
            # Retry
            return await func(*args, **kwargs)
            
        except Exception as e:
            last_exception = e
            logger.warning(f"Attempt {attempt+1}/{max_retries+1} failed for {func.__name__}: {str(e)}")
    
    # If we get here, all retries failed
    logger.error(f"All {max_retries+1} attempts failed for {func.__name__}")
    raise last_exception

async def safe_fetch_address_transactions(address: str, tx_limit: int):
    """
    Fetch address transactions with circuit breaker and retry logic.
    
    Args:
        address: Address to fetch transactions for
        tx_limit: Maximum number of transactions to fetch
        
    Returns:
        Transaction data dictionary
    """
    try:
        # First try to execute with circuit breaker
        return await address_api_circuit_breaker.execute(
            with_retry,
            fetch_address_transactions, address, tx_limit,
            max_retries=3, base_delay=1.0
        )
    except Exception as e:
        logger.error(f"Failed to fetch transactions for {address} after retries: {str(e)}")
        # Return empty response instead of failing
        return {"items": [], "total": 0}

async def identify_entities(address: str, depth: int = 2, tx_limit: int = 20,
                          concurrency_limit: int = DEFAULT_CONCURRENCY_LIMIT,
                          memory_limit_mb: int = DEFAULT_MEMORY_LIMIT_MB,
                          batch_size: int = DEFAULT_BATCH_SIZE,
                          transactions_per_batch: int = DEFAULT_TRANSACTIONS_PER_BATCH) -> Tuple[List[str], Dict[str, List[str]], List[Dict], Dict]:
    """
    Identify potential entities based on transaction analysis.
    
    Args:
        address: Ergo address to analyze
        depth: How many degrees of separation to analyze (1-3)
        tx_limit: Maximum transactions to analyze per address
        concurrency_limit: Maximum number of concurrent API requests
        memory_limit_mb: Maximum memory usage in MB before throttling
        batch_size: Size of address batches for processing
        transactions_per_batch: Number of transactions to process in a batch
        
    Returns:
        Tuple containing (list of addresses, clusters, relationships, performance metrics)
    """
    # Create a global performance monitor for the entire operation
    global_monitor = PerformanceMonitor()
    global_monitor.start_timer("total")
    
    start_time = time.time()
    global_monitor.capture_memory_usage("start")
    
    if depth < 1:
        depth = 1
    elif depth > 3:
        logger.warning(f"Depth {depth} is high and may result in very large graphs. Consider using a lower value.")
    
    logger.info(f"Starting entity identification for address {address} with depth {depth}, tx_limit {tx_limit}")
    logger.info(f"Configuration: concurrency_limit={concurrency_limit}, "
                f"memory_limit_mb={memory_limit_mb}, batch_size={batch_size}, "
                f"transactions_per_batch={transactions_per_batch}")
    
    # Create entity detector with specified parameters
    detector = EntityDetector(
        memory_limit_mb=memory_limit_mb,
        transactions_per_batch=transactions_per_batch
    )
    
    # Add initial address to processing queue
    to_process = {address}
    processed = set()
    
    # Create a semaphore to limit concurrency
    concurrency_semaphore = Semaphore(concurrency_limit)
    
    # Track time spent fetching transactions
    global_monitor.start_timer("transaction_fetching")
    fetch_start_time = time.time()
    
    # Track success/failure statistics
    stats = {
        "fetch_attempts": 0,
        "fetch_successes": 0,
        "fetch_failures": 0,
        "empty_responses": 0
    }
    
    # Process addresses by level up to specified depth
    for level in range(depth):
        logger.info(f"Processing level {level+1}/{depth} with {len(to_process)} addresses")
        global_monitor.capture_memory_usage(f"level_{level+1}_start")
        
        if not to_process:
            logger.warning(f"No addresses to process at level {level+1}")
            break
        
        # Collect addresses for this level
        level_addresses = list(to_process)
        processed.update(to_process)
        to_process = set()
        
        # Check memory usage and throttle if needed
        if not detector.check_memory_usage_and_throttle():
            logger.warning(f"Memory usage high at {detector.performance_metrics['memory_usage_mb']:.2f}MB. Limiting processing.")
            # Take a smaller subset of addresses
            level_addresses = level_addresses[:min(len(level_addresses), batch_size // 2)]
            logger.info(f"Reduced address list to {len(level_addresses)} addresses due to memory constraints")
        
        # Process each address in this level in batches
        address_batches = [level_addresses[i:i+batch_size] 
                          for i in range(0, len(level_addresses), batch_size)]
        
        for batch_idx, address_batch in enumerate(address_batches):
            logger.info(f"Processing address batch {batch_idx+1}/{len(address_batches)} with {len(address_batch)} addresses")
            global_monitor.capture_memory_usage(f"batch_{level+1}_{batch_idx+1}_start")
            global_monitor.start_timer(f"batch_{level+1}_{batch_idx+1}")
            
            # Fetch transactions for all addresses in this batch concurrently
            async def fetch_with_limit(addr):
                async with concurrency_semaphore:
                    stats["fetch_attempts"] += 1
                    logger.info(f"Fetching transactions for {addr} (limit: {tx_limit})")
                    try:
                        # Use the safe fetch function with circuit breaker and retry
                        result = await safe_fetch_address_transactions(addr, tx_limit)
                        stats["fetch_successes"] += 1
                        
                        # Check if the response is empty
                        items = result.get("items", [])
                        if not items:
                            stats["empty_responses"] += 1
                            logger.warning(f"No transactions found for {addr}")
                        
                        return result
                    except Exception as e:
                        stats["fetch_failures"] += 1
                        logger.error(f"Error fetching transactions for {addr}: {str(e)}")
                        return {"items": []}
            
            # Execute all fetches concurrently within concurrency limits
            fetch_tasks = [fetch_with_limit(addr) for addr in address_batch]
            
            try:
                batch_results = await asyncio.gather(*fetch_tasks)
            except Exception as e:
                logger.error(f"Batch fetch failed: {str(e)}")
                batch_results = [{"items": []} for _ in address_batch]
            
            # Capture memory after fetching
            global_monitor.capture_memory_usage(f"batch_{level+1}_{batch_idx+1}_after_fetch")
            
            # Process each address's transactions and update the graph
            for addr_idx, addr in enumerate(address_batch):
                tx_response = batch_results[addr_idx]
                
                if not isinstance(tx_response, dict):
                    logger.error(f"Invalid response for {addr}: {type(tx_response).__name__}")
                    continue
                
                # Extract transaction items from response
                tx_items = tx_response.get("items", [])
                
                if not tx_items:
                    logger.warning(f"No transactions found for address {addr}")
                    continue
                
                logger.info(f"Found {len(tx_items)} transactions for {addr}")
                
                try:
                    # Analyze the transactions to build the graph
                    await detector.analyze_transactions([addr], tx_items)
                    
                    # Collect new addresses for the next level
                    if level < depth - 1:
                        for neighbor in detector.graph.neighbors(addr):
                            if neighbor not in processed:
                                to_process.add(neighbor)
                except Exception as e:
                    logger.error(f"Error analyzing transactions for {addr}: {str(e)}")
            
            global_monitor.stop_timer(f"batch_{level+1}_{batch_idx+1}")
            global_monitor.capture_memory_usage(f"batch_{level+1}_{batch_idx+1}_end")
        
        global_monitor.capture_memory_usage(f"level_{level+1}_end")
    
    # Update performance metrics
    global_monitor.stop_timer("transaction_fetching")
    detector.performance_metrics["transaction_fetch_time"] = time.time() - fetch_start_time
    
    # Add request statistics to performance metrics
    detector.performance_metrics["fetch_stats"] = stats
    
    # Identify clusters
    global_monitor.start_timer("clustering")
    clustering_start = time.time()
    try:
        address_to_cluster, relationships = detector.identify_clusters()
    except Exception as e:
        logger.error(f"Error identifying clusters: {str(e)}")
        # Return empty results in case of failure
        address_to_cluster = {}
        relationships = []
    
    detector.performance_metrics["clustering_time"] = time.time() - clustering_start
    global_monitor.stop_timer("clustering")
    
    # Calculate total time
    detector.performance_metrics["total_time"] = time.time() - start_time
    
    # Collect final results
    addresses = list(detector.address_set)
    
    # Capture final memory usage
    global_monitor.capture_memory_usage("end")
    global_monitor.stop_timer("total")
    
    # Add global performance monitor data to metrics
    detailed_metrics = global_monitor.get_detailed_metrics()
    detailed_metrics.update(detector.performance_metrics)
    detailed_metrics["addresses_found"] = len(addresses)
    detailed_metrics["clusters_found"] = len(address_to_cluster)
    detailed_metrics["relationships_found"] = len(relationships)
    
    logger.info(f"Entity identification complete in {detector.performance_metrics['total_time']:.2f} seconds")
    logger.info(f"Found {len(addresses)} addresses in {len(address_to_cluster)} clusters")
    logger.info(f"Peak memory usage: {detailed_metrics['memory']['peak_mb']:.2f}MB")
    logger.info(f"Performance: Fetch: {detector.performance_metrics['transaction_fetch_time']:.2f}s, "
                f"Analysis: {detector.performance_metrics['transaction_analysis_time']:.2f}s, "
                f"Clustering: {detector.performance_metrics['clustering_time']:.2f}s")
    logger.info(f"Request stats: Attempts: {stats['fetch_attempts']}, "
                f"Successes: {stats['fetch_successes']}, "
                f"Failures: {stats['fetch_failures']}, "
                f"Empty: {stats['empty_responses']}")
    
    return addresses, address_to_cluster, relationships, detailed_metrics

async def fetch_transactions_in_parallel(addresses: List[str], tx_limit: int, 
                                         concurrency_limit: int = DEFAULT_CONCURRENCY_LIMIT,
                                         batch_size: int = DEFAULT_BATCH_SIZE) -> Dict[str, Any]:
    """
    Fetch transactions for multiple addresses in parallel with concurrency control.
    
    Args:
        addresses: List of addresses to fetch transactions for
        tx_limit: Maximum transactions to fetch per address
        concurrency_limit: Maximum number of concurrent requests
        batch_size: Size of batches for processing
        
    Returns:
        Dictionary mapping addresses to their transaction data
    """
    if not addresses:
        return {}
    
    logger.info(f"Fetching transactions for {len(addresses)} addresses with concurrency limit {concurrency_limit}")
    
    # Use a semaphore to limit concurrency
    semaphore = Semaphore(concurrency_limit)
    results = {}
    
    async def fetch_with_semaphore(address):
        """Fetch transactions for an address with semaphore for concurrency control"""
        async with semaphore:
            try:
                logger.debug(f"Fetching transactions for {address} (limit: {tx_limit})")
                start = time.time()
                result = await fetch_address_transactions(address, limit=tx_limit)
                duration = time.time() - start
                logger.debug(f"Fetched transactions for {address} in {duration:.2f}s")
                return address, result
            except Exception as e:
                logger.error(f"Error fetching transactions for {address}: {str(e)}")
                return address, {"items": [], "total": 0}
    
    # Process addresses in batches to avoid creating too many tasks at once
    for i in range(0, len(addresses), batch_size):
        batch = addresses[i:i+batch_size]
        logger.debug(f"Processing batch {i//batch_size + 1} with {len(batch)} addresses")
        
        # Create fetch tasks for this batch
        tasks = [fetch_with_semaphore(addr) for addr in batch]
        
        # Execute tasks in parallel
        batch_results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Process results
        for address, data in batch_results:
            if address and data:
                results[address] = data
    
    logger.info(f"Successfully fetched transactions for {len(results)}/{len(addresses)} addresses")
    return results

async def identify_entities_json(address: str, depth: int = 2, tx_limit: int = 100, 
                               concurrency_limit: int = DEFAULT_CONCURRENCY_LIMIT,
                               memory_limit_mb: int = DEFAULT_MEMORY_LIMIT_MB,
                               batch_size: int = DEFAULT_BATCH_SIZE,
                               transactions_per_batch: int = DEFAULT_TRANSACTIONS_PER_BATCH,
                               include_detailed_metrics: bool = False,
                               compact_output: bool = True) -> str:
    """
    Identify potential entities and return the results as a JSON string.
    
    Args:
        address: Ergo address to analyze
        depth: How many degrees of separation to analyze (1-3)
        tx_limit: Maximum transactions to analyze per address
        concurrency_limit: Maximum number of concurrent API requests
        memory_limit_mb: Maximum memory usage in MB before throttling
        batch_size: Size of address batches for processing
        transactions_per_batch: Number of transactions to process in a batch
        include_detailed_metrics: Whether to include detailed performance metrics in the response
        compact_output: Whether to produce a compact response with minimal data for LLM processing. Default is True.
        
    Returns:
        JSON string with entity identification results
    """
    start_time = time.time()
    
    try:
        # Increase both depth and tx_limit to find more relationships
        if depth < 2:
            depth = 2  # Ensure we look at least 2 levels deep
        
        if tx_limit < 100:
            tx_limit = 100  # Ensure we look at enough transactions
            
        logger.info(f"Starting entity identification for {address} with depth={depth}, tx_limit={tx_limit}")
        
        # Call identify_entities to find relationships
        addresses, address_to_cluster, relationships, performance_metrics = await identify_entities(
            address, depth, tx_limit, concurrency_limit,
            memory_limit_mb, batch_size, transactions_per_batch
        )
        
        # Convert clusters to a format suitable for the response
        cluster_map = defaultdict(list)
        for addr, cluster_id in address_to_cluster.items():
            cluster_map[cluster_id].append(addr)
        
        # Find the cluster for the seed address
        seed_cluster = address_to_cluster.get(address)
        
        # If no cluster was found for the seed address, create a singleton cluster
        if seed_cluster is None:
            logger.warning(f"No cluster found for seed address {address}, creating singleton cluster")
            seed_cluster = "singleton"
            address_to_cluster[address] = seed_cluster
            cluster_map[seed_cluster] = [address]
            addresses.append(address)
        
        # Ensure the address is in the addresses list
        if address not in addresses:
            logger.warning(f"Seed address {address} was not in the addresses list, adding it")
            addresses.append(address)
        
        # Check if we got any relationships
        if not relationships and len(addresses) > 1:
            logger.warning(f"No relationships found despite having {len(addresses)} addresses")
            # Try to build some basic relationships from the cluster data
            for cluster_id, addrs in cluster_map.items():
                if len(addrs) > 1 and address in addrs:
                    for addr in addrs:
                        if addr != address:
                            relationships.append({
                                "source": address,
                                "target": addr,
                                "strength": 1,
                                "inferred": True
                            })
        
        total_time = time.time() - start_time
        
        # Extract request stats if available
        request_stats = performance_metrics.get("fetch_stats", {})
        
        # Prepare basic performance metrics
        basic_perf_metrics = {
            "total_time_ms": int(total_time * 1000),
            "address_count": len(addresses),
            "cluster_count": len(cluster_map),
            "relationship_count": len(relationships)
        }
        
        # Create full performance metrics if needed
        if not compact_output:
            perf_metrics = {
                "total_time_ms": int(performance_metrics.get("total_time", 0) * 1000),
                "fetch_time_ms": int(performance_metrics.get("transaction_fetch_time", 0) * 1000),
                "analysis_time_ms": int(performance_metrics.get("transaction_analysis_time", 0) * 1000),
                "clustering_time_ms": int(performance_metrics.get("clustering_time", 0) * 1000),
                "transactions_analyzed": performance_metrics.get("transactions_analyzed", 0),
                "memory_usage_mb": round(performance_metrics.get("memory_usage_mb", 0), 2),
                "peak_memory_mb": round(performance_metrics.get("peak_memory_mb", 0), 2),
                "request_stats": {
                    "attempts": request_stats.get("fetch_attempts", 0),
                    "successes": request_stats.get("fetch_successes", 0),
                    "failures": request_stats.get("fetch_failures", 0),
                    "empty_responses": request_stats.get("empty_responses", 0)
                },
                "success_rate": round(request_stats.get("fetch_successes", 0) / max(request_stats.get("fetch_attempts", 1), 1) * 100, 2)
            }
            
            # Include detailed metrics if requested
            if include_detailed_metrics:
                perf_metrics["detailed"] = {
                    k: v for k, v in performance_metrics.items() 
                    if k not in ["fetch_stats"] and isinstance(v, (int, float, str, dict, list))
                }
        else:
            perf_metrics = basic_perf_metrics
        
        # Calculate cluster statistics
        if not compact_output:
            cluster_stats = {
                "total_clusters": len(cluster_map),
                "largest_cluster_size": max([len(addrs) for addrs in cluster_map.values()]) if cluster_map else 0,
                "smallest_cluster_size": min([len(addrs) for addrs in cluster_map.values()]) if cluster_map else 0,
                "avg_cluster_size": sum([len(addrs) for addrs in cluster_map.values()]) / max(len(cluster_map), 1) if cluster_map else 0,
                "addresses_in_clusters": sum([len(addrs) for addrs in cluster_map.values()]) if cluster_map else 0
            }
        else:
            cluster_stats = {
                "total_clusters": len(cluster_map),
                "largest_cluster_size": max([len(addrs) for addrs in cluster_map.values()]) if cluster_map else 0
            }
        
        # Create the compact or full response object
        if compact_output:
            # For compact output, only include essential information
            # Limit number of addresses and relationships to prevent verbose output
            MAX_ADDRESSES = 10  # Only show the first 10 addresses
            MAX_RELATIONSHIPS = 5  # Only show the first 5 relationships
            MAX_CLUSTER_ADDRESSES = 5  # Only show up to 5 addresses per cluster
            
            # Create a compact version of clusters
            compact_clusters = {}
            for cluster_id, cluster_addresses in cluster_map.items():
                if cluster_id == seed_cluster:
                    # For seed cluster, include all addresses up to the limit
                    compact_clusters[cluster_id] = cluster_addresses[:MAX_CLUSTER_ADDRESSES]
                    if len(cluster_addresses) > MAX_CLUSTER_ADDRESSES:
                        compact_clusters[cluster_id].append(f"...and {len(cluster_addresses) - MAX_CLUSTER_ADDRESSES} more")
            
            result = {
                "seed_address": address,
                "seed_cluster_id": seed_cluster,
                "addresses_sample": addresses[:MAX_ADDRESSES],
                "address_count": len(addresses),
                "clusters": compact_clusters,
                "relationships_sample": relationships[:MAX_RELATIONSHIPS],
                "relationship_count": len(relationships),
                "performance": basic_perf_metrics
            }
        else:
            # Create the full response object
            result = {
                "seed_address": address,
                "seed_cluster_id": seed_cluster,
                "addresses": addresses,
                "clusters": {k: v for k, v in cluster_map.items() if k is not None},
                "relationships": relationships,
                "total_addresses": len(addresses),
                "total_clusters": len(cluster_map),
                "cluster_stats": cluster_stats,
                "performance": perf_metrics,
                "configuration": {
                    "depth": depth,
                    "tx_limit": tx_limit,
                    "concurrency_limit": concurrency_limit,
                    "memory_limit_mb": memory_limit_mb,
                    "batch_size": batch_size,
                    "transactions_per_batch": transactions_per_batch
                }
            }
        
        logger.info(f"Entity identification complete: found {len(addresses)} addresses in {len(cluster_map)} clusters")
        logger.info(f"Total execution time: {total_time:.2f} seconds")
        
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in entity identification: {str(e)}", exc_info=True)
        # Create a minimal response with the error
        error_response = {
            "seed_address": address,
            "seed_cluster_id": "error",
            "addresses": [address],
            "error": str(e),
            "performance": {
                "total_time_ms": int((time.time() - start_time) * 1000),
                "error": True
            }
        }
        return json.dumps(error_response)

def format_entity_detection_result(entity_data: Dict[str, Any], html: bool = False) -> str:
    """
    Format entity detection results for display.
    
    Args:
        entity_data: Entity detection data from identify_entities
        html: Whether to format as HTML
        
    Returns:
        Formatted text/html string
    """
    seed_address = entity_data.get("seed_address", "Unknown")
    seed_cluster = entity_data.get("seed_cluster_id")
    
    # Handle both compact and full output formats
    if "clusters" in entity_data:
        # Full format
        clusters = entity_data.get("clusters", {})
    else:
        # Compact format might have different structure
        clusters = {}
    
    # Get address count
    if "address_count" in entity_data:
        # Using compact format
        address_count = entity_data.get("address_count", 0)
        relationship_count = entity_data.get("relationship_count", 0)
        cluster_count = len(entity_data.get("clusters", {}))
    else:
        # Using full format
        address_count = len(entity_data.get("addresses", []))
        relationship_count = len(entity_data.get("relationships", []))
        cluster_count = entity_data.get("total_clusters", 0)
    
    # Format basic information - keep it concise for both HTML and text
    if html:
        result = f"<h3>Entity Analysis for {seed_address}</h3>"
        result += f"<p>Found {cluster_count} potential entity clusters with {address_count} addresses.</p>"
        result += f"<p>The address belongs to cluster {seed_cluster}.</p>"
        
        # Only add cluster details if we have a reasonable amount
        if cluster_count > 0 and cluster_count <= 5:
            result += "<h4>Clusters:</h4><ul>"
            for cluster_id, addresses in clusters.items():
                if isinstance(addresses, list):
                    count = len(addresses)
                    result += f"<li>Cluster {cluster_id}: {count} addresses</li>"
            result += "</ul>"
            
        # Add performance summary
        perf = entity_data.get("performance", {})
        if perf:
            total_time_ms = perf.get("total_time_ms", 0)
            result += f"<p>Analysis completed in {total_time_ms/1000:.2f} seconds.</p>"
    else:
        # Create a concise text summary
        result = f"Entity Analysis for {seed_address}: "
        result += f"Found {cluster_count} potential entity clusters with {address_count} addresses and {relationship_count} relationships. "
        result += f"The seed address belongs to cluster {seed_cluster}."
        
        # Add performance summary
        perf = entity_data.get("performance", {})
        if perf:
            total_time_ms = perf.get("total_time_ms", 0)
            result += f" Analysis completed in {total_time_ms/1000:.2f} seconds."
    
    return result 