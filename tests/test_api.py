from fastapi.testclient import TestClient

from app.main import app


def test_status_and_protected_simulation() -> None:
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        status = client.get("/api/status")
        assert status.status_code == 200
        denied = client.post("/api/simulate", json={"distance_cm": 40})
        assert denied.status_code == 401
        accepted = client.post("/api/simulate", json={"distance_cm": 40}, headers={"X-API-Key": "doorsense-local-demo"})
        assert accepted.status_code == 200
        assert accepted.json()["state"] == "open"
