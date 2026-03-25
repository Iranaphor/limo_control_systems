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
ICONS_DIR="${PROJECT_DIR}/tools/desktop_shortcuts/icons"

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
# Write a wrapper that bakes in PROJECT_DIR then calls the real source script.
cat > "${CONKY_SCRIPT_DST}" <<WRAPPER
#!/usr/bin/env bash
export PROJECT_DIR="${PROJECT_DIR}"
exec "${CONKY_SCRIPT_SRC}" "\$@"
WRAPPER
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
  local icon="$3"
  local file_name="$4"
  local file_path="${TARGET_DIR}/${file_name}"

  cat > "${file_path}" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=${name}
Exec=${exec_line}
Icon=${icon}
Terminal=false
Categories=Utility;
EOF

  chmod +x "${file_path}"
  echo "Created ${file_path}"
}

create_shortcut "Research Docker On"    "bash -lc 'zenity --question --title=\"Start Research Services\" --text=\"Start all Research Docker services?\" --ok-label=YES --cancel-label=NO --width=360 && cd \"${PROJECT_DIR}\" && docker compose up -d'"       "${ICONS_DIR}/research-on.png"     "limo-research-on.desktop"
create_shortcut "Research Docker Off"   "bash -lc 'zenity --question --title=\"Stop Research Services\" --text=\"Stop all Research Docker services?\" --ok-label=YES --cancel-label=NO --width=360 && cd \"${PROJECT_DIR}\" && docker compose down'"         "${ICONS_DIR}/research-off.png"    "limo-research-off.desktop"
create_shortcut "Remove Research Tools" "bash -lc 'zenity --question --title=\"Remove Research Tools\" --text=\"Are you sure you want to remove all installed Research tools?\n\nThis will remove the Conky widget, desktop shortcuts and helper scripts.\" --ok-label=YES --cancel-label=NO --width=420 && bash \"${PROJECT_DIR}/tools/desktop_shortcuts/uninstall_desktop_shortcuts.sh\"'" "${ICONS_DIR}/research-remove.png" "limo-research-remove.desktop"

# Also install app launcher entries for desktop environments that ignore ~/Desktop.
APP_DIR="${REAL_HOME}/.local/share/applications"
mkdir -p "${APP_DIR}"
cp -f "${TARGET_DIR}/limo-research-on.desktop" "${APP_DIR}/"
cp -f "${TARGET_DIR}/limo-research-off.desktop" "${APP_DIR}/"
cp -f "${TARGET_DIR}/limo-research-remove.desktop" "${APP_DIR}/"

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
    "${TARGET_DIR}/limo-research-on.desktop" \
    "${TARGET_DIR}/limo-research-off.desktop" \
    "${TARGET_DIR}/limo-research-remove.desktop" \
    "${APP_DIR}/limo-research-on.desktop" \
    "${APP_DIR}/limo-research-off.desktop" \
    "${APP_DIR}/limo-research-remove.desktop" 2>/dev/null || true
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
