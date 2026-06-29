from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz_contract():
    # 兼容已有路由命名：优先 /healthz，不存在则尝试 /health
    r = client.get("/healthz")
    if r.status_code == 404:
        r = client.get("/health")

    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)

    # 宽松契约：至少有可表达状态的字段
    assert any(k in data for k in ("status", "ok", "service"))
