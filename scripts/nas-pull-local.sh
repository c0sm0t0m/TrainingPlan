#!/usr/bin/env bash
# One-way refresh: NAS Postgres -> local Postgres.
# Read-only on the NAS. Replaces the local public schema with the NAS dump.
# Skips quietly when the NAS is unreachable. Skips the restore when
# PAUSE_NAS_PULL exists in the backup directory (an open local outage must not be wiped).
# Dumps and the last-success stamp live in ~/Library/Application Support/kinesis/db-backups/.
#
# Usage:
#   ./scripts/nas-pull-local.sh
#
# LaunchAgent: ./scripts/install-nas-pull-agent.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Repo checkout when this file lives in scripts/. The LaunchAgent copy lives
# outside Documents and takes PROJECT_DIR from nas-pull.env instead.
if [[ -f "${SCRIPT_DIR}/nas-config.sh" ]]; then
  # shellcheck source=nas-config.sh
  source "${SCRIPT_DIR}/nas-config.sh"
  PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

ENV_FILE="${NAS_PULL_ENV:-}"
if [[ -z "$ENV_FILE" && -f "${SCRIPT_DIR}/nas-pull.env" ]]; then
  ENV_FILE="${SCRIPT_DIR}/nas-pull.env"
elif [[ -z "$ENV_FILE" && -f "${HOME}/Library/Application Support/kinesis/nas-pull.env" ]]; then
  ENV_FILE="${HOME}/Library/Application Support/kinesis/nas-pull.env"
