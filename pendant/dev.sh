#!/bin/bash

# Stop any running containers
echo "Stopping any running containers..."
docker compose -f docker-compose.dev.yml down

# Build and start the development containers
echo "Starting development environment with hot-reload..."
docker compose -f docker-compose.dev.yml up --build

# This script will keep running until you press Ctrl+C
# When you do, it will automatically stop the containe  rs
