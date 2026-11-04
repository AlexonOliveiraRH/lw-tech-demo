# Part 2 — Live Technical Demo Runbook (20 min)

**Audience:** AppSec Lead & Artifactory Administrators  
**Primary goal:** Prove integration takes minutes, works with Poetry/Pipenv/Artifactory, and eliminates vulnerability noise on eligible packages — without app rewrite.

---

## 0. Agenda (1 min)

> “We’ll do five things: show the feed, wire Artifactory, redirect Poetry, build+test, scan before/after, and glance at Lens with an SBOM.”

Confirm: Artifactory sandbox or screen-share, Lightwell feed URL, FastAPI sample open, Trivy + SBOM scripts ready.

**Preferred live path:** GitHub **Actions → Lightwell Demo → Run workflow** with pipeline `scan-build` (or stepwise `scan-before` / `build` / `scan-after`). Paste `lightwell_user` + `lightwell_token` in the form (or use repo secrets). Artifacts attach to the run for screen-share.

---

## 1. Repository Walkthrough (3 min)

**Owner focus:** AppSec + Artifactory

1. Open Lightwell PyPI feed in browser (`LIGHTWELL_PYPI_URL` / customer-ready Secure CDN docs).
2. Pick the demo pin: **`sqlparse==0.5.5`** (on Python Validated as vulnerable; Lightwell **Remediated** serves `0.5.5+rhlw.1`). Feed also has PyPDF2 / tokenizers. Console has four repos — we stack **Python Remediated + Python Validated**.
3. Show: patched artifact available for consume **without source changes**.
4. Point out signing / metadata / security artifacts as available.

**Talk track:** “Same package name and compatible API surface — remediated content behind your existing resolver.”

**Backup:** Screenshots / feed docs under customer materials if the live feed is unreachable.

---

## 2. Artifactory & Python Tooling (5 min)

**Owner focus:** Artifactory Admin

### Artifactory (two Python remotes → one virtual)

Console has **four** repos (Python Remediated, Python Validated, Java Remediated, Java). Wire both Python remotes:

1. Remote `pypi-lightwell-remediated` → `https://packages.redhat.com/api/pulp-content/lightwell/python/remediated/`
2. Remote `pypi-lightwell-validated` → `https://packages.redhat.com/api/pulp-content/lightwell/python/validated/`
3. Basic auth: `11009103|dasmlwsvc` + service account token
4. Virtual `pypi-virtual` includes remediated **first**, then validated
5. Developers point Poetry at the virtual only

Local rehearsal: [integration/artifactory/SETUP.md](integration/artifactory/SETUP.md) + `./scripts/artifactory-bootstrap.sh`  
Feeds explainer: [docs/lightwell-feeds.md](docs/lightwell-feeds.md)

### Developer redirect (show Poetry; mention others)

| Tool | Snippet |
|------|---------|
| Poetry (primary) | [integration/poetry/pyproject.source.toml](integration/poetry/pyproject.source.toml) |
| Pipenv | [integration/pipenv/Pipfile.source](integration/pipenv/Pipfile.source) |
| pip | [integration/pip/pip.conf](integration/pip/pip.conf) |

**Talk track:** “Admins change the remote once. Developers don’t learn a new package manager.”

---

## 3. Remediation & Build (5 min)

**Owner focus:** AppSec / Eng

1. Start from `apps/vulnerable-fastapi` — Poetry lock with intentional vulnerable pin.
2. Resolve / install via Artifactory → Lightwell:
   ```bash
   export USE_LIGHTWELL=true
   export PYPI_INDEX_URL="https://<host>/artifactory/api/pypi/<virtual>/simple"
   ./scripts/configure-poetry-source.sh
   cd apps/vulnerable-fastapi && poetry lock && poetry install
   ```
3. Run pytest (local or GitHub Actions `demo-build` workflow).
4. Show: dependency resolves to Lightwell-patched artifact; tests pass.

**Talk track:** “Remediation without the major-version refactor tax.”

Helper: `./scripts/demo-build.sh`

---

## 4. Scanner Validation (3 min)

**Owner focus:** AppSec

1. **Before:** `./scripts/scan-before.sh` — Trivy on public/`0.5.5` — sqlparse HIGH CVEs visible.
2. **After:** `./scripts/scan-after.sh` — show `poetry show sqlparse` → **`0.5.5+rhlw.1`**. Trivy may still list the same CVE IDs (version fingerprint); Installed Version column shows the remediated local label.
3. Bridge to segment 5: Lens VEX is what turns fingerprint noise into “triaged / not affected.”

**Talk track:** “Your scanner. Your gate. The binary changed — `+rhlw.1` — without a major-version rewrite. Lens closes the fingerprint gap with VEX.”

---

## 5. Lightwell Lens (2 min)

**Owner focus:** AppSec

1. `./scripts/sbom-generate.sh` → CycloneDX under `sbom/out/`
2. Upload to Lightwell Lens (`LIGHTWELL_LENS_URL`)
3. Show component visibility + VEX triage reducing noise to actionable items

**Talk track:** “Transparency for AppSec without forcing a new runtime scanner purchase for Day-1 remediation.”

Details: [sbom/README.md](sbom/README.md)

---

## 6. Close (1 min)

Restate three perceptions: **functional in under 24 hours**, **self-sufficient**, **100% process compatible**.

Ask:

- Who owns Artifactory virtuals?
- Who owns AppSec gates?
- Who owns the pilot service?

Book pilot / PoC window.

### Success criteria (say out loud)

- Remote repo created in minutes
- Poetry/Pipenv resolve through Artifactory → Lightwell
- Tests pass on remediated dependency
- Scanner delta visible
- SBOM visible in Lens with VEX context
