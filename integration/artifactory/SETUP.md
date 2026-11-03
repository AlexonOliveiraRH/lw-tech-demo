# Artifactory sandbox — remote PyPI → Lightwell

Rehearsal path for **segment 2** (5 min). Prefer screen-sharing the customer’s Artifactory when available; this Compose stack is the laptop backup.

## Start

```bash
cd integration/artifactory
mkdir -p data
docker compose up -d
# Wait until ping succeeds (first boot can take 1–3 minutes)
curl -sf http://localhost:8082/artifactory/api/system/ping
```

UI: http://localhost:8082/ui/  
Default credentials are shown on first-boot / image docs (commonly `admin` / `password` — **change immediately**).

## Create remote (UI — matches live talk track)

1. **Administration** → **Repositories** → **Add Repositories** → **Remote Repository**
2. Package type: **PyPI**
3. Repository key: `pypi-lightwell-remote`
4. URL: value of `LIGHTWELL_PYPI_URL` (Lightwell Secure CDN / PyPI endpoint)
5. Authentication: as provided for the feed (`LIGHTWELL_PYPI_TOKEN` / basic)
6. Save

## Attach to virtual used by engineering

1. Create or edit virtual PyPI repo, e.g. `pypi-virtual`
2. Include:
   - `pypi-lightwell-remote` (**first** / highest priority for eligible packages)
   - optional public `pypi-remote` fallback for non-eligible packages
3. (Optional) Include patterns limiting Lightwell remote to known eligible package names

Simple index URL for Poetry / pip:

```text
http://localhost:8082/artifactory/api/pypi/pypi-virtual/simple
```

Set locally:

```bash
export ARTIFACTORY_URL=http://localhost:8082/artifactory
export PYPI_INDEX_URL=http://localhost:8082/artifactory/api/pypi/pypi-virtual/simple
export ARTIFACTORY_USER=admin
export ARTIFACTORY_PASSWORD='<changed-password>'
export USE_LIGHTWELL=true
```

## REST sketch (optional automation)

Exact endpoints depend on Artifactory version. Prefer UI during the live demo; use REST only for prep automation.

## Stop

```bash
docker compose down
# wipe local data if needed:
# rm -rf data
```

## Backup if Artifactory blocked

Use committed screenshots / sample reports under `artifacts/sample-reports/` and configure Poetry **directly** at `LIGHTWELL_PYPI_URL` for the build segment so the remediated resolve still works.
