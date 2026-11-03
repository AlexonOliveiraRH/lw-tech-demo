#!/usr/bin/env bash
# Segment 3 helper: install + pytest for the vulnerable FastAPI sample.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${ROOT}/apps/vulnerable-fastapi"

# Load .env if present
if [[ -f "${ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT}/.env"
  set +a
fi

echo "==> configure sources (USE_LIGHTWELL=${USE_LIGHTWELL:-false})"
"${ROOT}/scripts/configure-poetry-source.sh"

echo "==> poetry install"
(
  cd "${APP}"
  if [[ "${USE_LIGHTWELL:-false}" == "true" ]]; then
    poetry lock --no-interaction
  fi
  poetry install --no-interaction
  echo "==> resolved urllib3"
  poetry show urllib3
  echo "==> pytest"
  poetry run pytest -q
)

echo "demo-build OK"
