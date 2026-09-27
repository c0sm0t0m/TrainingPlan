#!/usr/bin/env bash
set -euo pipefail

# Bidirectional training DB sync between Mac (local Postgres) and NAS (Postgres).
# Full replace only — not a merge. Always backs up the target first.
#
# Usage:
#   ./scripts/db-sync.sh pull              # NAS -> Mac (overwrite local)
#   ./scripts/db-sync.sh push              # Mac -> NAS (overwrite NAS)
#   ./scripts/db-sync.sh pull --with-uploads
#   ./scripts/db-sync.sh push --yes        # skip confirmation (automation)
#
# Prerequisites:
#   - Local: docker compose up -d postgres  (container trainingplan_postgres)
#   - NAS: stack running with trainingplan_postgres
#   - SSH access (same as deploy-qnap.sh)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
# shellcheck source=nas-config.sh
source "${SCRIPT_DIR}/nas-config.sh"

DIRECTION=""
WITH_UPLOADS="false"
SKIP_CONFIRM="false"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    pull|push)
      DIRECTION="$1"
      shift
      ;;
    --with-uploads)
      WITH_UPLOADS="true"
      shift
      ;;
    --yes|-y)
      SKIP_CONFIRM="true"
      shift
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    --path)
      NAS_PATH="$2"
      shift 2
      ;;
    -h|--help)
      sed -n '1,20p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$DIRECTION" ]]; then
  echo "Usage: $0 pull|push [--with-uploads] [--yes] [--dry-run]"
  exit 1
fi

SSH_TARGET="${NAS_USER}@${NAS_IP}"
CONTROL_SOCKET="/tmp/kinesis-qnap-${NAS_USER}@${NAS_IP//./_}.sock"
SSH_BASE_OPTS=(
  -o ControlMaster=auto
  -o ControlPersist=10m
  -o ControlPath="$CONTROL_SOCKET"
)
BACKUP_DIR="${PROJECT_DIR}/backups/db"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

remote_prefix() {
  # Common PATH + writable docker config dirs on QNAP
  echo "export PATH=\"/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/bin:/share/CACHEDEV1_DATA/.qpkg/container-station/bin:\$PATH\"; \
[ -f /etc/profile ] && . /etc/profile >/dev/null 2>&1 || true; \
export HOME='${NAS_PATH}/.qnap-home'; \
export XDG_CONFIG_HOME='${NAS_PATH}/.qnap-home/.config'; \
export DOCKER_CONFIG='${NAS_PATH}/.qnap-home/.docker'; \
mkdir -p \"\$HOME\" \"\$XDG_CONFIG_HOME\" \"\$DOCKER_CONFIG\"; \
cd '${NAS_PATH}'"
}

ssh_nas() {
  ssh "${SSH_BASE_OPTS[@]}" "$SSH_TARGET" "$(remote_prefix); $*"
}

ensure_local_postgres() {
  if ! docker inspect -f '{{.State.Running}}' "$POSTGRES_CONTAINER" 2>/dev/null | grep -qx true; then
    echo "Local Postgres container '${POSTGRES_CONTAINER}' is not running."
    echo "Start with: cd ${PROJECT_DIR} && docker compose up -d postgres"
    exit 1
  fi
}

reset_schema_local() {
  docker exec -i "$POSTGRES_CONTAINER" \
    psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 \
    -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO public;"
}

reset_schema_remote() {
  ssh_nas "docker exec -i ${POSTGRES_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME} -v ON_ERROR_STOP=1 \
    -c \"DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO public;\""
}

pg_dump_local() {
  local out="$1"
  docker exec "$POSTGRES_CONTAINER" \
    pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc --no-owner --no-acl > "$out"
}

pg_dump_remote() {
  local out="$1"
  ssh_nas "docker exec ${POSTGRES_CONTAINER} pg_dump -U ${DB_USER} -d ${DB_NAME} -Fc --no-owner --no-acl" > "$out"
}

