import importlib
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


# -----------------------------
# 基础接口行为
# -----------------------------
def test_score_success(client):
    resp = client.post("/score", json={"text": "这是用于成功路径的测试文本，用于满足最小长度要求。"})
    assert resp.status_code == 200
    data = resp.json()
    assert "score" in data
    assert "channel" in data


def test_score_missing_text(client):
    resp = client.post("/score", json={})
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["reason"] == "MISSING_FIELD"


def test_score_text_type_error(client):
    resp = client.post("/score", json={"text": 123})
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["reason"] == "INVALID_TYPE"


def test_score_response_has_request_id(client):
    resp = client.post(
        "/score",
        json={"text": "hello request id, this sentence is definitely long enough."},
    )
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    assert resp.headers["X-Request-ID"]


# -----------------------------
# LLM 开关与回退逻辑（纯单测，不打外网）
# -----------------------------
def test_score_llm_enabled_but_no_key_fallback_rule(monkeypatch):
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    import app.core.config as config
    import app.services.scorer as scorer

    importlib.reload(config)
    importlib.reload(scorer)

    result = scorer.score_text("这是一个用于触发回退逻辑的测试文本，长度满足要求。")
    assert result["channel"] == "rule"
    assert "score" in result


def test_score_llm_enabled_with_key_hit_llm(monkeypatch):
    """
    不依赖真实 API Key，不调用外部服务，直接 mock scorer.score_with_llm。
    """
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.setenv("LLM_API_KEY", "dummy-key")

    import app.core.config as config
    import app.services.scorer as scorer

    importlib.reload(config)
    importlib.reload(scorer)

    def mock_score_with_llm(*args, **kwargs):
        return {
            "score": 91,
            "level": "A",
            "feedback": "mocked llm response",
            "channel": "llm",
            "reason": "llm_based",
        }

    monkeypatch.setattr(scorer, "score_with_llm", mock_score_with_llm)

    result = scorer.score_text("这是一个用于触发LLM通道的测试文本，长度满足要求。")
    assert result["channel"] == "llm"
    assert "score" in result


def test_score_llm_timeout_fallback_rule(client, monkeypatch):
    import app.services.scorer as scorer
    from app.services import llm_client
    from app.core.config import settings

    monkeypatch.setattr(settings, "ENABLE_LLM", True)
    monkeypatch.setattr(settings, "LLM_API_KEY", "fake-key")

    def mock_timeout(*args, **kwargs):
        raise llm_client.LLMTimeoutError("request timeout")

    monkeypatch.setattr(scorer, "score_with_llm", mock_timeout)

    resp = client.post(
        "/score",
        json={"text": "timeout case text is intentionally longer than twenty chars."},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["channel"] == "rule"
    assert data.get("reason") in ("rule_based", "fallback_rule", "llm_timeout_fallback")


def test_score_llm_auth_error_fallback_rule(client, monkeypatch):
    import app.services.scorer as scorer
    from app.services import llm_client
    from app.core.config import settings

    monkeypatch.setattr(settings, "ENABLE_LLM", True)
    monkeypatch.setattr(settings, "LLM_API_KEY", "bad-key")

    def mock_auth_error(*args, **kwargs):
        raise llm_client.LLMAuthError("invalid api key")

    monkeypatch.setattr(scorer, "score_with_llm", mock_auth_error)

    resp = client.post(
        "/score",
        json={"text": "auth fail case text is intentionally longer than twenty chars."},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["channel"] == "rule"
    assert data.get("reason") in ("rule_based", "fallback_rule", "llm_auth_fallback")


def test_score_unknown_llm_error_should_not_fallback(client, monkeypatch):
    """
    未知异常不应被吞掉回退为 rule，应该返回 500。
    """
    import app.services.scorer as scorer
    from app.core.config import settings

    class UnknownLLMError(Exception):
        pass

    def raise_unknown(*args, **kwargs):
        raise UnknownLLMError("boom")

    monkeypatch.setattr(settings, "ENABLE_LLM", True)
    monkeypatch.setattr(settings, "LLM_API_KEY", "dummy-key")
    monkeypatch.setattr(scorer, "score_with_llm", raise_unknown)

    client_no_raise = TestClient(app, raise_server_exceptions=False)
    resp = client_no_raise.post(
        "/score",
        json={"text": "trigger unknown error with enough length for validation pass"},
    )
    assert resp.status_code == 500
    data = resp.json()
    assert data["error"]["code"] == "INTERNAL_ERROR"


# -----------------------------
# text 边界覆盖（按新语义）
# -----------------------------
def test_score_text_len_20_boundary(client):
    text = "测" * 20
    resp = client.post("/score", json={"text": text})
    assert resp.status_code == 200


def test_score_text_len_20000_boundary(client):
    text = "测" * 20000
    resp = client.post("/score", json={"text": text})
    assert resp.status_code == 200


def test_score_text_over_limit_current_behavior(client):
    text = "测" * 20001
    resp = client.post("/score", json={"text": text})
    # 新实现：超长返回 422
    assert resp.status_code == 422
    data = resp.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["reason"] == "TEXT_TOO_LONG"


def test_score_text_null(client):
    resp = client.post("/score", json={"text": None})
    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["reason"] == "INVALID_TYPE"
