"""Minimal FastAPI gateway used in the Lightwell Part 2 remediation demo."""

from __future__ import annotations

import urllib3
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Acme Payments Gateway (demo)",
    description=(
        "Sample high-throughput API surface for Lightwell SSA demos. "
        "Depends on a pinned urllib3; remediation is via Lightwell-patched wheels, "
        "not application rewrites."
    ),
    version="0.1.0",
)


class EchoRequest(BaseModel):
    message: str


class EchoResponse(BaseModel):
    message: str
    urllib3_version: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/deps")
def deps() -> dict[str, str]:
    """Expose resolved urllib3 version for live demo narration."""
    return {"urllib3": urllib3.__version__}


@app.post("/v1/echo", response_model=EchoResponse)
def echo(body: EchoRequest) -> EchoResponse:
    """Business-looking route that keeps tests green across remediated wheels."""
    return EchoResponse(message=body.message, urllib3_version=urllib3.__version__)
