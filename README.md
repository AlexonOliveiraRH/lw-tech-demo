# Lightwell Part 2 Technical Demo Kit

**Audience:** salesperson / SSA  
**Goal:** show CVE noise → remediate via the **Lightwell Network** → prove it in Lens — no app rewrite.

Repo: [dasmlab/lw-tech-demo](https://github.com/dasmlab/lw-tech-demo)

---

## What you run (only two workflows)

In **Actions** you may see four names. **Only use the numbered ones:**

| Workflow | Sales? | What it does |
|----------|--------|----------------|
| **1 · Scan (vulnerable)** | ✅ Step 1 | Public pins + scanners + **SBOM before** + visual report |
| **2 · Remediate (Lightwell)** | ✅ Step 2 | Lightwell feeds → `+rhlw.1` + **SBOM after** + visual report |
| `z · CI (maintainers)` | ❌ ignore | PR/push smoke test |
| `z · Advanced (composite)` | ❌ ignore | Power-user pipeline |

---

## Steps

### 1 — Scan (no Lightwell login)

1. [Actions → **1 · Scan (vulnerable)**](https://github.com/dasmlab/lw-tech-demo/actions/workflows/01-scan.yml) → **Run workflow**
2. Open the green run → **Summary** (glanceable report in the page)
3. Artifacts → **`scan-before`** → download **`demo-report-before.html`** → open in a browser (screen-share this, not the logs)
4. Same artifact → **`sbom-before.cdx.json`** → upload to **Lightwell Lens** (show hooks / catch)

**Say:** “These three packages are exactly what Lightwell remediates — public builds light up scanners and Lens.”

### 2 — Remediate (paste token for this run only)

1. [Actions → **2 · Remediate (Lightwell)**](https://github.com/dasmlab/lw-tech-demo/actions/workflows/02-remediate.yml) → **Run workflow**
2. Required inputs (not stored in this public repo):
   - **lightwell_user** — `orgId|service-account-name` (shape: `11009103|dasmlwsvc`)
   - **lightwell_token** — service-account token from Lightwell Console
3. Open **Summary** on the green run
4. Artifacts → **`remediate-proof`** → **`demo-report-after.html`** (browser) + **`sbom-after.cdx.json`** → Lens

**Say / point at:**

- Versions are **`+rhlw.1`** from the **Lightwell Network**
- **Remediated** = sqlparse / PyPDF2 / tokenizers  
- **Validated** = rest of the catalog (FastAPI, …)
- Public CVE records no longer bind to these builds  
- Tests pass — **no application rewrite**

---

## Pins

| Package | Step 1 (public) | Step 2 (Lightwell) |
|---------|-----------------|--------------------|
| sqlparse | `0.5.5` | `0.5.5+rhlw.1` · Remediated |
| PyPDF2 | `3.0.1` | `3.0.1+rhlw.1` · Remediated |
| tokenizers | `0.23.1` | `0.23.1+rhlw.1` · Remediated |
| FastAPI / httpx / … | public | **Validated** |

Console has four repos; this demo uses the **two Python** feeds. Details: [docs/lightwell-feeds.md](docs/lightwell-feeds.md)

---

## Optional

| Item | When |
|------|------|
| [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md) | Fuller talk track |
| [sbom/README.md](sbom/README.md) | Lens upload notes |
| [integration/artifactory](integration/artifactory/) | Local Artifactory sandbox |

---

## Secrets

Step 2 takes the token **in the workflow form** so forks and sales laptops stay clean — nothing Lightwell-secret is committed here.
