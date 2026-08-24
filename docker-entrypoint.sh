#!/bin/bash
# docker-entrypoint.sh

set -e

echo "🚀 Starting Smart Spreadsheet Automation Agent"
echo "==============================================="

# Create workspace directory if it doesn't exist
mkdir -p /app/workspace

# Check if GROQ_API_KEY is set
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  Warning: GROQ_API_KEY not set in environment variables."
    echo "   Set it in .env file or pass it as an environment variable."
else
    echo "✅ GROQ_API_KEY found"
fi

# Check if static directory exists
if [ ! -d "/app/static" ]; then
    echo "📁 Creating static directory..."
    mkdir -p /app/static
fi

echo "✅ Starting server on http://0.0.0.0:8000"
echo "==============================================="

# Execute the command passed to the container
exec "$@"