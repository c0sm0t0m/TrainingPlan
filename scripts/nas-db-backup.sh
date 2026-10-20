#!/bin/bash
# Daily disaster-recovery dump of the NAS Postgres database.
# Runs on the QNAP. Dumps stay outside the deploy tree so rsync cannot delete them.
#
# Restore (replaces the public schema in the running database):
#   docker exec -i trainingplan_postgres pg_restore -U trainingplan_user -d trainingplan \
#     --no-owner --no-acl --clean --if-exists --schema=public \
#     < /share/Container/kinesis-backups/db/trainingplan-YYYYMMDD-HHMMSS.dump
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/share/Container/kinesis-backups/db}"
KEEP_DAYS="${KEEP_DAYS:-30}"
CONTAINER="${POSTGRES_CONTAINER:-trainingplan_postgres}"
DB_USER="${DB_USER:-trainingplan_user}"
DB_NAME="${DB_NAME:-trainingplan}"

find_docker() {
  local candidate cs_path
  export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/bin:/share/CACHEDEV1_DATA/.qpkg/container-station/bin:$PATH"
  if command -v getcfg >/dev/null 2>&1; then
    cs_path="$(getcfg container-station Install_Path 2>/dev/null || true)"
    if [ -n "$cs_path" ] && [ -x "$cs_path/bin/docker" ]; then
      echo "$cs_path/bin/docker"
      return 0
    fi
  fi
  for candidate in \
    /share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker \
    /share/MD0_DATA/.qpkg/container-station/bin/docker \
    /usr/local/bin/docker \
    /usr/bin/docker
  do
    if [ -x "$candidate" ]; then
      echo "$candidate"
      return 0
    fi
  done
  for candidate in /share/*/.qpkg/container-station/bin/docker; do
    if [ -x "$candidate" ]; then
      echo "$candidate"
      return 0
    fi
  done
  if command -v docker >/dev/null 2>&1; then
    command -v docker
    return 0
  fi
  return 1
}

DOCKER_BIN="$(find_docker)" || {
  echo "ERROR: docker binary not found on NAS." >&2
  exit 1
}

mkdir -p "$BACKUP_DIR"
stamp="$(date +%Y%m%d-%H%M%S)"
out="$BACKUP_DIR/trainingplan-${stamp}.dump"
partial="${out}.partial"

# public schema only. Timescale internal schemas are large and not app data.
"$DOCKER_BIN" exec "$CONTAINER" \
  pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc -n public --no-owner --no-acl \
  > "$partial"

magic="$(head -c 5 "$partial" || true)"
size="$(wc -c < "$partial" | tr -d ' ')"
if [ "$magic" != "PGDMP" ] || [ "$size" -lt 100000 ]; then
  echo "ERROR: dump looks invalid (magic=${magic} bytes=${size}). Left at ${partial}" >&2
  exit 1
fi
mv "$partial" "$out"

find "$BACKUP_DIR" -name 'trainingplan-*.dump' -type f -mtime +"$KEEP_DAYS" -exec rm -f {} \;

echo "$(date '+%Y-%m-%dT%H:%M:%S') ok ${out} ${size} bytes"
