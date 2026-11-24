#!/usr/bin/env bash
# Start the GATE 2024 clone (no dependencies beyond Node.js). Usage: ./run.sh [port]
cd "$(dirname "$0")" && exec node server.js "${1:-8080}"
