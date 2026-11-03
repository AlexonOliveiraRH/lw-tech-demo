"""Behavioral tests — assert API contract, not CVE presence."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_deps_reports_urllib3() -> None:
    response = client.get("/deps")
    assert response.status_code == 200
    assert "urllib3" in response.json()
    assert response.json()["urllib3"]


def test_echo_preserves_message() -> None:
    response = client.post("/v1/echo", json={"message": "pilot-ready"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "pilot-ready"
    assert payload["urllib3_version"]
