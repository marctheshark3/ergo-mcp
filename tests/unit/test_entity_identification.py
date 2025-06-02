"""
Unit tests for the entity_identification.py module.
"""

import asyncio
import json
import logging
import pytest
import networkx as nx
from unittest.mock import patch, MagicMock, AsyncMock
from collections import defaultdict

from ergo_explorer.tools.entity_identification import (
    EntityDetector, 
    identify_entities, 
    identify_entities_json,
    CircuitBreaker,
    safe_fetch_address_transactions,
    with_retry,
    PerformanceMonitor
)

# Disable noisy logging during tests
logging.basicConfig(level=logging.ERROR)

# Mock transaction data
MOCK_TX_DATA = [
    {
        "id": "tx1",
        "inputs": [
            {"address": "addr1"},
            {"address": "addr2"}
        ],
        "outputs": [
            {"address": "addr3"},
            {"address": "addr4"}
        ]
    },
    {
        "id": "tx2",
        "inputs": [
            {"address": "addr3"},
            {"address": "addr5"}
        ],
        "outputs": [
            {"address": "addr6"},
            {"address": "addr2"}
        ]
    },
    {
        "id": "tx3",
        "inputs": [
            {"address": "addr4"}
        ],
        "outputs": [
            {"address": "addr5"},
            {"address": "addr7"}
        ]
    }
]

@pytest.fixture
def entity_detector():
    """Create an EntityDetector instance for testing."""
    detector = EntityDetector(memory_limit_mb=100, transactions_per_batch=10)
    return detector

class TestEntityDetector:
    """Test the EntityDetector class."""

    @pytest.mark.asyncio
    async def test_analyze_transaction_batch(self, entity_detector):
        """Test the analyze_transaction_batch method."""
        relationships = await entity_detector.analyze_transaction_batch(MOCK_TX_DATA)
        
        # We should find relationships between all input and output addresses
        assert len(relationships) == 5  # 2 inputs * 2 outputs + 1 input * 2 outputs
        
        # Check specific relationships
        assert ("addr1", "addr3") in relationships
        assert ("addr1", "addr4") in relationships
        assert ("addr2", "addr3") in relationships
        assert ("addr2", "addr4") in relationships
        assert ("addr4", "addr5") in relationships
        assert ("addr4", "addr7") in relationships

    @pytest.mark.asyncio
    async def test_add_to_graph(self, entity_detector):
        """Test the add_to_graph method."""
        relationships = [
            ("addr1", "addr3"),
            ("addr1", "addr4"),
            ("addr2", "addr3"),
            ("addr1", "addr3"),  # Duplicate to test weight incrementing
        ]
        
        relationships_found = await entity_detector.add_to_graph(relationships)
        
        # Check graph structure
        assert len(entity_detector.graph.nodes()) == 4  # addr1, addr2, addr3, addr4
        assert len(entity_detector.graph.edges()) == 3  # Unique edges
        
        # Check that weights are correct
        assert entity_detector.graph["addr1"]["addr3"]["weight"] == 2  # Incremented for duplicate
        assert entity_detector.graph["addr1"]["addr4"]["weight"] == 1
        assert entity_detector.graph["addr2"]["addr3"]["weight"] == 1
        
        # Check relationships added count
        assert relationships_found == 3  # Number of unique edges added

    @pytest.mark.asyncio
    async def test_analyze_transactions(self, entity_detector):
        """Test the analyze_transactions method."""
        addresses = ["addr1", "addr2", "addr3"]
        
        await entity_detector.analyze_transactions(addresses, MOCK_TX_DATA)
        
        # Verify graph has been constructed
        assert len(entity_detector.graph.nodes()) > 0
        assert len(entity_detector.graph.edges()) > 0
        
        # Check transaction counter
        assert entity_detector.transactions_analyzed == 3
        
        # Test with invalid data
        await entity_detector.analyze_transactions(addresses, "invalid data")  # Should handle gracefully
        await entity_detector.analyze_transactions(addresses, [])  # Empty list
        
        # Verify the same transaction count
        assert entity_detector.transactions_analyzed == 3  # Unchanged due to invalid data

    def test_check_memory_usage_and_throttle(self, entity_detector):
        """Test the check_memory_usage_and_throttle method."""
        # Mock psutil.Process to control the reported memory usage
        with patch('psutil.Process') as mock_process:
            # Set memory usage below the limit
            mock_process.return_value.memory_info.return_value.rss = 50 * 1024 * 1024  # 50MB
            
            # Should not throttle
            result = entity_detector.check_memory_usage_and_throttle()
            assert result is True
            
            # Set memory usage above the limit
            mock_process.return_value.memory_info.return_value.rss = 200 * 1024 * 1024  # 200MB
            
            # Should throttle
            result = entity_detector.check_memory_usage_and_throttle()
            assert result is False

    def test_identify_clusters(self, entity_detector):
        """Test the identify_clusters method."""
        # Add some test data to the graph
        entity_detector.graph.add_edge("addr1", "addr2", weight=3)
        entity_detector.graph.add_edge("addr2", "addr3", weight=2)
        entity_detector.graph.add_edge("addr4", "addr5", weight=1)
        entity_detector.address_set = {"addr1", "addr2", "addr3", "addr4", "addr5", "addr6"}
        
        # Run cluster identification
        clusters, relationships = entity_detector.identify_clusters(min_confidence=0.5)
        
        # Check that all addresses have cluster assignments
        assert len(clusters) == len(entity_detector.address_set)
        
        # Check that addr1, addr2, addr3 are in the same cluster
        assert clusters["addr1"] == clusters["addr2"]
        assert clusters["addr2"] == clusters["addr3"]
        
        # Check that addr6 has its own singleton cluster
        assert clusters["addr6"] not in [clusters["addr1"], clusters["addr4"]]
        
        # Check relationships
        assert len(relationships) == 2  # Only edges with weight >= 0.5


