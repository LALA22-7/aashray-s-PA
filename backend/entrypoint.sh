#!/bin/sh
set -e

echo "================================================="
echo " 🚀 Aashray'sPA Production Entrypoint Starting..."
echo "================================================="

# Wait for database if DATABASE_URL is PostgreSQL
if echo "$DATABASE_URL" | grep -q "postgres"; then
    echo "🔍 Waiting for PostgreSQL database connection..."
    python -c "
import sys, time, os
from sqlalchemy import create_engine
url = os.getenv('DATABASE_URL')
for i in range(30):
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            print('✅ Database connection established!')
            sys.exit(0)
    except Exception as exc:
        print(f'⏳ Database not ready yet ({exc}). Retrying in 2s ({i+1}/30)...')
        time.sleep(2)
sys.exit(1)
"
fi

# Apply database migrations
echo "📦 Running database migrations with Alembic..."
alembic upgrade head

# Seed initial accounts and business knowledge if needed
echo "🌱 Ensuring default accounts and business knowledge are seeded..."
python -m scripts.seed_accounts || true

# Determine port (Render assigns $PORT dynamically)
SERVER_PORT="${PORT:-8000}"

echo "🌟 Launching Uvicorn on 0.0.0.0:${SERVER_PORT}..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$SERVER_PORT" \
    --proxy-headers \
    --forwarded-allow-ips='*'

