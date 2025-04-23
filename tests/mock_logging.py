"""
Mock logging configuration for tests.

This module replaces the actual logging configuration to prevent permission errors during tests.
"""

import logging
import os

# Create a logs directory for tests
logs_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, "test.log")),
        logging.StreamHandler()
    ]
)

# Simple mock for the get_logger function
def get_logger(module_name, log_level=None):
    """Mock implementation of get_logger."""
    logger = logging.getLogger(module_name)
    if log_level:
        logger.setLevel(log_level)
    return logger

# Mock for configure_logging function
def configure_logging(module_name, log_level=None):
    """Mock implementation of configure_logging."""
    return get_logger(module_name, log_level)

# Mock for init_root_logger function
def init_root_logger():
    """Mock implementation of init_root_logger."""
    return None 