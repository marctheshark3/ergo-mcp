FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files
COPY . .

# Create and activate virtual environment, install dependencies
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt && \
    /venv/bin/pip install -e .

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

# Create an entrypoint script
RUN echo '#!/bin/bash\npython -m ergo_explorer "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"] 