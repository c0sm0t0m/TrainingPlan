#!/usr/bin/env bash
set -euo pipefail

# Kinesis -> QNAP deploy script (release on Mac, rebuild on NAS)
# - Writes VERSION, syncs code via rsync (never overwrites NAS .env)
# - Rebuilds/restarts containers using QNAP compose override
# - Runs backend migrations
#
# Interactive password entry is used by default (no sshpass, no stored secrets).
#
# Usage:
#   ./deploy-qnap.sh
#   ./deploy-qnap.sh --path /share/Container/kinesis-deploy
#   ./deploy-qnap.sh --skip-migrations
#   ./deploy-qnap.sh --dry-run
#   ./deploy-qnap.sh --debug

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=scripts/nas-config.sh
source "${SCRIPT_DIR}/scripts/nas-config.sh"

SKIP_MIGRATIONS="false"
DRY_RUN="false"
DEBUG="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)
      NAS_PATH="$2"
      shift 2
      ;;
    --skip-migrations)
      SKIP_MIGRATIONS="true"
      shift
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    --debug)
      DEBUG="true"
      shift
      ;;
    -h|--help)
      sed -n '1,25p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Use --help for usage."
      exit 1
      ;;
  esac
done

PROJECT_DIR="$SCRIPT_DIR"
SSH_TARGET="${NAS_USER}@${NAS_IP}"
CONTROL_SOCKET="/tmp/kinesis-qnap-${NAS_USER}@${NAS_IP//./_}.sock"
SSH_BASE_OPTS=(
  -o ControlMaster=auto
  -o ControlPersist=10m
  -o ControlPath="$CONTROL_SOCKET"
  -o ServerAliveInterval=30
  -o ServerAliveCountMax=120
)

# Remote prelude: resolve absolute docker/compose on QNAP (PATH is unreliable over SSH).
# Expanded inside remote ssh scripts — escape carefully.
REMOTE_DOCKER_SETUP=$(cat <<'EOS'
set -e
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/bin:/share/CACHEDEV1_DATA/.qpkg/container-station/bin:$PATH"
[ -f /etc/profile ] && . /etc/profile >/dev/null 2>&1 || true

DOCKER_BIN=""
for candidate in \
  /share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker \
  /usr/local/bin/docker \
  "$(command -v docker 2>/dev/null || true)"; do
  if [ -n "$candidate" ] && [ -x "$candidate" ]; then
    DOCKER_BIN="$candidate"
    break
  fi
done
if [ -z "$DOCKER_BIN" ]; then
  echo "ERROR: docker binary not found on NAS."
  echo "Tried: Container Station bin, /usr/local/bin/docker, PATH"
  exit 1
fi
# Ensure wrappers that call bare 'docker' still work
export PATH="$(dirname "$DOCKER_BIN"):$PATH"

COMPOSE_CMD=""
if "$DOCKER_BIN" compose version >/dev/null 2>&1; then
  COMPOSE_CMD="$DOCKER_BIN compose"
elif [ -x /share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker-compose ]; then
  COMPOSE_CMD="/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker-compose"
elif [ -x /usr/local/bin/docker-compose ]; then
  COMPOSE_CMD="/usr/local/bin/docker-compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="$(command -v docker-compose)"
else
  echo "ERROR: neither '$DOCKER_BIN compose' nor docker-compose is available on NAS."
  exit 1
fi
EOS
)

# --- VERSION file (git describe when available) ---
GIT_DESC="unknown"
if command -v git >/dev/null 2>&1 && git -C "$PROJECT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  GIT_DESC="$(git -C "$PROJECT_DIR" describe --tags --always --dirty 2>/dev/null || git -C "$PROJECT_DIR" rev-parse --short HEAD)"
fi
VERSION_STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ) ${GIT_DESC}"
echo "$VERSION_STAMP" > "${PROJECT_DIR}/VERSION"

echo "Kinesis QNAP Deploy"
echo "Project: ${PROJECT_DIR}"
echo "Version: ${VERSION_STAMP}"
echo "NAS:     ${SSH_TARGET}"
echo "Path:    ${NAS_PATH}"
echo "Debug:   ${DEBUG}"
echo

for cmd in rsync ssh; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Required command not found: $cmd"
    exit 1
  fi
done

if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry-run mode enabled (no remote changes will be applied)"
fi

if [[ "$DEBUG" == "true" ]]; then
  echo "Debug (local):"
  echo "  - rsync: $(command -v rsync)"
  echo "  - ssh:   $(command -v ssh)"
  echo "  - control socket: ${CONTROL_SOCKET}"
  echo
fi

