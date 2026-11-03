#!/usr/bin/env bash
# Segment 4 — Trivy scan after Artifactory → Lightwell resolve.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${ROOT}/apps/vulnerable-fastapi"
OUT_DIR="${ROOT}/artifacts/live"
SAMPLE="${ROOT}/artifacts/sample-reports"
mkdir -p "${OUT_DIR}"

if ! command -v trivy >/dev/null 2>&1; then
  echo "trivy not found on PATH" >&2
  exit 1
fi

# shellcheck disable=SC1091
source "${ROOT}/scripts/load-lightwell-env.sh"

if [[ "${USE_LIGHTWELL:-false}" != "true" ]]; then
  echo "USE_LIGHTWELL not true — showing sample AFTER report for backup narration:"
  if [[ -f "${SAMPLE}/trivy-after.txt" ]]; then
    cat "${SAMPLE}/trivy-after.txt"
  else
    echo "(no sample report yet)" >&2
    exit 1
  fi
  exit 0
fi

"${ROOT}/scripts/configure-poetry-source.sh"
(
  cd "${APP}"
  poetry lock --no-interaction
  poetry install --no-interaction
)

REPORT="${OUT_DIR}/trivy-after.txt"
JSON="${OUT_DIR}/trivy-after.json"

echo "==> Trivy AFTER (Artifactory → Lightwell)"
trivy fs --scanners vuln --pkg-types library \
  --severity HIGH,CRITICAL \
  --format table --output "${REPORT}" \
  "${APP}" || true
trivy fs --scanners vuln --pkg-types library \
  --severity HIGH,CRITICAL \
  --format json --output "${JSON}" \
  "${APP}" || true

if command -v jq >/dev/null 2>&1 && [[ -f "${JSON}" ]]; then
  echo "==> sqlparse-related findings (summary)"
  jq -r '
    .Results[]? | .Vulnerabilities[]? |
    select(.PkgName == "sqlparse") |
    "\(.VulnerabilityID) \(.Severity) \(.PkgName) \(.InstalledVersion)"
  ' "${JSON}" 2>/dev/null | sort -u | head -40 || echo "(none)"
fi

echo "Wrote ${REPORT}"
cat "${REPORT}"
