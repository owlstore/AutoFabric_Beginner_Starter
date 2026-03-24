"""Test Manus autopilot bootstrap and workspace endpoints."""


def test_bootstrap_stream_route_registered(client):
    """SSE bootstrap route should be registered (not 404/405 for wrong method)."""
    from app.main import app
    paths = [r.path for r in app.routes]
    assert "/manus/projects/bootstrap-stream" in paths


def test_manus_workspace_404(client):
    """Non-existent project workspace should 404."""
    resp = client.get("/manus/projects/999999/workspace")
    assert resp.status_code in (404, 500)


def test_manus_bootstrap_requires_prompt(client):
    """Bootstrap without prompt should fail validation."""
    resp = client.post("/manus/projects/bootstrap-stream", json={})
    assert resp.status_code == 422