pg_restore_local() {
  local dump="$1"
  reset_schema_local
  # pg_restore often exits 1 on harmless warnings after a clean schema reset
  set +e
  docker exec -i "$POSTGRES_CONTAINER" \
    pg_restore -U "$DB_USER" -d "$DB_NAME" --no-owner --no-acl < "$dump"
  local rc=$?
  set -e
  docker exec "$POSTGRES_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null
  if [[ "$rc" -gt 1 ]]; then
    echo "pg_restore failed with exit code ${rc}"
    exit "$rc"
  fi
}

pg_restore_remote() {
  local dump="$1"
  local remote_dump="/tmp/kinesis-restore-${TIMESTAMP}.dump"
  scp -o ControlPath="$CONTROL_SOCKET" "$dump" "${SSH_TARGET}:${remote_dump}"
  reset_schema_remote
  set +e
  ssh_nas "docker exec -i ${POSTGRES_CONTAINER} pg_restore -U ${DB_USER} -d ${DB_NAME} --no-owner --no-acl < ${remote_dump}"
  local rc=$?
  set -e
  ssh_nas "docker exec ${POSTGRES_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME} -c 'SELECT 1;' >/dev/null; rm -f ${remote_dump}"
  if [[ "$rc" -gt 1 ]]; then
    echo "Remote pg_restore failed with exit code ${rc}"
    exit "$rc"
  fi
}

sync_uploads_pull() {
  echo "Syncing uploads: NAS -> Mac..."
  local tmp_tar="${BACKUP_DIR}/uploads_from_nas_${TIMESTAMP}.tar.gz"
  local remote_name="kinesis-uploads-${TIMESTAMP}.tar.gz"

  set +e
  ssh_nas "docker inspect trainingplan_backend >/dev/null 2>&1"
  local has_backend=$?
  set -e
  if [[ "$has_backend" -ne 0 ]]; then
    echo "trainingplan_backend not found on NAS; skipping uploads."
    return 0
  fi

  ssh_nas "docker run --rm --volumes-from trainingplan_backend -v /tmp:/out alpine \
    tar czf /out/${remote_name} -C /app uploads 2>/dev/null || tar czf /out/${remote_name} -C /app --files-from /dev/null"
  scp -o ControlPath="$CONTROL_SOCKET" "${SSH_TARGET}:/tmp/${remote_name}" "$tmp_tar"
  ssh_nas "rm -f /tmp/${remote_name}"

  if [[ ! -s "$tmp_tar" ]]; then
    echo "No uploads archive received; skipping."
    return 0
  fi

  if docker inspect trainingplan_backend >/dev/null 2>&1; then
    docker run --rm --volumes-from trainingplan_backend -v "${BACKUP_DIR}:/backup" alpine \
      sh -c "mkdir -p /app/uploads && rm -rf /app/uploads/* && tar xzf /backup/$(basename "$tmp_tar") -C /app"
    echo "Uploads restored into local trainingplan_backend volume."
  else
    mkdir -p "${PROJECT_DIR}/backend/uploads"
    tar xzf "$tmp_tar" -C "${PROJECT_DIR}/backend"
    echo "Uploads extracted to backend/uploads (backend container not running)."
  fi
}

