# Secrets and configuration

Do **not** commit credentials. Configure locally or as GitHub Actions secrets.

See also [lightwell-feeds.md](lightwell-feeds.md) for the four Console repositories (two Python + two Java).

## Required for live Lightwell path

| Variable | Example | Notes |
|----------|---------|-------|
| `LIGHTWELL_PYPI_USER` | `11009103\|dasmlwsvc` | Format `<orgId>\|<service-account-name>` |
| `LIGHTWELL_TOKEN_FILE` | `/home/dasm/dasmlwsvc.token` | Preferred over inlining the token |
| `LIGHTWELL_PYPI_TOKEN` | _(from token file)_ | Password for basic auth |
| `LIGHTWELL_REMEDIATED_SIMPLE` | `https://packages.redhat.com/lightwell/python/remediated/simple` | Patched `+rhlw.N` packages |
| `LIGHTWELL_VALIDATED_SIMPLE` | `https://packages.redhat.com/lightwell/python/validated/simple` | Broad RH-built catalog |
| `PYPI_INDEX_URL` | Artifactory virtual simple index | Prefer virtual that stacks both remotes |
| `USE_LIGHTWELL` | `true` | Enables Lightwell/Artifactory Poetry sources |

## Optional

| Variable | Purpose |
|----------|---------|
| `LIGHTWELL_LENS_URL` | Browser URL for Lens upload demo |
| `SNYK_TOKEN` | Only if demonstrating Snyk |
| `ARTIFACTORY_URL` / `ARTIFACTORY_USER` / `ARTIFACTORY_PASSWORD` | Local Artifactory sandbox |
| `NEXUS_URL` | Optional Nexus UI |

## GitHub Actions secrets

Set on `dasmlab/lw-tech-demo`:

- `LIGHTWELL_PYPI_USER`
- `LIGHTWELL_PYPI_TOKEN`
- `PYPI_INDEX_URL` (Artifactory virtual when available)

Repository variable: `USE_LIGHTWELL=true` for the remediated CI path.

## Local env file

```bash
cp .env.example .env
# token loaded from LIGHTWELL_TOKEN_FILE by scripts/load-lightwell-env.sh
```
