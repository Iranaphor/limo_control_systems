#!/usr/bin/env bash
set -euo pipefail

CONKY_CONFIG="${HOME}/.config/conky/limo-compose.conkyrc"

if ! command -v conky >/dev/null 2>&1; then
  echo "conky not found. Install with: sudo apt install conky-all"
  exit 1
fi

if [ ! -f "${CONKY_CONFIG}" ]; then
  echo "Conky config not found: ${CONKY_CONFIG}"
  exit 1
fi

# Resolve DISPLAY: use current env var, or default to :0.
if [ -z "${DISPLAY:-}" ]; then
  DISPLAY=:0
fi
export DISPLAY

# Restart only the dedicated compose-status Conky instance, not the user's existing one.
pkill -f "conky -c ${CONKY_CONFIG}" >/dev/null 2>&1 || true
conky -c "${CONKY_CONFIG}" -d
