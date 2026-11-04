"""Acme Payments Gateway — Lightwell Part 2 sales demo app.

Intentionally pins the three packages currently on Lightwell Python Remediated:
sqlparse, PyPDF2, tokenizers. Narrate /deps before vs after remediate.
"""

from __future__ import annotations

import importlib.metadata as metadata
from io import BytesIO

import sqlparse
from fastapi import FastAPI
from pydantic import BaseModel
from PyPDF2 import PdfReader, PdfWriter
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace

app = FastAPI(
    title="Acme Payments Gateway (demo)",
    description=(
        "Fintech-style API sample for Lightwell SSA demos. "
        "Pins sqlparse, PyPDF2, and tokenizers at public vulnerable versions. "
        "Remediation = Lightwell Python Remediated (+rhlw.1) for those three; "
        "everything else resolves from Lightwell Python Validated."
    ),
    version="0.1.0",
)


def _pkg_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "unknown"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/deps")
def deps() -> dict[str, object]:
    """Call this out on screen: before = plain versions; after = +rhlw.1 on remediated set."""
    return {
        "remediated_set": {
            "sqlparse": _pkg_version("sqlparse"),
            "PyPDF2": _pkg_version("PyPDF2"),
            "tokenizers": _pkg_version("tokenizers"),
        },
        "feeds": {
            "note": (
                "After remediate: remediated_set comes from Lightwell Python Remediated; "
                "FastAPI/httpx/etc. come from Lightwell Python Validated."
            )
        },
    }


class EchoRequest(BaseModel):
    message: str


class EchoResponse(BaseModel):
    message: str
    sqlparse_version: str


@app.post("/v1/echo", response_model=EchoResponse)
def echo(body: EchoRequest) -> EchoResponse:
    return EchoResponse(message=body.message, sqlparse_version=sqlparse.__version__)


class SqlPreviewRequest(BaseModel):
    sql: str


class SqlPreviewResponse(BaseModel):
    statements: int
    sqlparse_version: str


@app.post("/v1/sql/preview", response_model=SqlPreviewResponse)
def sql_preview(body: SqlPreviewRequest) -> SqlPreviewResponse:
    statements = sqlparse.split(body.sql)
    return SqlPreviewResponse(
        statements=len(statements),
        sqlparse_version=_pkg_version("sqlparse"),
    )


@app.get("/v1/pdf/smoke")
def pdf_smoke() -> dict[str, object]:
    """Touch PyPDF2 so the pin is exercised (same API on +rhlw.1)."""
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buf = BytesIO()
    writer.write(buf)
    buf.seek(0)
    reader = PdfReader(buf)
    return {
        "pages": len(reader.pages),
        "PyPDF2_version": _pkg_version("PyPDF2"),
    }


@app.get("/v1/tokenize/smoke")
def tokenize_smoke() -> dict[str, object]:
    """Touch tokenizers so the pin is exercised (same API on +rhlw.1)."""
    tok = Tokenizer(WordLevel(unk_token="[UNK]"))
    tok.pre_tokenizer = Whitespace()
    # Minimal vocab so encode works without training noise
    tok.add_tokens(["hello", "lightwell", "demo"])
    encoded = tok.encode("hello lightwell demo")
    return {
        "tokens": encoded.tokens,
        "tokenizers_version": _pkg_version("tokenizers"),
    }
