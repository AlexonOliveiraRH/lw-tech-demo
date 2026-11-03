#!/usr/bin/env bash
# Wire Poetry in apps/vulnerable-fastapi to Artifactory virtual / Lightwell simple index.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${ROOT}/apps/vulnerable-fastapi"
PYPROJECT="${APP}/pyproject.toml"

if [[ "${USE_LIGHTWELL:-false}" != "true" ]]; then
  echo "USE_LIGHTWELL is not true; leaving Poetry on default PyPI."
  exit 0
fi

if [[ -z "${PYPI_INDEX_URL:-}" ]]; then
  echo "PYPI_INDEX_URL is required when USE_LIGHTWELL=true" >&2
  exit 1
fi

# Strip trailing slash for Poetry consistency
INDEX_URL="${PYPI_INDEX_URL%/}"

MARKER="# BEGIN LIGHTWELL DEMO SOURCE"
if grep -q "${MARKER}" "${PYPROJECT}"; then
  echo "Lightwell source block already present in ${PYPROJECT}"
else
  cat >> "${PYPROJECT}" <<EOF

${MARKER}
[[tool.poetry.source]]
name = "lightwell"
url = "${INDEX_URL}"
priority = "primary"
# END LIGHTWELL DEMO SOURCE
EOF
  echo "Appended primary Poetry source → ${INDEX_URL}"
fi

# Optional basic auth for Lightwell direct or Artifactory
if [[ -n "${LIGHTWELL_PYPI_TOKEN:-}" ]]; then
  poetry -C "${APP}" config http-basic.lightwell "__token__" "${LIGHTWELL_PYPI_TOKEN}"
  echo "Configured poetry http-basic for source 'lightwell'"
elif [[ -n "${ARTIFACTORY_USER:-}" && -n "${ARTIFACTORY_PASSWORD:-}" ]]; then
  poetry -C "${APP}" config http-basic.lightwell "${ARTIFACTORY_USER}" "${ARTIFACTORY_PASSWORD}"
  echo "Configured poetry http-basic for Artifactory user ${ARTIFACTORY_USER}"
fi
