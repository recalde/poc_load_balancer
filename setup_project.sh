#!/bin/bash

# Set the base project directory name
PROJECT_NAME="load_balancer_project"

# Create the project directory
mkdir -p $PROJECT_NAME

# Change to the project directory
cd $PROJECT_NAME

# Create the 'app' directory and its sub-files
mkdir -p app

# Create empty Python files in 'app'
touch app/__init__.py
touch app/main.py
touch app/config.py
touch app/s3_helper.py
touch app/state_manager.py
touch app/health.py

# Create project-level files
touch Dockerfile
touch requirements.txt
touch .env
touch docker-compose.yml

# Add executable permissions to the script itself (if it's being run locally)
chmod +x setup_project.sh

# Provide feedback
echo "Project structure created successfully under the directory: $PROJECT_NAME"
