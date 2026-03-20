from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


def test_parse_goal():
    response = client.post("/goals/parse", json={"raw_input": "Ubuntu with Docker and Git"})
    assert response.status_code == 200
    data = response.json()
    assert data["goal_type"] == "environment_build"
    assert "docker" in data["packages"]
