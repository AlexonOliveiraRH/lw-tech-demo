# Lightwell Part 2 Technical Demo Kit

**Audience:** salesperson / SSA running a live AppSec + Artifactory demo  
**Goal:** click through GitHub Actions, show CVE noise, then remediate via the **Lightwell Network** — no app rewrite.

Public repo: [dasmlab/lw-tech-demo](https://github.com/dasmlab/lw-tech-demo)

---

## Sales click-path (do this)

### Step 1 — Scan (no login to Lightwell)

1. Open **[Actions → 1 · Scan (vulnerable)](https://github.com/dasmlab/lw-tech-demo/actions/workflows/01-scan.yml)**
2. Click **Run workflow** → **Run workflow**
3. When green, open the run → **Job summary** and artifact **`scan-before`**
4. Download **`sbom-before.cdx.json`** → upload to **Lightwell Lens** to show the catch / hooks on the public pins
5. **Say:** “Same three packages Lightwell remediates today — sqlparse, PyPDF2, tokenizers — scanners *and* Lens light up on the public builds.”

### Step 2 — Remediate (paste token for this run only)

1. Open **[Actions → 2 · Remediate (Lightwell)](https://github.com/dasmlab/lw-tech-demo/actions/workflows/02-remediate.yml)**
2. Click **Run workflow**
3. Fill in (required every time — not stored in this public repo):
   - **lightwell_user** — `orgId|service-account-name` (example shape: `11009103|dasmlwsvc`)
   - **lightwell_token** — service account token from Lightwell Console
4. Run → open **Job summary**
5. **Say / point at:**
   - Versions are now **`+rhlw.1`** → built by the **Lightwell Network**
   - **Remediated** feed = those three patched packages  
   - **Validated** feed = the rest of the RH-built catalog (FastAPI, etc.)
   - pip-audit no longer treats them as the public vulnerable PyPI artifacts  
   - Tests still pass — **no application rewrite**
6. Download **`sbom-after.cdx.json`** from **`remediate-proof`** → upload to Lens as the clean / remediated SBOM

Artifacts to screen-share: **`remediate-proof`** → `lightwell-proof.md` + `sbom-after.cdx.json`

---

## What the app is pinning

| Package | Public pin (Step 1) | After Lightwell (Step 2) |
|---------|---------------------|---------------------------|
| sqlparse | `0.5.5` | `0.5.5+rhlw.1` from **Remediated** |
| PyPDF2 | `3.0.1` | `3.0.1+rhlw.1` from **Remediated** |
| tokenizers | `0.23.1` | `0.23.1+rhlw.1` from **Remediated** |
| FastAPI / httpx / … | public or Validated | **Validated** catalog |

Lightwell Console exposes **four** repos (Python Remediated, Python Validated, Java Remediated, Java). This demo uses the **two Python** feeds. Details: [docs/lightwell-feeds.md](docs/lightwell-feeds.md)

---

## Optional deeper toolkit

| Item | When |
|------|------|
| [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md) | Full 20‑minute talk track |
| [Lightwell Demo](https://github.com/dasmlab/lw-tech-demo/actions/workflows/demo.yml) workflow | Composite `scan-build` / `full` for power users |
| [integration/artifactory](integration/artifactory/) | Local Artifactory OSS sandbox (Pro needed for remotes) |
| Local scripts | `./scripts/scan-before.sh` then `USE_LIGHTWELL=true ./scripts/scan-after.sh` |

PR/push **CI** only runs public Poetry + pytest (no token).

---

## Secrets note

Step 2 asks for the token **in the workflow form** so forks and sales laptops stay agnostic — nothing Lightwell-secret is committed here. Maintainers may still set repo secrets for other composite workflows; the Remediate sales job intentionally uses the pasted inputs for that run only.
