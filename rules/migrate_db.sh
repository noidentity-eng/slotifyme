#!/bin/bash

set -e

echo "🗄️ Running database migrations on RDS..."

# Set environment variables for Alembic
export DATABASE_URL="postgresql+psycopg://user:pwd@db_url:5432/barbershop"

# Run Alembic migrations
echo "📋 Running Alembic migrations..."
alembic upgrade head

echo "✅ Database migrations completed successfully!"
