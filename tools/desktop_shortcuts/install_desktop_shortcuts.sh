#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TARGET_DIR="${HOME}/Desktop"
SCRIPTS_DIR="${HOME}/scripts"
CONKY_SCRIPT_SRC="${PROJECT_DIR}/tools/conky_compose_status/check_compose_services.sh"
CONKY_SCRIPT_DST="${SCRIPTS_DIR}/check_compose_services.sh"
CONKY_LAUNCHER_SRC="${PROJECT_DIR}/tools/conky_compose_status/start_compose_conky.sh"
CONKY_LAUNCHER_DST="${SCRIPTS_DIR}/start_compose_conky.sh"
CONKY_CONFIG_SRC="${PROJECT_DIR}/tools/conky_compose_status/conkyrc.compose_status"
CONKY_CONFIG_DIR="${HOME}/.config/conky"
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
APP_DIR="${HOME}/.local/share/applications"
mkdir -p "${APP_DIR}"
cp -f "${TARGET_DIR}/Limo Compose Up.desktop" "${APP_DIR}/"
cp -f "${TARGET_DIR}/Limo Compose Down.desktop" "${APP_DIR}/"
cp -f "${TARGET_DIR}/Limo Compose Logs.desktop" "${APP_DIR}/"
cp -f "${TARGET_DIR}/Limo Compose Conky Restart.desktop" "${APP_DIR}/"

# Autostart only the dedicated compose-status Conky instance.
AUTOSTART_DIR="${HOME}/.config/autostart"
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

"${CONKY_LAUNCHER_DST}" || true

echo "Desktop shortcuts installed."
