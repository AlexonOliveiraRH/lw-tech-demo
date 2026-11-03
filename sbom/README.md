# SBOM → Lightwell Lens (segment 5)

## Generate

From repo root:

```bash
./scripts/sbom-generate.sh
```

Output: `sbom/out/vulnerable-fastapi-*.cdx.json` (CycloneDX) plus `vulnerable-fastapi-latest.cdx.json` symlink.

Uses **Syft** when installed; otherwise **Trivy** `--format cyclonedx`.

## Upload to Lens

1. Open `${LIGHTWELL_LENS_URL}` (tenant provided for the engagement).
2. Upload the CycloneDX JSON from `sbom/out/`.
3. Show:
   - software component inventory for the FastAPI demo
   - automated **VEX** triage / noise reduction to actionable items

## Talk track

> “Transparency for AppSec without forcing a new runtime scanner purchase for Day-1 remediation.”

## Formats

| Generator | Format flag | File |
|-----------|-------------|------|
| Syft | `cyclonedx-json` | `*.cdx.json` |
| Trivy | `--format cyclonedx` | `*.cdx.json` |

SPDX is acceptable if the Lens tenant expects it; adjust the script flag accordingly for that engagement.