# Open one SSH master connection (prompts for password only once)
echo "Opening SSH session (password prompt only once)..."
rm -f "$CONTROL_SOCKET"
ssh "${SSH_BASE_OPTS[@]}" -MNf "$SSH_TARGET"
trap 'ssh "${SSH_BASE_OPTS[@]}" -O exit "$SSH_TARGET" >/dev/null 2>&1 || true' EXIT

# 1) Ensure target folder exists on NAS
echo "Ensuring target directory exists on NAS..."
ssh "${SSH_BASE_OPTS[@]}" "$SSH_TARGET" "mkdir -p '$NAS_PATH'"

if [[ "$DEBUG" == "true" ]]; then
  echo "Debug (remote preflight):"
  ssh "${SSH_BASE_OPTS[@]}" "$SSH_TARGET" "
    set -e
    export PATH=\"/usr/local/bin:/opt/bin:/share/CACHEDEV1_DATA/.qpkg/container-station/bin:\$PATH\"
    echo '  - PATH='\"\$PATH\"
    echo '  - docker='\"\$(command -v docker || true)\"
    echo '  - docker-compose='\"\$(command -v docker-compose || true)\"
    if docker compose version >/dev/null 2>&1; then
      echo '  - docker compose: available'
    else
      echo '  - docker compose: unavailable'
    fi
  "
  echo
fi

# 2) Sync local project to NAS (incremental) — never clobber NAS .env / local DBs
echo "Syncing project files to NAS (rsync incremental)..."
RSYNC_FLAGS=(
  -avz
  --progress
  --delete
  --exclude '.git/'
  --exclude '.DS_Store'
  --exclude '.env'
  --exclude '.env.local'
  --exclude 'backend/.env'
  --exclude 'backend/.env.local'
  --exclude 'frontend/.env'
  --exclude 'frontend/.env.local'
  --exclude 'backend/*.db'
  --exclude 'backend/*.db-*'
  --exclude 'backend/*.sqlite'
  --exclude 'backend/*.sqlite3'
  --exclude '.venv/'
  --exclude 'backend/venv/'
  --exclude 'backend/venv313/'
  --exclude 'frontend/node_modules/'
  --exclude 'frontend/dist/'
  --exclude '__pycache__/'
  --exclude '*.pyc'
  --exclude '.pytest_cache/'
  --exclude '.cursor/'
  --exclude 'Pics and movies/'
  --exclude 'exports/'
  --exclude 'generated plans/'
  --exclude 'backups/'
  --exclude 'docs/ig-outbox/'
  --exclude 'ux-research/'
  --exclude 'wiki/'
  --exclude 'test-data/'
  --exclude '.qnap-home/'
  --exclude '*.MP4'
  --exclude '*.HEIC'
  --exclude '*.mov'
  --exclude '*.MOV'
)

if [[ "$DRY_RUN" == "true" ]]; then
  RSYNC_FLAGS+=(--dry-run)
fi

rsync -e "ssh -o ControlMaster=auto -o ControlPersist=10m -o ControlPath=$CONTROL_SOCKET" \
  "${RSYNC_FLAGS[@]}" "$PROJECT_DIR/" "${SSH_TARGET}:${NAS_PATH}/"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry-run complete. No changes deployed."
  exit 0
fi

# Bootstrap NAS .env once from example if missing (never overwrite existing)
echo "Ensuring NAS .env exists (bootstrap only if missing)..."
ssh "${SSH_BASE_OPTS[@]}" "$SSH_TARGET" "
  set -e
  cd '$NAS_PATH'
  if [[ ! -f .env ]]; then
    if [[ -f .env.example ]]; then
      cp .env.example .env
      echo 'Created .env from .env.example — edit secrets on NAS before relying on production.'
    else
      echo 'WARNING: No .env and no .env.example on NAS. Compose may fail.'
    fi
  else
    echo 'NAS .env preserved (not overwritten).'
  fi
"

