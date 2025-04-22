"""
Centralized logging configuration for the Ergo Explorer MCP.

This module provides a consistent logging setup across all components of the application,
making it easier to manage log levels, formats, and output destinations.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Default log level from environment or INFO
DEFAULT_LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

# Standard log format with timestamp, level, logger name, and message
STANDARD_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
SIMPLE_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

def get_log_level(level_name=None):
    """Convert string log level to logging constant."""
    level_name = level_name or DEFAULT_LOG_LEVEL
    
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    return log_levels.get(level_name, logging.INFO)

def configure_logging(module_name=None, log_level=None, log_file=None):
    """
    Configure logging for a module.
    
    Args:
        module_name: Name of the module (used for both logger name and default log file name)
        log_level: Log level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Custom log file name
        
    Returns:
        Configured logger instance
    """
    # Determine logger name
    logger_name = module_name or 'ergo_explorer'
    
    # Get logger
    logger = logging.getLogger(logger_name)
    
    # Skip if logger is already configured
    if logger.handlers:
        return logger
    
    # Set log level
    level = get_log_level(log_level)
    logger.setLevel(level)
    
    # Determine log file name
    if not log_file and module_name:
        date_suffix = datetime.now().strftime('%Y%m%d')
        log_file = f"logs/{module_name.replace('.', '_')}_{date_suffix}.log"
    elif not log_file:
        log_file = f"logs/ergo_explorer_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Use rotating file handler to prevent large log files
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)
    
    # Create formatters
    console_formatter = logging.Formatter(SIMPLE_FORMAT)
    file_formatter = logging.Formatter(STANDARD_FORMAT)
    
    # Set formatters
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(module_name, log_level=None):
    """
    Get a configured logger for a module.
    
    This is the main function that should be used by modules to get a logger.
    
    Args:
        module_name: Usually __name__ of the calling module
        log_level: Optional override of the default log level
        
    Returns:
        Configured logger instance
    """
    return configure_logging(module_name, log_level)

# Initialize root logger with basic configuration
def init_root_logger():
    """Initialize the root logger with basic configuration."""
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure root logger
    level = get_log_level()
    root_logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(SIMPLE_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    return root_logger 