# Lightwell Python Focused Technical Demo

**Goal:** demonstrate ease of implementation with Lightwell and the before/after effects — **no application rewrite** — and prove it in **Lens**.

Repo: [dasmlab/lw-tech-demo](https://github.com/dasmlab/lw-tech-demo)

---

## Prerequisites

1. **Lightwell entitlement** on [console.redhat.com](https://console.redhat.com)  
2. Create a Lightwell **service account** → copy `orgId|name` + token  
3. Know where **Lens** is for your tenant (Console → Lightwell → Lens)  
4. Run workflows here **or fork** this repo and enable Actions (GitHub-hosted `ubuntu-latest` by default)

You do **not** need dasmlab secrets or self-hosted runners. Run titles show `@your-github-user` automatically (Remediate also shows the Lightwell username).

---

## What you run (two workflows per ecosystem)

In **Actions** you may see several names. **Use the numbered ones** (`1`/`2` for Python, `J1`/`J2` for Java):

| Workflow | Use? | What it does |
|----------|------|----------------|
| **1 · Scan (vulnerable)** | ✅ Step 1 | Public pins + scanners + **SBOM before** + visual report |
| **2 · Remediate (Lightwell)** | ✅ Step 2 | Lightwell feeds → `+rhlw.1` + **SBOM after** + visual report |
| **J1 · Java Scan (vulnerable)** | ✅ Java step 1 | Spring app on public Maven Central + Trivy + **SBOM before** + visual report |
| **J2 · Java Remediate (Lightwell)** | ✅ Java step 2 | Lightwell Java feeds → `rhlw` builds + **SBOM after** + visual report |
| `z · CI (maintainers)` | ❌ ignore | PR/push smoke test |
| `z · Advanced (composite)` | ❌ ignore | Power-user pipeline |

---

## Steps

### 1 — Scan (no Lightwell login)

1. [Actions → **1 · Scan (vulnerable)**](https://github.com/dasmlab/lw-tech-demo/actions/workflows/01-scan.yml) → **Run workflow** (leave runner = `ubuntu-latest`)
2. When the run is green, open **Summary** → click **Download `scan-before` zip** (or use Artifacts at the bottom)
3. Unzip — files are at the **zip root**:
   - Open **`demo-report-before.html`** in a browser
   - Upload **`sbom-before.cdx.json`** to **Lightwell Lens**

**Notable**

- These three packages are exactly what Lightwell remediates — public builds light up scanners and Lens.

### 2 — Remediate (paste token for this run only)

1. [Actions → **2 · Remediate (Lightwell)**](https://github.com/dasmlab/lw-tech-demo/actions/workflows/02-remediate.yml) → **Run workflow**
2. Required inputs (not stored in this public repo):
   - **lightwell_user** — `orgId|service-account-name` (shape: `11009103|dasmlwsvc`)
   - **lightwell_token** — service-account token from Lightwell Console
   - **runner** — leave `ubuntu-latest` unless you intentionally use self-hosted
3. When the run is green, open **Summary** → click **Download `remediate-proof` zip**, then unzip
4. At the zip root: open **`demo-report-after.html`**, and upload **`sbom-after.cdx.json`** to **Lens** to see the difference

**Notable**

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

## Java (Spring) variant

Same three beats - break it, fix it, prove it - on a Spring app ([apps/vulnerable-spring](apps/vulnerable-spring/)). Lightwell has many more Java remediations than Python, so this run shows **17 libraries** swapped for Lightwell builds.

1. [Actions → **J1 · Java Scan (vulnerable)**](https://github.com/dasmlab/lw-tech-demo/actions/workflows/java-1-scan.yml) → **Run workflow** → download the `java-scan-before` zip → open `demo-report-before.html`, upload `sbom-before.cdx.json` to **Lens**
2. [Actions → **J2 · Java Remediate (Lightwell)**](https://github.com/dasmlab/lw-tech-demo/actions/workflows/java-2-remediate.yml) → same `lightwell_user` + `lightwell_token` as step 2 → download the `java-remediate-proof` zip → open `demo-report-after.html`, upload `sbom-after.cdx.json` to **Lens**

**Notable**

- Same code, same JUnit tests, same pipeline - only `mvn -P lightwell` changes the package source
- Remediated set (Spring 5.3.18, Spring Boot 2.7.18, Spring Security 5.7.11, Logback 1.2.11, commons-beanutils 1.9.4, Avro 1.11.0, jackson-databind 2.13.4, XStream 1.4.18) resolves as `X.Y.Z.rhlw-NNNNN` from **Java Remediated**; the run fails if any of them does not
- Other dependencies come from **Java Validated** when it has them, otherwise Maven Central - the report shows which repository served every jar
- Lens on the before SBOM lists the CVEs with a Lightwell fix available; version-matching scanners (Trivy) keep reporting upstream CVE IDs on `rhlw` builds, so use Lens to compare before and after

---

## Optional

| Item | When |
|------|------|
| [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md) | Fuller step-by-step |
| [docs/HOW_TO_RUN_DEMO_SLIDES.md](docs/HOW_TO_RUN_DEMO_SLIDES.md) | 6-slide “how to run” outline |
| [docs/secrets.md](docs/secrets.md) | Auth / runner / fork notes |
| [sbom/README.md](sbom/README.md) | Lens upload notes |
| [integration/artifactory](integration/artifactory/) | Local Artifactory sandbox |

---

## Secrets

Step 2 takes the token **in the workflow form** so forks stay clean — nothing Lightwell-secret is committed here. Prefer a short-lived token; rotate after the engagement if the run is public.
