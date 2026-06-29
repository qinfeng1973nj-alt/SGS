from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_validation_error_envelope_shape():
    # 用一个更稳定的触发方式：给 /score 传缺失必填字段的 payload
    r = client.post("/score", json={"bad": "payload"})
    assert r.status_code in (400, 422)

    data = r.json()
    assert isinstance(data, dict)
    assert "error" in data
    assert isinstance(data["error"], dict)

    err = data["error"]
    for k in ["code", "reason", "message", "path", "trace_id"]:
        assert k in err
