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

