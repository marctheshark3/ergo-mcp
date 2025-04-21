#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${YELLOW}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║      Stopping Ergo Explorer + MCPO Docker            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Docker Compose is installed (either standalone or as plugin)
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo -e "${RED}Docker Compose is required but not installed. Please install Docker Compose and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}Using Docker Compose command: ${DOCKER_COMPOSE_CMD}${NC}"

# Stop the Docker containers
echo -e "${YELLOW}Stopping Ergo Explorer and MCPO with Docker Compose...${NC}"
$DOCKER_COMPOSE_CMD down

echo -e "${GREEN}Services stopped successfully!${NC}" 