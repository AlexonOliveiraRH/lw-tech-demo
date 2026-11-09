# Demo runbook (clean path)

**Time:** ~10–15 minutes  
**You need:** browser + Lightwell service account (`orgId|name` + token) + Lens URL

In Actions: open a **Demo · …** workflow (e.g. **Demo · Python · Trivy**) and run **step = scan** then **step = remediate** (runner default `ubuntu-latest`). Ignore anything named `z · …`.  
Run titles show `@github-user` and the step. Fork + enable Actions works without dasmlab runners.

---

## 0. Open the repo

https://github.com/dasmlab/lw-tech-demo → README **Steps**

---

## 1. Scan (vulnerable)

Actions → **Demo · Python · Trivy** → Run workflow → **step = scan**.

| Look at | Why |
|---------|-----|
| Artifacts → unzip `scan-before` | Flat zip root (no nested folders) |
| `demo-report-before.html` | Visual before report |
| `sbom-before.cdx.json` | Upload to **Lens** → hooks on public inventory |

**Notable:** the app pins the same three packages Lightwell remediates — scanners and Lens light up on public builds.

---

## 2. Remediate (Lightwell)

Actions → **Demo · Python · Trivy** → Run workflow → **step = remediate**.

- `lightwell_user` = `NNNNNNN|service-account-name`
- `lightwell_token` = token for **this run only**

**While it runs:** Remediated + Validated remotes; no app rewrite; token not stored in the public repo.

| Look at | Why |
|---------|-----|
| Artifacts → unzip `remediate-proof` | Flat zip root (no nested folders) |
| `demo-report-after.html` | Origin proof (`+rhlw.1` / Lightwell Network) |
| `sbom-after.cdx.json` | Upload to Lens and compare with before |
| `lightwell-proof.md` | One-pager if needed |

---

## 3. Wrap-up

- Index / remote change on the build machine = the integration surface  
- Remediated clears eligible CVE noise at the package  
- Validated keeps the rest RH-built  
- Before SBOM → Lens hooks; after SBOM → Lightwell builds  