sync_uploads_push() {
  echo "Syncing uploads: Mac -> NAS..."
  local tmp_tar="${BACKUP_DIR}/uploads_to_nas_${TIMESTAMP}.tar.gz"
  local remote_name="kinesis-uploads-${TIMESTAMP}.tar.gz"

  if docker inspect trainingplan_backend >/dev/null 2>&1 \
    && docker inspect -f '{{.State.Running}}' trainingplan_backend 2>/dev/null | grep -qx true; then
    docker run --rm --volumes-from trainingplan_backend -v "${BACKUP_DIR}:/backup" alpine \
      sh -c "tar czf /backup/$(basename "$tmp_tar") -C /app uploads 2>/dev/null || tar czf /backup/$(basename "$tmp_tar") -C /app --files-from /dev/null"
  elif [[ -d "${PROJECT_DIR}/backend/uploads" ]]; then
    tar czf "$tmp_tar" -C "${PROJECT_DIR}/backend" uploads
  else
    echo "No local uploads found; skipping."
    return 0
  fi

  if [[ ! -s "$tmp_tar" ]]; then
    echo "Empty uploads archive; skipping."
    return 0
  fi

  set +e
  ssh_nas "docker inspect trainingplan_backend >/dev/null 2>&1"
  local has_backend=$?
  set -e
  if [[ "$has_backend" -ne 0 ]]; then
    echo "trainingplan_backend not found on NAS; skipping uploads."
    return 0
  fi

  scp -o ControlPath="$CONTROL_SOCKET" "$tmp_tar" "${SSH_TARGET}:/tmp/${remote_name}"
  ssh_nas "docker run --rm --volumes-from trainingplan_backend -v /tmp:/in alpine \
    sh -c 'mkdir -p /app/uploads && rm -rf /app/uploads/* && tar xzf /in/${remote_name} -C /app'; \
    rm -f /tmp/${remote_name}"
  echo "Uploads pushed to NAS."
}

echo "Kinesis DB sync (${DIRECTION})"
echo "NAS:   ${SSH_TARGET}:${NAS_PATH}"
echo "Local: ${POSTGRES_CONTAINER}/${DB_NAME}"
echo

ensure_local_postgres

if [[ "$SKIP_CONFIRM" != "true" ]]; then
  if [[ "$DIRECTION" == "pull" ]]; then
    echo "This will OVERWRITE your local Postgres DB with the NAS copy."
  else
    echo "This will OVERWRITE the NAS Postgres DB with your local copy."
  fi
  read -r -p "Type '${DIRECTION}' to continue: " reply
  if [[ "$reply" != "$DIRECTION" ]]; then
    echo "Aborted."
    exit 1
  fi
fi

if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry-run: would ${DIRECTION} database (and uploads=${WITH_UPLOADS}). No changes made."
  exit 0
fi

for cmd in ssh scp docker; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Required command not found: $cmd"
    exit 1
  fi
done

echo "Opening SSH session..."
rm -f "$CONTROL_SOCKET"
ssh "${SSH_BASE_OPTS[@]}" -MNf "$SSH_TARGET"
trap 'ssh "${SSH_BASE_OPTS[@]}" -O exit "$SSH_TARGET" >/dev/null 2>&1 || true' EXIT

if [[ "$DIRECTION" == "pull" ]]; then
  LOCAL_BACKUP="${BACKUP_DIR}/local_before_pull_${TIMESTAMP}.dump"
  SOURCE_DUMP="${BACKUP_DIR}/from_nas_${TIMESTAMP}.dump"

  echo "Backing up local DB -> ${LOCAL_BACKUP}"
  pg_dump_local "$LOCAL_BACKUP"

  echo "Dumping NAS DB -> ${SOURCE_DUMP}"
  pg_dump_remote "$SOURCE_DUMP"

  echo "Restoring NAS dump into local Postgres..."
  pg_restore_local "$SOURCE_DUMP"

  if [[ "$WITH_UPLOADS" == "true" ]]; then
    sync_uploads_pull
  fi

  echo
  echo "Pull complete. Local DB now matches NAS."
  echo "Local backup: ${LOCAL_BACKUP}"
else
  NAS_BACKUP="${BACKUP_DIR}/nas_before_push_${TIMESTAMP}.dump"
  SOURCE_DUMP="${BACKUP_DIR}/from_local_${TIMESTAMP}.dump"

  echo "Backing up NAS DB -> ${NAS_BACKUP}"
  pg_dump_remote "$NAS_BACKUP"

  echo "Dumping local DB -> ${SOURCE_DUMP}"
  pg_dump_local "$SOURCE_DUMP"

  echo "Restoring local dump onto NAS..."
  pg_restore_remote "$SOURCE_DUMP"

  if [[ "$WITH_UPLOADS" == "true" ]]; then
    sync_uploads_push
  fi

  echo
  echo "Push complete. NAS DB now matches local."
  echo "NAS backup (kept locally): ${NAS_BACKUP}"
fi
