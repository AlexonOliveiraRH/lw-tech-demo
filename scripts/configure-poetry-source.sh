#!/usr/bin/env bash
# Wire Poetry to Lightwell Python Validated (catalog) + Remediated (explicit pins).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${ROOT}/apps/vulnerable-fastapi"
PYPROJECT="${APP}/pyproject.toml"

# shellcheck disable=SC1091
source "${ROOT}/scripts/load-lightwell-env.sh"

if [[ "${USE_LIGHTWELL:-false}" != "true" ]]; then
  echo "USE_LIGHTWELL is not true; leaving Poetry on default PyPI."
  exit 0
fi

use_artifactory_virtual=false
if [[ "${PYPI_INDEX_URL:-}" == *"/artifactory/"* ]]; then
  use_artifactory_virtual=true
fi

python3 - <<'PY' "$PYPROJECT" "$use_artifactory_virtual" "${PYPI_INDEX_URL:-}" "${LIGHTWELL_REMEDIATED_SIMPLE}" "${LIGHTWELL_VALIDATED_SIMPLE}"
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
use_artifactory = sys.argv[2] == "true"
pypi_index = sys.argv[3].rstrip("/")
rem = sys.argv[4].rstrip("/")
val = sys.argv[5].rstrip("/")

text = path.read_text()
text = re.sub(
    r"\n?# BEGIN LIGHTWELL DEMO SOURCE\n.*?# END LIGHTWELL DEMO SOURCE\n?",
    "\n",
    text,
    flags=re.S,
)

# Public-style pins (Artifactory virtual owns routing) vs explicit remediated sources.
if use_artifactory:
    pins = {
        "sqlparse": 'sqlparse = "0.5.5"',
        "PyPDF2": 'PyPDF2 = "3.0.1"',
        "tokenizers": 'tokenizers = "0.23.1"',
    }
    block = f"""
# BEGIN LIGHTWELL DEMO SOURCE
[[tool.poetry.source]]
name = "lightwell"
url = "{pypi_index}"
priority = "primary"
# END LIGHTWELL DEMO SOURCE
"""
else:
    pins = {
        "sqlparse": 'sqlparse = { version = "0.5.5", source = "lightwell-remediated" }',
        "PyPDF2": 'PyPDF2 = { version = "3.0.1", source = "lightwell-remediated" }',
        "tokenizers": 'tokenizers = { version = "0.23.1", source = "lightwell-remediated" }',
    }
    block = f"""
# BEGIN LIGHTWELL DEMO SOURCE
# Validated = broad RH-built catalog (FastAPI, httpx, …)
# Remediated = CVE-patched +rhlw.N for eligible pins (sqlparse, PyPDF2, tokenizers)
[[tool.poetry.source]]
name = "lightwell-validated"
url = "{val}"
priority = "primary"

[[tool.poetry.source]]
name = "lightwell-remediated"
url = "{rem}"
priority = "explicit"
# END LIGHTWELL DEMO SOURCE
"""

for name, line in pins.items():
    text, n = re.subn(rf"^{re.escape(name)}\s*=\s*.*$", line, text, count=1, flags=re.M)
    if n != 1:
        raise SystemExit(f"{name} dependency line not found or duplicated")

path.write_text(text.rstrip() + "\n" + block)
print("Wrote Lightwell sources; artifactory_virtual=", use_artifactory)
PY

if [[ "${use_artifactory_virtual}" == "true" ]]; then
  echo "Poetry → Artifactory virtual ${PYPI_INDEX_URL}"
  if [[ -n "${ARTIFACTORY_USER:-}" && -n "${ARTIFACTORY_PASSWORD:-}" ]]; then
    poetry -C "${APP}" config http-basic.lightwell "${ARTIFACTORY_USER}" "${ARTIFACTORY_PASSWORD}"
  else
    poetry -C "${APP}" config http-basic.lightwell "${LIGHTWELL_PYPI_USER}" "${LIGHTWELL_PYPI_TOKEN}"
  fi
else
  echo "Poetry → Validated (catalog) + Remediated (sqlparse, PyPDF2, tokenizers)"
  poetry -C "${APP}" config http-basic.lightwell-validated "${LIGHTWELL_PYPI_USER}" "${LIGHTWELL_PYPI_TOKEN}"
  poetry -C "${APP}" config http-basic.lightwell-remediated "${LIGHTWELL_PYPI_USER}" "${LIGHTWELL_PYPI_TOKEN}"
fi
