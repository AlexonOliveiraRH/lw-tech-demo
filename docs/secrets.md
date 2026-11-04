# Secrets and configuration

Do **not** commit credentials. See [lightwell-feeds.md](lightwell-feeds.md) for the four Console repositories.

## GitHub Actions UI (public demo)

Preferred path: **Actions → Lightwell Demo → Run workflow**.

| Input | When required | Notes |
|-------|---------------|-------|
| `pipeline` | always | `scan-before` / `build` / `scan-after` / `test` / `scan-build` / `full` / `publish` |
| `lightwell_user` | Lightwell stages | `orgId\|service-account-name` |
| `lightwell_token` | Lightwell stages | Pasted per run; masked in logs via `::add-mask::` |
| `use_lightwell_for_build` | `build` / `test` | Default `true` |

Lightwell stages: `scan-after`, `scan-build`, `full`, `publish`, and `build`/`test` when the checkbox is on.

**Resolution order:** workflow input → repository secret (`LIGHTWELL_PYPI_USER` / `LIGHTWELL_PYPI_TOKEN`).  
If both are empty on a Lightwell stage, the run fails fast in **Resolve credentials**.

> Workflow dispatch inputs are visible to anyone who can see the Actions run metadata. Prefer short-lived tokens for public demos; rotate after the engagement if needed.

## Repository secrets (optional, maintainers)

| Secret | Purpose |
|--------|---------|
| `LIGHTWELL_PYPI_USER` | Default username when input left blank |
| `LIGHTWELL_PYPI_TOKEN` | Default token when input left blank |
| `PYPI_INDEX_URL` | Optional Artifactory virtual simple index |

```bash
# Example (maintainers only — never commit values)
gh secret set LIGHTWELL_PYPI_USER --body '11009103|dasmlwsvc' --repo dasmlab/lw-tech-demo
gh secret set LIGHTWELL_PYPI_TOKEN < /home/dasm/dasmlwsvc.token --repo dasmlab/lw-tech-demo
```

## Local env

| Variable | Example | Notes |
|----------|---------|-------|
| `LIGHTWELL_PYPI_USER` | `11009103\|dasmlwsvc` | Format `<orgId>\|<sa>` |
| `LIGHTWELL_TOKEN_FILE` | `/home/dasm/dasmlwsvc.token` | Preferred locally |
| `LIGHTWELL_PYPI_TOKEN` | _(token)_ | Or set directly |
| `USE_LIGHTWELL` | `true` | Enables Lightwell Poetry sources |

```bash
cp .env.example .env
# scripts/load-lightwell-env.sh reads LIGHTWELL_TOKEN_FILE
```
