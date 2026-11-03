# Secrets and configuration

Do **not** commit credentials. Configure locally or as GitHub Actions secrets.

## Required for live Lightwell path

| Variable | Example | Notes |
|----------|---------|-------|
| `LIGHTWELL_PYPI_URL` | `https://<lightwell-cdn>/...` | Customer-ready Secure CDN / PyPI endpoint |
| `LIGHTWELL_PYPI_TOKEN` | `lw_...` | Feed authentication |
| `PYPI_INDEX_URL` | `https://arti.example/artifactory/api/pypi/pypi-virtual/simple` | Prefer Artifactory virtual in the live path |
| `USE_LIGHTWELL` | `true` | Enables Lightwell/Artifactory Poetry source |

## Optional

| Variable | Purpose |
|----------|---------|
| `LIGHTWELL_LENS_URL` | Browser URL for Lens upload demo |
| `SNYK_TOKEN` | Only if demonstrating Snyk instead of / in addition to Trivy |
| `ARTIFACTORY_URL` | Base URL for local or sandbox Artifactory |
| `ARTIFACTORY_USER` / `ARTIFACTORY_PASSWORD` | Admin API / UI login for sandbox |

## GitHub Actions secrets

Set on `dasmlab/lw-tech-demo` (Settings → Secrets and variables → Actions):

- `LIGHTWELL_PYPI_URL`
- `LIGHTWELL_PYPI_TOKEN`
- `PYPI_INDEX_URL` (Artifactory virtual simple index when available)

Repository variable:

- `USE_LIGHTWELL` = `true` for the remediated CI path; omit or `false` for public-index baseline.

## Local env file

Copy `.env.example` to `.env` (gitignored) for rehearsal.
