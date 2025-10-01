#!/bin/bash

# Discord Webhook Server - Local Development Runner
# This script sets up and runs the Discord webhook server locally

set -e  # Exit on any error

echo "🚀 Starting Discord Webhook Server locally..."

# Check if we're in the correct directory
if [[ ! -f "main.py" ]]; then
    echo "❌ Error: main.py not found. Please run this script from the discord-webhook-server directory"
    exit 1
fi

# Install dependencies if requirements.txt exists and is newer than last install
if [[ -f "requirements.txt" ]]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Load environment variables from .env if present (do not commit secrets)
if [[ -f ".env" ]]; then
    echo "🔐 Loading environment from .env"
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

# Ensure required variables are set without hardcoding secrets
if [[ -z "${WEBHOOK_GENERAL}" ]]; then
    echo "⚠️  WEBHOOK_GENERAL is not set. Set it via environment or .env file."
else
    echo "🔧 Environment configured:"
    echo "   WEBHOOK_GENERAL: [set]"
fi

# Start the Functions Framework
echo "🌐 Starting server on http://localhost:8080"
echo "   Press Ctrl+C to stop"
echo ""

functions-framework --target=discord_webhook --port=8080
