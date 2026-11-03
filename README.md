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

## Lightwell feeds (remember: four Console repos)

Python demo stacks **two** feeds; Java counterparts exist for Artifactory admins:

| Feed | Role |
|------|------|
| **Python Remediated** | Patched `+rhlw.N` (e.g. `sqlparse-0.5.5+rhlw.1`) |
| **Python Validated** | Broad RH-built catalog (~2400 pkgs) |
| Java Remediated / Java Validated | Same pattern — out of scope for this kit |

Details: [docs/lightwell-feeds.md](docs/lightwell-feeds.md)

## Quick start

```bash
cp .env.example .env   # uses 11009103|dasmlwsvc + /home/dasm/dasmlwsvc.token

# Before: public / validated vulnerable pin
cd apps/vulnerable-fastapi && poetry install && poetry run pytest

# After: Lightwell remediated (primary) + validated (supplemental)
cd ../..
export USE_LIGHTWELL=true
./scripts/configure-poetry-source.sh
cd apps/vulnerable-fastapi && poetry lock && poetry install && poetry show sqlparse && poetry run pytest

./scripts/scan-before.sh
./scripts/scan-after.sh
./scripts/sbom-generate.sh
```

Artifactory (two remotes → one virtual): `integration/artifactory/SETUP.md` + `./scripts/artifactory-bootstrap.sh`  
Nexus (optional / mTLS caveat): `integration/nexus/SETUP.md`

## Repo map

```
apps/vulnerable-fastapi/   sqlparse==0.5.5 pin + FastAPI + pytest
integration/artifactory/   Compose + remediated/validated remotes
integration/nexus/         Optional Nexus compose
integration/poetry|pipenv|pip/
docs/lightwell-feeds.md    Four-repo / two-Python explanation
scripts/                   Demo beat helpers
```

## Demo prep checklist

- [ ] Service account `11009103|dasmlwsvc` + token file validated against remediated **and** validated
- [ ] Artifactory sandbox with **both** Python remotes (or screen-share admin access)
- [ ] Sample FastAPI app + Poetry lock with intentional vulnerable pin (`sqlparse==0.5.5`)
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
| `LIGHTWELL_PYPI_USER` | env / GH secret | `11009103\|dasmlwsvc` |
| `LIGHTWELL_PYPI_TOKEN` / token file | env / GH secret | Service account token |
| `LIGHTWELL_REMEDIATED_*` / `VALIDATED_*` | env | Two Python feed URLs |
| `PYPI_INDEX_URL` | env / GH secret | Artifactory virtual simple index when ready |
| `USE_LIGHTWELL` | env / GH var | `true` to enable Lightwell sources |
| `LIGHTWELL_LENS_URL` | env / docs | Lens upload tenant |

Never commit tokens. See [docs/secrets.md](docs/secrets.md).

## License

Internal demo material for Lightwell SSA engagement rehearsal. Not for public redistribution until the repo is made public.
