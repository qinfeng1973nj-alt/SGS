import json
from pathlib import Path

from jsonschema import Draft202012Validator


def load_error_schema():
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "error_envelope.schema.json"
    with schema_path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def test_error_envelope_schema_validation():
    schema = load_error_schema()
    validator = Draft202012Validator(schema)

    payload = {
        "error": {
            "code": "NOT_FOUND",
            "reason": "resource_missing",
            "message": "Resource not found",
            "path": "/__not_found__",
            "trace_id": "trace-123"
        }
    }

    validator.validate(payload)
