# SBOM → Lightwell Lens

The demo flow produces **two** CycloneDX files:

| Stage | Workflow | Artifact file | Observation |
|-------|----------|---------------|-------------|
| **Before** | `Demo · …` · step = `scan` | `sbom-before.cdx.json` | Upload to Lens → hooks on public pins |
| **After** | `Demo · …` · step = `remediate` | `sbom-after.cdx.json` | Upload to Lens → Lightwell Network inventory (`+rhlw.1` / `*.rhlw-*`) |

## Generate locally

```bash
# Vulnerable / public pins (after ./scripts/scan-before.sh)
SBOM_STAGE=before SBOM_SKIP_INSTALL=1 ./scripts/sbom-generate.sh

# Lightwell remediated (after USE_LIGHTWELL=true ./scripts/scan-after.sh)
USE_LIGHTWELL=true SBOM_STAGE=after SBOM_SKIP_INSTALL=1 ./scripts/sbom-generate.sh
```

Outputs:

- `sbom/out/vulnerable-fastapi-before.cdx.json` / `…-after.cdx.json` (stable names)
- `artifacts/live/sbom-before.cdx.json` / `sbom-after.cdx.json` (working copies)
- Actions zip root: `sbom-before.cdx.json` / `sbom-after.cdx.json` (flat — see `scripts/stage-artifact-bundle.sh`)

- stamped `vulnerable-fastapi-{stage}-{UTC}.cdx.json` under `sbom/out/`

Uses **Syft** when installed; otherwise **Trivy** `--format cyclonedx`, then
`scripts/sbom-lens-normalize.py` so every component has a **Package URL (purl)** —
Lens skips entries without one (e.g. raw `poetry.lock` / filesystem path metadata from a directory scan).

## Upload to Lens

1. Open `${LIGHTWELL_LENS_URL}` (or console.redhat.com → Lightwell → Lens).
2. Upload the CycloneDX JSON from the Actions artifact (or `sbom/out/`).
3. **Before:** inventory + hooks on sqlparse / PyPDF2 / tokenizers.
4. **After:** compare the remediated SBOM — versions carry `+rhlw.1` from Lightwell Remediated.

## Notable

Lens on the before SBOM shows hooks; the after SBOM reflects Lightwell Network builds — transparency without rewriting the application.

## Formats

| Generator | Format flag | File |
|-----------|-------------|------|
| Syft | `cyclonedx-json` | `*.cdx.json` |
| Trivy | `--format cyclonedx` | `*.cdx.json` |

SPDX is acceptable if the Lens tenant expects it; adjust the script flag accordingly.
