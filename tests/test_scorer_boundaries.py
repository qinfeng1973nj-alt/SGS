from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_grade_preview_empty_text_returns_422():
    resp = client.post("/grade/preview", json={"student_text": ""})
    assert resp.status_code == 422


def test_grade_preview_overlong_text_returns_422():
    long_text = "A" * 20001
    resp = client.post("/grade/preview", json={"student_text": long_text})
    assert resp.status_code == 422


def test_grade_preview_invalid_field_type_returns_422():
    resp = client.post("/grade/preview", json={"student_text": 12345})
    assert resp.status_code == 422
