"""Behavioral tests — assert API contract, not CVE presence."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_deps_reports_sqlparse() -> None:
    response = client.get("/deps")
    assert response.status_code == 200
    assert "sqlparse" in response.json()
    assert response.json()["sqlparse"]


def test_echo_preserves_message() -> None:
    response = client.post("/v1/echo", json={"message": "pilot-ready"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "pilot-ready"
    assert payload["sqlparse_version"]


def test_sql_preview_splits_statements() -> None:
    response = client.post(
        "/v1/sql/preview",
        json={"sql": "SELECT 1; SELECT 2"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["statements"] == 2
    assert payload["sqlparse_version"]
