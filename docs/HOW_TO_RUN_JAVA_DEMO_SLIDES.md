# How to Run the Java Demo — 6 slides

Java (Spring/Maven) companion to [HOW_TO_RUN_DEMO_SLIDES.md](HOW_TO_RUN_DEMO_SLIDES.md). Same six beats, same screenshot callouts, with the Java workflows **J1** / **J2**.

Keep every slide to **one idea**. Bracketed lines = screenshot callouts.

Repo: https://github.com/dasmlab/lw-tech-demo  
Console: https://console.redhat.com (Lightwell → service account + Lens)

**Wording difference from the Python deck:** Python only changes where pip pulls packages from. Maven matches versions exactly and Lightwell Java builds carry their own version (`5.3.18.rhlw-00010`), so the build file also selects those versions. Application code and tests stay the same, but the build file changes, so say **"no application code change"**, not "no code change".

---

## Slide 1 — What this demo proves

**Title:** Same Spring app. Switch the Maven profile. Fault → fixed.

**One line under the title**

No application code change — one Maven profile selects the Lightwell builds and feeds.

**The story (four beats, left → right)**

| 1 · App | 2 · Scan | 3 · Point at Lightwell | 4 · Build again |
|---------|----------|------------------------|-----------------|
| One Spring Boot app | Public Maven Central pins | `mvn -P lightwell` = Lightwell Java feeds + `rhlw` versions | Same pipeline, same tests |
| Java code unchanged | See the fault (Trivy + Lens findings) | Build file, not a refactor | Fault remediated (`rhlw` builds) |

**Footer line**

Scan → switch the Maven profile → rebuild → prove it (report + Lens SBOM)

**Screenshot:** none required — this is the narrative slide  
**Layout hint:** one horizontal flow, not three feature columns

---

## Slide 2 — Setup (3 steps)

**Title:** Live Action Demo — Java Setup

**Subtitle:** Three steps. Then two clicks.

| 1 · GitHub | 2 · Lightwell Console | 3 · Run the demo |
|------------|------------------------|------------------|
| Open the repo and sign in with your **GitHub** ID | Sign in to **console.redhat.com** → create/get Lightwell **service account** (`orgId\|name` + token) | Actions → **J1 · Java Scan** then **J2 · Java Remediate** (2 clicks for before / after) |

The same service account works for the Python and Java demos.

**Repo:** https://github.com/dasmlab/lw-tech-demo  

**After the runs:** download the flat artifacts (report + SBOM) → open the HTML in-browser → upload the SBOM to **Lens**  
https://console.redhat.com/lightwell/lens

**Screenshot:** repo Actions sidebar with **J1** / **J2** · Console SA · Lens URL

---

## Slide 3 — Before: scan the app

**Title:** Step 1 — Java Scan (public Maven Central)

1. Actions → **J1 · Java Scan (vulnerable)** → Run  
2. Download `java-scan-before` → unzip (flat)  
3. Open **`demo-report-before.html`**  
4. Upload **`sbom-before.cdx.json`** to Lens  

**Look for:** status `FINDINGS` · 17 libraries served by Maven Central (Spring, Spring Boot, Spring Security, Logback, jackson-databind, XStream, Avro, commons-beanutils) · Trivy HIGH/CRITICAL findings · Lens lists the CVEs with a Lightwell fix available

**Screenshot:** FINDINGS report · Lens hooks on before SBOM

---

## Slide 4 — The only change

**Title:** Point the build at Lightwell (not the app)

- Java code and tests: **unchanged**  
- `pom.xml` profile **`lightwell`**: switches 17 library versions to their `rhlw` builds and adds the feeds **Lightwell Java Remediated** (+ **Validated**)  
- Same idea as flipping an Artifactory / Maven remote, plus the version switch because Maven matches versions exactly

**Screenshot (optional):** the `lightwell` profile in `apps/vulnerable-spring/pom.xml` (version properties `5.3.18` → `5.3.18.rhlw-00010`)

---

## Slide 5 — After: build again

**Title:** Step 2 — Java Remediate (Lightwell sources)

1. Actions → **J2 · Java Remediate (Lightwell)** → paste SA user + token → Run  
2. Download `java-remediate-proof` → unzip  
3. Open **`demo-report-after.html`**  
4. Upload **`sbom-after.cdx.json`** to Lens  

**Look for:** status `PASS` · 17 libraries at `X.Y.Z.rhlw-NNNNN` served by **Lightwell Java Remediated** · tests green · before/after difference in Lens

**Speaker note:** Trivy still lists upstream CVE IDs on the `rhlw` jars because it matches the upstream version inside them. The proof is the "Served by" column plus Lens, not the Trivy count.

**Screenshot:** PASS report with `rhlw` versions and "Served by" · Lens after SBOM

---

## Slide 6 — That’s the demo

**Title:** Fault in → Maven profile → fault out

- Same application code, same tests, same CI shape  
- Remediation from the **package source**, selected by one build profile  
- Proof: **demo-report.html** (who served each jar) + **Lens SBOM** (before and after)

**Ask:** Who owns the Maven remotes / Artifactory? Which Java service do we pilot first?

**Screenshot:** Actions sidebar — **J1** and **J2**
