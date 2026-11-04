# Demo runbook (clean path)

**Time:** ~10–15 minutes  
**You need:** browser + Lightwell service account (`orgId|name` + token) + Lens URL

In Actions: run **only** `1 · Scan` then `2 · Remediate`. Ignore anything named `z · …`.

---

## 0. Open the repo

https://github.com/dasmlab/lw-tech-demo → README **Steps**

---

## 1. Scan (vulnerable)

Actions → **1 · Scan (vulnerable)** → Run workflow.

| Look at | Why |
|---------|-----|
| Artifacts → unzip `scan-before` | Download from the green run |
| `demo-report-before.html` | Visual before report |
| `sbom-before.cdx.json` | Upload to **Lens** → hooks on public inventory |

**Notable:** the app pins the same three packages Lightwell remediates — scanners and Lens light up on public builds.

---

## 2. Remediate (Lightwell)

Actions → **2 · Remediate (Lightwell)** → Run workflow.

- `lightwell_user` = `NNNNNNN|service-account-name`
- `lightwell_token` = token for **this run only**

**While it runs:** Remediated + Validated remotes; no app rewrite; token not stored in the public repo.

| Look at | Why |
|---------|-----|
| Artifacts → unzip `remediate-proof` | Download from the green run |
| `demo-report-after.html` | Origin proof (`+rhlw.1` / Lightwell Network) |
| `sbom-after.cdx.json` | Upload to Lens and compare with before |
| `lightwell-proof.md` | One-pager if needed |

---

## 3. Wrap-up

- Index / remote change on the build machine = the integration surface  
- Remediated clears eligible CVE noise at the package  
- Validated keeps the rest RH-built  
- Before SBOM → Lens hooks; after SBOM → Lightwell builds  