fi
if [[ -n "$ENV_FILE" && -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

PROJECT_DIR="${PROJECT_DIR:-}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-${HOME}/Library/Application Support/kinesis/db-backups}"
KEEP_DUMPS="${KEEP_DUMPS:-8}"
MIN_INTERVAL_SECONDS="${MIN_INTERVAL_SECONDS:-3600}"
PROBE_TIMEOUT_SECONDS="${PROBE_TIMEOUT_SECONDS:-5}"
STAMP_FILE="${BACKUP_DIR}/last_nas_pull"
PAUSE_FILE="${BACKUP_DIR}/PAUSE_NAS_PULL"
LOCK_DIR="${BACKUP_DIR}/.pull.lock"

log() {
  echo "$(date '+%Y-%m-%dT%H:%M:%S%z') $*"
}

load_db_password() {
  local env_file="${PROJECT_DIR}/.env"
  local line
  if [[ -n "$PROJECT_DIR" && -r "$env_file" ]]; then
    line="$(grep -E '^DB_PASSWORD=' "$env_file" 2>/dev/null | tail -1 || true)"
    if [[ -n "$line" ]]; then
      DB_PASSWORD="${line#DB_PASSWORD=}"
      DB_PASSWORD="${DB_PASSWORD%\"}"
      DB_PASSWORD="${DB_PASSWORD#\"}"
      DB_PASSWORD="${DB_PASSWORD%\'}"
      DB_PASSWORD="${DB_PASSWORD#\'}"
    fi
  fi
  if [[ -z "${DB_PASSWORD:-}" || "${DB_PASSWORD}" == "change_this_password" ]]; then
    log "ERROR: DB_PASSWORD is missing. Re-run scripts/install-nas-pull-agent.sh."
    exit 1
  fi
}

nas_reachable() {
  nc -z -G "$PROBE_TIMEOUT_SECONDS" "$NAS_IP" "$DB_PORT" >/dev/null 2>&1
}

recent_enough() {
  [[ -f "$STAMP_FILE" ]] || return 1
  local pulled_at now last
  pulled_at="$(grep -E '^pulled_at=' "$STAMP_FILE" | tail -1 | cut -d= -f2- || true)"
  [[ -n "$pulled_at" ]] || return 1
  now="$(date +%s)"
  last="$(date -j -f '%Y-%m-%dT%H:%M:%S%z' "$pulled_at" +%s 2>/dev/null || true)"
  [[ -n "$last" ]] || return 1
  if (( now - last < MIN_INTERVAL_SECONDS )); then
    return 0
  fi
  return 1
}

acquire_lock() {
  if [[ -d "$LOCK_DIR" ]]; then
    local now mtime
    now="$(date +%s)"
    mtime="$(stat -f %m "$LOCK_DIR" 2>/dev/null || echo 0)"
    if (( now - mtime > 7200 )); then
      log "removing stale lock"
      rmdir "$LOCK_DIR" 2>/dev/null || true
    fi
  fi
  if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    log "skip: another pull is running"
    exit 0
  fi
  trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT
}

find_pg_dump() {
  local candidate
  if command -v pg_dump >/dev/null 2>&1; then
    command -v pg_dump
    return 0
  fi
  for candidate in \
    /opt/homebrew/opt/libpq/bin/pg_dump \
    /usr/local/opt/libpq/bin/pg_dump
  do
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

start_docker() {
  if docker info >/dev/null 2>&1; then
    return 0
  fi
  if [[ ! -d /Applications/Docker.app ]]; then
    return 1
  fi
  log "starting Docker"
  open -a Docker
  local i
  for i in $(seq 1 90); do
    if docker info >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  return 1
}

dump_via_docker() {
  local out="$1"
  local image="postgres:15"
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    log "pulling ${image}"
    docker pull "$image"
  fi
  docker run --rm \
    -e PGPASSWORD="$DB_PASSWORD" \
    -v "${BACKUP_DIR}:/backup" \
    "$image" \
    pg_dump -h "$NAS_IP" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
      -Fc -n public --no-owner --no-acl \
      -f "/backup/$(basename "$out")"
}

dump_nas() {
  local out="$1"
  local pg_dump_bin
  if pg_dump_bin="$(find_pg_dump)"; then
    if PGPASSWORD="$DB_PASSWORD" "$pg_dump_bin" \
      -h "$NAS_IP" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
      -Fc -n public --no-owner --no-acl \
      -f "$out"; then
      return 0
    fi
    log "host pg_dump could not reach the NAS; dumping through Docker"
    rm -f "$out"
  fi
  if ! start_docker; then
    log "ERROR: Docker is not running, so the NAS dump could not be taken."
    exit 1
  fi
  dump_via_docker "$out"
}

validate_dump() {
  local file="$1"
  local magic size
  [[ -s "$file" ]] || return 1
  magic="$(head -c 5 "$file" || true)"
  size="$(wc -c < "$file" | tr -d ' ')"
  [[ "$magic" == "PGDMP" && "$size" -gt 500 ]]
}

ensure_local_postgres() {
  if ! start_docker; then
    log "Docker is not running. Dump kept. Local Postgres was not updated."
    return 1
  fi
  if ! docker inspect -f '{{.State.Running}}' "$POSTGRES_CONTAINER" 2>/dev/null | grep -qx true; then
    if docker inspect "$POSTGRES_CONTAINER" >/dev/null 2>&1; then
      log "starting local Postgres"
      docker start "$POSTGRES_CONTAINER" >/dev/null
    elif [[ -n "$PROJECT_DIR" && -r "${PROJECT_DIR}/docker-compose.yml" ]]; then
      log "creating local Postgres"
      docker compose -f "${PROJECT_DIR}/docker-compose.yml" up -d postgres
    else
      log "Local Postgres is not running. Dump kept. Start it with: docker compose up -d postgres"
      return 1
    fi
  fi
  local i
  for i in $(seq 1 30); do
    if docker exec "$POSTGRES_CONTAINER" pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  log "ERROR: local Postgres did not become ready."
  return 1
}

restore_local() {
  local dump="$1"
  local pg_restore_bin err rc
  if ! pg_restore_bin="$(find_pg_dump)"; then
    log "ERROR: pg_restore is not installed. Install it with: brew install libpq"
    return 1
  fi
  pg_restore_bin="$(dirname "$pg_restore_bin")/pg_restore"
  docker exec -i "$POSTGRES_CONTAINER" \
    psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 \
    -c "DROP SCHEMA IF EXISTS public CASCADE;"
  err="$(mktemp)"
  set +e
  PGPASSWORD="$DB_PASSWORD" "$pg_restore_bin" \
    -h 127.0.0.1 -p 5432 -U "$DB_USER" -d "$DB_NAME" \
    --no-owner --no-acl "$dump" >"$err" 2>&1
  rc=$?
  set -e
  # pg_dump 18 writes transaction_timeout, which Postgres 15 reports and then ignores.
  if grep 'pg_restore: error:' "$err" | grep -v 'transaction_timeout' | grep -q .; then
    cat "$err" >&2
    rm -f "$err"
    log "pg_restore failed with exit code ${rc}"
    return 1
  fi
  rm -f "$err"
  docker exec "$POSTGRES_CONTAINER" \
    psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 \
    -c "CREATE EXTENSION IF NOT EXISTS timescaledb; CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"; SELECT COUNT(*) FROM users;" >/dev/null
}

write_stamp() {
  local dump="$1"
  local size
  size="$(wc -c < "$dump" | tr -d ' ')"
  cat > "$STAMP_FILE" <<EOF
pulled_at=$(date '+%Y-%m-%dT%H:%M:%S%z')
nas=${NAS_IP}:${DB_PORT}
dump=$(basename "$dump")
bytes=${size}
EOF
}

prune_dumps() {
  local extra
  extra="$(ls -1t "${BACKUP_DIR}"/trainingplan-*.dump 2>/dev/null | tail -n +"$((KEEP_DUMPS + 1))" || true)"
  if [[ -n "$extra" ]]; then
    # shellcheck disable=SC2086
    rm -f $extra
  fi
}

mkdir -p "$BACKUP_DIR"
load_db_password

if ! nas_reachable; then
  log "skip: NAS ${NAS_IP}:${DB_PORT} unreachable"
  exit 0
fi

if recent_enough; then
  log "skip: last pull is newer than ${MIN_INTERVAL_SECONDS}s"
  exit 0
fi

acquire_lock

stamp="$(date +%Y%m%d-%H%M%S)"
final="${BACKUP_DIR}/trainingplan-${stamp}.dump"
partial="${final}.partial"
rm -f "$partial"

log "dumping NAS ${NAS_IP}:${DB_PORT}/${DB_NAME}"
dump_nas "$partial"
if ! validate_dump "$partial"; then
  log "ERROR: NAS dump is invalid. Left at ${partial}"
  exit 1
fi
mv "$partial" "$final"
log "dump ok $(basename "$final")"

if [[ -f "$PAUSE_FILE" ]]; then
  log "PAUSE_NAS_PULL is set. Dump kept. Local Postgres was not replaced."
  exit 0
fi

previous="$(grep -E '^dump=' "$STAMP_FILE" 2>/dev/null | tail -1 | cut -d= -f2- || true)"

if ! ensure_local_postgres; then
  exit 0
fi

log "restoring into local ${POSTGRES_CONTAINER}/${DB_NAME}"
if ! restore_local "$final"; then
  if [[ -n "$previous" && -f "${BACKUP_DIR}/${previous}" ]]; then
    log "putting the previous local copy back (${previous})"
    restore_local "${BACKUP_DIR}/${previous}" || log "ERROR: could not restore the previous local copy"
  fi
  exit 1
fi

write_stamp "$final"
prune_dumps
log "local Postgres updated from NAS"
