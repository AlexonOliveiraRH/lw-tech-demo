# Sales demo script (clean path)

**Time:** ~10–15 minutes  
**You need:** browser + Lightwell service account (`orgId|name` + token) + Lens URL for the engagement

In Actions: run **only** `1 · Scan` then `2 · Remediate`. Ignore anything named `z · …`.

---

## 0. Open the repo

https://github.com/dasmlab/lw-tech-demo → README **Steps**

---

## 1. Scan (vulnerable)

Actions → **1 · Scan (vulnerable)** → Run workflow.

| Look at | Why |
|---------|-----|
| Run **Summary** | CVE / pin snapshot without digging logs |
| `demo-report-before.html` | Screen-share visual report |
| `sbom-before.cdx.json` | Upload to **Lens** → show hooks / catch |

**Talk:** “Customer pins the same three packages Lightwell remediates. Scanners and Lens light up.”

---

## 2. Remediate (Lightwell)

Actions → **2 · Remediate (Lightwell)** → Run workflow.

- `lightwell_user` = `NNNNNNN|service-account-name`
- `lightwell_token` = token for **this run only**

**Talk while it runs:** Remediated + Validated remotes; no app rewrite; token not stored in the public repo.

| Look at | Why |
|---------|-----|
| Run **Summary** | `+rhlw.1` table + PASS |
| `demo-report-after.html` | Visual “came from Lightwell Network” proof |
| `sbom-after.cdx.json` | Upload to Lens as the clean SBOM |
| `lightwell-proof.md` | One-pager if needed |

---

## 3. Close

- Index / remote change = minutes  
- Remediated clears eligible CVE noise at the package  
- Validated keeps the rest RH-built  
- Before SBOM → Lens hooks; after SBOM → Lightwell builds  
- Ask who owns Artifactory virtuals + which pilot service  
