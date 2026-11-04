#!/usr/bin/env bash
# BEFORE: public vulnerable pins — show CVE noise on the Lightwell remediated set.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${ROOT}/apps/vulnerable-fastapi"
OUT_DIR="${ROOT}/artifacts/live"
mkdir -p "${OUT_DIR}"

# shellcheck disable=SC1091
source "${ROOT}/scripts/load-lightwell-env.sh" 2>/dev/null || true
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
for name, line in (
    ("sqlparse", 'sqlparse = "0.5.5"'),
    ("PyPDF2", 'PyPDF2 = "3.0.1"'),
    ("tokenizers", 'tokenizers = "0.23.1"'),
):
    text, n = re.subn(rf"^{name}\s*=\s*.*$", line, text, count=1, flags=re.M)
    if n != 1:
        raise SystemExit(f"missing pin for {name}")
p.write_text(text.rstrip() + "\n")
PY
  poetry lock --no-interaction
  poetry install --no-interaction
)

REPORT="${OUT_DIR}/trivy-before.txt"
JSON="${OUT_DIR}/trivy-before.json"
AUDIT="${OUT_DIR}/pip-audit-before.txt"
SUMMARY="${OUT_DIR}/scan-before-summary.md"

if command -v trivy >/dev/null 2>&1; then
  echo "==> Trivy BEFORE"
  trivy fs --scanners vuln --pkg-types library \
    --severity HIGH,CRITICAL \
    --format table --output "${REPORT}" \
    "${APP}" || true
  trivy fs --scanners vuln --pkg-types library \
    --severity HIGH,CRITICAL \
    --format json --output "${JSON}" \
    "${APP}" || true
fi

echo "==> pip-audit BEFORE (catches PyPDF2 + sqlparse)"
(
  cd "${APP}"
  # Audit the venv packages (pip-audit on PATH from ci-install-tools / pip --user)
  poetry run pip install -q pip-audit
  poetry run pip-audit -f columns 2>&1 | tee "${AUDIT}" || true
)

{
  echo "# Scan BEFORE — public PyPI (vulnerable)"
  echo
  echo "App pins Lightwell's Python Remediated set at **public** versions:"
  echo
  echo "| Package | Pin |"
  echo "|---------|-----|"
  echo "| sqlparse | 0.5.5 |"
  echo "| PyPDF2 | 3.0.1 |"
  echo "| tokenizers | 0.23.1 |"
  echo
  echo "## Findings on the remediated set"
  echo
  echo '```'
  grep -iE 'sqlparse|pypdf|tokenizer' "${AUDIT}" || echo "(see full pip-audit / trivy artifacts)"
  echo '```'
  echo
  echo "## SBOM → Lightwell Lens"
  echo
  echo "Download **\`sbom-before.cdx.json\`** from this run’s artifacts and upload it to Lightwell Lens."
  echo "Lens hooks should catch the public vulnerable pins (sqlparse / PyPDF2 / tokenizers)."
  echo
  echo "Next: run **Remediate with Lightwell** (paste service-account user + token), then upload the after SBOM."
} > "${SUMMARY}"

cat "${SUMMARY}"
# Job Summary is composed once at end of the workflow (download link first).
