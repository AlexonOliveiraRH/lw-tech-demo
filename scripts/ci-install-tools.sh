#!/usr/bin/env bash
# Install Poetry (+ optional Trivy) for self-hosted runners without pipx.
set -euo pipefail

WITH_TRIVY="${WITH_TRIVY:-false}"

mkdir -p "${HOME}/.local/bin"
export PATH="${HOME}/.local/bin:${PATH}"
echo "${HOME}/.local/bin" >> "${GITHUB_PATH:-/dev/null}" 2>/dev/null || true

if ! command -v poetry >/dev/null 2>&1; then
  python3 -m pip install --user -q "poetry>=1.8,<3"
  # Ensure user base bin is on PATH (PEP 370)
  USER_BASE="$(python3 -m site --user-base)"
  export PATH="${USER_BASE}/bin:${PATH}"
  echo "${USER_BASE}/bin" >> "${GITHUB_PATH:-/dev/null}" 2>/dev/null || true
fi
poetry --version

# Scanner used in before/after sales proof (public PyPI; may be absent from Validated).
python3 -m pip install --user -q "pip-audit>=2.7"
export PATH="$(python3 -m site --user-base)/bin:${PATH}"

if [[ "${WITH_TRIVY}" == "true" ]]; then
  if ! command -v trivy >/dev/null 2>&1; then
    VER="${TRIVY_VERSION:-0.76.1}"
    curl -sL "https://github.com/aquasecurity/trivy/releases/download/v${VER}/trivy_${VER}_Linux-64bit.tar.gz" \
      | tar -xz -C "${HOME}/.local/bin" trivy
  fi
  trivy --version
fi
