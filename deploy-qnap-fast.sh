#!/usr/bin/env bash
set -euo pipefail

# Build NAS images on the Mac (linux/amd64), then sync the project and load
# the images on the QNAP. The NAS does not compile.
#
# Usage:
#   ./deploy-qnap-fast.sh
#   ./deploy-qnap-fast.sh --skip-migrations
#   ./deploy-qnap-fast.sh --dry-run
#   NAS_PLATFORM=linux/amd64 ./deploy-qnap-fast.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=scripts/nas-config.sh
source "${SCRIPT_DIR}/scripts/nas-config.sh"

DRY_RUN="false"
for arg in "$@"; do
  if [[ "$arg" == "--dry-run" ]]; then
    DRY_RUN="true"
  fi
done

if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry-run: skipping image build."
  exec "${SCRIPT_DIR}/deploy-qnap.sh" "$@"
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required."
  exit 1
fi

echo "Building ${BACKEND_IMAGE} and ${FRONTEND_IMAGE} for ${NAS_PLATFORM}"
echo "Unchanged Docker layers (npm/pip) are reused. Vite prod build forces VITE_DEV_AUTO_LOGIN=false."
echo

docker build \
  --platform "$NAS_PLATFORM" \
  -t "$BACKEND_IMAGE" \
  -f "${SCRIPT_DIR}/backend/Dockerfile" \
  "${SCRIPT_DIR}/backend"

docker build \
  --platform "$NAS_PLATFORM" \
  -t "$FRONTEND_IMAGE" \
  -f "${SCRIPT_DIR}/frontend/Dockerfile.prod" \
  "${SCRIPT_DIR}/frontend"

echo
echo "Images ready. Syncing project and loading them on the NAS..."
exec "${SCRIPT_DIR}/deploy-qnap.sh" --prebuilt "$@"
