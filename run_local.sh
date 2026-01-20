#!/bin/bash
# Script to run the glossary export action locally
# 
# Usage:
#   1. Copy .env.example to .env and fill in your credentials
#   2. Run: ./run_local.sh

set -e

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Error: .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

# Run the action
echo "Starting glossary export..."
datahub actions -c examples/local_config.yaml

echo "✅ Glossary export completed!"
