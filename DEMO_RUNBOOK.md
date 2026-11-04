# Sales demo script (GitHub Actions — minimal CLI)

**Time:** ~10–15 minutes of screen-share  
**You need:** browser + Lightwell service account (user `orgId|name` + token)

---

## 0. Open the repo

https://github.com/dasmlab/lw-tech-demo

Point at the README **Sales click-path**.

---

## 1. Scan (vulnerable) — no Lightwell auth

Actions → **1 · Scan (vulnerable)** → Run workflow.

**Talk:** “Customer app pins the same three packages Lightwell remediates: sqlparse, PyPDF2, tokenizers. Scanners light up.”

**Show:** Job summary + `scan-before` artifact (pip-audit lines for sqlparse / PyPDF2).

---

## 2. Remediate — paste auth for this run only

Actions → **2 · Remediate (Lightwell)** → Run workflow.

Enter:

- `lightwell_user` = `NNNNNNN|service-account-name`
- `lightwell_token` = token from Lightwell Console (this run only)

**Talk while it runs:**

- Admins wire **Python Remediated** + **Python Validated** (two of the four Console repos).
- Developers do not rewrite application code.
- Token is not stored in this public repo — pasted per demo run.

**Show Job summary:**

| Proof | What it means |
|-------|----------------|
| `sqlparse=0.5.5+rhlw.1` (and PyPDF2 / tokenizers) | Binary from **Lightwell Network Remediated** |
| FastAPI still resolves | Comes from **Lightwell Validated** |
| pytest green | No app rewrite |
| pip-audit: “not found on PyPI” for `+rhlw.1` | Public CVE records no longer bind to these builds |

Open artifact **`remediate-proof`** / `lightwell-proof.md` if you want a single page.

---

## 3. Close

- Remote / index change = minutes  
- **Remediated** clears eligible CVE noise at the package  
- **Validated** keeps the rest of the catalog RH-built  
- Ask who owns Artifactory virtuals + which pilot service  

Optional Artifactory admin deep-dive: `integration/artifactory/SETUP.md` (local OSS; Pro for remotes).
