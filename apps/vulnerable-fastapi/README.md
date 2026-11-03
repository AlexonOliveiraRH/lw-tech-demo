# vulnerable-fastapi

Sample FastAPI service for the Lightwell Part 2 demo.

## Why it is “vulnerable”

`urllib3` is intentionally pinned to **`1.26.18`** so Trivy (and similar scanners) surface CVE risk on the public PyPI path. Lightwell supplies a remediated artifact at a compatible version/API so Poetry resolve + pytest stay green without rewriting application code.

## Local

```bash
poetry install
poetry run pytest
poetry run uvicorn app.main:app --reload --port 8000
```

## Lightwell / Artifactory path

From repo root:

```bash
export USE_LIGHTWELL=true
export PYPI_INDEX_URL="https://<artifactory>/artifactory/api/pypi/<virtual>/simple"
./scripts/configure-poetry-source.sh
cd apps/vulnerable-fastapi
poetry lock && poetry install
poetry run pytest
```

Inspect resolved version: `GET /deps` or `poetry show urllib3`.
