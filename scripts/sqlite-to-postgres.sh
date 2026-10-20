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

# Prefer project .env over nas-config defaults (compose does the same).
env_get() {
  local key="$1" default="$2" line val
  if [[ -f .env ]]; then
    line="$(grep -E "^${key}=" .env | tail -n 1 || true)"
    if [[ -n "$line" ]]; then
      val="${line#*=}"
      val="${val%\"}"
      val="${val#\"}"
      val="${val%\'}"
      val="${val#\'}"
      echo "$val"
      return 0
    fi
  fi
  echo "$default"
}

DB_USER="$(env_get DB_USER "$DB_USER")"
DB_NAME="$(env_get DB_NAME "$DB_NAME")"
DB_PASSWORD="$(env_get DB_PASSWORD "$DB_PASSWORD")"
DB_PASS_SQL="${DB_PASSWORD//\'/\'\'}"
DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}"

echo "Using DB user=${DB_USER} db=${DB_NAME} (password from .env or defaults)"

echo "Starting local Postgres (and Redis) if not already up..."
docker compose up -d postgres redis

echo "Waiting for Postgres to be healthy..."
for i in $(seq 1 60); do
  if docker exec "$POSTGRES_CONTAINER" pg_isready -U "$DB_USER" >/dev/null 2>&1; then
    echo "  - postgres ready after ${i}s"
    break
  fi
  sleep 1
  if [[ "$i" -eq 60 ]]; then
    echo "Postgres did not become ready in time."
    exit 1
  fi
done

# Volume may have been created with a different POSTGRES_PASSWORD than current .env.
echo "Aligning Postgres role password with .env..."
if ! docker exec -i "$POSTGRES_CONTAINER" \
  psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 \
  -c "ALTER USER \"${DB_USER}\" WITH PASSWORD '${DB_PASS_SQL}';"; then
  echo "ALTER as app role failed; trying postgres superuser..."
  docker exec -i "$POSTGRES_CONTAINER" \
    psql -U postgres -d "$DB_NAME" -v ON_ERROR_STOP=1 \
    -c "ALTER USER \"${DB_USER}\" WITH PASSWORD '${DB_PASS_SQL}';" \
    || echo "WARNING: could not align password — alembic may still fail."
fi

echo "Bootstrapping / migrating schema..."
has_workouts="$(docker exec -i "$POSTGRES_CONTAINER" \
  psql -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT to_regclass('public.workouts');" | tr -d '[:space:]' || true)"

if [[ -z "$has_workouts" ]]; then
  echo "Empty local Postgres: create_all + alembic stamp head"
  docker compose run --rm --no-deps \
    -e "PYTHONPATH=/app" \
    -e "DATABASE_URL=${DATABASE_URL}" \
    -w /app \
    backend python init_db.py
  docker compose run --rm --no-deps \
    -e "PYTHONPATH=/app" \
    -e "DATABASE_URL=${DATABASE_URL}" \
    -w /app \
    backend alembic stamp head
else
  # Tables already match current models (create_all). Never re-run ALTER migrations —
  # a failed prior import can wipe alembic_version and cause DuplicateColumn errors.
  echo "Core tables present: alembic stamp head (skip upgrade)"
  docker compose run --rm --no-deps \
    -e "PYTHONPATH=/app" \
    -e "DATABASE_URL=${DATABASE_URL}" \
    -w /app \
    backend alembic stamp head
fi

echo "Importing SQLite -> Postgres..."
python3 "${SCRIPT_DIR}/sqlite_to_postgres.py" \
  --sqlite "$SQLITE_PATH" \
  --container "$POSTGRES_CONTAINER" \
  --db "$DB_NAME" \
  --user "$DB_USER" \
  $YES_FLAG

echo
echo "Import done. Local Postgres now has your SQLite data."
echo
echo "Next — push Mac → NAS (includes user account with --full):"
echo "  ./scripts/db-sync.sh push --full"
echo
echo "Optional: point Mac API at Postgres (or keep SQLite for daily work):"
echo "  DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}"
