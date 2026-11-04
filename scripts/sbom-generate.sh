#!/usr/bin/env bash
# CycloneDX SBOM for Lightwell Lens upload.
#
# SBOM_STAGE=before  → public/vulnerable pins (Scan workflow → show Lens hooks)
# SBOM_STAGE=after   → Lightwell +rhlw.1 (Remediate workflow → clean SBOM)
# SBOM_SKIP_INSTALL=1 → skip poetry install when the caller already resolved deps
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="${ROOT}/apps/vulnerable-fastapi"
OUT="${ROOT}/sbom/out"
LIVE="${ROOT}/artifacts/live"
mkdir -p "${OUT}" "${LIVE}"

STAGE="${SBOM_STAGE:-}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

case "${STAGE}" in
  before)
    LABEL="before"
    TALK="Upload to Lightwell Lens to show the catch / hooks on the public vulnerable pins."
    ;;
  after)
    LABEL="after"
    TALK="Upload to Lightwell Lens to show the remediated (+rhlw.1) inventory after Lightwell Network."
    ;;
  *)
    LABEL="latest"
    TALK="Upload this file to Lightwell Lens (${LIGHTWELL_LENS_URL:-set LIGHTWELL_LENS_URL})."
    ;;
esac

CDX="${OUT}/vulnerable-fastapi-${LABEL}-${STAMP}.cdx.json"
STABLE="${OUT}/vulnerable-fastapi-${LABEL}.cdx.json"
LIVE_COPY="${LIVE}/sbom-${LABEL}.cdx.json"

if [[ "${SBOM_SKIP_INSTALL:-0}" != "1" ]]; then
  (
    cd "${APP}"
    if [[ "${USE_LIGHTWELL:-false}" == "true" ]] || grep -q "BEGIN LIGHTWELL DEMO SOURCE" pyproject.toml; then
      poetry lock --no-interaction
    fi
    poetry install --no-interaction
  )
fi

if command -v syft >/dev/null 2>&1; then
  echo "==> Syft CycloneDX (${LABEL})"
  syft "dir:${APP}" -o cyclonedx-json > "${CDX}"
elif command -v trivy >/dev/null 2>&1; then
  echo "==> Trivy CycloneDX (${LABEL}; syft not installed)"
  trivy fs --format cyclonedx --output "${CDX}" "${APP}"
else
  echo "Need syft or trivy to generate SBOM" >&2
  exit 1
fi

cp -f "${CDX}" "${STABLE}"
ln -sfn "$(basename "${CDX}")" "${OUT}/vulnerable-fastapi-latest.cdx.json"
cp -f "${CDX}" "${LIVE_COPY}"

# Quick inventory check for the remediated set (helps Job Summary / demos)
INV="${LIVE}/sbom-${LABEL}-inventory.txt"
{
  echo "SBOM stage: ${LABEL}"
  echo "File: ${CDX}"
  echo
  python3 - "${CDX}" <<'PY'
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text())
comps = data.get("components") or []
want = {"sqlparse", "pypdf2", "tokenizers", "fastapi", "httpx"}
print(f"{'name':<16} {'version':<24} purl")
print("-" * 72)
for c in comps:
    name = (c.get("name") or "").lower()
    if name not in want:
        continue
    ver = c.get("version") or "?"
    purl = c.get("purl") or ""
    print(f"{c.get('name'):<16} {ver:<24} {purl}")
PY
} > "${INV}" || true

echo "SBOM: ${CDX}"
echo "Stable: ${STABLE}"
echo "Artifact copy: ${LIVE_COPY}"
echo
echo "${TALK}"
echo "See sbom/README.md for the Lens talk track."

if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  {
    echo
    echo "## SBOM for Lightwell Lens (${LABEL})"
    echo
    echo "${TALK}"
    echo
    echo "Download artifact file: \`sbom-${LABEL}.cdx.json\` (CycloneDX)."
    echo
    if [[ -f "${INV}" ]]; then
      echo '```'
      cat "${INV}"
      echo '```'
    fi
  } >> "${GITHUB_STEP_SUMMARY}"
fi
