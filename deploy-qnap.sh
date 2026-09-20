#!/usr/bin/env bash
set -euo pipefail

# Kinesis -> QNAP deploy script
# - Syncs latest local changes to NAS via rsync
# - Rebuilds/restarts containers using QNAP compose override
# - Runs backend migrations
#
# Interactive password entry is used by default (no sshpass, no stored secrets).
#
# Usage examples:
#   ./deploy-qnap.sh
#   ./deploy-qnap.sh --path /share/Container/kinesis-deploy
#   ./deploy-qnap.sh --skip-migrations
#   ./deploy-qnap.sh --dry-run
#   ./deploy-qnap.sh --debug

NAS_IP="192.168.178.42"
NAS_USER="thomas"
NAS_PATH="/share/Container/kinesis-deploy"
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
      sed -n '1,40p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Use --help for usage."
      exit 1
      ;;
  esac
done

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SSH_TARGET="${NAS_USER}@${NAS_IP}"
CONTROL_SOCKET="/tmp/kinesis-qnap-${NAS_USER}@${NAS_IP//./_}.sock"
SSH_BASE_OPTS=(
  -o ControlMaster=auto
  -o ControlPersist=10m
  -o ControlPath="$CONTROL_SOCKET"
)

echo "🚀 Kinesis QNAP Deploy"
echo "Project: ${PROJECT_DIR}"
echo "NAS:     ${SSH_TARGET}"
echo "Path:    ${NAS_PATH}"
echo "Debug:   ${DEBUG}"
echo

for cmd in rsync ssh; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "❌ Required command not found: $cmd"
    exit 1
  fi
done

if [[ "$DRY_RUN" == "true" ]]; then
  echo "🧪 Dry-run mode enabled (no remote changes will be applied)"
fi

if [[ "$DEBUG" == "true" ]]; then
  echo "🐞 Debug (local):"
  echo "  - rsync: $(command -v rsync)"
  echo "  - ssh:   $(command -v ssh)"
  echo "  - control socket: ${CONTROL_SOCKET}"
  echo
fi

# Open one SSH master connection (prompts for password only once)
echo "🔐 Opening SSH session (password prompt only once)..."
rm -f "$CONTROL_SOCKET"
ssh "${SSH_BASE_OPTS[@]}" -MNf "$SSH_TARGET"
trap 'ssh "${SSH_BASE_OPTS[@]}" -O exit "$SSH_TARGET" >/dev/null 2>&1 || true' EXIT

# 1) Ensure target folder exists on NAS
echo "📁 Ensuring target directory exists on NAS..."
ssh "${SSH_BASE_OPTS[@]}" "$SSH_TARGET" "mkdir -p '$NAS_PATH'"

if [[ "$DEBUG" == "true" ]]; then
  echo "🐞 Debug (remote preflight):"
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

# 2) Sync local project to NAS (incremental)
echo "🔄 Syncing project files to NAS (rsync incremental)..."
RSYNC_FLAGS=(
  -avz
  --progress
  --delete
  --exclude '.git/'
  --exclude '.DS_Store'
  --exclude '.venv/'
  --exclude 'backend/venv/'
  --exclude 'backend/venv313/'
  --exclude 'frontend/node_modules/'
  --exclude '__pycache__/'
  --exclude '*.pyc'
  --exclude '.pytest_cache/'
)

if [[ "$DRY_RUN" == "true" ]]; then
  RSYNC_FLAGS+=(--dry-run)
fi

rsync -e "ssh -o ControlMaster=auto -o ControlPersist=10m -o ControlPath=$CONTROL_SOCKET" \
  "${RSYNC_FLAGS[@]}" "$PROJECT_DIR/" "${SSH_TARGET}:${NAS_PATH}/"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "✅ Dry-run complete. No changes deployed."
  exit 0
fi

