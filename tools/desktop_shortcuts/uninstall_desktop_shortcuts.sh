#!/usr/bin/env bash
set -euo pipefail

# When run via sudo, target the real user's home.
if [ -n "${SUDO_USER:-}" ]; then
  REAL_USER="${SUDO_USER}"
  REAL_HOME="$(getent passwd "${SUDO_USER}" | cut -d: -f6)"
else
  REAL_USER="$(whoami)"
  REAL_HOME="${HOME}"
fi

echo "Removing Limo compose-status Conky instance..."
pkill -f "conky -c ${REAL_HOME}/.config/conky/limo-compose.conkyrc" >/dev/null 2>&1 || true

echo "Removing installed scripts..."
rm -f "${REAL_HOME}/scripts/check_compose_services.sh"
rm -f "${REAL_HOME}/scripts/start_compose_conky.sh"

echo "Removing Conky config..."
rm -f "${REAL_HOME}/.config/conky/limo-compose.conkyrc"

echo "Removing autostart entry..."
rm -f "${REAL_HOME}/.config/autostart/limo-compose-conky.desktop"

echo "Removing desktop shortcuts..."
rm -f "${REAL_HOME}/Desktop/limo-research-on.desktop"
rm -f "${REAL_HOME}/Desktop/limo-research-off.desktop"
rm -f "${REAL_HOME}/Desktop/limo-research-remove.desktop"

echo "Removing app launcher entries..."
APP_DIR="${REAL_HOME}/.local/share/applications"
rm -f "${APP_DIR}/limo-research-on.desktop"
rm -f "${APP_DIR}/limo-research-off.desktop"
rm -f "${APP_DIR}/limo-research-remove.desktop"

echo "Uninstall complete."
