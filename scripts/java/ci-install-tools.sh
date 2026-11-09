#!/usr/bin/env bash
# Install Maven (if missing) + Trivy for the Java demo workflows.
# GitHub-hosted ubuntu-latest already ships Maven; self-hosted runners may not.
set -euo pipefail

mkdir -p "${HOME}/.local/bin"
export PATH="${HOME}/.local/bin:${PATH}"
echo "${HOME}/.local/bin" >> "${GITHUB_PATH:-/dev/null}" 2>/dev/null || true

if ! command -v mvn >/dev/null 2>&1; then
  MVN_VER="${MAVEN_VERSION:-3.9.9}"
  curl -fsSL "https://archive.apache.org/dist/maven/maven-3/${MVN_VER}/binaries/apache-maven-${MVN_VER}-bin.tar.gz" \
    | tar -xz -C "${HOME}/.local"
  ln -sfn "${HOME}/.local/apache-maven-${MVN_VER}/bin/mvn" "${HOME}/.local/bin/mvn"
fi
mvn -v

if ! command -v trivy >/dev/null 2>&1; then
  VER="${TRIVY_VERSION:-0.76.1}"
  curl -fsSL "https://github.com/aquasecurity/trivy/releases/download/v${VER}/trivy_${VER}_Linux-64bit.tar.gz" \
    | tar -xz -C "${HOME}/.local/bin" trivy
fi
trivy --version

python3 --version
