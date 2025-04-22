#!/bin/bash
set -e

# Define constants
CONTAINER_NAME="ergo-mcp"
IMAGE_NAME="ergo-explorer-mcp:latest"
PORT="8000"
HOST_PORT="8000"

# Display help message
function show_help {
    echo "Ergo Explorer MCP Container Manager"
    echo ""
    echo "Usage: ./manage_mcp.sh COMMAND"
    echo ""
    echo "Commands:"
    echo "  start         Start the MCP container"
    echo "  stop          Stop the running MCP container"
    echo "  restart       Restart the MCP container"
    echo "  status        Show container status"
    echo "  logs          Show container logs"
    echo "  reload        Rebuild image and restart container"
    echo "  debug         Run with interactive shell for debugging"
    echo "  clean         Remove all stopped ergo containers"
    echo "  help          Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  ERGO_NODE_API       Ergo node API URL (default: http://localhost:9053)"
    echo "  ERGO_NODE_API_KEY   Ergo node API key (default: hashcream)"
    echo "  SERVER_PORT         MCP server port (default: 8000)"
    echo ""
}

# Start the container
function start_container {
    # Check if container is already running
    if docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo "Container $CONTAINER_NAME is already running."
        echo "Use './manage_mcp.sh restart' to restart it."
        return 0
    fi

    # Check if container exists but is stopped
    if docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo "Starting existing container $CONTAINER_NAME..."
        docker start $CONTAINER_NAME
        echo "Container started successfully."
        return 0
    fi

    # Set default values for environment variables if not provided
    ERGO_NODE_API=${ERGO_NODE_API:-http://host.docker.internal:9053}
    ERGO_NODE_API_KEY=${ERGO_NODE_API_KEY:-hashcream}
    HOST_PORT=${SERVER_PORT:-$HOST_PORT}
    CONTAINER_PORT=$PORT

    echo "Starting new container $CONTAINER_NAME..."
    docker run -d \
        --name $CONTAINER_NAME \
        --add-host=host.docker.internal:host-gateway \
        -p $HOST_PORT:$CONTAINER_PORT \
        -e ERGO_NODE_API=$ERGO_NODE_API \
        -e ERGO_NODE_API_KEY=$ERGO_NODE_API_KEY \
        -e SERVER_PORT=$CONTAINER_PORT \
        $IMAGE_NAME

    echo "Container started successfully."
    echo "MCP server available at http://localhost:$HOST_PORT"
}

# Stop the container
function stop_container {
    if ! docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo "Container $CONTAINER_NAME is not running."
        return 0
    fi

    echo "Stopping container $CONTAINER_NAME..."
    docker stop $CONTAINER_NAME
    echo "Container stopped successfully."
}

# Restart the container
function restart_container {
    stop_container
    start_container
}

# Show container status
function show_status {
    echo "Ergo MCP Container Status:"
    echo "----------------------------------------"
    
    # Check if container exists
    if docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo "Container: $CONTAINER_NAME"
        
        # Get container status
        STATUS=$(docker inspect --format='{{.State.Status}}' $CONTAINER_NAME)
        echo "Status: $STATUS"
        
        if [ "$STATUS" == "running" ]; then
            # Get port mappings
            PORTS=$(docker port $CONTAINER_NAME)
            echo "Port mappings: $PORTS"
            
            # Get container IP
            IP=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_NAME)
            echo "Container IP: $IP"
            
            # Get uptime
            STARTED=$(docker inspect --format='{{.State.StartedAt}}' $CONTAINER_NAME)
            echo "Started at: $STARTED"
            
            # Get image
            IMAGE=$(docker inspect --format='{{.Config.Image}}' $CONTAINER_NAME)
            echo "Image: $IMAGE"
        fi
    else
        echo "Container $CONTAINER_NAME does not exist."
    fi
    
    echo "----------------------------------------"
}

# Show container logs
function show_logs {
    if ! docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo "Container $CONTAINER_NAME does not exist."
        return 1
    fi

    echo "Showing logs for container $CONTAINER_NAME..."
    docker logs $CONTAINER_NAME
}

# Rebuild the image and restart the container
function reload_container {
    echo "Rebuilding image $IMAGE_NAME..."
    docker build -t $IMAGE_NAME .
    
    # Stop and remove the existing container if it exists
    if docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo "Removing existing container $CONTAINER_NAME..."
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
    fi
    
    # Start a new container
    start_container
}

# Run with interactive shell for debugging
function debug_container {
    echo "Starting $IMAGE_NAME in debug mode..."
    
    # Set default values for environment variables if not provided
    ERGO_NODE_API=${ERGO_NODE_API:-http://host.docker.internal:9053}
    ERGO_NODE_API_KEY=${ERGO_NODE_API_KEY:-hashcream}
    
    docker run -it --rm \
        --add-host=host.docker.internal:host-gateway \
        -e ERGO_NODE_API=$ERGO_NODE_API \
        -e ERGO_NODE_API_KEY=$ERGO_NODE_API_KEY \
        -e DEBUG=1 \
        $IMAGE_NAME
}

# Remove all stopped ergo containers
function clean_containers {
    echo "Cleaning up stopped ergo containers..."
    CONTAINERS=$(docker ps -a | grep -E 'ergo-explorer-mcp|mcp/ergo-explorer|ergo-mcp' | grep 'Exited' | awk '{print $1}')
    
    if [ -z "$CONTAINERS" ]; then
        echo "No stopped ergo containers found."
    else
        echo "Removing containers: $CONTAINERS"
        docker rm $CONTAINERS
        echo "Containers removed successfully."
    fi
}

# Main function to process commands
function main {
    case "$1" in
        start)
            start_container
            ;;
        stop)
            stop_container
            ;;
        restart)
            restart_container
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        reload)
            reload_container
            ;;
        debug)
            debug_container
            ;;
        clean)
            clean_containers
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "Unknown command: $1"
            echo "Run './manage_mcp.sh help' for usage information."
            exit 1
            ;;
    esac
}

# Run the main function with the provided arguments
main "$@" 