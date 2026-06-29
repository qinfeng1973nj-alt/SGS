from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_error_envelope_nested_error_shape():
    # 访问不存在路径，触发统一错误封装（通常 404）
    r = client.get("/__contract_test_not_found__")
    assert r.status_code in (400, 404, 422, 500)

    data = r.json()
    assert isinstance(data, dict)
    assert "error" in data and isinstance(data["error"], dict)

    err = data["error"]
    # v0.2.1 约定：error 下嵌套字段
    for k in ("code", "reason", "message", "path", "trace_id"):
        assert k in err
