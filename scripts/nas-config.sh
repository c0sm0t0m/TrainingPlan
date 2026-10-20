# Shared NAS defaults for deploy + db-sync (source this file; do not execute).
# Override any value via environment before calling the scripts.

NAS_IP="${NAS_IP:-192.168.178.42}"
NAS_USER="${NAS_USER:-thomas}"
NAS_PATH="${NAS_PATH:-/share/Container/kinesis-deploy}"

# QNAP Container Station is x86_64. Mac builds must target that, not ARM.
NAS_PLATFORM="${NAS_PLATFORM:-linux/amd64}"
BACKEND_IMAGE="${BACKEND_IMAGE:-kinesis-backend:nas}"
FRONTEND_IMAGE="${FRONTEND_IMAGE:-kinesis-frontend:nas}"

DB_NAME="${DB_NAME:-trainingplan}"
DB_USER="${DB_USER:-trainingplan_user}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-trainingplan_postgres}"

# Local compose project (Mac). DB password must match docker-compose / .env.
DB_PASSWORD="${DB_PASSWORD:-change_this_password}"
