import importlib

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_score_success(client):
    resp = client.post("/score", json={"text": "这是用于成功路径的测试文本"})
    assert resp.status_code == 200
    data = resp.json()
    assert "score" in data
    assert "channel" in data


def test_score_missing_text(client):
    resp = client.post("/score", json={})
    assert resp.status_code in (400, 422)


def test_score_text_type_error(client):
    resp = client.post("/score", json={"text": 123})
    assert resp.status_code in (400, 422)


def test_score_llm_enabled_but_no_key_fallback_rule(monkeypatch):
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    import app.core.config as config
    import app.services.scorer as scorer

    importlib.reload(config)
    importlib.reload(scorer)

    result = scorer.score_text("这是一个用于触发回退逻辑的测试文本")
    assert result["channel"] == "rule"
    assert "score" in result


def test_score_llm_enabled_with_key_hit_llm(monkeypatch):
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.setenv("LLM_API_KEY", "dummy-key")

    import app.core.config as config
    import app.services.scorer as scorer

    importlib.reload(config)
    importlib.reload(scorer)

    result = scorer.score_text("这是一个用于触发LLM通道的测试文本")
    assert result["channel"] == "llm"
    assert "score" in result


def test_score_llm_timeout_fallback_rule(client, monkeypatch):
    import app.services.scorer as scorer
    from app.services import llm_client
    from app.core.config import settings

    # 1) 强制开启 LLM 分支
    monkeypatch.setattr(settings, "ENABLE_LLM", True)
    monkeypatch.setattr(settings, "LLM_API_KEY", "fake-key")

    # 2) 造一个会抛超时异常的假函数
    def mock_timeout(text: str, api_key: str):
        raise llm_client.LLMTimeoutError("request timeout")

    # 3) 关键：patch scorer 模块里的 score_with_llm（不是 llm_client 里的）
    monkeypatch.setattr(scorer, "score_with_llm", mock_timeout)

    # 4) 调接口，断言回退 rule
    resp = client.post("/score", json={"text": "timeout case"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["channel"] == "rule"
    assert data["reason"] == "rule_based"


def test_score_llm_auth_error_fallback_rule(client, monkeypatch):
    import app.services.scorer as scorer
    from app.services import llm_client
    from app.core.config import settings

    # 1) 强制开启 LLM 分支
    monkeypatch.setattr(settings, "ENABLE_LLM", True)
    monkeypatch.setattr(settings, "LLM_API_KEY", "bad-key")

    # 2) 造一个会抛鉴权异常的假函数
    def mock_auth_error(text: str, api_key: str):
        raise llm_client.LLMAuthError("invalid api key")

    # 3) 关键：patch scorer 模块里的 score_with_llm（不是 llm_client 里的）
    monkeypatch.setattr(scorer, "score_with_llm", mock_auth_error)

    # 4) 调接口，断言回退 rule
    resp = client.post("/score", json={"text": "auth fail case"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["channel"] == "rule"
    assert data["reason"] == "rule_based"