class TestCircuitBreaker:
    """Test the CircuitBreaker class."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_execution(self):
        """Test the circuit breaker execution with success and failure."""
        circuit_breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,
            test_requests=1
        )
        
        # Mock function that succeeds
        mock_success = AsyncMock(return_value="success")
        
        # Test successful execution
        result = await circuit_breaker.execute(mock_success, "arg1", kwarg1="value1")
        assert result == "success"
        assert circuit_breaker.failures == 0
        assert circuit_breaker.state == "closed"
        
        # Mock function that fails
        mock_failure = AsyncMock(side_effect=Exception("test failure"))
        
        # Test first failure
        with pytest.raises(Exception) as exc_info:
            await circuit_breaker.execute(mock_failure)
        assert "test failure" in str(exc_info.value)
        assert circuit_breaker.failures == 1
        assert circuit_breaker.state == "closed"
        
        # Test second failure to open the circuit
        with pytest.raises(Exception):
            await circuit_breaker.execute(mock_failure)
        assert circuit_breaker.failures == 2
        assert circuit_breaker.state == "open"
        
        # Test rejection when circuit is open
        with pytest.raises(Exception) as exc_info:
            await circuit_breaker.execute(mock_success)
        assert "Circuit breaker is open" in str(exc_info.value)
        
        # Wait for recovery timeout
        await asyncio.sleep(0.2)
        
        # Test half-open state allowing one request
        result = await circuit_breaker.execute(mock_success)
        assert result == "success"
        assert circuit_breaker.state == "closed"  # Should close after success


class TestHelperFunctions:
    """Test helper functions in entity_identification.py."""
    
    @pytest.mark.asyncio
    async def test_with_retry(self):
        """Test the retry mechanism."""
        # Mock function that fails twice then succeeds
        mock_func = AsyncMock(side_effect=[
            Exception("first failure"),
            Exception("second failure"),
            "success"
        ])
        
        # Should succeed on third try
        result = await with_retry(mock_func, max_retries=2, base_delay=0.01)
        assert result == "success"
        assert mock_func.call_count == 3
        
        # Reset mock
        mock_func.reset_mock()
        
        # Mock function that always fails
        mock_func.side_effect = Exception("always fails")
        
        # Should raise exception after all retries
        with pytest.raises(Exception) as exc_info:
            await with_retry(mock_func, max_retries=2, base_delay=0.01)
        assert "always fails" in str(exc_info.value)
        assert mock_func.call_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_safe_fetch_address_transactions(self):
        """Test the safe_fetch_address_transactions function."""
        # Mock the dependencies
        with patch('ergo_explorer.tools.entity_identification.address_api_circuit_breaker.execute') as mock_execute, \
             patch('ergo_explorer.tools.entity_identification.with_retry') as mock_retry, \
             patch('ergo_explorer.tools.entity_identification.fetch_address_transactions') as mock_fetch:
                
            # Setup mock to return successful response
            mock_execute.return_value = {"items": [{"id": "tx1"}], "total": 1}
            
            # Test successful fetch
            result = await safe_fetch_address_transactions("test_address", 10)
            assert "items" in result
            assert result["total"] == 1
            
            # Setup mock to raise exception
            mock_execute.side_effect = Exception("API error")
            
            # Test failed fetch (should return empty response)
            result = await safe_fetch_address_transactions("test_address", 10)
            assert "items" in result
            assert len(result["items"]) == 0
            assert result["total"] == 0


@pytest.mark.asyncio
async def test_identify_entities():
    """Test the identify_entities function."""
    # Mock the safe_fetch_address_transactions function
    with patch('ergo_explorer.tools.entity_identification.safe_fetch_address_transactions') as mock_fetch:
        mock_fetch.return_value = {"items": MOCK_TX_DATA, "total": len(MOCK_TX_DATA)}
        
        # Call the function
        addresses, address_to_cluster, relationships, performance_metrics = await identify_entities(
            "addr1", depth=1, tx_limit=10, concurrency_limit=5,
            memory_limit_mb=100, batch_size=10, transactions_per_batch=10
        )
        
        # Check results
        assert "addr1" in addresses
        assert "addr1" in address_to_cluster
        assert len(relationships) > 0
        assert "total_time" in performance_metrics
        assert "memory_usage_mb" in performance_metrics
        assert "transaction_fetch_time" in performance_metrics
        
        # Test error case - empty response
        mock_fetch.return_value = {"items": [], "total": 0}
        
        # Call should still work
        addresses, address_to_cluster, relationships, performance_metrics = await identify_entities(
            "addr1", depth=1, tx_limit=10, concurrency_limit=5,
            memory_limit_mb=100, batch_size=10, transactions_per_batch=10
        )
        
        # Check results - should have the original address
        assert "addr1" in addresses
        assert len(address_to_cluster) >= 1  # At least the original address
        
        # Test with API error
        mock_fetch.side_effect = Exception("API error")
        
        # Call should still work and return the original address
        addresses, address_to_cluster, relationships, performance_metrics = await identify_entities(
            "addr1", depth=1, tx_limit=10, concurrency_limit=5,
            memory_limit_mb=100, batch_size=10, transactions_per_batch=10
        )
        
        # Check results - should have the original address
        assert "addr1" in addresses
        assert len(address_to_cluster) >= 1  # At least the original address


@pytest.mark.asyncio
async def test_identify_entities_json():
    """Test the identify_entities_json function."""
    # Mock the identify_entities function
    with patch('ergo_explorer.tools.entity_identification.identify_entities') as mock_identify:
        # Setup mock return values
        mock_identify.return_value = (
            ["addr1", "addr2", "addr3"],  # addresses
            {"addr1": "0", "addr2": "0", "addr3": "1"},  # address_to_cluster
            [{"source": "addr1", "target": "addr2", "strength": 2}],  # relationships
            {"total_time": 1.0}  # performance_metrics
        )
        
        # Call the function
        result_json = await identify_entities_json("addr1")
        
        # Parse the result
        result = json.loads(result_json)
        
        # Check basic structure
        assert result["seed_address"] == "addr1"
        assert result["seed_cluster_id"] == "0"
        assert "clusters" in result
        assert "0" in result["clusters"]
        assert "relationships" in result
        assert len(result["relationships"]) == 1
        assert "performance" in result
        
        # Test error case
        mock_identify.side_effect = Exception("Test error")
        
        # Should return error response
        result_json = await identify_entities_json("addr1")
        result = json.loads(result_json)
        
        # Check error response
        assert result["seed_address"] == "addr1"
        assert "error" in result
        assert "Test error" in result["error"]
        assert result["addresses"] == ["addr1"]
        assert result["performance"]["error"] is True


def test_performance_monitor():
    """Test the PerformanceMonitor class."""
    monitor = PerformanceMonitor()
    
    # Test timer functions
    monitor.start_timer("test_timer")
    monitor.stop_timer("test_timer")
    
    # Test counters
    monitor.increment_counter("test_counter")
    monitor.increment_counter("test_counter", 5)
    
    # Test memory capture
    monitor.capture_memory_usage("test_label")
    
    # Get metrics and verify structure
    metrics = monitor.get_detailed_metrics()
    
    assert "total_execution_time_seconds" in metrics
    assert "timers" in metrics
    assert "test_timer" in metrics["timers"]
    assert "counters" in metrics
    assert metrics["counters"]["test_counter"] == 6
    assert "memory" in metrics
    assert "current_mb" in metrics["memory"]
    assert "peak_mb" in metrics["memory"]
    assert "detailed" in metrics["memory"]
    assert len(metrics["memory"]["detailed"]) >= 2  # Init and test_label
    assert metrics["memory"]["detailed"][1]["label"] == "test_label" 