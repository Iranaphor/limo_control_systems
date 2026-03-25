#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# When run via sudo, install into the real user's home rather than root's.
if [ -n "${SUDO_USER:-}" ]; then
  REAL_USER="${SUDO_USER}"
  REAL_HOME="$(getent passwd "${SUDO_USER}" | cut -d: -f6)"
else
  REAL_USER="$(whoami)"
  REAL_HOME="${HOME}"
fi

TARGET_DIR="${REAL_HOME}/Desktop"
SCRIPTS_DIR="${REAL_HOME}/scripts"
CONKY_SCRIPT_SRC="${PROJECT_DIR}/tools/conky_compose_status/check_compose_services.sh"
CONKY_SCRIPT_DST="${SCRIPTS_DIR}/check_compose_services.sh"
CONKY_LAUNCHER_SRC="${PROJECT_DIR}/tools/conky_compose_status/start_compose_conky.sh"
CONKY_LAUNCHER_DST="${SCRIPTS_DIR}/start_compose_conky.sh"
CONKY_CONFIG_SRC="${PROJECT_DIR}/tools/conky_compose_status/conkyrc.compose_status"
CONKY_CONFIG_DIR="${REAL_HOME}/.config/conky"
CONKY_CONFIG_DST="${CONKY_CONFIG_DIR}/limo-compose.conkyrc"

mkdir -p "${TARGET_DIR}"

if [ ! -f "${CONKY_SCRIPT_SRC}" ]; then
  echo "Missing source script: ${CONKY_SCRIPT_SRC}"
  exit 1
fi

if [ ! -f "${CONKY_LAUNCHER_SRC}" ]; then
  echo "Missing source script: ${CONKY_LAUNCHER_SRC}"
  exit 1
fi

if [ ! -f "${CONKY_CONFIG_SRC}" ]; then
  echo "Missing Conky config template: ${CONKY_CONFIG_SRC}"
  exit 1
fi

mkdir -p "${SCRIPTS_DIR}"
cp -f "${CONKY_SCRIPT_SRC}" "${CONKY_SCRIPT_DST}"
chmod +x "${CONKY_SCRIPT_DST}"
echo "Installed ${CONKY_SCRIPT_DST}"

cp -f "${CONKY_LAUNCHER_SRC}" "${CONKY_LAUNCHER_DST}"
chmod +x "${CONKY_LAUNCHER_DST}"
echo "Installed ${CONKY_LAUNCHER_DST}"

mkdir -p "${CONKY_CONFIG_DIR}"
cp -f "${CONKY_CONFIG_SRC}" "${CONKY_CONFIG_DST}"
echo "Installed ${CONKY_CONFIG_DST}"

create_shortcut() {
  local name="$1"
  local exec_line="$2"
  local file_path="${TARGET_DIR}/${name}.desktop"

  cat > "${file_path}" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=${name}
Exec=${exec_line}
Terminal=true
Categories=Utility;
EOF

  chmod +x "${file_path}"
  echo "Created ${file_path}"
}

create_shortcut "Limo Compose Up" "bash -lc 'cd \"${PROJECT_DIR}\" && docker compose up -d'"
create_shortcut "Limo Compose Down" "bash -lc 'cd \"${PROJECT_DIR}\" && docker compose down'"
create_shortcut "Limo Compose Logs" "bash -lc 'cd \"${PROJECT_DIR}\" && docker compose logs -f --tail=200'"
create_shortcut "Limo Compose Conky Restart" "bash -lc '${CONKY_LAUNCHER_DST}'"

# Also install app launcher entries for desktop environments that ignore ~/Desktop.
APP_DIR="${REAL_HOME}/.local/share/applications"
mkdir -p "${APP_DIR}"
cp -f "${TARGET_DIR}/Limo Compose Up.desktop" "${APP_DIR}/"
cp -f "${TARGET_DIR}/Limo Compose Down.desktop" "${APP_DIR}/"
cp -f "${TARGET_DIR}/Limo Compose Logs.desktop" "${APP_DIR}/"
cp -f "${TARGET_DIR}/Limo Compose Conky Restart.desktop" "${APP_DIR}/"

# Autostart only the dedicated compose-status Conky instance.
AUTOSTART_DIR="${REAL_HOME}/.config/autostart"
mkdir -p "${AUTOSTART_DIR}"
cat > "${AUTOSTART_DIR}/limo-compose-conky.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Limo Compose Conky
Exec=${CONKY_LAUNCHER_DST}
Terminal=false
X-GNOME-Autostart-enabled=true
Categories=Utility;
EOF

# Fix ownership of all installed files back to the real user when run via sudo.
if [ -n "${SUDO_USER:-}" ]; then
  chown -R "${REAL_USER}:${REAL_USER}" \
    "${SCRIPTS_DIR}" \
    "${REAL_HOME}/.config/conky" \
    "${REAL_HOME}/.config/autostart/limo-compose-conky.desktop" \
    "${TARGET_DIR}/Limo Compose Up.desktop" \
    "${TARGET_DIR}/Limo Compose Down.desktop" \
    "${TARGET_DIR}/Limo Compose Logs.desktop" \
    "${TARGET_DIR}/Limo Compose Conky Restart.desktop" \
    "${APP_DIR}/Limo Compose Up.desktop" \
    "${APP_DIR}/Limo Compose Down.desktop" \
    "${APP_DIR}/Limo Compose Logs.desktop" \
    "${APP_DIR}/Limo Compose Conky Restart.desktop" 2>/dev/null || true
  echo "Ownership fixed to ${REAL_USER}"
fi

# Launch conky as the real user so DISPLAY resolves correctly.
if command -v conky >/dev/null 2>&1; then
  if [ -n "${SUDO_USER:-}" ]; then
    sudo -u "${REAL_USER}" "${CONKY_LAUNCHER_DST}" || true
  else
    "${CONKY_LAUNCHER_DST}" || true
  fi
fi

echo "Desktop shortcuts installed."
