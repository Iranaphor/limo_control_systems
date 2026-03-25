#!/usr/bin/env bash
set -euo pipefail

# Resolve project root from this script location unless PROJECT_DIR is provided.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
COMPOSE_FILE="${COMPOSE_FILE:-${PROJECT_DIR}/docker-compose.yml}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker: not found"
  exit 0
fi

if [ ! -f "${COMPOSE_FILE}" ]; then
  echo "compose file missing"
  exit 0
fi

services="$(docker compose -f "${COMPOSE_FILE}" config --services 2>/dev/null || true)"
if [ -z "${services}" ]; then
  echo "no compose services"
  exit 0
fi

# Sort services alphabetically before processing
services="$(echo "${services}" | sort)"

# First pass: collect names and statuses
declare -a _names=()
declare -a _labels=()

while IFS= read -r svc; do
  [ -z "${svc}" ] && continue

  # Pretty-print: underscores to spaces, title case each word
  display_name="$(echo "${svc}" | tr '_' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2)); print}')"

  cid="$(docker compose -f "${COMPOSE_FILE}" ps -q "${svc}" 2>/dev/null || true)"
  if [ -z "${cid}" ]; then
    _names+=("${display_name}")
    _labels+=("DOWN")
    continue
  fi

  state="$(docker inspect -f '{{.State.Status}}' "${cid}" 2>/dev/null || echo "unknown")"

  case "${state}" in
    running)            lbl="RUNNING" ;;
    exited|dead)        lbl="ERROR" ;;
    created|restarting) lbl="STARTING" ;;
    paused)             lbl="PAUSED" ;;
    *)                  lbl="${state^^}" ;;
  esac

  _names+=("${display_name}")
  _labels+=("${lbl}")
done <<< "${services}"

# Find longest service name for consistent column alignment
max_len=0
for n in "${_names[@]}"; do
  [ ${#n} -gt ${max_len} ] && max_len=${#n}
done

# Second pass: print as aligned table with vertical pipe separator
for i in "${!_names[@]}"; do
  printf "%-${max_len}s  |  %s\n" "${_names[$i]}" "${_labels[$i]}"
done
