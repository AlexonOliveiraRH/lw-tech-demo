# Secrets and configuration

Do **not** commit credentials. See [lightwell-feeds.md](lightwell-feeds.md) for the four Console repositories.

## Primary demo path (self-service)

Use the numbered workflows only:

| Workflow | Auth | Runner |
|----------|------|--------|
| **[1 · Scan (vulnerable)](../.github/workflows/01-scan.yml)** | none | default `ubuntu-latest` (optional `self-hosted`) |
| **[2 · Remediate (Lightwell)](../.github/workflows/02-remediate.yml)** | paste `lightwell_user` + `lightwell_token` per run | default `ubuntu-latest` (optional `self-hosted`) |
| **[J1 · Java Scan (vulnerable)](../.github/workflows/java-1-scan.yml)** | none | default `ubuntu-latest` (optional `self-hosted`) |
| **[J2 · Java Remediate (Lightwell)](../.github/workflows/java-2-remediate.yml)** | paste `lightwell_user` + `lightwell_token` per run | default `ubuntu-latest` (optional `self-hosted`) |

Run titles include the GitHub actor automatically (`@you`) and, for Remediate, the Lightwell username — no extra “who are you” field.

| Input | Workflow | Notes |
|-------|----------|-------|
| `lightwell_user` | 2, J2 | `orgId\|service-account-name` from console.redhat.com |
| `lightwell_token` | 2, J2 | Pasted per run; masked in logs via `::add-mask::` |
| `runner` | all | `ubuntu-latest` (default) or `self-hosted` |

> Workflow dispatch **inputs** (including the token) are visible to anyone who can see the Actions run metadata. Prefer short-lived tokens; rotate after the engagement if needed.

**Fork path (recommended for most people):** fork this repo → enable Actions → run **1** then **2** on your fork with your Lightwell SA. No dasmlab secrets required.

## Optional: advanced composite

**Actions → `z · Advanced (composite)`** is for maintainers / power users (`scan-build`, `full`, etc.). It can fall back to repository secrets when inputs are blank. Prefer **1** / **2** for demos.

## Repository secrets (optional, maintainers only)

Used only by the advanced composite when inputs are left blank — **not** by sales steps 1 / 2.

| Secret | Purpose |
|--------|---------|
| `LIGHTWELL_PYPI_USER` | Default username when advanced input left blank |
| `LIGHTWELL_PYPI_TOKEN` | Default token when advanced input left blank |
| `PYPI_INDEX_URL` | Optional Artifactory virtual simple index |

```bash
# Example (maintainers only — never commit values)
gh secret set LIGHTWELL_PYPI_USER --body '11009103|dasmlwsvc' --repo dasmlab/lw-tech-demo
gh secret set LIGHTWELL_PYPI_TOKEN < /path/to/token --repo dasmlab/lw-tech-demo
```

## Local env

| Variable | Example | Notes |
|----------|---------|-------|
| `LIGHTWELL_PYPI_USER` | `11009103\|dasmlwsvc` | Format `<orgId>\|<sa>` |
| `LIGHTWELL_TOKEN_FILE` | `/path/to/token` | Preferred locally |
| `LIGHTWELL_PYPI_TOKEN` | _(token)_ | Or set directly |
| `USE_LIGHTWELL` | `true` | Enables Lightwell Poetry sources |

```bash
cp .env.example .env
# scripts/load-lightwell-env.sh reads LIGHTWELL_TOKEN_FILE
```