# 3) Rebuild/restart on NAS with QNAP override
echo "Rebuilding and starting containers on NAS..."
ssh "${SSH_BASE_OPTS[@]}" "$SSH_TARGET" "
  ${REMOTE_DOCKER_SETUP}

  # QNAP workaround: force compose/docker config into writable project-local dirs
  export HOME='$NAS_PATH/.qnap-home'
  export XDG_CONFIG_HOME='${NAS_PATH}/.qnap-home/.config'
  export DOCKER_CONFIG='${NAS_PATH}/.qnap-home/.docker'
  mkdir -p \"\$HOME\" \"\$XDG_CONFIG_HOME\" \"\$DOCKER_CONFIG\"

  cd '$NAS_PATH'

  if [[ '$DEBUG' == 'true' ]]; then
    echo 'Debug (remote compose resolution):'
    echo \"  - DOCKER_BIN=\$DOCKER_BIN\"
    echo \"  - COMPOSE_CMD=\$COMPOSE_CMD\"
  fi

  echo 'Stopping previous stack (if running) and removing stale containers...'
  \$COMPOSE_CMD -f docker-compose.yml -f docker-compose.qnap.yml down --remove-orphans || true

  for c in trainingplan_backend trainingplan_frontend trainingplan_postgres trainingplan_redis trainingplan_celery_worker trainingplan_celery_beat trainingplan_traefik; do
    if \"\$DOCKER_BIN\" ps -a --format '{{.Names}}' | grep -qx \"\$c\"; then
      echo \"  - removing stale container: \$c\"
      \"\$DOCKER_BIN\" rm -f \"\$c\" >/dev/null 2>&1 || true
    fi
  done

  # Free host ports claimed by ANY container (common after a partial/failed deploy
  # or a second compose project on QNAP Container Station).
  echo 'Freeing host ports 8000/3000/5432/6379 if still allocated...'
  for port in 8000 3000 5432 6379; do
    ids=\$(\"\$DOCKER_BIN\" ps -q --filter \"publish=\${port}\" 2>/dev/null || true)
    if [[ -n \"\$ids\" ]]; then
      echo \"  - port \${port} held by:\"
      \"\$DOCKER_BIN\" ps --filter \"publish=\${port}\" --format '    {{.Names}} ({{.ID}}) {{.Ports}}'
      echo \"\$ids\" | xargs -r \"\$DOCKER_BIN\" rm -f >/dev/null 2>&1 || \\
        echo \"\$ids\" | xargs \"\$DOCKER_BIN\" rm -f >/dev/null 2>&1 || true
    fi
  done

  # Brief pause so docker's port proxy can release bindings on QNAP
  sleep 2

  echo 'Port usage before start:'
  \"\$DOCKER_BIN\" ps --format '  - {{.Names}} => {{.Ports}}' | grep -E '(:3000->|:8000->|:5432->|:6379->)' \\
    || echo '  - no matching published ports'

  \$COMPOSE_CMD -f docker-compose.yml -f docker-compose.qnap.yml up -d --build
  \$COMPOSE_CMD -f docker-compose.yml -f docker-compose.qnap.yml ps
"

# 4) Run migrations (optional)
if [[ "$SKIP_MIGRATIONS" != "true" ]]; then
  echo "Running database migrations on NAS..."
  ssh "${SSH_BASE_OPTS[@]}" "$SSH_TARGET" "
    ${REMOTE_DOCKER_SETUP}

    export HOME='$NAS_PATH/.qnap-home'
    export XDG_CONFIG_HOME='${NAS_PATH}/.qnap-home/.config'
    export DOCKER_CONFIG='${NAS_PATH}/.qnap-home/.docker'
    mkdir -p \"\$HOME\" \"\$XDG_CONFIG_HOME\" \"\$DOCKER_CONFIG\"

    cd '$NAS_PATH'

    echo 'Waiting for Postgres to become healthy...'
    for i in \$(seq 1 60); do
      status=\$(\"\$DOCKER_BIN\" inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' trainingplan_postgres 2>/dev/null || echo missing)
      if [[ \"\$status\" == \"healthy\" ]]; then
        echo \"  - postgres healthy after \${i}s\"
        break
      fi
      if [[ \"\$i\" -eq 60 ]]; then
        echo \"Postgres not healthy after 60s (status=\$status). Aborting migrations.\"
        \"\$DOCKER_BIN\" logs --tail 40 trainingplan_postgres || true
        exit 1
      fi
      sleep 1
    done

    # One-off container: do not exec into the long-running backend (it may be
    # crash-looping / restarting, which makes 'compose exec' hang forever).
    echo 'Running alembic in a one-off backend container...'
    \$COMPOSE_CMD -f docker-compose.yml -f docker-compose.qnap.yml run --rm --no-deps \\
      -e PYTHONPATH=/app \\
      -w /app \\
      backend alembic upgrade head
    echo 'Migrations finished successfully.'

    echo 'Backend status after migrations:'
    \"\$DOCKER_BIN\" ps -a --filter name=trainingplan_backend --format '  - {{.Names}} {{.Status}}' || true
    if ! \"\$DOCKER_BIN\" inspect -f '{{.State.Running}}' trainingplan_backend 2>/dev/null | grep -q true; then
      echo 'WARNING: backend is not running. Recent logs:'
      \"\$DOCKER_BIN\" logs --tail 60 trainingplan_backend || true
    fi
  "
else
  echo "Skipping migrations (--skip-migrations)"
fi

echo
echo "Deployment complete"
echo "Version:  ${VERSION_STAMP}"
echo "Frontend: http://${NAS_IP}:3000"
echo "API Docs: http://${NAS_IP}:8000/docs"
echo "Health:   http://${NAS_IP}:8000/health"
echo
echo "DB sync is separate: ./scripts/db-sync.sh pull|push"
