# How to Run the Demo — 6 slides

Keep every slide to **one idea**. Bracketed lines = screenshot callouts.

Repo: https://github.com/dasmlab/lw-tech-demo  
Console: https://console.redhat.com (Lightwell → service account + Lens)

---

## Slide 1 — What this demo proves

**Title:** Same app. Change the package source. Fault → fixed.

**One line under the title**

No code rewrite — only where the build pulls packages from.

**The story (four beats, left → right)**

| 1 · App | 2 · Scan | 3 · Point at Lightwell | 4 · Build again |
|---------|----------|------------------------|-----------------|
| One FastAPI app | Public open-source pins | Source / remote = Lightwell Network | Same pipeline |
| Unchanged | See the fault (CVE noise) | Not a refactor | Fault remediated (`+rhlw.1`) |

**Footer line**

Scan → change source provider → rebuild → prove it (report + Lens SBOM)

**Screenshot:** none required — this is the narrative slide  
**Layout hint:** one horizontal flow, not three feature columns

---

## Slide 2 — What you need (once)

**Title:** Prerequisites

1. Lightwell entitlement on **console.redhat.com**  
2. A **service account** (`orgId|name` + token)  
3. **Lens** in your tenant  
4. This repo **or a fork** (Actions → GitHub-hosted by default)

**Screenshot:** Console SA create

---

## Slide 3 — Before: scan the app

**Title:** Step 1 — Scan (public sources)

1. Actions → **1 · Scan (vulnerable)** → Run  
2. Download `scan-before` → unzip (flat)  
3. Open **`demo-report-before.html`**  
4. Upload **`sbom-before.cdx.json`** to Lens  

**Look for:** findings on sqlparse / PyPDF2 / tokenizers

**Screenshot:** FINDINGS report · Lens hooks on before SBOM

---

## Slide 4 — The only change

**Title:** Point the build at Lightwell (not the app)

- App code: **unchanged**  
- Build machine: resolve from **Lightwell Remediated** (+ Validated catalog)  
- Same idea as flipping an Artifactory / pip remote

**Screenshot (optional):** `source = "lightwell-remediated"` on the three pins

---

## Slide 5 — After: build again

**Title:** Step 2 — Remediate (Lightwell sources)

1. Actions → **2 · Remediate (Lightwell)** → paste SA user + token → Run  
2. Download `remediate-proof` → unzip  
3. Open **`demo-report-after.html`**  
4. Upload **`sbom-after.cdx.json`** to Lens  

**Look for:** `+rhlw.1` · tests green · before/after difference in Lens

**Screenshot:** PASS report with `+rhlw.1` · Lens after SBOM

---

## Slide 6 — That’s the demo

**Title:** Fault in → source change → fault out

- Same application and CI shape  
- Remediation from the **package source**, not a rewrite  
- Proof: **demo-report.html** + **Lens SBOM** (before and after)

**Ask:** Who owns the index/remotes? Which app do we pilot first?

**Screenshot:** Actions sidebar — only **1** and **2**
