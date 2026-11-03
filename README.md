# Lightwell Part 2 Technical Demo Kit

Private demo assets for the **20-minute AppSec Lead & Artifactory Administrators** technical demonstration.

Primary goal: prove integrating Lightwell into a Python build pipeline takes minutes, works with Poetry/Pipenv/Artifactory, and eliminates vulnerability noise on eligible packages — without an application rewrite.

CISO / Part 1 slide narrative lives elsewhere; this repo is the live demo kit and runbook.

## 20-minute agenda

| # | Segment | Mins | Owner focus |
|---|---------|------|-------------|
| 0 | Setup check / agenda | 1 | SSA |
| 1 | PyPI feed walkthrough | 3 | AppSec + Artifactory |
| 2 | Artifactory remote + Python tooling | 5 | Artifactory Admin |
| 3 | Remediation build (FastAPI + pytest) | 5 | AppSec / Eng |
| 4 | Scanner before/after | 3 | AppSec |
| 5 | Lightwell Lens + SBOM/VEX | 2 | AppSec |
| 6 | Recap → next steps | 1 | SSA |

Full speaker script: [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md)

## Quick start

```bash
# App (vulnerable pin; public PyPI by default)
cd apps/vulnerable-fastapi
poetry install
poetry run pytest

# Point resolve at Artifactory virtual / Lightwell
export USE_LIGHTWELL=true
export PYPI_INDEX_URL="https://<artifactory>/artifactory/api/pypi/<virtual>/simple"
./scripts/configure-poetry-source.sh   # from repo root
poetry lock && poetry install
poetry run pytest

# Scanner before/after
./scripts/scan-before.sh
./scripts/scan-after.sh

# SBOM for Lens
./scripts/sbom-generate.sh
```

## Repo map

```
apps/vulnerable-fastapi/   Intentional CVE pin + FastAPI + pytest
integration/artifactory/   Compose sandbox + remote/virtual setup
integration/poetry|pipenv|pip/   Index redirect snippets
scripts/                   Demo beat helpers
sbom/                      SBOM → Lens notes
artifacts/sample-reports/  Backup before/after Trivy output
.github/workflows/         Install → pytest (+ optional scan)
```

## Demo prep checklist

- [ ] Lightwell PyPI credentials / endpoint validated (`LIGHTWELL_PYPI_URL`, `LIGHTWELL_PYPI_TOKEN`)
- [ ] Artifactory sandbox up (`integration/artifactory`) or screen-share admin access
- [ ] Sample FastAPI app + Poetry lock with intentional vulnerable pin
- [ ] GitHub Actions (or local) pytest green path ready
- [ ] Trivy CLI ready for before/after
- [ ] Syft or Trivy SBOM generation ready (`./scripts/sbom-generate.sh`)
- [ ] Lightwell Lens tenant / upload path ready (`LIGHTWELL_LENS_URL`)
- [ ] Backup recording / sample reports if live Artifactory is blocked

## Success criteria (say out loud at end)

1. Remote repo created in minutes
2. Poetry/Pipenv resolve through Artifactory → Lightwell
3. Tests pass on remediated dependency
4. Scanner delta visible
5. SBOM visible in Lens with VEX context

## Secrets / env

| Name | Where | Purpose |
|------|-------|---------|
| `LIGHTWELL_PYPI_URL` | env / GH secret | Lightwell Secure CDN / PyPI endpoint |
| `LIGHTWELL_PYPI_TOKEN` | env / GH secret | Feed auth |
| `PYPI_INDEX_URL` | env / GH secret | Artifactory virtual (or direct Lightwell) simple index |
| `USE_LIGHTWELL` | env / GH var | `true` to prefer Lightwell/Artifactory source |
| `LIGHTWELL_LENS_URL` | env / docs | Lens upload tenant |

Never commit tokens. See [docs/secrets.md](docs/secrets.md).

## License

Internal demo material for Lightwell SSA engagement rehearsal. Not for public redistribution until the repo is made public.
