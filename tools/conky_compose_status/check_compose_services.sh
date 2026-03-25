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

while IFS= read -r svc; do
  [ -z "${svc}" ] && continue

  cid="$(docker compose -f "${COMPOSE_FILE}" ps -q "${svc}" 2>/dev/null || true)"
  if [ -z "${cid}" ]; then
    printf "%-14s : DOWN\n" "${svc}"
    continue
  fi

  state="$(docker inspect -f '{{.State.Status}}' "${cid}" 2>/dev/null || echo "unknown")"
  health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "${cid}" 2>/dev/null || true)"

  case "${state}" in
    running)
      label="RUNNING"
      ;;
    exited|dead)
      label="ERROR"
      ;;
    created|restarting)
      label="STARTING"
      ;;
    paused)
      label="PAUSED"
      ;;
    *)
      label="${state^^}"
      ;;
  esac

  if [ -n "${health}" ]; then
    printf "%-14s : %s (%s)\n" "${svc}" "${label}" "${health}"
  else
    printf "%-14s : %s\n" "${svc}" "${label}"
  fi
done <<< "${services}"
