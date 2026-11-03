# Nexus (optional)

Lightwell Console → **Nexus** tab (Python Remediated example):

- Remote URL: `https://packages.redhat.com/lightwell/python/remediated/`
- Auth note in Console: **mTLS client certificates** (not the same basic-auth path as Artifactory/Poetry).

## Local spin-up

```bash
cd integration/nexus
mkdir -p data
docker compose up -d
# Initial admin password:
docker exec lw-demo-nexus cat /nexus-data/admin.password
```

UI: http://localhost:8081

Create a **PyPI (proxy)** repo pointing at remediated, and a second proxy for validated, then a group repo — same layering story as Artifactory.

## Demo guidance

- Show the Console Nexus snippet for completeness.
- Do **not** block the 20-minute clock on mTLS if certs are not provisioned; fall back to Artifactory (basic auth + service account) as the working integration.
