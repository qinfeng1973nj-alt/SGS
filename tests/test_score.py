from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_score_success():
    resp = client.post("/score", json={"text": "这是用于成功路径的测试文本"})
    assert resp.status_code == 200
    data = resp.json()
    assert "score" in data
    assert "channel" in data


def test_score_missing_text():
    resp = client.post("/score", json={})
    # 按你当前契约，缺失字段通常是 422（FastAPI/Pydantic）
    assert resp.status_code in (400, 422)


def test_score_text_type_error():
    resp = client.post("/score", json={"text": 123})
    assert resp.status_code in (400, 422)


def test_score_llm_enabled_but_no_key_fallback_rule(monkeypatch):
    # 开启 LLM 但不给 key，期望回退 rule
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    import importlib
    import app.core.config as config
    import app.services.scorer as scorer

    importlib.reload(config)
    importlib.reload(scorer)

    result = scorer.score_text("这是一个用于触发回退逻辑的测试文本")
    assert result["channel"] == "rule"
    assert "score" in result


def test_score_llm_enabled_with_key_hit_llm(monkeypatch):
    # 开启 LLM，且提供 key，期望走 llm 通道
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.setenv("LLM_API_KEY", "dummy-key")

    import importlib
    import app.core.config as config
    import app.services.scorer as scorer

    # 先重载 config，再重载 scorer，确保 scorer 使用新 settings
    importlib.reload(config)
    importlib.reload(scorer)

    result = scorer.score_text("这是一个用于触发LLM通道的测试文本")
    assert result["channel"] == "llm"
    assert "score" in result
