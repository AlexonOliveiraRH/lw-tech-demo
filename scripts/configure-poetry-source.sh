#!/usr/bin/env bash
# Wire Poetry to Lightwell:
#   - Direct: validated = primary catalog; remediated = explicit source for sqlparse
#   - Artifactory virtual: single primary (virtual already stacks remotes)
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

# Strip any previous demo source block
text = re.sub(
    r"\n?# BEGIN LIGHTWELL DEMO SOURCE\n.*?# END LIGHTWELL DEMO SOURCE\n?",
    "\n",
    text,
    flags=re.S,
)

if use_artifactory:
    sqlparse_line = 'sqlparse = "0.5.5"'
    block = f"""
# BEGIN LIGHTWELL DEMO SOURCE
[[tool.poetry.source]]
name = "lightwell"
url = "{pypi_index}"
priority = "primary"
# END LIGHTWELL DEMO SOURCE
"""
else:
    sqlparse_line = 'sqlparse = { version = "0.5.5", source = "lightwell-remediated" }'
    block = f"""
# BEGIN LIGHTWELL DEMO SOURCE
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

text, n = re.subn(r"^sqlparse\s*=\s*.*$", sqlparse_line, text, count=1, flags=re.M)
if n != 1:
    raise SystemExit("sqlparse dependency line not found or duplicated")

text = text.rstrip() + "\n" + block
path.write_text(text)
print("Wrote Lightwell sources; artifactory_virtual=", use_artifactory)
PY

if [[ "${use_artifactory_virtual}" == "true" ]]; then
  echo "Poetry → Artifactory virtual ${PYPI_INDEX_URL}"
  if [[ -n "${ARTIFACTORY_USER:-}" && -n "${ARTIFACTORY_PASSWORD:-}" ]]; then
    poetry -C "${APP}" config http-basic.lightwell "${ARTIFACTORY_USER}" "${ARTIFACTORY_PASSWORD}"
  elif [[ -n "${LIGHTWELL_PYPI_USER:-}" && -n "${LIGHTWELL_PYPI_TOKEN:-}" ]]; then
    poetry -C "${APP}" config http-basic.lightwell "${LIGHTWELL_PYPI_USER}" "${LIGHTWELL_PYPI_TOKEN}"
  fi
else
  echo "Poetry → validated (primary) + remediated (explicit sqlparse)"
  poetry -C "${APP}" config http-basic.lightwell-validated "${LIGHTWELL_PYPI_USER}" "${LIGHTWELL_PYPI_TOKEN}"
  poetry -C "${APP}" config http-basic.lightwell-remediated "${LIGHTWELL_PYPI_USER}" "${LIGHTWELL_PYPI_TOKEN}"
  echo "poetry http-basic for validated + remediated (user=${LIGHTWELL_PYPI_USER})"
fi
