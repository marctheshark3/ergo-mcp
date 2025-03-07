#!/usr/bin/env python
"""
Setup script for ergo-explorer-mcp package.
"""

from setuptools import setup, find_packages

setup(
    name="ergo-explorer-mcp",
    version="0.1.0",
    description="MCP server for exploring the Ergo blockchain",
    author="Ergo MCP Team",
    author_email="example@example.com",
    url="https://github.com/yourusername/ergo-explorer-mcp",
    packages=find_packages(),
    install_requires=[
        "mcp>=0.5.0",
        "httpx",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 