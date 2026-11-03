#!/usr/bin/env bash
# Segment 4 — Trivy scan on public-PyPI resolved tree (vulnerable path).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${ROOT}/apps/vulnerable-fastapi"
OUT_DIR="${ROOT}/artifacts/live"
mkdir -p "${OUT_DIR}"

if ! command -v trivy >/dev/null 2>&1; then
  echo "trivy not found on PATH" >&2
  exit 1
fi

# Ensure vulnerable pin is installed from public index
export USE_LIGHTWELL=false
(
  cd "${APP}"
  # Remove demo source block if a prior after-scan left it
  if grep -q "# BEGIN LIGHTWELL DEMO SOURCE" pyproject.toml; then
    python3 - <<'PY'
from pathlib import Path
p = Path("pyproject.toml")
text = p.read_text()
start = text.find("# BEGIN LIGHTWELL DEMO SOURCE")
end = text.find("# END LIGHTWELL DEMO SOURCE")
if start != -1 and end != -1:
    end = text.find("\n", end) + 1
    p.write_text(text[:start] + text[end:])
PY
  fi
  poetry install --no-interaction
)

REPORT="${OUT_DIR}/trivy-before.txt"
JSON="${OUT_DIR}/trivy-before.json"

echo "==> Trivy BEFORE (public PyPI / vulnerable pin)"
trivy fs --scanners vuln --pkg-types library \
  --severity HIGH,CRITICAL \
  --format table --output "${REPORT}" \
  "${APP}" || true
trivy fs --scanners vuln --pkg-types library \
  --severity HIGH,CRITICAL \
  --format json --output "${JSON}" \
  "${APP}" || true

# Highlight urllib3 findings for narration
if command -v jq >/dev/null 2>&1 && [[ -f "${JSON}" ]]; then
  echo "==> urllib3-related findings (summary)"
  jq -r '
    .Results[]? | .Vulnerabilities[]? |
    select(.PkgName == "urllib3") |
    "\(.VulnerabilityID) \(.Severity) \(.PkgName) \(.InstalledVersion)"
  ' "${JSON}" 2>/dev/null | sort -u | head -40 || true
fi

echo "Wrote ${REPORT}"
cat "${REPORT}"
