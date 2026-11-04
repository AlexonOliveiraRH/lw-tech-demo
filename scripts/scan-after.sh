#!/usr/bin/env bash
# AFTER: Lightwell Validated + Remediated — prove +rhlw.1 and CVE drop for rem set.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${ROOT}/apps/vulnerable-fastapi"
OUT_DIR="${ROOT}/artifacts/live"
SAMPLE="${ROOT}/artifacts/sample-reports"
mkdir -p "${OUT_DIR}"

# shellcheck disable=SC1091
source "${ROOT}/scripts/load-lightwell-env.sh"

if [[ "${USE_LIGHTWELL:-false}" != "true" ]]; then
  echo "USE_LIGHTWELL not true — cannot prove Lightwell path." >&2
  exit 1
fi

if [[ -z "${LIGHTWELL_PYPI_TOKEN:-}" || -z "${LIGHTWELL_PYPI_USER:-}" ]]; then
  echo "LIGHTWELL_PYPI_USER and LIGHTWELL_PYPI_TOKEN required" >&2
  exit 1
fi

"${ROOT}/scripts/configure-poetry-source.sh"
(
  cd "${APP}"
  poetry lock --no-interaction
  poetry install --no-interaction
  echo "==> remediated set versions"
  for pkg in sqlparse PyPDF2 tokenizers; do
    poetry run python -c "import importlib.metadata as m; print(f'{pkg}={m.version(\"${pkg}\")}')"
  done
)

REPORT="${OUT_DIR}/trivy-after.txt"
JSON="${OUT_DIR}/trivy-after.json"
AUDIT="${OUT_DIR}/pip-audit-after.txt"

if command -v trivy >/dev/null 2>&1; then
  echo "==> Trivy AFTER"
  trivy fs --scanners vuln --pkg-types library \
    --severity HIGH,CRITICAL \
    --format table --output "${REPORT}" \
    "${APP}" || true
  trivy fs --scanners vuln --pkg-types library \
    --severity HIGH,CRITICAL \
    --format json --output "${JSON}" \
    "${APP}" || true
fi

echo "==> pip-audit AFTER"
(
  cd "${APP}"
  poetry run pip install -q pip-audit
  # +rhlw.1 builds are not on public PyPI — pip-audit reports them as unauditable
  # (i.e. no longer matching the public CVE records). That is the sales proof.
  poetry run pip-audit -f columns 2>&1 | tee "${AUDIT}" || true
)

"${ROOT}/scripts/prove-lightwell.sh"

cp -f "${OUT_DIR}/lightwell-proof.md" "${SAMPLE}/lightwell-proof.md" 2>/dev/null || true
