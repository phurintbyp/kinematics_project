@echo off
REM Windows batch script for running the development environment

echo Stopping any running containers...
docker compose -f docker-compose.dev.yml down

echo Starting development environment with hot-reload...
docker compose -f docker-compose.dev.yml up --build

REM This script will keep running until you press Ctrl+C
REM When you do, it will automatically stop the containers
