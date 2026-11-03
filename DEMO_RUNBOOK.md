# Part 2 — Live Technical Demo Runbook (20 min)

**Audience:** AppSec Lead & Artifactory Administrators  
**Primary goal:** Prove integration takes minutes, works with Poetry/Pipenv/Artifactory, and eliminates vulnerability noise on eligible packages — without app rewrite.

---

## 0. Agenda (1 min)

> “We’ll do five things: show the feed, wire Artifactory, redirect Poetry, build+test, scan before/after, and glance at Lens with an SBOM.”

Confirm: Artifactory sandbox or screen-share, Lightwell feed URL, FastAPI sample open, Trivy + SBOM scripts ready.

---

## 1. Repository Walkthrough (3 min)

**Owner focus:** AppSec + Artifactory

1. Open Lightwell PyPI feed in browser (`LIGHTWELL_PYPI_URL` / customer-ready Secure CDN docs).
2. Pick the demo pin: **`urllib3==1.26.18`** (known CVE surface; Lightwell-eligible once feed validated — swap if customer prefers `cryptography` / `pydantic`).
3. Show: patched artifact available for consume **without source changes**.
4. Point out signing / metadata / security artifacts as available.

**Talk track:** “Same package name and compatible API surface — remediated content behind your existing resolver.”

**Backup:** Screenshots / feed docs under customer materials if the live feed is unreachable.

---

## 2. Artifactory & Python Tooling (5 min)

**Owner focus:** Artifactory Admin

### Artifactory

1. Admin → Repositories → **Remote**
2. Package type: **PyPI**
3. URL → Lightwell Secure CDN / PyPI endpoint
4. Add remote to the **virtual** PyPI used by eng
5. (Optional) Priority / include pattern for Lightwell-eligible packages

Local rehearsal: [integration/artifactory/SETUP.md](integration/artifactory/SETUP.md) + `docker compose up`.

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

1. **Before:** `./scripts/scan-before.sh` — Trivy on vulnerable env / lock — critical CVE visible.
2. **After:** `./scripts/scan-after.sh` — same scan path post-Lightwell resolve — CVE cleared for that component (or show committed sample delta under `artifacts/sample-reports/`).

**Talk track:** “Your scanner. Your gate. Cleaner result — because the binary changed, not the policy engine.”

**Note:** If a version-fingerprint scanner still flags a same-version patched wheel, call out Lens VEX (segment 5) as the noise-reduction proof and use Lightwell’s documented scanner-clean pair when available.

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
