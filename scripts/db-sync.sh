#!/usr/bin/env bash
set -euo pipefail

# Bidirectional training DB sync between Mac (local Postgres) and NAS (Postgres).
# Always backs up the target first.
#
# Default (safe): sync all tables, then restore the DESTINATION "users" table
# so passwords, Garmin/ICU tokens, and zone settings are NOT overwritten.
#
# Usage:
#   ./scripts/db-sync.sh push                      # Mac -> NAS (normal)
#   ./scripts/db-sync.sh push --with-uploads
#   ./scripts/db-sync.sh pull --allow-pull          # NAS -> Mac (blocked unless flagged)
#   ./scripts/db-sync.sh pull --allow-pull --full
#   ./scripts/db-sync.sh push --yes
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
# Default safeguard: keep destination users (pwd, garmin/icu, zones)
FULL_SYNC="false"
# Pull (NAS -> Mac) is blocked by default — Mac is currently source of truth.
ALLOW_PULL="false"

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
    --full)
      FULL_SYNC="true"
      shift
      ;;
    --preserve-users)
      # Explicit alias for default (documented)
      FULL_SYNC="false"
      shift
      ;;
    --allow-pull)
      ALLOW_PULL="true"
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
      sed -n '1,25p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$DIRECTION" ]]; then
  echo "Usage: $0 push [--preserve-users|--full] [--with-uploads] [--yes] [--dry-run]"
  echo "       $0 pull --allow-pull [...]   # NAS->Mac; requires explicit allow"
  exit 1
fi

if [[ "$DIRECTION" == "pull" && "$ALLOW_PULL" != "true" ]]; then
  echo "Refused: 'pull' (NAS → Mac) is blocked to avoid wiping a working Mac DB."
  echo "Mac is treated as source of truth until you opt in."
  echo
  echo "Use:"
  echo "  ./scripts/db-sync.sh push              # Mac → NAS (safe default path)"
  echo "  ./scripts/db-sync.sh pull --allow-pull # only when NAS should overwrite Mac"
  exit 1
fi

SSH_TARGET="${NAS_USER}@${NAS_IP}"
CONTROL_SOCKET="/tmp/kinesis-qnap-${NAS_USER}@${NAS_IP//./_}.sock"
SSH_BASE_OPTS=(
  -o ControlMaster=auto
  -o ControlPersist=10m
  -o ControlPath="$CONTROL_SOCKET"
  -o ServerAliveInterval=30
  -o ServerAliveCountMax=120
)
BACKUP_DIR="${PROJECT_DIR}/backups/db"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

