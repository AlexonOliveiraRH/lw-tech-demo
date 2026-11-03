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
  python3 - <<'PY'
import re
from pathlib import Path
p = Path("pyproject.toml")
text = p.read_text()
text = re.sub(
    r"\n?# BEGIN LIGHTWELL DEMO SOURCE\n.*?# END LIGHTWELL DEMO SOURCE\n?",
    "\n",
    text,
    flags=re.S,
)
text, _ = re.subn(r"^sqlparse\s*=\s*.*$", 'sqlparse = "0.5.5"', text, count=1, flags=re.M)
p.write_text(text.rstrip() + "\n")
PY
  poetry lock --no-interaction
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

# Highlight sqlparse findings for narration
if command -v jq >/dev/null 2>&1 && [[ -f "${JSON}" ]]; then
  echo "==> sqlparse-related findings (summary)"
  jq -r '
    .Results[]? | .Vulnerabilities[]? |
    select(.PkgName == "sqlparse") |
    "\(.VulnerabilityID) \(.Severity) \(.PkgName) \(.InstalledVersion)"
  ' "${JSON}" 2>/dev/null | sort -u | head -40 || true
fi

echo "Wrote ${REPORT}"
cat "${REPORT}"
