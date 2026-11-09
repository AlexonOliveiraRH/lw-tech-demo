# Secrets and configuration

Do **not** commit credentials. See [lightwell-feeds.md](lightwell-feeds.md) for the four Console repositories.

## Primary demo path (self-service)

Pick a row from the README **Table of Self-Service Demos**. Each demo is **one** workflow — choose **step = scan** or **step = remediate**.

| Workflow | Auth | Runner |
|----------|------|--------|
| **[Demo · Python · Trivy](../.github/workflows/demo-python-trivy.yml)** | Scan: none · Remediate: paste `lightwell_user` + `lightwell_token` | default `ubuntu-latest` (optional `self-hosted`) |
| **[Demo · Java · Maven · Trivy](../.github/workflows/demo-java-maven-trivy.yml)** | Scan: none · Remediate: paste `lightwell_user` + `lightwell_token` | default `ubuntu-latest` (optional `self-hosted`) |

Run titles include the GitHub actor (`@you`) and the step name. Lightwell usernames stay out of the run title.

| Input | When | Notes |
|-------|------|-------|
| `step` | always | `scan` or `remediate` |
| `lightwell_user` | remediate | `orgId\|service-account-name` from console.redhat.com |
| `lightwell_token` | remediate | Pasted per run; masked in logs via `::add-mask::` |
| `runner` | always | `ubuntu-latest` (default) or `self-hosted` |

> Workflow dispatch **inputs** (including the token) are visible to anyone who can see the Actions run metadata. Prefer short-lived tokens; rotate after the engagement if needed.

**Fork path (recommended for most people):** fork this repo → enable Actions → run a **Demo · …** workflow on your fork with your Lightwell SA. No dasmlab secrets required.

## Optional: advanced composite

**Actions → `z · Advanced (composite)`** is for maintainers / power users (`scan-build`, `full`, etc.). It can fall back to repository secrets when inputs are blank. Prefer the **Demo · …** workflows for demos.

## Repository secrets (optional, maintainers only)

Used only by the advanced composite when inputs are left blank — **not** by the self-service demos.

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

See [../integration/artifactory/SETUP.md](../integration/artifactory/SETUP.md) for the Artifactory sandbox path.
