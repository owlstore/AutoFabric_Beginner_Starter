"""Basic smoke tests — verify app starts and core routes exist."""


def test_app_has_routes(client):
    """App should have registered routes."""
    from app.main import app
    routes = [r.path for r in app.routes]
    assert "/health" in routes
    assert "/projects" in routes


def test_openapi_schema(client):
    """OpenAPI schema should be accessible."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert schema["info"]["title"] == "AutoFabric API"
