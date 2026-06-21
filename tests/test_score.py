from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_score_success():
    payload = {"text": "客户有稳定收入，过往履约良好，无明显违约记录。"}
    resp = client.post("/score", json=payload)
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)


def test_score_missing_text():
    resp = client.post("/score", json={})
    assert resp.status_code == 422


def test_score_text_wrong_type():
    resp = client.post("/score", json={"text": 123})
    assert resp.status_code == 422


def test_score_llm_enabled_but_no_key_fallback_rule(monkeypatch):
    # 开启 LLM，但不给 key，期望自动回退到 rule
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    # 关键：重载 scorer 模块，让 settings 读取到新环境变量
    import importlib
    import app.services.scorer as scorer
    importlib.reload(scorer)

    result = scorer.score_text("这是一个用于触发回退逻辑的测试文本")
    assert result["channel"] == "rule"
    assert "score" in result
