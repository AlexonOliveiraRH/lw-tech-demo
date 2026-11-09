# Lightwell Technical Demo

**Goal:** demonstrate ease of implementation with Lightwell and the before/after effects — **no application rewrite** — and prove it in **Lens**.

---

## Table of Self-Service Demos

All you need is your **Lightwell service account** (for the Remediate step). Each row is **one** Actions workflow — pick **step = scan** then **step = remediate**. Ignore anything named `z · …`.

| Name / Target | Link to workflow | Description |
|---------------|------------------|---------------|
| **Python with Trivy** | [Demo · Python · Trivy](https://github.com/dasmlab/lw-tech-demo/actions/workflows/demo-python-trivy.yml) | FastAPI/Poetry app on public pins, then Lightwell PyPI Remediated + Validated. Trivy report + CycloneDX SBOM before/after for Lens. |
| **Java (Maven) with Trivy** | [Demo · Java · Maven · Trivy](https://github.com/dasmlab/lw-tech-demo/actions/workflows/demo-java-maven-trivy.yml) | Spring/Maven app on Maven Central, then Lightwell Java feeds (`rhlw` builds). Same Trivy + SBOM before/after pattern. |
| Python with JFrog / Xray | — | Planned — same before/after beats with Xray as the scanner surface. |
| Java with SonarQube / Nexus | — | Planned — same before/after beats with Sonar + Nexus as the integration surface. |

---

## Prerequisites

1. **Lightwell entitlement** on [console.redhat.com](https://console.redhat.com)  
2. Create a Lightwell **service account** → copy `orgId|name` + token  
3. Know where **Lens** is for your tenant (Console → Lightwell → Lens)  
4. Run workflows here **or fork** this repo and enable Actions (GitHub-hosted `ubuntu-latest` by default)

You do **not** need dasmlab secrets or self-hosted runners. Run titles show `@your-github-user` automatically.

---

## Steps

Same for every demo above. Open the workflow link → **Run workflow** → choose the step.

### 1 — Scan (no Lightwell login)

1. Open the demo workflow → **Run workflow** → **step = `scan`** (leave runner = `ubuntu-latest`)
2. When the run is green, open **Summary** → click **Download … zip** (or use Artifacts at the bottom)
3. Unzip — files are at the **zip root**:
   - Open **`demo-report-before.html`** in a browser
   - Upload **`sbom-before.cdx.json`** to **Lightwell Lens**

**Notable**

- Public builds light up scanners and Lens — these are the packages Lightwell remediates.

### 2 — Remediate (paste token for this run only)

1. Same demo workflow → **Run workflow** → **step = `remediate`**
2. Required inputs (not stored in this public repo):
   - **lightwell_user** — `orgId|service-account-name` (shape: `11009103|dasmlwsvc`)
   - **lightwell_token** — service-account token from Lightwell Console
   - **runner** — leave `ubuntu-latest` unless you intentionally use self-hosted
3. When the run is green, open **Summary** → click **Download … zip**, then unzip
4. At the zip root: open **`demo-report-after.html`**, and upload **`sbom-after.cdx.json`** to **Lens** to see the difference

**Notable**

- Builds come from the **Lightwell Network** (Python `+rhlw.1`, Java `*.rhlw-*`)
- Public CVE records no longer bind the same way in Lens  
- Tests pass — **no application rewrite**

---

## Pins

### Python (Trivy demo)

| Package | Step 1 (public) | Step 2 (Lightwell) |
|---------|-----------------|--------------------|
| sqlparse | `0.5.5` | `0.5.5+rhlw.1` · Remediated |
| PyPDF2 | `3.0.1` | `3.0.1+rhlw.1` · Remediated |
| tokenizers | `0.23.1` | `0.23.1+rhlw.1` · Remediated |
| FastAPI / httpx / … | public | **Validated** |

Console has four repos; this demo uses the **two Python** feeds. Details: [docs/lightwell-feeds.md](docs/lightwell-feeds.md)

### Java (Maven · Trivy demo)

Same three beats on a Spring app ([apps/vulnerable-spring](apps/vulnerable-spring/)). Lightwell has many more Java remediations than Python, so this run shows **17 libraries** swapped for Lightwell builds.

**Notable**

- Same code, same JUnit tests, same pipeline — only `mvn -P lightwell` changes the package source
- Remediated set (Spring 5.3.18, Spring Boot 2.7.18, Spring Security 5.7.11, Logback 1.2.11, commons-beanutils 1.9.4, Avro 1.11.0, jackson-databind 2.13.4, XStream 1.4.18) resolves as `X.Y.Z.rhlw-NNNNN` from **Java Remediated**; the run fails if any of them does not
- Other dependencies come from **Java Validated** when it has them, otherwise Maven Central — the report shows which repository served every jar
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
