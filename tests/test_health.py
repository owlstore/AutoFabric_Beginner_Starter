"""Test the health endpoint."""


def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["service"] == "AutoFabric API"
    assert "version" in data


def test_health_version_format(client):
    resp = client.get("/health")
    version = resp.json()["version"]
    parts = version.split(".")
    assert len(parts) >= 2, "version should be semver-ish"
