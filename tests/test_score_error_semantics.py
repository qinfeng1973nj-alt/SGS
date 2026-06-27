from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_score_422_when_text_too_short():
    resp = client.post("/score", json={"text": "short"})
    assert resp.status_code == 422


def test_score_422_when_text_too_long():
    long_text = "a" * 20001
    resp = client.post("/score", json={"text": long_text})
    assert resp.status_code == 422


def test_score_400_when_missing_text_field():
    resp = client.post("/score", json={})
    assert resp.status_code == 400


def test_score_400_when_invalid_type():
    resp = client.post("/score", json={"text": 123})
    assert resp.status_code == 400


def test_score_unknown_exception_maps_to_internal_error(monkeypatch):
    def _boom(_text):
        raise RuntimeError("boom")

    # main.py 里是 from app.services.scorer import score_text
    # 所以 patch app.main.score_text
    monkeypatch.setattr("app.main.score_text", _boom)

    resp = client.post("/score", json={"text": "x" * 30})
    assert resp.status_code == 500

    body = resp.json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert body["error"]["reason"] == "INTERNAL_ERROR"
    assert body["error"]["details"]["reason"] == "RuntimeError"
