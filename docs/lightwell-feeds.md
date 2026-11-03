# Lightwell package feeds (four repos)

Lightwell Console exposes **four** network repositories. This demo kit focuses on the **two Python** feeds; Java is listed for completeness when talking to Artifactory admins.

| Console name | Role | Simple index (Poetry / pip / Pipenv) | Artifactory remote URL |
|--------------|------|--------------------------------------|-------------------------|
| **Python Remediated** | CVE-backported wheels/sdists (`+rhlw.N`), same public version + compatible API | `https://packages.redhat.com/lightwell/python/remediated/simple` | `https://packages.redhat.com/api/pulp-content/lightwell/python/remediated/` |
| **Python Validated** | Broad RH-built/validated catalog (~2400+ packages) — enterprise index instead of raw PyPI | `https://packages.redhat.com/lightwell/python/validated/simple` | `https://packages.redhat.com/api/pulp-content/lightwell/python/validated/` |
| Java Remediated | Same pattern for Maven/Java (out of scope for this Python demo) | _(Console → Java Remediated)_ | _(Console)_ |
| Java Validated / Java | Validated Java catalog (out of scope) | _(Console)_ | _(Console)_ |

## Why both Python remotes matter

```text
Developer / CI
    → Artifactory virtual `pypi-virtual`
        1) remote pypi-lightwell-remediated   (eligible patched packages win)
        2) remote pypi-lightwell-validated    (everything else from RH catalog)
        3) optional public-pypi               (policy-dependent escape hatch)
```

- **Validated alone**: supply-chain provenance / RH-built binaries, but **does not** clear CVEs that need a remediated rebuild (e.g. public `sqlparse==0.5.5` is on validated and still flags in Trivy).
- **Remediated on top**: `sqlparse-0.5.5+rhlw.1` (and peers) — demo “CVE noise eliminated” beat without app rewrite.

Current remediated Python set (verify live before the meeting): `sqlparse`, `PyPDF2`, `tokenizers`.

## Auth (all feeds)

- Username: `<orgId>|<service-account-name>` e.g. `11009103|dasmlwsvc`
- Password: service account token (`LIGHTWELL_TOKEN_FILE` / `LIGHTWELL_PYPI_TOKEN`)
- Nexus tab notes **mTLS** for some paths; Artifactory uses **basic auth** with the same service account.
