#!/bin/bash

# Router Service Development Setup Script

set -e

echo "🚀 Setting up Router Service development environment..."

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -e ".[dev]"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration values"
fi

# Initialize Alembic if not already done
if [ ! -f "alembic/versions" ]; then
    echo "🗄️  Initializing Alembic..."
    alembic init alembic
fi

echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database and Redis URLs"
echo "2. Run 'docker-compose up -d' to start PostgreSQL and Redis"
echo "3. Run 'alembic upgrade head' to create database tables"
echo "4. Run 'uvicorn app.main:app --reload --port 8003' to start the service"
echo ""
echo "📖 API documentation will be available at: http://localhost:8003/docs"
