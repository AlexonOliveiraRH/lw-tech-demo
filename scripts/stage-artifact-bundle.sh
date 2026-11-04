#!/usr/bin/env bash
# Copy demo hero files into a flat bundle dir for Actions upload-artifact.
# Zip root should be: demo-report-*.html + sbom-*.cdx.json (no nested digging).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIVE="${ROOT}/artifacts/live"
STAGE="${1:-}"

case "${STAGE}" in
  before|after) ;;
  *)
    echo "usage: $0 before|after" >&2
    exit 1
    ;;
esac

BUNDLE="${ROOT}/artifacts/bundle-${STAGE}"
rm -rf "${BUNDLE}"
mkdir -p "${BUNDLE}"

copy_if() {
  local src="$1" dest="$2"
  if [[ -f "${src}" ]]; then
    cp -f "${src}" "${dest}"
    echo "  + $(basename "${dest}")"
  else
    echo "  (missing) ${src}" >&2
  fi
}

echo "Staging flat artifact bundle → artifacts/bundle-${STAGE}/"
copy_if "${LIVE}/demo-report-${STAGE}.html" "${BUNDLE}/demo-report-${STAGE}.html"
copy_if "${LIVE}/sbom-${STAGE}.cdx.json" "${BUNDLE}/sbom-${STAGE}.cdx.json"

# Helpful extras still flat (optional for demos that dig one level deeper into the zip)
copy_if "${LIVE}/demo-report-${STAGE}.md" "${BUNDLE}/demo-report-${STAGE}.md"
copy_if "${LIVE}/sbom-${STAGE}-inventory.txt" "${BUNDLE}/sbom-${STAGE}-inventory.txt"
copy_if "${LIVE}/pip-audit-${STAGE}.txt" "${BUNDLE}/pip-audit-${STAGE}.txt"
copy_if "${LIVE}/trivy-${STAGE}.txt" "${BUNDLE}/trivy-${STAGE}.txt"

if [[ "${STAGE}" == "before" ]]; then
  copy_if "${LIVE}/scan-before-summary.md" "${BUNDLE}/scan-before-summary.md"
else
  copy_if "${LIVE}/lightwell-proof.md" "${BUNDLE}/lightwell-proof.md"
fi

echo "Bundle ready: ${BUNDLE}"
ls -la "${BUNDLE}"
