"""Minimal FastAPI gateway used in the Lightwell Part 2 remediation demo."""

from __future__ import annotations

import sqlparse
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Acme Payments Gateway (demo)",
    description=(
        "Sample high-throughput API surface for Lightwell SSA demos. "
        "Depends on a pinned sqlparse; remediation is via Lightwell-patched wheels, "
        "not application rewrites."
    ),
    version="0.1.0",
)


class EchoRequest(BaseModel):
    message: str


class EchoResponse(BaseModel):
    message: str
    sqlparse_version: str


class SqlPreviewRequest(BaseModel):
    sql: str


class SqlPreviewResponse(BaseModel):
    statements: int
    sqlparse_version: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/deps")
def deps() -> dict[str, str]:
    """Expose resolved sqlparse version for live demo narration."""
    return {"sqlparse": sqlparse.__version__}


@app.post("/v1/echo", response_model=EchoResponse)
def echo(body: EchoRequest) -> EchoResponse:
    """Business-looking route that keeps tests green across remediated wheels."""
    return EchoResponse(message=body.message, sqlparse_version=sqlparse.__version__)


@app.post("/v1/sql/preview", response_model=SqlPreviewResponse)
def sql_preview(body: SqlPreviewRequest) -> SqlPreviewResponse:
    """Light use of sqlparse — same call works on public and +rhlw.1 wheels."""
    statements = sqlparse.split(body.sql)
    return SqlPreviewResponse(
        statements=len(statements),
        sqlparse_version=sqlparse.__version__,
    )
