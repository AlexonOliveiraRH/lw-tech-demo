#!/usr/bin/env bash
# Load Lightwell demo env. Safe to source from other scripts.
# Token file default: /home/dasm/dasmlwsvc.token (never commit).

_LW_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "${_LW_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${_LW_ROOT}/.env"
  set +a
fi

# Service account: <orgId>|<service-account-name>
export LIGHTWELL_PYPI_USER="${LIGHTWELL_PYPI_USER:-11009103|dasmlwsvc}"

# --- Python Remediated (patched +rhlw.N) ---
export LIGHTWELL_REMEDIATED_SIMPLE="${LIGHTWELL_REMEDIATED_SIMPLE:-https://packages.redhat.com/lightwell/python/remediated/simple}"
export LIGHTWELL_REMEDIATED_REMOTE="${LIGHTWELL_REMEDIATED_REMOTE:-https://packages.redhat.com/api/pulp-content/lightwell/python/remediated/}"

# --- Python Validated (broad RH-built catalog) ---
export LIGHTWELL_VALIDATED_SIMPLE="${LIGHTWELL_VALIDATED_SIMPLE:-https://packages.redhat.com/lightwell/python/validated/simple}"
export LIGHTWELL_VALIDATED_REMOTE="${LIGHTWELL_VALIDATED_REMOTE:-https://packages.redhat.com/api/pulp-content/lightwell/python/validated/}"

# Back-compat aliases used by older snippets
export LIGHTWELL_PYPI_URL="${LIGHTWELL_PYPI_URL:-${LIGHTWELL_REMEDIATED_SIMPLE}}"
export LIGHTWELL_ARTIFACTORY_REMOTE_URL="${LIGHTWELL_ARTIFACTORY_REMOTE_URL:-${LIGHTWELL_REMEDIATED_REMOTE}}"
export LIGHTWELL_REGISTRY_URL="${LIGHTWELL_REGISTRY_URL:-https://packages.redhat.com/lightwell/python/remediated/}"

TOKEN_FILE="${LIGHTWELL_TOKEN_FILE:-/home/dasm/dasmlwsvc.token}"
if [[ -z "${LIGHTWELL_PYPI_TOKEN:-}" && -f "${TOKEN_FILE}" ]]; then
  LIGHTWELL_PYPI_TOKEN="$(tr -d '\n' < "${TOKEN_FILE}")"
  export LIGHTWELL_PYPI_TOKEN
fi

# Default Poetry/pip index when Artifactory virtual is not set:
# prefer remediated simple so eligible pins get +rhlw.N; scripts also add validated.
if [[ -z "${PYPI_INDEX_URL:-}" ]]; then
  export PYPI_INDEX_URL="${LIGHTWELL_REMEDIATED_SIMPLE}"
fi
