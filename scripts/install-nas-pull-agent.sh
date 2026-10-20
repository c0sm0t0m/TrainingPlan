#!/usr/bin/env bash
# Install the Mac LaunchAgent that refreshes local Postgres from the NAS
# at login and every 6 hours while the Mac is awake.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
# shellcheck source=nas-config.sh
source "${SCRIPT_DIR}/nas-config.sh"
LABEL="com.kinesis.nas-db-pull"
SUPPORT_DIR="${HOME}/Library/Application Support/kinesis"
AGENTS_DIR="${HOME}/Library/LaunchAgents"
PLIST="${AGENTS_DIR}/${LABEL}.plist"
PULL="${SUPPORT_DIR}/nas-pull-local.sh"
ENV_FILE="${SUPPORT_DIR}/nas-pull.env"
LOG_DIR="${SUPPORT_DIR}"
UID_NUM="$(id -u)"

DB_PASSWORD_VALUE=""
if [[ -r "${PROJECT_DIR}/.env" ]]; then
  DB_PASSWORD_VALUE="$(grep -E '^DB_PASSWORD=' "${PROJECT_DIR}/.env" | tail -1 | cut -d= -f2- | tr -d '"' | tr -d "'")"
fi
if [[ -z "$DB_PASSWORD_VALUE" || "$DB_PASSWORD_VALUE" == "change_this_password" ]]; then
  echo "DB_PASSWORD is missing in ${PROJECT_DIR}/.env" >&2
  exit 1
fi

mkdir -p "$AGENTS_DIR" "$SUPPORT_DIR" "${SUPPORT_DIR}/db-backups"
cp "${SCRIPT_DIR}/nas-pull-local.sh" "$PULL"
chmod +x "$PULL"
umask 077
{
  printf 'NAS_IP=%q\n' "$NAS_IP"
  printf 'DB_PORT=%q\n' "5432"
  printf 'DB_USER=%q\n' "$DB_USER"
  printf 'DB_NAME=%q\n' "$DB_NAME"
  printf 'DB_PASSWORD=%q\n' "$DB_PASSWORD_VALUE"
  printf 'POSTGRES_CONTAINER=%q\n' "$POSTGRES_CONTAINER"
  printf 'PROJECT_DIR=%q\n' "$PROJECT_DIR"
  printf 'BACKUP_DIR=%q\n' "${SUPPORT_DIR}/db-backups"
} > "$ENV_FILE"
chmod 600 "$ENV_FILE"
unset DB_PASSWORD_VALUE

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${PULL}</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${SUPPORT_DIR}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>21600</integer>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/nas-pull.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/nas-pull.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/${UID_NUM}" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/${UID_NUM}" "$PLIST"
launchctl enable "gui/${UID_NUM}/${LABEL}"
echo "Installed ${PLIST}"
echo "Runs at login and every 6 hours. Log: ${LOG_DIR}/nas-pull.log"
