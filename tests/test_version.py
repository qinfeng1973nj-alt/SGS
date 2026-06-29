from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_version_contract():
    r = client.get("/version")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)

    # 常见版本字段，至少一个
    assert any(k in data for k in ("version", "app_version", "build", "commit"))
