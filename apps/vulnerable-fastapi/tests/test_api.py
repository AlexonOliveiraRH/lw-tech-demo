"""Behavioral tests — API contract stays green on public and +rhlw.1 wheels."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_deps_lists_remediated_set() -> None:
    response = client.get("/deps")
    assert response.status_code == 200
    payload = response.json()
    rem = payload["remediated_set"]
    assert rem["sqlparse"]
    assert rem["PyPDF2"]
    assert rem["tokenizers"]


def test_echo_preserves_message() -> None:
    response = client.post("/v1/echo", json={"message": "pilot-ready"})
    assert response.status_code == 200
    assert response.json()["message"] == "pilot-ready"


def test_sql_preview_splits_statements() -> None:
    response = client.post("/v1/sql/preview", json={"sql": "SELECT 1; SELECT 2"})
    assert response.status_code == 200
    assert response.json()["statements"] == 2


def test_pdf_smoke() -> None:
    response = client.get("/v1/pdf/smoke")
    assert response.status_code == 200
    assert response.json()["pages"] == 1


def test_tokenize_smoke() -> None:
    response = client.get("/v1/tokenize/smoke")
    assert response.status_code == 200
    assert "hello" in response.json()["tokens"]
