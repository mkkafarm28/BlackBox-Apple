#!/bin/sh
set -e

echo "=========================================="
echo "🚀 Apple Music Bot - Docker Entrypoint"
echo "=========================================="

# Get current mode
MODE="${RUN_MODE:-bot}"
echo "📌 Mode: $MODE"
echo ""

# Ensure config exists
if [ ! -f "/app/config.toml" ]; then
    echo "❌ Error: config.toml not found!"
    echo "   Please mount config.toml: -v \$(pwd)/config.toml:/app/config.toml"
    exit 1
fi
echo "✅ config.toml found"

# Ensure directories exist
mkdir -p /app/downloads
mkdir -p /app/logs
echo "✅ directories created"
echo ""

# Start service based on mode
if [ "$MODE" = "bot" ]; then
    echo "🤖 Starting Telegram Bot Mode..."
    echo "=========================================="
    echo ""
    cd /app
    export PATH="/root/.local/bin:$PATH"
    exec poetry run python telegram_main.py
    
elif [ "$MODE" = "cli" ]; then
    echo "💻 Starting CLI Mode..."
    echo "=========================================="
    echo ""
    cd /app
    export PATH="/root/.local/bin:$PATH"
    exec poetry run python main.py
    
else
    echo "⚠️  Unknown RUN_MODE: $MODE"
    echo "   Supported modes: bot, cli"
    exit 1
fi