# 3) Rebuild/restart on NAS with QNAP override
#    (fallback: docker-compose if docker compose plugin is unavailable)
echo "🐳 Rebuilding and starting containers on NAS..."
ssh "${SSH_BASE_OPTS[@]}" "$SSH_TARGET" "
  set -e
  export PATH=\"/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/bin:/share/CACHEDEV1_DATA/.qpkg/container-station/bin:\$PATH\"
  [ -f /etc/profile ] && . /etc/profile >/dev/null 2>&1 || true

  # QNAP workaround: force compose/docker config into writable project-local dirs
  export HOME='$NAS_PATH/.qnap-home'
  export XDG_CONFIG_HOME='${NAS_PATH}/.qnap-home/.config'
  export DOCKER_CONFIG='${NAS_PATH}/.qnap-home/.docker'
  mkdir -p "\$HOME" "\$XDG_CONFIG_HOME" "\$DOCKER_CONFIG"

  cd '$NAS_PATH'

  # Resolve compose command with QNAP fallbacks
  if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD='docker compose'
  elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD='docker-compose'
  elif [[ -x /usr/local/bin/docker-compose ]]; then
    COMPOSE_CMD='/usr/local/bin/docker-compose'
  elif [[ -x /share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker-compose ]]; then
    COMPOSE_CMD='/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker-compose'
  elif [[ -x /usr/local/bin/docker ]] && /usr/local/bin/docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD='/usr/local/bin/docker compose'
  elif [[ -x /share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker ]] && /share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD='/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker compose'
  else
    echo '❌ Neither docker compose nor docker-compose is available on NAS.'
    echo '   Tried: docker compose, docker-compose, /usr/local/bin/docker-compose,'
    echo '          /share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker-compose,'
    echo '          /usr/local/bin/docker compose, /share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker compose'
    echo '   Troubleshooting:'
    echo '     1) Enable/install Container Station'
    echo '     2) SSH and run: export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/bin:/share/CACHEDEV1_DATA/.qpkg/container-station/bin:$PATH'
    echo '     3) Verify: docker version && docker compose version || docker-compose version'
    exit 1
  fi

  if [[ '$DEBUG' == 'true' ]]; then
    echo '🐞 Debug (remote compose resolution):'
    echo "  - COMPOSE_CMD=\$COMPOSE_CMD"
  fi

  echo '🧹 Stopping previous stack (if running) and removing stale containers...'
  \$COMPOSE_CMD -f docker-compose.yml -f docker-compose.qnap.yml down --remove-orphans || true

  if command -v docker >/dev/null 2>&1; then
    for c in trainingplan_backend trainingplan_frontend trainingplan_postgres trainingplan_redis trainingplan_celery_worker trainingplan_celery_beat trainingplan_traefik; do
      if docker ps -a --format '{{.Names}}' | grep -qx "\$c"; then
        echo "  - removing stale container: \$c"
        docker rm -f "\$c" >/dev/null 2>&1 || true
      fi
    done

    if [[ '$DEBUG' == 'true' ]]; then
      echo '🐞 Debug (remote port usage before start):'
      docker ps --format '  - {{.Names}} => {{.Ports}}' | grep -E '(:3000->|:8000->|:5432->|:6379->)' || echo '  - no matching published ports'
    fi
  fi

  \$COMPOSE_CMD -f docker-compose.yml -f docker-compose.qnap.yml up -d --build
  \$COMPOSE_CMD -f docker-compose.yml -f docker-compose.qnap.yml ps
"

# 4) Run migrations (optional)
if [[ "$SKIP_MIGRATIONS" != "true" ]]; then
  echo "🗄️ Running database migrations on NAS..."
  ssh "${SSH_BASE_OPTS[@]}" "$SSH_TARGET" "
    set -e
    export PATH=\"/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/bin:/share/CACHEDEV1_DATA/.qpkg/container-station/bin:\$PATH\"
    [ -f /etc/profile ] && . /etc/profile >/dev/null 2>&1 || true

    # Keep same writable runtime dirs for compose exec
    export HOME='$NAS_PATH/.qnap-home'
    export XDG_CONFIG_HOME='${NAS_PATH}/.qnap-home/.config'
    export DOCKER_CONFIG='${NAS_PATH}/.qnap-home/.docker'
    mkdir -p "\$HOME" "\$XDG_CONFIG_HOME" "\$DOCKER_CONFIG"

    cd '$NAS_PATH'

    if docker compose version >/dev/null 2>&1; then
      COMPOSE_CMD='docker compose'
    elif command -v docker-compose >/dev/null 2>&1; then
      COMPOSE_CMD='docker-compose'
    elif [[ -x /usr/local/bin/docker-compose ]]; then
      COMPOSE_CMD='/usr/local/bin/docker-compose'
    elif [[ -x /share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker-compose ]]; then
      COMPOSE_CMD='/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker-compose'
    elif [[ -x /usr/local/bin/docker ]] && /usr/local/bin/docker compose version >/dev/null 2>&1; then
      COMPOSE_CMD='/usr/local/bin/docker compose'
    elif [[ -x /share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker ]] && /share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker compose version >/dev/null 2>&1; then
      COMPOSE_CMD='/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker compose'
    else
      COMPOSE_CMD=''
    fi

    if [[ -n \"\$COMPOSE_CMD\" ]]; then
      \$COMPOSE_CMD -f docker-compose.yml -f docker-compose.qnap.yml exec -T backend alembic upgrade head
    else
      echo '⚠️ Compose command not available for migrations; skipping.'
    fi
  "
else
  echo "⏭️ Skipping migrations (--skip-migrations)"
fi

echo
echo "✅ Deployment complete"
echo "Frontend: http://${NAS_IP}:3000"
echo "API Docs: http://${NAS_IP}:8000/docs"
echo "Health:   http://${NAS_IP}:8000/health"