remote_prefix() {
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

# Only dump app schema — Timescale internal schemas are huge and break QNAP /tmp scp.
PG_DUMP_OPTS=(-n public --no-owner --no-acl)

pg_dump_local() {
  local out="$1"
  docker exec "$POSTGRES_CONTAINER" \
    pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc "${PG_DUMP_OPTS[@]}" > "$out"
}

pg_dump_remote() {
  local out="$1"
  ssh_nas "docker exec ${POSTGRES_CONTAINER} pg_dump -U ${DB_USER} -d ${DB_NAME} -Fc -n public --no-owner --no-acl" > "$out"
}

pg_dump_users_local() {
  local out="$1"
  docker exec "$POSTGRES_CONTAINER" \
    pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc --no-owner --no-acl -t users > "$out"
}

pg_dump_users_remote() {
  local out="$1"
  ssh_nas "docker exec ${POSTGRES_CONTAINER} pg_dump -U ${DB_USER} -d ${DB_NAME} -Fc --no-owner --no-acl -t users" > "$out"
}

count_users_in_dump() {
  local dump="$1"
  [[ -s "$dump" ]] || return 1
  return 0
}

list_user_ids_local() {
  docker exec "$POSTGRES_CONTAINER" \
    psql -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COALESCE(string_agg(id::text, ',' ORDER BY id), '') FROM users;" 2>/dev/null || echo ""
}

list_user_ids_remote() {
  ssh_nas "docker exec ${POSTGRES_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME} -tAc \"SELECT COALESCE(string_agg(id::text, ',' ORDER BY id), '') FROM users;\"" 2>/dev/null || echo ""
}

pg_restore_local() {
  local dump="$1"
  reset_schema_local
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
  # Stream over SSH — do NOT scp into QNAP /tmp (small/tmpfs; large dumps get Connection closed).
  echo "Streaming restore to NAS over SSH ($(du -h "$dump" | awk '{print $1}')) — no scp..."
  reset_schema_remote
  set +e
  gzip -c "$dump" | ssh "${SSH_BASE_OPTS[@]}" "$SSH_TARGET" \
    "$(remote_prefix); gunzip | docker exec -i ${POSTGRES_CONTAINER} pg_restore -U ${DB_USER} -d ${DB_NAME} --no-owner --no-acl"
  local rc=$?
  set -e
  ssh_nas "docker exec ${POSTGRES_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME} -c 'SELECT 1;' >/dev/null"
  if [[ "$rc" -gt 1 ]]; then
    echo "Remote streamed pg_restore failed with exit code ${rc}"
    exit "$rc"
  fi
  echo "Remote restore finished (stream)."
}

# Restore users-only dump via SSH stream (avoid /tmp scp).
restore_users_remote_stream() {
  local users_dump="$1"
  echo "Restoring preserved NAS users/settings (stream)..."
  ssh_nas "docker exec -i ${POSTGRES_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME} -v ON_ERROR_STOP=1 -c \"SET session_replication_role = replica; DELETE FROM users;\""
  set +e
  gzip -c "$users_dump" | ssh "${SSH_BASE_OPTS[@]}" "$SSH_TARGET" \
    "$(remote_prefix); gunzip | docker exec -i ${POSTGRES_CONTAINER} pg_restore -U ${DB_USER} -d ${DB_NAME} --data-only --no-owner --no-acl -t users"
  local rc=$?
  set -e
  ssh_nas "docker exec -i ${POSTGRES_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME} -v ON_ERROR_STOP=1 -c \"SET session_replication_role = DEFAULT;\""
  if [[ "$rc" -gt 1 ]]; then
    echo "Failed to restore preserved NAS users (exit ${rc})."
    exit "$rc"
  fi
  echo "Destination users preserved (password, Garmin/ICU, zones)."
}

# Replace users rows with a previously dumped users-only archive (FK checks off).
restore_users_local() {
  local users_dump="$1"
  echo "Restoring preserved local users/settings..."
  docker exec -i "$POSTGRES_CONTAINER" \
    psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 <<'SQL'
SET session_replication_role = replica;
DELETE FROM users;
SQL
  set +e
  docker exec -i "$POSTGRES_CONTAINER" \
    pg_restore -U "$DB_USER" -d "$DB_NAME" --data-only --no-owner --no-acl -t users < "$users_dump"
  local rc=$?
  set -e
  docker exec -i "$POSTGRES_CONTAINER" \
    psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 \
    -c "SET session_replication_role = DEFAULT;"
  if [[ "$rc" -gt 1 ]]; then
    echo "Failed to restore preserved users (exit ${rc}). Full backup is still in backups/db/."
    exit "$rc"
  fi
  echo "Destination users preserved (password, Garmin/ICU, zones)."
}

restore_users_remote() {
  restore_users_remote_stream "$1"
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

MODE_LABEL="preserve-users (default)"
if [[ "$FULL_SYNC" == "true" ]]; then
  MODE_LABEL="FULL (includes users/settings)"
fi

echo "Kinesis DB sync (${DIRECTION})  [db-sync v3-stream — no scp for restore]"
echo "Mode:  ${MODE_LABEL}"
echo "NAS:   ${SSH_TARGET}:${NAS_PATH}"
echo "Local: ${POSTGRES_CONTAINER}/${DB_NAME}"
echo

ensure_local_postgres

if [[ "$SKIP_CONFIRM" != "true" || "$DIRECTION" == "pull" ]]; then
  # Pull always requires the long phrase (even with --yes) — Mac wipe is high risk.
  if [[ "$FULL_SYNC" == "true" ]]; then
    echo "WARNING: --full will OVERWRITE destination users (passwords, Garmin/ICU tokens, zones)."
    if [[ "$DIRECTION" == "pull" ]]; then
      echo "This will replace your LOCAL database entirely (including settings)."
      read -r -p "Type 'pull-full' to continue: " reply
      if [[ "$reply" != "pull-full" ]]; then
        echo "Aborted."
        exit 1
      fi
    elif [[ "$SKIP_CONFIRM" != "true" ]]; then
      echo "This will replace the NAS database entirely (including settings)."
      read -r -p "Type 'push-full' to continue: " reply
      if [[ "$reply" != "push-full" ]]; then
        echo "Aborted."
        exit 1
      fi
    fi
  else
    if [[ "$DIRECTION" == "pull" ]]; then
      echo "Will overwrite local training data from NAS."
      echo "Will KEEP your local users row(s): password, Garmin/ICU, zone settings."
      echo "EXTRA CONFIRM: Mac is normally source of truth."
      read -r -p "Type 'overwrite-mac-from-nas' to continue: " reply
      if [[ "$reply" != "overwrite-mac-from-nas" ]]; then
        echo "Aborted."
        exit 1
      fi
    elif [[ "$SKIP_CONFIRM" != "true" ]]; then
      echo "Will overwrite NAS training data from Mac."
      echo "Will KEEP NAS users row(s): password, Garmin/ICU, zone settings."
      read -r -p "Type '${DIRECTION}' to continue: " reply
      if [[ "$reply" != "$DIRECTION" ]]; then
        echo "Aborted."
        exit 1
      fi
    fi
  fi
fi

if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry-run: would ${DIRECTION} (mode=${MODE_LABEL}, uploads=${WITH_UPLOADS}). No changes made."
  exit 0
fi

for cmd in ssh docker gzip; do
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
  USERS_PRESERVE="${BACKUP_DIR}/local_users_preserve_${TIMESTAMP}.dump"

  DEST_IDS="$(list_user_ids_local | tr -d '[:space:]')"
  SRC_IDS="$(list_user_ids_remote | tr -d '[:space:]')"
  echo "User ids — local(dest): [${DEST_IDS:-none}]  nas(src): [${SRC_IDS:-none}]"
  if [[ "$FULL_SYNC" != "true" && -n "$DEST_IDS" && -n "$SRC_IDS" && "$DEST_IDS" != "$SRC_IDS" ]]; then
    echo "WARNING: user id sets differ. Preserving local users; training rows from NAS may reference other ids."
  fi

  echo "Backing up local DB -> ${LOCAL_BACKUP}"
  pg_dump_local "$LOCAL_BACKUP"

  if [[ "$FULL_SYNC" != "true" ]]; then
    echo "Saving local users/settings to preserve -> ${USERS_PRESERVE}"
    pg_dump_users_local "$USERS_PRESERVE"
  fi

  echo "Dumping NAS DB -> ${SOURCE_DUMP}"
  pg_dump_remote "$SOURCE_DUMP"

  echo "Restoring NAS dump into local Postgres..."
  pg_restore_local "$SOURCE_DUMP"

  if [[ "$FULL_SYNC" != "true" ]]; then
    if count_users_in_dump "$USERS_PRESERVE"; then
      restore_users_local "$USERS_PRESERVE"
    else
      echo "No local users to preserve (empty destination) — keeping users from NAS dump."
    fi
  fi

  if [[ "$WITH_UPLOADS" == "true" ]]; then
    sync_uploads_pull
  fi

  echo
  echo "Pull complete."
  if [[ "$FULL_SYNC" == "true" ]]; then
    echo "Mode: FULL — local users/settings replaced by NAS."
  else
    echo "Mode: preserve-users — local password/Garmin/ICU/zones kept."
  fi
  echo "Local backup: ${LOCAL_BACKUP}"
else
  NAS_BACKUP="${BACKUP_DIR}/nas_before_push_${TIMESTAMP}.dump"
  SOURCE_DUMP="${BACKUP_DIR}/from_local_${TIMESTAMP}.dump"
  USERS_PRESERVE="${BACKUP_DIR}/nas_users_preserve_${TIMESTAMP}.dump"

  DEST_IDS="$(list_user_ids_remote | tr -d '[:space:]')"
  SRC_IDS="$(list_user_ids_local | tr -d '[:space:]')"
  echo "User ids — nas(dest): [${DEST_IDS:-none}]  local(src): [${SRC_IDS:-none}]"
  if [[ "$FULL_SYNC" != "true" && -n "$DEST_IDS" && -n "$SRC_IDS" && "$DEST_IDS" != "$SRC_IDS" ]]; then
    echo "WARNING: user id sets differ. Preserving NAS users; training rows from Mac may reference other ids."
  fi

  echo "Backing up NAS DB -> ${NAS_BACKUP}"
  pg_dump_remote "$NAS_BACKUP"

  if [[ "$FULL_SYNC" != "true" ]]; then
    echo "Saving NAS users/settings to preserve -> ${USERS_PRESERVE}"
    pg_dump_users_remote "$USERS_PRESERVE"
  fi

  echo "Dumping local DB -> ${SOURCE_DUMP}"
  pg_dump_local "$SOURCE_DUMP"

  echo "Restoring local dump onto NAS..."
  pg_restore_remote "$SOURCE_DUMP"

  if [[ "$FULL_SYNC" != "true" ]]; then
    if count_users_in_dump "$USERS_PRESERVE"; then
      restore_users_remote "$USERS_PRESERVE"
    else
      echo "No NAS users to preserve (empty destination) — keeping users from Mac dump."
    fi
  fi

  if [[ "$WITH_UPLOADS" == "true" ]]; then
    sync_uploads_push
  fi

  echo
  echo "Push complete."
  if [[ "$FULL_SYNC" == "true" ]]; then
    echo "Mode: FULL — NAS users/settings replaced by Mac."
  else
    echo "Mode: preserve-users — NAS password/Garmin/ICU/zones kept."
  fi
  echo "NAS backup (kept locally): ${NAS_BACKUP}"
fi
