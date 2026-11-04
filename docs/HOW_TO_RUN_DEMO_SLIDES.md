# How to Run the Demo — 6 slides

Paste into your deck as-is. Bracketed lines are **screenshot callouts**.

Repo: https://github.com/dasmlab/lw-tech-demo  
Console: https://console.redhat.com (Lightwell entitlement → service account)

---

## Slide 1 — What this demo proves (in ~15 minutes)

**Title:** Live before → after with the Lightwell Network + Lens

**Body**

- Same FastAPI app. **No application rewrite.**
- **Before:** public PyPI pins → scanners + Lens light up  
- **After:** build machine pulls from the **Lightwell Network** → `+rhlw.1` remediated builds + Validated catalog  
- Immediate value in an **existing CI pipeline** (GitHub Actions standing in for a typical SDLC)

**Observation points**

1. Ease of integration — remotes / index on the build machine, not a rewrite  
2. Anyone with a Lightwell **service account** (from console.redhat.com) can run this repo or a fork  
3. Before/after **SBOMs** (Lens) + **demo-report.html** from the Actions artifacts

**Screenshot:** repo README “Steps” / Actions sidebar showing **1 · Scan** and **2 · Remediate** (ignore `z · …`)

---

## Slide 2 — Setup & what it simulates

**Title:** SDLC simplified — Scan then Remediate

**What it simulates**

| Pipeline motion | This kit |
|-----------------|----------|
| CI scans the app on public deps | **1 · Scan (vulnerable)** |
| Pipeline remotes point at Lightwell; rebuild | **2 · Remediate (Lightwell)** |
| Review SBOM / findings | **Lens** + **demo-report.html** |

**Setup (once)**

- Entitlement on **console.redhat.com** → create Lightwell **service account** → copy `orgId|name` + token  
- Fork this repo (or run here if you have Actions access) — default runner is **GitHub-hosted** `ubuntu-latest`  
- Token is pasted **per run**, not stored in the public repo; run title shows `@github-user`

**The integration story**

- App code is unchanged.  
- The build machine points Poetry at Lightwell (**Validated** + **Remediated** for sqlparse / PyPDF2 / tokenizers) — same idea as a remote / index line — then consumes results (tests, SBOM, Lens).

**Screenshot:** Lightwell Console service-account create (or `orgId|sa` form fields on workflow **2**)  
**Screenshot (optional):** config snippet showing `source = "lightwell-remediated"` on the three pins

---

## Slide 3 — Step 1: Scan (vulnerable)

**Title:** Run **1 · Scan (vulnerable)** — no Lightwell login

**Do**

1. Actions → **1 · Scan (vulnerable)** → Run workflow  
2. When green, open the run, scroll down, **download artifacts** (`scan-before`), unzip (flat root)  
3. Open **`demo-report-before.html`**  
4. Upload **`sbom-before.cdx.json`** to **Lightwell Lens**

**Look for**

- Public pins: sqlparse `0.5.5`, PyPDF2 `3.0.1`, tokenizers `0.23.1`  
- pip-audit / Trivy **FINDINGS** on that set  
- Lens **hooks** on the before SBOM

**Notable:** same three packages Lightwell remediates — noise appears before any remotes change.

**Screenshot:** Actions artifacts download  
**Screenshot:** browser with `demo-report-before.html` (FINDINGS)  
**Screenshot:** Lens after uploading `sbom-before.cdx.json`

---

## Slide 4 — Step 2: Remediate (Lightwell Network)

**Title:** Run **2 · Remediate (Lightwell)** — paste SA for this run only

**Do**

1. Actions → **2 · Remediate (Lightwell)** → Run workflow  
2. Inputs: `lightwell_user` = `orgId|service-account-name` · `lightwell_token` = token  
3. When green, download **`remediate-proof`**, unzip  
4. Open **`demo-report-after.html`** · upload **`sbom-after.cdx.json`** to Lens

**Look for**

| Signal | Meaning |
|--------|---------|
| `…+rhlw.1` on the three packages | **Remediated** feed / Lightwell Network builds |
| FastAPI / httpx still resolve | **Validated** catalog |
| pytest green | No app rewrite |
| pip-audit: not found on public PyPI | Not the vulnerable public wheels |

**Screenshot:** workflow_dispatch form with user + token fields  
**Screenshot:** `+rhlw.1` in Summary or after report  
**Screenshot:** `demo-report-after.html` (PASS)

---

## Slide 5 — Lens + reports (before / after)

**Title:** Prove it two ways — Lens SBOM + demo-report.html

**Before**

- `sbom-before.cdx.json` → Lens → hooks on public inventory  
- `demo-report-before.html` → CVE / pin snapshot

**After**

- `sbom-after.cdx.json` → Lens → inventory with `+rhlw.1`  
- `demo-report-after.html` → origin proof without reading CI logs

**Observation points**

- Same app and pipeline shape before / after  
- Artifacts come from the Actions run — token is per-run for forks

**Screenshot:** Lens before vs after  
**Screenshot:** artifacts list showing `sbom-*.cdx.json` + `demo-report-*.html`

---

## Slide 6 — Wrap-up

**Title:** Minutes to value — takeaways

**Recap**

- Pipeline motion: **scan → point build at Lightwell → remediate → SBOM / Lens**  
- Integration is on the **build machine / remotes**, not a rewrite  
- Runnable with a Lightwell SA from **console.redhat.com** (this repo or a fork)

**Next**

- Who owns Artifactory (or pip index) remotes?  
- Which pilot service for Remediated + Validated?  

**Screenshot (optional):** Actions sidebar — only **1** and **2**
