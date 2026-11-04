# SBOM → Lightwell Lens

Sales flow produces **two** CycloneDX files:

| Stage | Workflow | Artifact file | Demo beat |
|-------|----------|---------------|-----------|
| **Before** | `1 · Scan (vulnerable)` | `sbom-before.cdx.json` | Upload to Lens → show catch / hooks on public pins |
| **After** | `2 · Remediate (Lightwell)` | `sbom-after.cdx.json` | Upload to Lens → show `+rhlw.1` Lightwell Network inventory |

## Generate locally

```bash
# Vulnerable / public pins (after ./scripts/scan-before.sh)
SBOM_STAGE=before SBOM_SKIP_INSTALL=1 ./scripts/sbom-generate.sh

# Lightwell remediated (after USE_LIGHTWELL=true ./scripts/scan-after.sh)
USE_LIGHTWELL=true SBOM_STAGE=after SBOM_SKIP_INSTALL=1 ./scripts/sbom-generate.sh
```

Outputs:

- `sbom/out/vulnerable-fastapi-before.cdx.json` / `…-after.cdx.json` (stable names)
- `artifacts/live/sbom-before.cdx.json` / `sbom-after.cdx.json` (Actions artifact copies)
- stamped `vulnerable-fastapi-{stage}-{UTC}.cdx.json` under `sbom/out/`

Uses **Syft** when installed; otherwise **Trivy** `--format cyclonedx`.

## Upload to Lens

1. Open `${LIGHTWELL_LENS_URL}` (tenant provided for the engagement).
2. Upload the CycloneDX JSON from the Actions artifact (or `sbom/out/`).
3. **Before:** show software inventory + automated hooks catching sqlparse / PyPDF2 / tokenizers.
4. **After:** re-upload (or compare) the remediated SBOM — versions carry `+rhlw.1` from Lightwell Remediated.

## Talk track

> “Transparency for AppSec without forcing a new runtime scanner purchase for Day-1 remediation — Lens hooks on the before SBOM, then the after SBOM proves the Lightwell Network builds.”

## Formats

| Generator | Format flag | File |
|-----------|-------------|------|
| Syft | `cyclonedx-json` | `*.cdx.json` |
| Trivy | `--format cyclonedx` | `*.cdx.json` |

SPDX is acceptable if the Lens tenant expects it; adjust the script flag accordingly for that engagement.
