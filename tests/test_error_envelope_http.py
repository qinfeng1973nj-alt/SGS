from fastapi.testclient import TestClient


def test_404_should_return_error_envelope(client: TestClient):
    resp = client.get("/__route_not_found__")
    assert resp.status_code == 404

    data = resp.json()
    assert "error" in data

    err = data["error"]
    assert err["code"] == "HTTP_ERROR"
    assert err["reason"] == "NOT_FOUND"
    assert err["path"] == "/__route_not_found__"
    assert "trace_id" in err
    assert isinstance(err["trace_id"], str)
    assert err["trace_id"] != ""


def test_score_missing_text_should_return_error_envelope(client: TestClient):
    # 触发 /score 请求体验证错误（缺少 text）
    resp = client.post("/score", json={})
    assert resp.status_code == 400

    data = resp.json()
    assert "error" in data

    err = data["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert err["reason"] == "MISSING_FIELD"
    assert err["message"] == "text is required"
    assert err["path"] == "/score"
    assert "trace_id" in err
    assert isinstance(err["trace_id"], str)
    assert err["trace_id"] != ""
