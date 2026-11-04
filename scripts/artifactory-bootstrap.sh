#!/usr/bin/env bash
# Attempt to create Lightwell Python remotes + virtual via Artifactory REST.
# NOTE: Remote / virtual repo REST APIs require Artifactory Pro (or a trial license).
# OSS will return HTTP 400 — use UI on a Pro/trial instance, or the direct Lightwell
# Poetry path (validated + remediated) which is already proven in this kit.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT}/scripts/load-lightwell-env.sh"

ART_URL="${ARTIFACTORY_URL:-http://localhost:8082/artifactory}"
ART_USER="${ARTIFACTORY_USER:-admin}"
ART_PASS="${ARTIFACTORY_PASSWORD:-password}"

if [[ -z "${LIGHTWELL_PYPI_TOKEN:-}" ]]; then
  echo "LIGHTWELL_PYPI_TOKEN required" >&2
  exit 1
fi

auth=(-u "${ART_USER}:${ART_PASS}")

echo "==> ping ${ART_URL}"
curl -sf "${auth[@]}" "${ART_URL}/api/system/ping" >/dev/null
echo OK

license=$(curl -sf "${auth[@]}" "${ART_URL}/api/system/version" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("license",""))')
echo "license=${license}"

put_remote() {
  local key="$1" url="$2"
  echo "==> remote repo ${key} → ${url}"
  local body code
  body=$(curl -sS "${auth[@]}" -w '\n%{http_code}' -X PUT -H 'Content-Type: application/json' \
    "${ART_URL}/api/repositories/${key}" \
    -d "{\"key\":\"${key}\",\"rclass\":\"remote\",\"packageType\":\"pypi\",\"url\":\"${url}\",\"username\":\"${LIGHTWELL_PYPI_USER}\",\"password\":\"${LIGHTWELL_PYPI_TOKEN}\"}")
  code=$(echo "$body" | tail -n1)
  echo "$body" | head -n -1
  if [[ "$code" != "200" && "$code" != "201" ]]; then
    echo "FAILED HTTP ${code}" >&2
    if echo "$body" | grep -qi 'Artifactory Pro'; then
      echo >&2
      echo "Artifactory OSS cannot create remote PyPI repos. Options:" >&2
      echo "  1) Apply a Pro/trial license to this sandbox" >&2
      echo "  2) In the customer Pro Artifactory UI, create remotes" >&2
      echo "  3) Demo the working direct Lightwell Poetry path (remediated + validated)" >&2
      echo "     USE_LIGHTWELL=true ./scripts/configure-poetry-source.sh" >&2
    fi
    return 1
  fi
}

put_remote "pypi-lightwell-remediated" "${LIGHTWELL_REMEDIATED_REMOTE}"
put_remote "pypi-lightwell-validated" "${LIGHTWELL_VALIDATED_REMOTE}"

echo "==> virtual pypi-virtual"
curl -sf "${auth[@]}" -X PUT -H 'Content-Type: application/json' \
  "${ART_URL}/api/repositories/pypi-virtual" \
  -d '{
    "key": "pypi-virtual",
    "rclass": "virtual",
    "packageType": "pypi",
    "repositories": ["pypi-lightwell-remediated", "pypi-lightwell-validated"]
  }'
echo
echo "Virtual simple index: ${ART_URL}/api/pypi/pypi-virtual/simple"
