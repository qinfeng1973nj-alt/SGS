from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _pick_trace_id(resp):
    return resp.headers.get("X-Trace-Id")

def test_generates_trace_id_when_missing():
    resp = client.get("/health")
    assert resp.status_code in (200, 404)
    tid = _pick_trace_id(resp)
    assert tid is not None
    assert tid.strip() != ""

def test_prefers_x_trace_id_over_x_request_id():
    resp = client.get(
        "/health",
        headers={
            "X-Trace-Id": "trace-preferred-123",
            "X-Request-ID": "request-fallback-456",
        },
    )
    tid = _pick_trace_id(resp)
    assert tid == "trace-preferred-123"

def test_uses_x_request_id_when_x_trace_id_missing():
    resp = client.get("/health", headers={"X-Request-ID": "request-only-789"})
    tid = _pick_trace_id(resp)
    assert tid == "request-only-789"

def test_blank_header_regenerates_trace_id():
    resp = client.get("/health", headers={"X-Trace-Id": "   "})
    tid = _pick_trace_id(resp)
    assert tid is not None
    assert tid.strip() != ""
    assert tid != "   "
