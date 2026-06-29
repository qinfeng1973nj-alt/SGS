from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_version_ok():
    r = client.get("/version")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "version" in data
    assert "commit" in data
