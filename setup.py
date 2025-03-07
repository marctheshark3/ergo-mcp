#!/usr/bin/env python
"""
Setup script for ergo-explorer-mcp package.
"""

from setuptools import setup, find_packages

setup(
    name="ergo_explorer_mcp",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "mcp>=0.5.0",
        "httpx",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "ergo-explorer-mcp=ergo_explorer:run_server",
        ],
    },
    author="Ergo Explorer MCP Team",
    author_email="info@example.com",
    description="MCP server for exploring and analyzing the Ergo blockchain",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/ergo-explorer-mcp",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 