#!/usr/bin/env bash
# Segment 5 — generate CycloneDX SBOM for Lightwell Lens upload.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${ROOT}/apps/vulnerable-fastapi"
OUT="${ROOT}/sbom/out"
mkdir -p "${OUT}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
CDX="${OUT}/vulnerable-fastapi-${STAMP}.cdx.json"

(
  cd "${APP}"
  poetry install --no-interaction
)

if command -v syft >/dev/null 2>&1; then
  echo "==> Syft CycloneDX"
  syft "dir:${APP}" -o cyclonedx-json > "${CDX}"
elif command -v trivy >/dev/null 2>&1; then
  echo "==> Trivy CycloneDX (syft not installed)"
  trivy fs --format cyclonedx --output "${CDX}" "${APP}"
else
  echo "Need syft or trivy to generate SBOM" >&2
  exit 1
fi

ln -sfn "$(basename "${CDX}")" "${OUT}/vulnerable-fastapi-latest.cdx.json"
echo "SBOM: ${CDX}"
echo "Latest symlink: ${OUT}/vulnerable-fastapi-latest.cdx.json"
echo
echo "Upload this file to Lightwell Lens (${LIGHTWELL_LENS_URL:-set LIGHTWELL_LENS_URL})."
echo "See sbom/README.md for VEX triage talk track."
