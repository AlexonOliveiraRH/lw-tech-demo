# vulnerable-fastapi

Sample FastAPI service for the Lightwell Python technical demo.

## Why it is “vulnerable”

`sqlparse` is intentionally pinned to **`0.5.5`**.

| Resolve path | Artifact | Trivy |
|--------------|----------|-------|
| Public PyPI / **Python Validated** | `sqlparse-0.5.5` | HIGH CVEs (e.g. CVE-2026-54284 family) |
| **Python Remediated** | `sqlparse-0.5.5+rhlw.1` | Remediated binary (same API) |

## Local (before)

```bash
poetry install
poetry run pytest
poetry run uvicorn app.main:app --reload --port 8000
```

## Lightwell (after)

From repo root (loads `.env` + `/home/dasm/dasmlwsvc.token`):

```bash
export USE_LIGHTWELL=true
./scripts/configure-poetry-source.sh
cd apps/vulnerable-fastapi
poetry lock && poetry install
poetry show sqlparse    # expect 0.5.5+rhlw.1 when remediated wins
poetry run pytest
```

`GET /deps` and `POST /v1/sql/preview` for live narration.
