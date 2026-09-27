#!/usr/bin/env bash
set -euo pipefail

# One-shot: start local Postgres (if needed), migrate schema, import SQLite data.
#
# Usage:
#   ./scripts/sqlite-to-postgres.sh
#   ./scripts/sqlite-to-postgres.sh --sqlite backend/trainingplan.db --yes

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
# shellcheck source=nas-config.sh
source "${SCRIPT_DIR}/nas-config.sh"

SQLITE_PATH="${PROJECT_DIR}/backend/trainingplan.db"
YES_FLAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sqlite)
      SQLITE_PATH="$2"
      shift 2
      ;;
    --yes)
      YES_FLAG="--yes"
      shift
      ;;
    -h|--help)
      sed -n '1,12p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

cd "$PROJECT_DIR"

echo "Starting local Postgres (and Redis) if not already up..."
docker compose up -d postgres redis

echo "Waiting for Postgres to be healthy..."
for i in $(seq 1 30); do
  if docker exec "$POSTGRES_CONTAINER" pg_isready -U "$DB_USER" >/dev/null 2>&1; then
    break
  fi
  sleep 1
  if [[ "$i" -eq 30 ]]; then
    echo "Postgres did not become ready in time."
    exit 1
  fi
done

echo "Applying Alembic migrations via backend image..."
# Build/run a one-off backend container against compose network if stack isn't fully up.
if docker compose ps --status running --services 2>/dev/null | grep -qx backend; then
  docker compose exec -T backend alembic upgrade head
else
  docker compose run --rm --no-deps \
    -e "DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}" \
    backend alembic upgrade head
fi

echo "Importing SQLite -> Postgres..."
python3 "${SCRIPT_DIR}/sqlite_to_postgres.py" \
  --sqlite "$SQLITE_PATH" \
  --container "$POSTGRES_CONTAINER" \
  --db "$DB_NAME" \
  --user "$DB_USER" \
  $YES_FLAG

echo
echo "Next: point your local API at Postgres, e.g. in backend/.env or project .env:"
echo "  DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}"
echo "  DB_HOST=localhost"
echo "  DB_PASSWORD=${DB_PASSWORD}"
echo
echo "Then use: ./scripts/db-sync.sh pull|push"
