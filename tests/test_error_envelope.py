import json
from pathlib import Path

from jsonschema import Draft202012Validator


def load_error_schema():
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "error_envelope.schema.json"
    with schema_path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def test_error_envelope_schema_validation(client):
    schema = load_error_schema()
    validator = Draft202012Validator(schema)

    # 用非法请求体触发错误响应（避免命中 FastAPI 默认 404 格式）
    resp = client.post("/score", json={})
    assert resp.status_code in (400, 422, 500)

    payload = resp.json()
    validator.validate(payload)
