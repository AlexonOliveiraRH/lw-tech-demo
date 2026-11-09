#!/usr/bin/env bash
# Lightwell Java demo - build, test, scan and SBOM for one stage.
#
#   scripts/java/scan.sh before   # public Maven Central (vulnerable pins), no auth
#   scripts/java/scan.sh after    # Lightwell Java Remediated + Validated
#                                 # needs LIGHTWELL_USER (orgId|name) + LIGHTWELL_TOKEN
#
# Each stage uses its own empty Maven local repository, so the after run cannot
# reuse jars downloaded from Maven Central by an earlier build.
set -euo pipefail

STAGE="${1:-}"
case "${STAGE}" in
  before|after) ;;
  *) echo "usage: $0 before|after" >&2; exit 1 ;;
esac

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
APP="${ROOT}/apps/vulnerable-spring"
LIVE="${ROOT}/artifacts/live"
M2="${RUNNER_TEMP:-${APP}/target}/m2-${STAGE}"
CYCLONEDX="org.cyclonedx:cyclonedx-maven-plugin:2.9.1"
mkdir -p "${LIVE}"
rm -rf "${M2}"

MVN=(mvn -B -ntp "-Dmaven.repo.local=${M2}")
if [[ "${STAGE}" == "after" ]]; then
  if [[ -z "${LIGHTWELL_USER:-}" || -z "${LIGHTWELL_TOKEN:-}" ]]; then
    echo "LIGHTWELL_USER and LIGHTWELL_TOKEN are required for the after stage" >&2
    exit 1
  fi
  if [[ "${LIGHTWELL_USER}" != *"|"* ]]; then
    echo "LIGHTWELL_USER must look like orgId|service-account-name" >&2
    exit 1
  fi
  # Fail fast with a readable message instead of a Maven dependency-resolution error.
  # Credentials go to curl via stdin config, not argv.
  REMEDIATED_URL="https://packages.redhat.com/api/pulp-content/lightwell/java/remediated/"
  esc() { local v="${1//\\/\\\\}"; printf '%s' "${v//\"/\\\"}"; }
  code="$(printf 'user = "%s:%s"\n' "$(esc "${LIGHTWELL_USER}")" "$(esc "${LIGHTWELL_TOKEN}")" \
    | curl -s -o /dev/null -w '%{http_code}' --max-time 30 --config - "${REMEDIATED_URL}" || true)"
  if [[ "${code}" != "200" ]]; then
    echo "::error::Lightwell Java Remediated feed returned HTTP ${code:-none}. Check lightwell_user (orgId|name) and lightwell_token." >&2
    exit 1
  fi
  MVN+=(-s "${APP}/.mvn/lightwell-settings.xml" -P lightwell)
fi

cd "${APP}"

echo "==> Build + tests (${STAGE})"
"${MVN[@]}" verify | tee "${LIVE}/maven-${STAGE}.txt"

echo "==> Resolved runtime dependencies (${STAGE})"
rm -rf "target/lib-${STAGE}"
"${MVN[@]}" -q dependency:copy-dependencies -DincludeScope=runtime "-DoutputDirectory=target/lib-${STAGE}"
"${MVN[@]}" -q dependency:list -DincludeScope=runtime -DoutputAbsoluteArtifactFilename=true \
  "-DoutputFile=target/deps-${STAGE}.txt"

echo "==> CycloneDX SBOM for Lightwell Lens (${STAGE})"
"${MVN[@]}" -q "${CYCLONEDX}:makeBom" -DoutputFormat=json "-DoutputName=sbom-${STAGE}"
cp -f "target/sbom-${STAGE}.json" "${LIVE}/sbom-${STAGE}.cdx.json"

if command -v trivy >/dev/null 2>&1; then
  echo "==> Trivy on the built jars (${STAGE})"
  trivy rootfs -q --scanners vuln --severity HIGH,CRITICAL \
    --format table --output "${LIVE}/trivy-${STAGE}.txt" "target/lib-${STAGE}" || true
  trivy rootfs -q --scanners vuln --severity HIGH,CRITICAL \
    --format json --output "${LIVE}/trivy-${STAGE}.json" "target/lib-${STAGE}" || true
else
  echo "trivy not found - skipping scanner step" >&2
fi

echo "==> Report + provenance check (${STAGE})"
python3 "${ROOT}/scripts/java/java-report.py" "${STAGE}"
